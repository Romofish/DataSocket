from __future__ import annotations
from typing import BinaryIO, Dict, List, Any, Optional, Tuple
import io
import re
import warnings
import pandas as pd

# Silence noisy but harmless openpyxl UserWarnings in some RAVE ALS files
warnings.filterwarnings(
    "ignore",
    message=r"File contains an invalid specification for",
    module=r"openpyxl\.reader\.workbook"
)
warnings.filterwarnings(
    "ignore",
    message=r"Defined names for sheet index .* cannot be located",
    module=r"openpyxl\.reader\.workbook"
)

MATRIX_SHEET_DEFAULT = "MASTERDASHBOARD"  # preferred default when present

# ---------- Matrix sheet discovery ----------
def discover_matrix_sheets(xl: pd.ExcelFile) -> List[Dict[str, str]]:
    """
    Return list of available matrix definitions in the workbook.

    Each item is:
      { "matrixOID": str, "sheet": str }

    Rules:
      - 'MASTERDASHBOARD' -> matrixOID 'MASTERDASHBOARD'
      - 'Matrix'          -> matrixOID 'Matrix'
      - 'MatrixN#OID'     -> matrixOID 'OID'  (e.g., 'Matrix11#EPEDD' -> 'EPEDD')
    Sorting:
      - MASTERDASHBOARD (if present)
      - Matrix (if present)
      - Then by the numeric N in 'MatrixN#OID' (ascending)
    """
    items: List[Dict[str, str]] = []
    numbered: List[Tuple[int, str, str]] = []  # (N, OID, sheet)

    for s in xl.sheet_names:
        s_trim = s.strip()
        sl = s_trim.lower()
        if sl == "masterdashboard":
            items.append({"matrixOID": "MASTERDASHBOARD", "sheet": s_trim})
            continue
        if sl == "matrix":
            items.append({"matrixOID": "Matrix", "sheet": s_trim})
            continue
        m = re.match(r"^matrix\s*(\d+)\s*#\s*(.+)$", s_trim, flags=re.IGNORECASE)
        if m:
            n = int(m.group(1))
            oid = m.group(2).strip()
            numbered.append((n, oid, s_trim))

    # sort numbered by N ascending
    for n, oid, sheet in sorted(numbered, key=lambda x: x[0]):
        items.append({"matrixOID": oid, "sheet": sheet})

    # dedupe by matrixOID (first occurrence wins)
    seen = set()
    deduped = []
    for it in items:
        if it["matrixOID"] in seen:
            continue
        deduped.append(it)
        seen.add(it["matrixOID"])
    return deduped


def choose_matrix_sheet(xl: pd.ExcelFile, matrix_oid: Optional[str]) -> str:
    """
    Resolve the worksheet name to parse based on requested matrix_oid.
    Preference order:
      1) exact matrix_oid match (case-insensitive)
      2) MASTERDASHBOARD
      3) Matrix
      4) else raise
    """
    matrices = discover_matrix_sheets(xl)
    if matrix_oid:
        for m in matrices:
            if m["matrixOID"].lower() == matrix_oid.strip().lower():
                return m["sheet"]
    for pref in [MATRIX_SHEET_DEFAULT, "Matrix"]:
        for m in matrices:
            if m["matrixOID"].lower() == pref.lower():
                return m["sheet"]
    raise ValueError(f"No usable Matrix sheet found. Available matrixOIDs: {[m['matrixOID'] for m in matrices]}")


def _find_sheet_fuzzy(xl: pd.ExcelFile, name: str) -> str:
    # exact
    for s in xl.sheet_names:
        if s.strip().lower() == name.strip().lower():
            return s
    # contains
    for s in xl.sheet_names:
        if name.strip().lower() in s.strip().lower():
            return s
    raise ValueError(f"Required sheet '{name}' not found in ALS. Available: {xl.sheet_names}")


def _get_col(df: pd.DataFrame, options: List[str]) -> Optional[str]:
    lowmap = {str(c).strip().lower(): str(c) for c in df.columns}
    for opt in options:
        if opt.strip().lower() in lowmap:
            return lowmap[opt.strip().lower()]
    return None


def _first_header_row(df_raw: pd.DataFrame, probe_rows: int = 30) -> int:
    """
    More tolerant header detector:
      - scans up to `probe_rows`
      - ignores empty/merged-note rows
      - looks for typical tokens
    """
    header_tokens = {
        "formoid", "form oid", "formname", "form name", "draftformname", "draft form name",
        "folderoid", "folder oid", "foldername", "folder name"
    }
    n = min(probe_rows, len(df_raw))
    for i in range(n):
        row_vals = list(df_raw.iloc[i].values)
        # skip rows that are fully blank
        if all((str(x).strip() == "" or pd.isna(x)) for x in row_vals):
            continue
        row_strs = [str(x).strip().lower() for x in row_vals]
        if any(tok in row_strs for tok in header_tokens):
            return i
    # fallback to first non-empty row
    for i in range(n):
        row_vals = list(df_raw.iloc[i].values)
        if not all((str(x).strip() == "" or pd.isna(x)) for x in row_vals):
            return i
    return 0


