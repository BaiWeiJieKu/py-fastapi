import io
import time
import numpy as np
from PIL import Image
from celery import Celery
from moviepy.editor import ImageClip, concatenate_videoclips
from redis import Redis


# 配置Celery
# celery_app = Celery('tasks', broker='redis://:JBYPcWEQkogI3wRW@test.redis.wealthyhealthy.cn:6379/0', backend='redis://:JBYPcWEQkogI3wRW@test.redis.wealthyhealthy.cn:6379/0')
celery_app = Celery('image_to_video', broker='redis://localhost:26379/0', backend='redis://localhost:26379/0')
celery_app.conf.worker_concurrency = 1  # 设置并发数为1

# 配置Redis
redis_client = Redis(host='localhost', port=26379, db=0)


@celery_app.task(bind=True)
def create_video(self, image_data, location: str):
    """
    图片生成视频任务
    """
    task_id = self.request.id
    redis_client.set(f"progress_{task_id}", 0, ex=60)

    # 开始处理图像数据
    image = Image.open(io.BytesIO(image_data))
    img_array = np.array(image)
    image_clip = ImageClip(img_array).set_duration(5)  # 5秒视频

    # 完成视频创建
    video = concatenate_videoclips([image_clip])
    video_path = location + task_id + ".mp4"
    print(video_path)

    # 写入视频文件
    video.write_videofile(video_path, codec='libx264', fps=24)

    # 模拟一个耗时操作，例如渲染视频
    total_steps = 30  # 代表30秒，每秒一步
    for step in range(total_steps):
        # 模拟工作，这里使用time.sleep代替实际工作
        time.sleep(1)

        # 更新进度状态
        progress = int((step + 1) / total_steps * 100)
        self.update_state(state='PROGRESS', meta={'progress': progress})
        redis_client.set(f"progress_{task_id}", progress)

    redis_client.set(f"progress_{task_id}", 100)
    # 返回最终状态

    return video_path