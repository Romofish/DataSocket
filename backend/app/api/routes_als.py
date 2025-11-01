from fastapi import APIRouter, UploadFile, File, HTTPException
from typing import Optional, Dict, Any, List
from ..services.als_matrix import extract_matrix

router = APIRouter(prefix="/als", tags=["ALS"])

@router.post("/matrix")
async def parse_matrix(
    als_file: UploadFile = File(...),
    # optional SSD compare payload (FolderOID -> [FormOID,...])
    ssd_folder_forms: Optional[Dict[str, List[str]]] = None
) -> Dict[str, Any]:
    try:
        content = await als_file.read()
        result = extract_matrix(content, ssd_matrix=ssd_folder_forms)
        return result
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"ALS parse error: {e}")
