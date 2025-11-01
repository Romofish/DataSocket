from __future__ import annotations
from typing import BinaryIO, Dict, List, Any, Optional, Tuple
import io
import re
import pandas as pd

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
      - 'MatrixN#OID'     -> matrixOID 'OID' (e.g., 'Matrix2#SCREENING' -> 'SCREENING')
    """
    out: List[Dict[str, str]] = []
    for s in xl.sheet_names:
      s_lower = s.lower()
      if s_lower == "masterdashboard":
          out.append({"matrixOID": "MASTERDASHBOARD", "sheet": s})
      elif s_lower == "matrix":
          out.append({"matrixOID": "Matrix", "sheet": s})
      else:
          # Match Matrix<number>#<OID>
          m = re.match(r"^Matrix(\d+)?#(.+)$", s, flags=re.IGNORECASE)
          if m:
              oid = m.group(2).strip()
              out.append({"matrixOID": oid, "sheet": s})

    # Deduplicate by matrixOID preserving first occurrence
    seen = set()
    deduped = []
    for item in out:
        if item["matrixOID"] in seen:
            continue
        deduped.append(item)
        seen.add(item["matrixOID"])
    return deduped


def choose_matrix_sheet(xl: pd.ExcelFile, matrix_oid: Optional[str]) -> str:
    """
    Resolve the worksheet name to parse based on requested matrix_oid.
    Preference order:
      1) exact matrix_oid match from discover_matrix_sheets()
      2) MASTERDASHBOARD (if exists)
      3) Matrix (if exists)
      4) else: raise
    """
    matrices = discover_matrix_sheets(xl)
    if matrix_oid:
        for m in matrices:
            if m["matrixOID"].lower() == matrix_oid.lower():
                return m["sheet"]
    # fallback preferences
    for pref in [MATRIX_SHEET_DEFAULT, "Matrix"]:
        for m in matrices:
            if m["matrixOID"].lower() == pref.lower():
                return m["sheet"]
    raise ValueError(f"No usable Matrix sheet found. Available matrixOIDs: {[m['matrixOID'] for m in matrices]}")

# ---------- Helper ----------
def _get_col(df: pd.DataFrame, options: List[str]) -> Optional[str]:
    lowmap = {c.lower(): c for c in df.columns}
    for opt in options:
        if opt.lower() in lowmap:
            return lowmap[opt.lower()]
    return None

# --- Public: single entry point ---
def extract_matrix(
    file: BinaryIO | bytes,
    matrix_oid: Optional[str] = None,   # NEW: let caller choose which matrix to parse (default resolved to MASTERDASHBOARD/Matrix)
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
        "availableMatrices": [ {"matrixOID": str, "sheet": str}, ... ]  # for frontend selectors, if needed
      },
      "folders": [ { folderOID, folderName, forms: [ {formOID, formName} ... ] } ... ],
      "diff": { ... }  # only if ssd_matrix provided
    }
    """
    xls_bytes = file if isinstance(file, (bytes, bytearray)) else file.read()
    xl = pd.ExcelFile(io.BytesIO(xls_bytes))

    # Resolve WHICH matrix to parse
    matrix_ws = choose_matrix_sheet(xl, matrix_oid)
    available = discover_matrix_sheets(xl)

    # Load Folder/Form metadata
    df_folder_raw = pd.read_excel(xl, _find_sheet_fuzzy(xl, folder_sheet))
    df_form_raw   = pd.read_excel(xl, _find_sheet_fuzzy(xl, form_sheet))

    # Folder meta
    folderOID_col  = _get_col(df_folder_raw, ["FolderOID", "Folder OID", "OID"])
    folderName_col = _get_col(df_folder_raw, ["FolderName", "Folder Name", "Name"])
    folder_meta: Dict[str, Optional[str]] = {}
    if folderOID_col:
        for _, r in df_folder_raw.iterrows():
            oid = str(r.get(folderOID_col, "")).strip()
            if not oid:
                continue
            folder_meta[oid] = str(r.get(folderName_col, "")).strip() if folderName_col else None

    # Form meta  —— prefer DraftFormName, then FormName
    formOID_col   = _get_col(df_form_raw, ["FormOID", "Form OID", "OID"])
    # IMPORTANT: DraftFormName first, then Fall back to FormName variants
    formName_col  = _get_col(df_form_raw, ["DraftFormName", "Draft Form Name", "FormName", "Form Name", "Name"])
    form_meta: Dict[str, Optional[str]] = {}
    if formOID_col:
        for _, r in df_form_raw.iterrows():
            oid = str(r.get(formOID_col, "")).strip()
            if not oid:
                continue
            form_meta[oid] = str(r.get(formName_col, "")).strip() if formName_col else None

    # Parse the chosen Matrix worksheet
    df_matrix_raw = pd.read_excel(xl, matrix_ws, header=None)

    # Try to detect header row (up to first 10 rows)
    header_row_idx = None
    header_tokens = {
        "formoid", "form oid", "formname", "form name", "draftformname", "draft form name",
        "folderoid", "folder oid", "foldername", "folder name"
    }
    for i in range(min(10, len(df_matrix_raw))):
        row_strs = [str(x).strip().lower() for x in list(df_matrix_raw.iloc[i].values)]
        if any(tok in row_strs for tok in header_tokens):
            header_row_idx = i
            break
    if header_row_idx is None:
        header_row_idx = 0

    df_matrix = pd.read_excel(xl, matrix_ws, header=header_row_idx)
    df_matrix = df_matrix.dropna(how="all").dropna(axis=1, how="all")

    # Identify columns in Matrix sheet (long-format if both FolderOID & FormOID exist)
    m_form_oid_col   = _get_col(df_matrix, ["FormOID", "Form OID", "FORM OID", "Form", "Form Oid"])
    # Also accept DraftFormName in Matrix sheet if present (some exports include it)
    m_form_name_col  = _get_col(df_matrix, ["DraftFormName", "Draft Form Name", "FormName", "Form Name", "FORM NAME", "Name"])
    m_folder_oid_col = _get_col(df_matrix, ["FolderOID", "Folder OID", "FOLDER OID", "Folder", "Folder Oid"])
    m_folder_name_col= _get_col(df_matrix, ["FolderName", "Folder Name", "FOLDER NAME"])

    matrix_pairs: List[Tuple[str, str]] = []  # (FolderOID, FormOID)

    if m_folder_oid_col and m_form_oid_col:
        # Long format: one row per relationship
        for _, r in df_matrix.iterrows():
            foid = str(r.get(m_folder_oid_col, "")).strip()
            frmid = str(r.get(m_form_oid_col, "")).strip()
            if foid and frmid:
                matrix_pairs.append((foid, frmid))
    else:
        # Crosstab: forms in rows, folders in columns with X/1/Yes/True markers
        id_cols = [c for c in [m_form_oid_col, m_form_name_col] if c] or [df_matrix.columns[0]]
        folder_cols = [c for c in df_matrix.columns if c not in id_cols]

        def is_marked(val: Any) -> bool:
            if pd.isna(val): return False
            s = str(val).strip().lower()
            return s in {"x", "1", "yes", "y", "true"}

        def ensure_form_oid(row: pd.Series) -> str:
            if m_form_oid_col:
                return str(row.get(m_form_oid_col, "")).strip()
            base = str(row.get(m_form_name_col or id_cols[0], "")).strip()
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
                # IMPORTANT: expose 'formName' but source from DraftFormName when available
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

    if ssd_matrix is not None:
        als_map = {f["folderOID"]: [x["formOID"] for x in f["forms"]] for f in folders_sorted}
        missing_in_db: Dict[str, List[str]] = {}
        extra_in_db: Dict[str, List[str]] = {}

        for foid, ssd_forms in ssd_matrix.items():
            als_forms = set(als_map.get(foid, []))
            miss = sorted([frm for frm in set(ssd_forms) if frm not in als_forms])
            if miss:
                missing_in_db[foid] = miss

        for foid, als_forms in als_map.items():
            ssd_forms = set(ssd_matrix.get(foid, []))
            extra = sorted([frm for frm in set(als_forms) if frm not in ssd_forms])
            if extra:
                extra_in_db[foid] = extra

        result["diff"] = {"missing_in_db": missing_in_db, "extra_in_db": extra_in_db}

    return result


# --------- small internal helper(s) ----------
def _find_sheet_fuzzy(xl: pd.ExcelFile, name: str) -> str:
    for s in xl.sheet_names:
        if s.lower() == name.lower():
            return s
    for s in xl.sheet_names:
        if name.lower() in s.lower():
            return s
    raise ValueError(f"Required sheet '{name}' not found in ALS. Available: {xl.sheet_names}")


def _resolve_matrix_oid_from_sheet(sheet_name: str) -> str:
    if sheet_name.lower() == "masterdashboard":
        return "MASTERDASHBOARD"
    if sheet_name.lower() == "matrix":
        return "Matrix"
    m = re.match(r"^Matrix(\d+)?#(.+)$", sheet_name, flags=re.IGNORECASE)
    if m:
        return m.group(2).strip()
    return sheet_name
