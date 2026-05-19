from pydantic import BaseModel, Field


class MessageRequest(BaseModel):
    message: str = Field(..., min_length=1)


class MessageResponse(BaseModel):
    response: str


class StatusResponse(BaseModel):
    status: str = "success"
    message: str


class UploadResponse(StatusResponse):
    filename: str