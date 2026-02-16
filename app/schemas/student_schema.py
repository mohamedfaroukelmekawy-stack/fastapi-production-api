from pydantic import BaseModel ,Field
from pydantic_settings import  SettingsConfigDict


class StudenBase(BaseModel):
    name:str=Field(...,min_length=3,max_length=50)
    age:int=Field(...,gt=0,lt=150)
    grade:str=Field(...,min_length=1,max_length=10)



class StudentCreate(StudenBase):
    pass


class StudentUpdate(StudenBase):
    name:str|None=Field(None,min_length=3,max_length=50)
    age:int|None=Field(None,gt=0,lt=150)
    grade:str|None=Field(None,min_length=1,max_length=10)



class StudentOut(StudenBase):
    id:int

    model_config=SettingsConfigDict(from_attributes=True)    
