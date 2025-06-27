from pydantic import BaseModel
from typing import List


class Person(BaseModel):
    name: str
    relation: str
    occupation: str


class LandDetail(BaseModel):
    survey_number: str
    area: str


class HakkasodPatraRequest(BaseModel):
    relinquishers: List[Person]
    receiver_name: str
    receiver_relation: str
    receiver_occupation: str
    village: str
    district: str
    land_details: List[LandDetail]
    date: str
