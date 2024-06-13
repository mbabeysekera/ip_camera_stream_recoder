import cv2
import time
import os
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


class Camera:
    def __init__(
        self,
        rtsp_link: str,
        device_name: str = "Camera",
        rec_en: bool = False,
        duration: int = 1,
    ) -> None:
        logger.info("Camera initialized as: %s", device_name)
        self.rtsp_link: str = rtsp_link
        self.device_name: str = device_name
        self.rec_en: bool = rec_en
        self.duration: int = duration
        self.stop_stream_capture: bool = False
        self.frame_size: cv2.typing.Size = (960, 540)
        self.video: cv2.VideoCapture = cv2.VideoCapture(self.rtsp_link)
        self.output: cv2.VideoWriter

    def record_config(
        self,
        format: str = "mp4v",
        path: str = "D:\ip-cam",
    ) -> None:
        logger.info("Recording config - format: %s, save to: %s", format, path)
        if not os.path.exists(path):
            os.mkdir(path)
        date_format: str = datetime.now().strftime("%d%m%Y_%H%M%S")
        record_name: str = os.path.join(path, f"{self.device_name}_{date_format}.mp4")
        logger.debug("Recoring name: %s", record_name)
        rec_format: int = cv2.VideoWriter.fourcc(*format)
        self.output = cv2.VideoWriter(
            filename=record_name, fourcc=rec_format, fps=10.0, frameSize=self.frame_size
        )

    def start_camera(self) -> None:
        logger.info("Camera: %s started.", self.device_name)
        self.stop_stream_capture = True
        started_time = time.time()
        while True:
            _, frame = self.video.read()
            cv2.namedWindow(self.device_name, cv2.WINDOW_NORMAL)
            custom_window = cv2.resize(frame, self.frame_size)
            cv2.imshow(self.device_name, custom_window)
            frame = cv2.resize(frame, self.frame_size)
            self.output.write(frame)
            cv2.waitKey(1)
            track_duration = (time.time() - started_time) / 60
            if (track_duration > self.duration) or (self.stop_stream_capture == False):
                break

    def stop_camera(self) -> None:
        self.stop_stream_capture = False
        self.output.release()
        self.video.release()
        cv2.destroyAllWindows()
        logger.info("Camera: %s stopped.", self.device_name)
