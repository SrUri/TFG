from pydantic import BaseModel

class CompareRequest(BaseModel):
    url1: str
    url2: str
    subject_title: str

class CompareSubjectsRequest(BaseModel):
    url1: str
    subject_title1: str
    url2: str
    subject_title2: str