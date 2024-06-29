FROM python:3.11.5 as base

RUN mkdir /home/ip-cam-stream
WORKDIR /app
RUN apt install git
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6  -y
RUN pip install --upgrade pip setuptools wheel

RUN git clone https://github.com/mbabeysekera/ip_camera_stream_recoder.git
WORKDIR /app/ip_camera_stream_recoder
RUN git checkout feature/dockerfile
RUN git fetch
RUN git pull
RUN pip install -r requirements.txt

ENTRYPOINT [ "python", "/app/ip_camera_stream_recoder/ip_cam_recoder/recorder.py" ]