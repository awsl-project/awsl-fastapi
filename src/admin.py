from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import settings, wb_headers

router = APIRouter(prefix="/admin", tags=["admin"])
_security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(_security)):
    if credentials.credentials != settings.token:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
        )


@router.get("/wb_headers", response_model=Dict[str, str], dependencies=[Depends(verify_token)])
def get_wb_headers():
    return wb_headers.get()


@router.put("/wb_headers", response_model=Dict[str, str], dependencies=[Depends(verify_token)])
def update_wb_headers(headers: Dict[str, str], merge: bool = True):
    """Update Weibo API headers.

    - merge=True (default): merge into existing headers
    - merge=False: replace all headers entirely
    """
    if merge:
        wb_headers.update(headers)
    else:
        wb_headers.replace(headers)
    return wb_headers.get()
