import os
from typing import Optional

import requests
import uvicorn
from fastapi import APIRouter, File, UploadFile, HTTPException, Form, Query
from fastapi.responses import JSONResponse, StreamingResponse

import celery_task

"""
设计并实现一个 Web 应用程序，允许用户上传图像并接收基于该图像生成的视频。系统必须处理有限内存的约束并模拟资源密集型且具有固定处理时间的人工智能(AI)模型。

celery 启动参数
celery -A image_to_video worker --loglevel=info

对于防止浏览器下载视频，有多种方法，可以把视频转换为流传给前端，或者用CSP
"""

# 创建一个应用
iv_app = APIRouter()

# 图片大小限制
MAX_FILE_SIZE = 5 * 1024 * 1024  # 5MB

def get_static_dir():
    # 获取当前文件的绝对路径
    current_file_path = os.path.abspath(__file__)
    # 获取当前文件所在的目录
    current_dir = os.path.dirname(current_file_path)
    # 上溯到项目根目录（假设静态文件在项目根目录下）
    root_dir = os.path.dirname(current_dir)
    # 返回静态文件目录的绝对路径
    return os.path.join(root_dir, 'static')

@iv_app.post("/upload")
async def upload_image(file: Optional[UploadFile] = File(None), url: Optional[str] = Form(None)):
    """
    上传图像文件或图片URL，并生成视频。
    """
    if file:
        if file.size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large")
        image_data = await file.read()
    elif url:
        response = requests.get(url)
        if response.status_code != 200:
            raise HTTPException(status_code=400, detail="Invalid image URL")
        image_data = response.content
    else:
        raise HTTPException(status_code=400, detail="No file or URL provided")

    location = get_static_dir() + "/videos/"
    task = celery_task.create_video.delay(image_data, location)
    return JSONResponse(content={"task_id": task.id, "url": location + task.id + ".mp4"})


@iv_app.get("/progress/{task_id}")
async def get_progress(task_id: str):
    """
    获取任务的进度。
    """
    progress = celery_task.redis_client.get(f"progress_{task_id}")
    if progress is None:
        return JSONResponse(content={"status": "pending"})
    return JSONResponse(content={"progress": int(progress)})


@iv_app.get("/video")
async def video(video_url: str = Query(..., description="Video url")):
    """
    获取视频文件流。
    """
    # 这里可以根据 video_url 来确定要返回的视频文件
    video_path = video_url

    def generate():
        with open(video_path, "rb") as f:
            data = f.read(1024)
            while data:
                yield data
                data = f.read(1024)

    return StreamingResponse(generate(), media_type="video/mp4")


if __name__ == "__main__":
    # uvicorn reqandresp.image_to_video:iv_app --host 127.0.0.1 --port 8000 --log-config log_config.ini
    uvicorn.run(iv_app, host="127.0.0.1", port=8000, access_log=True)
