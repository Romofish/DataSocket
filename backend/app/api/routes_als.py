from fastapi import APIRouter, UploadFile, File, HTTPException, Query
from typing import Optional, Dict, Any, List
from ..services.als_matrix import extract_matrix, discover_matrix_sheets
import pandas as pd
import io

router = APIRouter(prefix="/als", tags=["ALS"])

@router.post("/matrix")
async def parse_matrix(
    als_file: UploadFile = File(...),
    matrix_oid: Optional[str] = Query(default=None, description="Pick which Matrix to parse; default prefers MASTERDASHBOARD"),
    ssd_folder_forms: Optional[Dict[str, List[str]]] = None
) -> Dict[str, Any]:
    try:
        content = await als_file.read()
        result = extract_matrix(content, matrix_oid=matrix_oid, ssd_matrix=ssd_folder_forms)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"ALS parse error: {e}")


@router.post("/matrices")
async def list_matrices(als_file: UploadFile = File(...)) -> Dict[str, Any]:
    """
    Returns list of available matrices (matrixOID -> sheet) without parsing the matrix itself.
    Useful for driving a UI selector before extraction.
    """
    try:
        content = await als_file.read()
        xl = pd.ExcelFile(io.BytesIO(content))
        mats = discover_matrix_sheets(xl)
        return {"availableMatrices": mats, "preferredDefault": "MASTERDASHBOARD"}
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"ALS matrix discovery error: {e}")
