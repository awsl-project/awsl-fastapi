import hmac
from typing import Dict

from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import JSONResponse
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials

from config import settings, wb_headers
from src.db.base import DBClientBase
from src.response_models import Message

router = APIRouter(prefix="/admin", tags=["admin"])
_security = HTTPBearer()


def verify_token(credentials: HTTPAuthorizationCredentials = Depends(_security)):
    if not hmac.compare_digest(credentials.credentials, settings.token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="invalid token",
        )


@router.post("/approve_producers", response_model=bool, responses={404: {"model": Message}},
             dependencies=[Depends(verify_token)])
def approve_producers(uid: str):
    if not uid:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"message": "uid is None"}
        )
    DBClientBase.get_client().approve_producers(uid=uid)
    return True


@router.get("/wb_headers", response_model=Dict[str, str], dependencies=[Depends(verify_token)])
def get_wb_headers():
    return wb_headers.get()


@router.put("/wb_headers", response_model=Dict[str, str], dependencies=[Depends(verify_token)])
def update_wb_headers(headers: Dict[str, str]):
    wb_headers.replace(headers)
    return wb_headers.get()
