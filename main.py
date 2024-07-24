from fastapi import FastAPI  # FastAPI 是一个为你的 API 提供了所有功能的 Python 类。
import uvicorn
import logging
from loguru import logger
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware
import os

from imageToVideo.image_to_video import iv_app

# 这个实例将是创建你所有 API 的主要交互对象。这个 app 同样在如下命令中被 uvicorn 所引用
app = FastAPI()

app.include_router(iv_app, prefix="/iv", tags=["图片生成视频", ])

# 设置允许的源、方法和头部
origins = [
    "http://127.0.0.1",
    "http://localhost",
    "http://localhost:63342",  # 添加你的前端开发服务器地址
]

# 处理跨域
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],  # 允许所有HTTP方法
    allow_headers=["*"],  # 允许所有头部
)

# 配置日志
logging.basicConfig(
    filename='app.log',  # 日志文件名
    filemode='w',  # 写入模式，'w'会覆盖原有内容，'a'则追加
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',  # 日志格式
    datefmt='%Y-%m-%d %H:%M:%S',  # 时间格式
    level=logging.INFO  # 日志级别
)

# 配置logger
logger.add("startup.log", format="{time} {level} {message}", level="INFO")


@app.on_event("startup")
async def startup_event():
    logger.info("FastAPI应用启动")


@app.on_event("shutdown")
async def shutdown_event():
    logger.info("FastAPI应用关闭")


@app.middleware("http")
async def add_csp(request, call_next):
    response = await call_next(request)
    response.headers["Content-Security-Policy"] = "media-src 'self'"
    return response


# 静态文件目录
static_dir = os.path.join(os.path.dirname(__file__), "static")
print(static_dir)
# 检查静态文件目录是否存在
if not os.path.exists(static_dir):
    raise FileNotFoundError(f"The static directory {static_dir} does not exist.")

# 配置静态文件目录
app.mount("/static", StaticFiles(directory=static_dir),
          name="static")

if __name__ == '__main__':
    print("Hello World")

    # 命令行运行：uvicorn testmain:appname --reload
    # 运行 uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True, log_config="log_config.ini")
