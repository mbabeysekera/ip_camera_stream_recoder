import multiprocessing.shared_memory
import cv2
import time
import os
import logging

# import numpy as np
from datetime import datetime
import multiprocessing

logger = logging.getLogger(__name__)


class Camera:
    def __init__(
        self,
        rtsp_link: str,
        device_name: str = "Camera",
        rec_en: bool = False,
        duration: int = 1,
        human_detection: bool = False,
        frame_size: cv2.typing.Size = (960, 540),
        record_path: str = "",
    ) -> None:
        logger.info("Camera initialized as: %s", device_name)
        self.rtsp_link = rtsp_link
        self.device_name = device_name
        self.rec_en = rec_en
        self.duration = duration
        self.stop_stream_capture = False
        self.frame_size = frame_size
        self.human_detection = human_detection
        self.record_path = record_path
        if len(record_path) == 0 and rec_en:
            raise Exception(
                "ERROR | If recording is enabled, record_path must be specified!"
            )

    def __record_config(
        self,
        format: str = "mp4v",
        path: str = "",
    ) -> cv2.VideoWriter:
        logger.info("Recording config - format: %s, save to: %s", format, path)
        if not os.path.exists(path):
            os.mkdir(path)
        date_format = datetime.now().strftime("%d%m%Y_%H%M%S")
        record_name = os.path.join(path, f"{self.device_name}_{date_format}.mp4")
        logger.debug("Recoring name: %s", record_name)
        rec_format = cv2.VideoWriter.fourcc(*format)
        return cv2.VideoWriter(
            filename=record_name, fourcc=rec_format, fps=15.0, frameSize=self.frame_size
        )

    def __enable_human_detection(self) -> cv2.CascadeClassifier:
        self.human_detection = True
        cascade_classifire = cv2.CascadeClassifier("haarcascade_fullbody.xml")
        return cascade_classifire

    def capture_stream(
        self,
        rtsp_link: str,
        rtsp_stream: multiprocessing.Queue,
        stop_event: multiprocessing.Event,
    ):
        # logger.info("RTSP stream initialized for %s", self.device_name)
        capture = cv2.VideoCapture(rtsp_link)
        while stop_event.is_set() != True:
            ret, frame = capture.read()
            if not ret:
                continue
            rtsp_stream.put(frame)
            time.sleep(0.01)
        capture.release()
        while rtsp_stream.empty() != True:
            rtsp_stream.get_nowait()

    def captured_stream_processor(
        self, rtsp_stream: multiprocessing.Queue, stop_event: multiprocessing.Event
    ):
        # logger.info("RTSP stream processor initialized for %s", self.device_name)
        writer = self.__record_config(path=self.record_path)
        self.stop_stream_capture = True
        started_time = time.time()
        if self.human_detection:
            human_detector = self.__enable_human_detection()
            logger.info("Human detection enabled for camera: %s", self.device_name)
        cv2.namedWindow(self.device_name, cv2.WINDOW_NORMAL)
        while True:
            if rtsp_stream.empty() != True:
                custom_window = cv2.resize(rtsp_stream.get(), self.frame_size)
                gray_frame = cv2.cvtColor(custom_window, cv2.COLOR_BGR2GRAY)
                rects = human_detector.detectMultiScale(
                    gray_frame, scaleFactor=1.5, minSize=(50, 50)
                )
                for x, y, w, h in rects:
                    cv2.rectangle(custom_window, (x, y), (x + w, y + h), (0, 255, 0), 2)
                cv2.imshow(self.device_name, custom_window)
                writer.write(custom_window)
            cv2.waitKey(20)
            track_duration = (time.time() - started_time) / 60
            if (track_duration > self.duration) or (self.stop_stream_capture == False):
                stop_event.set()
                break
        writer.release()
        cv2.destroyAllWindows()

    def start_camera(self) -> None:
        logger.info("Camera: %s started.", self.device_name)
        rtsp_stream = multiprocessing.Queue(maxsize=10)
        stop_event = multiprocessing.Event()
        cap_strm = multiprocessing.Process(
            target=self.capture_stream,
            args=(
                self.rtsp_link,
                rtsp_stream,
                stop_event,
            ),
        )
        cap_strm_proc = multiprocessing.Process(
            target=self.captured_stream_processor,
            args=(
                rtsp_stream,
                stop_event,
            ),
        )
        cap_strm.start()
        cap_strm_proc.start()
        cap_strm.join()
        cap_strm_proc.join()

    # def stop_camera(self) -> None:
    #     self.stop_stream_capture = False
    #     logger.info("Camera: %s stopped.", self.device_name)
