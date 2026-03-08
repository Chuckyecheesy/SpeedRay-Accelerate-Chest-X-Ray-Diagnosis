"""Log submission endpoint for SpeedRay frontend."""

from fastapi import APIRouter
from pydantic import BaseModel
from ...storage import submit_log

router = APIRouter(prefix="/log", tags=["log"])


class LogRequest(BaseModel):
    run_id: str
    study_id: str
    payload: dict


@router.post("/submit")
def submit_log_entry(req: LogRequest):
    return submit_log(req.run_id, req.study_id, req.payload)
