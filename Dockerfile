# 使用官方的Python基础镜像
FROM python:3.9-alpine

# 设置工作目录
WORKDIR /app


# 复制requirements.txt到工作目录
COPY requirements.txt /app

# 安装依赖，包括Celery
RUN pip install --no-cache-dir -r requirements.txt

# 复制项目代码到工作目录
COPY . /app

# 给 start.sh 添加执行权限
RUN chmod 777 /app/start.sh

# 设置环境变量（可选，例如设置FastAPI的环境为开发模式）
ENV FASTAPI_ENV=VENV

# 暴露端口
EXPOSE 8000

# 运行命令，这里以uvicorn启动FastAPI应用
# 设置 ENTRYPOINT 为 start.sh
ENTRYPOINT ["/app/start.sh"]
