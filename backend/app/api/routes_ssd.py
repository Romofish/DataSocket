"""
SSD Compare API
Accepts an ALS file and an SSD specification file (JSON/CSV/XLSX),
parses them, compares FolderOID/FormOID pairs, and returns differences.

Response keys include both snake_case and camelCase for convenience:
  - diff: { missing_in_db, extra_in_db }
  - missingInDB, extraInDB (aliases of the above)
"""
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import Dict, Any, List, Optional
from ..services.als_matrix import extract_matrix
import pandas as pd
import json
import io

router = APIRouter(prefix="/ssd", tags=["SSD"])


def _map_from_rows(df: pd.DataFrame) -> Dict[str, List[str]]:
    # normalize column names for lookup
    cols = {str(c).strip().lower(): str(c) for c in df.columns}
    def pick(options: List[str]) -> Optional[str]:
        for opt in options:
            k = opt.strip().lower()
            if k in cols:
                return cols[k]
        return None

    fo_col = pick(["FolderOID", "Folder OID"])  # type: ignore[arg-type]
    # Form OID may be labeled just "OID" in SSD exports
    fm_col = pick(["OID", "FormOID", "Form OID"])      # type: ignore[arg-type]
    if not fo_col or not fm_col:
        return {}
    out: Dict[str, List[str]] = {}
    seen: Dict[str, set] = {}
    for _, r in df.iterrows():
        fo = str(r.get(fo_col) or "").strip()
        fm = str(r.get(fm_col) or "").strip()
        if not fo or not fm:
            continue
        # normalize for robust comparison (case-insensitive)
        fm_norm = fm.upper()
        fo_norm = fo.upper()
        if fo_norm not in seen:
            seen[fo_norm] = set()
        if fm_norm not in seen[fo_norm]:
            seen[fo_norm].add(fm_norm)
    for k, v in seen.items():
        out[k] = sorted(v)
    return out


def _parse_ssd_upload(content: bytes, filename: str) -> Dict[str, List[str]]:
    name = filename.lower()
    # JSON path
    if name.endswith(".json"):
        try:
            obj = json.loads(content.decode("utf-8"))
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")
        if isinstance(obj, dict):
            out: Dict[str, List[str]] = {}
            for k, v in obj.items():
                if isinstance(v, list):
                    out[str(k)] = sorted({str(x).upper() for x in v})
            return out
        if isinstance(obj, list):
            try:
                df = pd.DataFrame(obj)
            except Exception as e:
                raise HTTPException(status_code=400, detail=f"Invalid JSON rows: {e}")
            return _map_from_rows(df)
        raise HTTPException(status_code=400, detail="Unsupported JSON structure for SSD")

    # CSV path
    if name.endswith(".csv"):
        try:
            df = pd.read_csv(io.BytesIO(content), dtype=str, keep_default_na=False)
            return _map_from_rows(df)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid CSV: {e}")

    # Excel path
    if name.endswith(".xlsx") or name.endswith(".xls"):
        try:
            df = pd.read_excel(io.BytesIO(content), engine="openpyxl", dtype=str, keep_default_na=False)
            return _map_from_rows(df)
        except Exception as e:
            raise HTTPException(status_code=400, detail=f"Invalid Excel file: {e}")

    raise HTTPException(status_code=400, detail="Unsupported SSD file format; use JSON, CSV, or XLSX")


@router.post("/compare")
async def compare(
    als_file: UploadFile = File(...),
    ssd_file: UploadFile = File(...),
    matrix_oid: Optional[str] = Query(default=None)
) -> Dict[str, Any]:
    try:
        als_bytes = await als_file.read()
        ssd_bytes = await ssd_file.read()
        if not als_bytes:
            raise HTTPException(status_code=400, detail="ALS file is empty")
        if not ssd_bytes:
            raise HTTPException(status_code=400, detail="SSD file is empty")

        ssd_map = _parse_ssd_upload(ssd_bytes, ssd_file.filename or "")
        # Reuse extract_matrix to compute diff
        parsed = extract_matrix(als_bytes, matrix_oid=matrix_oid, ssd_matrix=ssd_map)
        diff = parsed.get("diff", {"missing_in_db": {}, "extra_in_db": {}})
        folders = parsed.get("folders", [])
        n_forms = sum(len(f.get("forms", [])) for f in folders)
        return {
            "status": "ok",
            "meta": parsed.get("meta", {}),
            "counts": {"folders": len(folders), "forms": n_forms},
            "diff": diff,
            # camelCase aliases
            "missingInDB": diff.get("missing_in_db", {}),
            "extraInDB": diff.get("extra_in_db", {}),
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"SSD compare error: {e}")