# --- Public: single entry point ---
def extract_matrix(
    file: BinaryIO | bytes,
    matrix_oid: Optional[str] = None,
    folder_sheet: str = "Folder",
    form_sheet: str = "Form",
    ssd_matrix: Optional[Dict[str, List[str]]] = None,
) -> Dict[str, Any]:
    """
    Extract a RAVE ALS visit-form matrix into a normalized structure (folder -> forms[]).
    - Honors DraftFormName as the canonical form name (exposed as 'formName').
    - Supports multiple matrix sheets; 'matrix_oid' chooses which to parse.

    Returns:
    {
      "meta": {
        "matrixOID": str,
        "sheet": str,
        "availableMatrices": [ {"matrixOID": str, "sheet": str}, ... ]
      },
      "folders": [ { folderOID, folderName, forms: [ {formOID, formName} ... ] } ... ],
      "diff": { ... }  # only if ssd_matrix provided
    }
    """
    xls_bytes = file if isinstance(file, (bytes, bytearray)) else file.read()
    xl = pd.ExcelFile(io.BytesIO(xls_bytes), engine="openpyxl")

    # which matrix
    matrix_ws = choose_matrix_sheet(xl, matrix_oid)
    available = discover_matrix_sheets(xl)

    # load meta sheets (robust dtype=str to avoid 1/True confusion; no NA casting)
    df_folder_raw = pd.read_excel(
        xl, _find_sheet_fuzzy(xl, folder_sheet), engine="openpyxl",
        dtype=str, keep_default_na=False
    )
    df_form_raw   = pd.read_excel(
        xl, _find_sheet_fuzzy(xl, form_sheet), engine="openpyxl",
        dtype=str, keep_default_na=False
    )

    # Folder meta
    folderOID_col  = _get_col(df_folder_raw, ["FolderOID", "Folder OID", "OID"])
    folderName_col = _get_col(df_folder_raw, ["FolderName", "Folder Name", "Name"])
    folder_meta: Dict[str, Optional[str]] = {}
    if folderOID_col:
        for _, r in df_folder_raw.iterrows():
            oid = (r.get(folderOID_col) or "").strip()
            if not oid:
                continue
            folder_meta[oid] = ((r.get(folderName_col) or "").strip() if folderName_col else None)

    # Form meta  —— prefer DraftFormName, then FormName
    formOID_col   = _get_col(df_form_raw, ["FormOID", "Form OID", "OID"])
    formName_col  = _get_col(df_form_raw, ["DraftFormName", "Draft Form Name", "FormName", "Form Name", "Name"])
    form_meta: Dict[str, Optional[str]] = {}
    if formOID_col:
        for _, r in df_form_raw.iterrows():
            oid = (r.get(formOID_col) or "").strip()
            if not oid:
                continue
            form_meta[oid] = ((r.get(formName_col) or "").strip() if formName_col else None)

    # Parse Matrix sheet (robust)
    df_matrix_raw = pd.read_excel(
        xl, matrix_ws, header=None, engine="openpyxl",
        dtype=str, keep_default_na=False
    )

    header_row_idx = _first_header_row(df_matrix_raw, probe_rows=40)

    df_matrix = pd.read_excel(
        xl, matrix_ws, header=header_row_idx, engine="openpyxl",
        dtype=str, keep_default_na=False
    )
    # strip whitespace in headers
    df_matrix.columns = [str(c).strip() for c in df_matrix.columns]
    # drop fully empty rows/cols after trimming
    df_matrix = df_matrix.dropna(how="all").dropna(axis=1, how="all")

    # Identify columns in Matrix sheet (long-format if both FolderOID & FormOID exist)
    m_form_oid_col   = _get_col(df_matrix, ["FormOID", "Form OID", "FORM OID", "Form", "Form Oid"])
    m_form_name_col  = _get_col(df_matrix, ["DraftFormName", "Draft Form Name", "FormName", "Form Name", "FORM NAME", "Name"])
    m_folder_oid_col = _get_col(df_matrix, ["FolderOID", "Folder OID", "FOLDER OID", "Folder", "Folder Oid"])
    # m_folder_name_col not required, but we’ll try to read if present
    m_folder_name_col= _get_col(df_matrix, ["FolderName", "Folder Name", "FOLDER NAME"])

    matrix_pairs: List[Tuple[str, str]] = []  # (FolderOID, FormOID)

    if m_folder_oid_col and m_form_oid_col:
        # Long format: one row per relationship
        for _, r in df_matrix.iterrows():
            foid = (r.get(m_folder_oid_col) or "").strip()
            frmid = (r.get(m_form_oid_col) or "").strip()
            if foid and frmid:
                matrix_pairs.append((foid, frmid))
    else:
        # Crosstab: forms in rows, folders in columns with X/1/Yes/True markers
        id_cols = [c for c in [m_form_oid_col, m_form_name_col] if c] or [df_matrix.columns[0]]
        folder_cols = [c for c in df_matrix.columns if c not in id_cols]

        def is_marked(val: Any) -> bool:
            s = (val or "").strip().lower()
            return s in {"x", "1", "yes", "y", "true"}

        def ensure_form_oid(row: pd.Series) -> str:
            if m_form_oid_col:
                cand = (row.get(m_form_oid_col) or "").strip()
                if cand:
                    return cand
            base = (row.get(m_form_name_col or id_cols[0]) or "").strip()
            token = re.sub(r"[^A-Za-z0-9_]+", "_", base).strip("_").upper()
            return token or "FORM_UNKNOWN"

        for _, r in df_matrix.iterrows():
            frmid = ensure_form_oid(r)
            for fc in folder_cols:
                if is_marked(r.get(fc)):
                    foid_guess = str(fc).strip()
                    foid = re.sub(r"\s+", "", foid_guess)
                    matrix_pairs.append((foid, frmid))

    # Group + enrich
    by_folder: Dict[str, Dict[str, Any]] = {}
    for foid, frmid in matrix_pairs:
        if not foid or not frmid:
            continue
        if foid not in by_folder:
            by_folder[foid] = {
                "folderOID": foid,
                "folderName": folder_meta.get(foid),
                "forms": []
            }
        if not any(f.get("formOID") == frmid for f in by_folder[foid]["forms"]):
            by_folder[foid]["forms"].append({
                "formOID": frmid,
                # Expose as 'formName' but source from DraftFormName when available
                "formName": form_meta.get(frmid)
            })

    folders_sorted = sorted(by_folder.values(), key=lambda x: x["folderOID"])
    for f in folders_sorted:
        f["forms"] = sorted(f["forms"], key=lambda x: x["formOID"])

    result = {
        "meta": {
            "matrixOID": _resolve_matrix_oid_from_sheet(matrix_ws),
            "sheet": matrix_ws,
            "availableMatrices": discover_matrix_sheets(xl),
        },
        "folders": folders_sorted
    }

    # SSD diff (optional)
    if ssd_matrix is not None:
        # Normalize ALS forms to uppercase for case-insensitive compare
        als_map_raw = {f["folderOID"]: [x["formOID"] for x in f["forms"]] for f in folders_sorted}
        als_map_norm: Dict[str, set] = {fo: {str(frm).upper() for frm in frms} for fo, frms in als_map_raw.items()}
        missing_in_db: Dict[str, List[str]] = {}
        extra_in_db: Dict[str, List[str]] = {}

        # ssd_matrix values may already be normalized by caller; ensure uppercase
        ssd_norm: Dict[str, set] = {fo: {str(frm).upper() for frm in frms} for fo, frms in ssd_matrix.items()}

        # Missing: present in SSD but not in ALS
        for foid, ssd_forms in ssd_norm.items():
            als_forms = als_map_norm.get(foid, set())
            miss_norm = sorted([frm for frm in ssd_forms if frm not in als_forms])
            if miss_norm:
                # Return missing using the original (upper) tokens
                missing_in_db[foid] = miss_norm

        # Extra: present in ALS but not in SSD
        for foid, als_forms in als_map_norm.items():
            ssd_forms = ssd_norm.get(foid, set())
            extra_norm = sorted([frm for frm in als_forms if frm not in ssd_forms])
            if extra_norm:
                extra_in_db[foid] = extra_norm

        result["diff"] = {"missing_in_db": missing_in_db, "extra_in_db": extra_in_db}

    return result


def _resolve_matrix_oid_from_sheet(sheet_name: str) -> str:
    s = sheet_name.strip()
    if s.lower() == "masterdashboard":
        return "MASTERDASHBOARD"
    if s.lower() == "matrix":
        return "Matrix"
    m = re.match(r"^matrix\s*(\d+)\s*#\s*(.+)$", s, flags=re.IGNORECASE)
    if m:
        return m.group(2).strip()
    return s
