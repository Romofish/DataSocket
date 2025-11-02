# file path: /backend/app/api/routes_als.py
from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import Optional, Dict, Any, List
from ..services.als_matrix import extract_matrix, discover_matrix_sheets
import pandas as pd
import io
import logging

router = APIRouter(prefix="/als", tags=["ALS"])
log = logging.getLogger("als")

def _ok(payload: Dict[str, Any]) -> Dict[str, Any]:
    return {"status": "ok", **payload}

@router.post("/matrices")
async def list_matrices(als_file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Returns list of available matrices (matrixOID -> sheet) as JSON.
    """
    try:
        content = await als_file.read()
        if not content:
            raise ValueError("Empty upload")
        xl = pd.ExcelFile(io.BytesIO(content))
        mats = discover_matrix_sheets(xl)
        log.info("Discovered %d matrices from %s", len(mats), als_file.filename)
        return _ok({
            "file_name": als_file.filename,
            "count": len(mats),
            "availableMatrices": mats,
            "preferredDefault": "MASTERDASHBOARD"
        })
    except Exception as e:
        log.exception("ALS matrix discovery error")
        raise HTTPException(status_code=400, detail=f"ALS matrix discovery error: {e}")

@router.post("/matrix")
async def parse_matrix(
    als_file: UploadFile = File(...),
    matrix_oid: Optional[str] = Query(default=None, description="Pick which Matrix to parse; default prefers MASTERDASHBOARD"),
    ssd_folder_forms: Optional[Dict[str, List[str]]] = None
) -> Dict[str, Any]:
    try:
        content = await als_file.read()
        if not content:
            raise ValueError("Empty upload")
        result = extract_matrix(content, matrix_oid=matrix_oid, ssd_matrix=ssd_folder_forms)
        folders = result.get("folders", [])
        n_forms = sum(len(f.get("forms", [])) for f in folders)
        log.info("Parsed matrix=%s: %d folders, %d forms", result.get("meta", {}).get("matrixOID"), len(folders), n_forms)
        # keep original result; just add counters for visibility
        result["meta"] = {**result.get("meta", {}), "folderCount": len(folders), "formCount": n_forms}
        return _ok(result)
    except Exception as e:
        log.exception("ALS parse error")
        raise HTTPException(status_code=400, detail=f"ALS parse error: {e}")

# Optional: very small ping to test server quickly
@router.get("/ping")
def ping() -> Dict[str, Any]:
    return _ok({"message":"pong"})
