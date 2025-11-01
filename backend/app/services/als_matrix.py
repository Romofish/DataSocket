from __future__ import annotations
from typing import BinaryIO, Dict, List, Any, Optional, Tuple
import io
import re
import pandas as pd

# --- Public: single entry point you asked for ---
def extract_matrix(
    file: BinaryIO | bytes,
    matrix_sheet: str = "Matrix",
    folder_sheet: str = "Folder",
    form_sheet: str = "Form",
    ssd_matrix: Optional[Dict[str, List[str]]] = None,
) -> Dict[str, Any]:
    """
    Extracts a RAVE ALS visit-form matrix into a normalized structure (folder -> forms[]).
    If `ssd_matrix` is provided as {FolderOID: [FormOID, ...]}, returns a diff block.

    Returns:
    {
      "folders": [
        {
          "folderOID": str,
          "folderName": str | None,
          "forms": [
             {"formOID": str, "formName": str | None}
          ]
        }, ...
      ],
      "diff": {
        "missing_in_db": {FolderOID: [FormOID, ...]},   # in SSD but not in ALS
        "extra_in_db":    {FolderOID: [FormOID, ...]}    # in ALS but not in SSD
      }  # only when ssd_matrix provided
    }
    """
    xls_bytes = file if isinstance(file, (bytes, bytearray)) else file.read()

    # Load sheets (tolerant to slight naming differences)
    xl = pd.ExcelFile(io.BytesIO(xls_bytes))

    def _find_sheet(name: str) -> str:
        candidates = [s for s in xl.sheet_names if s.lower() == name.lower()]
        if candidates:
            return candidates[0]
        # fallback: fuzzy contains
        for s in xl.sheet_names:
            if name.lower() in s.lower():
                return s
        raise ValueError(f"Required sheet '{name}' not found in ALS. Available: {xl.sheet_names}")

    matrix_ws = _find_sheet(matrix_sheet)
    folder_ws = _find_sheet(folder_sheet)
    form_ws   = _find_sheet(form_sheet)

    df_matrix_raw = pd.read_excel(xl, matrix_ws, header=None)
    df_folder_raw = pd.read_excel(xl, folder_ws)
    df_form_raw   = pd.read_excel(xl, form_ws)

    # Build lookup tables for names
    # Try common columns; be forgiving about exact header cases.
    def _get_col(df: pd.DataFrame, options: List[str]) -> Optional[str]:
        lowmap = {c.lower(): c for c in df.columns}
        for opt in options:
            if opt.lower() in lowmap:
                return lowmap[opt.lower()]
        return None

    # Normalize folder meta
    folderOID_col = _get_col(df_folder_raw, ["FolderOID", "Folder OID", "OID"])
    folderName_col = _get_col(df_folder_raw, ["FolderName", "Folder Name", "Name"])
    folder_meta = {}
    if folderOID_col:
        for _, r in df_folder_raw.iterrows():
            oid = str(r.get(folderOID_col, "")).strip()
            if not oid:
                continue
            folder_meta[oid] = str(r.get(folderName_col, "")).strip() if folderName_col else None

    # Normalize form meta
    formOID_col = _get_col(df_form_raw, ["FormOID", "Form OID", "OID"])
    formName_col = _get_col(df_form_raw, ["FormName", "Form Name", "Name"])
    form_meta = {}
    if formOID_col:
        for _, r in df_form_raw.iterrows():
            oid = str(r.get(formOID_col, "")).strip()
            if not oid:
                continue
            form_meta[oid] = str(r.get(formName_col, "")).strip() if formName_col else None

    # ------- Parse Matrix sheet (supports two common layouts) -------
    # Layout A (long format): columns already include FolderOID + FormOID (+ maybe names)
    # Layout B (cross-tab): rows describe forms, columns after a certain point are folders; cells have 'X' markers.

    # Try to identify a header row automatically by looking for tokens like 'FormOID'/'FolderOID'/'Form Name' etc.
    header_row_idx = None
    header_tokens = {"formoid", "form oid", "formname", "form name", "folderoid", "folder oid", "foldername", "folder name"}
    for i in range(min(10, len(df_matrix_raw))):
        row_strs = [str(x).strip().lower() for x in list(df_matrix_raw.iloc[i].values)]
        if any(tok in row_strs for tok in header_tokens):
            header_row_idx = i
            break
    if header_row_idx is None:
        # fallback assume first row is header
        header_row_idx = 0

    df_matrix = pd.read_excel(xl, matrix_ws, header=header_row_idx)
    df_matrix = df_matrix.dropna(how="all").dropna(axis=1, how="all")

    # Find potential identity columns for forms
    m_form_oid_col = _get_col(df_matrix, ["FormOID", "Form OID", "FORM OID", "Form", "Form Oid"])
    m_form_name_col = _get_col(df_matrix, ["FormName", "Form Name", "FORM NAME", "Name"])

    # Find potential identity columns for folders (long format)
    m_folder_oid_col = _get_col(df_matrix, ["FolderOID", "Folder OID", "FOLDER OID", "Folder", "Folder Oid"])
    m_folder_name_col = _get_col(df_matrix, ["FolderName", "Folder Name", "FOLDER NAME"])

    matrix_pairs: List[Tuple[str, str]] = []  # (FolderOID, FormOID)

    if m_folder_oid_col and m_form_oid_col:
        # Layout A: already long-format relationships
        for _, r in df_matrix.iterrows():
            foid = str(r.get(m_folder_oid_col, "")).strip()
            frmid = str(r.get(m_form_oid_col, "")).strip()
            if foid and frmid:
                matrix_pairs.append((foid, frmid))
    else:
        # Layout B: cross-tab with 'X's
        # Heuristic: first 1–3 columns are form identity; the remaining columns are folder columns
        id_cols = [c for c in [m_form_oid_col, m_form_name_col] if c]
        if not id_cols:
            # last-ditch: assume first column is FormOID
            id_cols = [df_matrix.columns[0]]

        folder_cols = [c for c in df_matrix.columns if c not in id_cols]
        # Cell contains an 'X' (case-insensitive) => membership
        def is_marked(val: Any) -> bool:
            if pd.isna(val):
                return False
            s = str(val).strip().lower()
            return s == "x" or s == "1" or s == "yes" or s == "y" or s == "true"

        # We need FormOID for robust mapping; if missing, synthesize from name
        def ensure_form_oid(row: pd.Series) -> str:
            if m_form_oid_col:
                return str(row.get(m_form_oid_col, "")).strip()
            # synthesize from FormName or first id col
            base = str(row.get(m_form_name_col or id_cols[0], "")).strip()
            # Make an OID-safe token
            token = re.sub(r"[^A-Za-z0-9_]+", "_", base).strip("_").upper()
            return token or "FORM_UNKNOWN"

        for _, r in df_matrix.iterrows():
            frmid = ensure_form_oid(r)
            for fc in folder_cols:
                if is_marked(r.get(fc)):
                    # folder column header is treated as FolderOID; try to map to known OIDs if needed
                    foid_guess = str(fc).strip()
                    foid = re.sub(r"\s+", "", foid_guess)  # typical ALS folder headers are already OIDs; compact just in case
                    matrix_pairs.append((foid, frmid))

    # ---- Normalize + enrich with names ----
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
        # de-dup per folder
        if not any(f.get("formOID") == frmid for f in by_folder[foid]["forms"]):
            by_folder[foid]["forms"].append({
                "formOID": frmid,
                "formName": form_meta.get(frmid)
            })

    # Sort for stable outputs
    folders_sorted = sorted(by_folder.values(), key=lambda x: x["folderOID"])
    for f in folders_sorted:
        f["forms"] = sorted(f["forms"], key=lambda x: x["formOID"])

    result = {"folders": folders_sorted}

    # ---- Optional SSD compare ----
    if ssd_matrix is not None:
        # ssd_matrix format: {FolderOID: [FormOID, ...]}
        missing_in_db: Dict[str, List[str]] = {}
        extra_in_db: Dict[str, List[str]] = {}

        als_map = {f["folderOID"]: [x["formOID"] for x in f["forms"]] for f in folders_sorted}

        # In SSD but not in ALS
        for foid, ssd_forms in ssd_matrix.items():
            als_forms = set(als_map.get(foid, []))
            miss = sorted([frm for frm in set(ssd_forms) if frm not in als_forms])
            if miss:
                missing_in_db[foid] = miss

        # In ALS but not in SSD
        for foid, als_forms in als_map.items():
            ssd_forms = set(ssd_matrix.get(foid, []))
            extra = sorted([frm for frm in set(als_forms) if frm not in ssd_forms])
            if extra:
                extra_in_db[foid] = extra

        result["diff"] = {
            "missing_in_db": missing_in_db,
            "extra_in_db": extra_in_db
        }

    return result
