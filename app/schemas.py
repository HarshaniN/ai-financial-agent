from pydantic import BaseModel


class QueryRequest(BaseModel):
    question: str


class DatasetPathRequest(BaseModel):
    file_path: str