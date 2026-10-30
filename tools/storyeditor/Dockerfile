# 神雕侠侣 · 剧情编辑器（Docker 镜像）
# 只用 Python 标准库，无需 pip install；仓库通过 compose 挂到 /repo
FROM python:3.12-slim

ENV PYTHONIOENCODING=utf-8 \
    PYTHONUNBUFFERED=1

WORKDIR /app
COPY . /app/storyeditor

EXPOSE 8777

# --mod 指向挂载进来的仓库；容器里靠它反推 tools/shendiao 做校验
CMD ["python", "/app/storyeditor/serve.py", \
     "--host", "0.0.0.0", "--port", "8777", \
     "--mod", "/repo/jyx2/Assets/Mods/shendiao"]
