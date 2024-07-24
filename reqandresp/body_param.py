from typing import Union, List, Optional

from fastapi import FastAPI, Form, File, UploadFile, Request
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel, Field, ValidationError, field_validator
import uvicorn
from datetime import date

import os


# 类要继承pydantic的BaseModel
class Addr(BaseModel):
    province: str
    city: str


class User(BaseModel):
    name: str
    # 指定规则
    age: int = Field(default=0, lt=100, gt=0)
    birth: Optional[date] = None
    friends: List[int] = []
    description: Union[str, None] = None
    addr: Union[Addr, None] = None  # 类型嵌套

    # 规则函数
    @field_validator('name')
    def name_must_alpha(cls, v):
        assert v.isalpha(), 'name must be alpha'
        return v


# 类型嵌套
class Data(BaseModel):
    users: List[User]


app = FastAPI()

app.mount("/static",StaticFiles(directory="statics"))


@app.post("/data/")
async def create_data(data: Data):
    # 添加数据库
    return data


@app.post("/form")
async def create_data_form(username: str = Form(max_length=16, min_length=8, regex='[a-zA-Z]'),
                           password: str = Form(min_length=8, regex='[a-zA-Z]')):
    print(f"username:{username},password:{password}")
    return {"username": username, "password": password}


# file: bytes = File()：适合小文件上传
@app.post("/files/")
async def create_file(file: bytes = File()):
    print("file:", file)
    return {"file_size": len(file)}


# 多文件上传
@app.post("/multiFiles/")
async def create_files(files: List[bytes] = File()):
    return {"file_sizes": [len(file) for file in files]}


# file: UploadFile：适合大文件上传

@app.post("/uploadFile/")
async def create_upload_file(file: UploadFile):
    with open(f"{file.filename}", 'wb') as f:
        for chunk in iter(lambda: file.file.read(1024), b''):
            f.write(chunk)
    return {"filename": file.filename}


@app.post("/multiUploadFiles/")
async def create_upload_files(files: List[UploadFile]):
    for file in files:
        path = os.path.join("upload", file.filename)
        with open(path, 'wb') as f:
            for line in file.file:
                f.write(line)
    return {"filenames": [file.filename for file in files]}


@app.get("/req")
async def items(request: Request):
    return {
        "请求URL：": request.url,
        "请求ip：": request.client.host,
        "请求宿主：": request.headers.get("user-agent"),
        "cookies": request.cookies,
    }


if __name__ == '__main__':
    uvicorn.run("body_param:app", host="127.0.0.1", port=8000, reload=True)
