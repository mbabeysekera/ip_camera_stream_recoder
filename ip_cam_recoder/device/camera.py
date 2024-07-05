import multiprocessing
import cv2
import time
import os
import logging
import numpy as np
from datetime import datetime, timezone

logger = logging.getLogger(__name__)


class Camera:
    def __init__(
        self,
        main_stream_channel: str,
        sub_stream_channel: str,
        max_retries: int = 5,
        device_name: str = "Camera",
        rec_en: bool = False,
        duration: int = 1,
        human_detection: bool = False,
        frame_size: cv2.typing.Size = (640, 480),
        record_path: str = "",
    ) -> None:
        logger.info("Camera initialized as: %s", device_name)
        self.main_stream_channel = main_stream_channel
        self.sub_stream_channel = sub_stream_channel
        self.max_retries = max_retries
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
        date_format = datetime.now().strftime("%Y-%m-%d_%H%M%S")
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
        main_stream_channel: str,
        sub_stream_channel: str,
        max_retries: int,
        rtsp_queue: multiprocessing.Queue,
        stop_event: multiprocessing.Event,
        alter_resolution: multiprocessing.Event,
    ):
        # logger.info("RTSP stream initialized for %s", self.device_name)
        default_channel = sub_stream_channel
        print("initial channel: " + default_channel)
        capture = cv2.VideoCapture(default_channel)
        retry_counter = 0
        while not stop_event.is_set():
            if alter_resolution.is_set():
                capture.release()
                if default_channel == sub_stream_channel:
                    default_channel = main_stream_channel
                else:
                    default_channel = sub_stream_channel
                print("Altered channel: " + default_channel)
                capture = cv2.VideoCapture(default_channel)
                # time.sleep(0.05)
                alter_resolution.clear()
            ret, frame = capture.read()
            if not ret:
                retry_counter += 1
                if retry_counter > max_retries:
                    print("RTSP Stream is lost!")
                print(
                    "Failed to read frame. connection attempts: %d/%d",
                    retry_counter,
                    max_retries,
                )
                time.sleep(1)
                capture.release()
                capture = cv2.VideoCapture(default_channel)
                continue
            retry_counter = 0
            if not rtsp_queue.full():
                rtsp_queue.put(frame)
            time.sleep(0.04)
        capture.release()
        stop_event.set()
        while not rtsp_queue.empty():
            rtsp_queue.get_nowait()
        print("Capture stopped")

    def captured_stream_processor(
        self,
        is_recording_enabled: bool,
        frame_size: cv2.typing.Size,
        rtsp_queue: multiprocessing.Queue,
        stop_event: multiprocessing.Event,
        alter_resolution: multiprocessing.Event,
    ):
        # logger.info("RTSP stream processor initialized for %s", self.device_name)
        started_time = time.time()
        if self.human_detection:
            human_detector = self.__enable_human_detection()
        # logger.info("Human detection enabled for camera: %s", self.device_name)
        cv2.namedWindow(self.device_name, cv2.WINDOW_NORMAL)
        record_init_time = 0
        recording = False
        while not stop_event.is_set():
            if not rtsp_queue.empty():
                frame = rtsp_queue.get()
                custom_window = cv2.resize(frame, (640, 480))
                if self.human_detection:
                    gray_frame = cv2.cvtColor(custom_window, cv2.COLOR_BGR2GRAY)
                    detected = human_detector.detectMultiScale(
                        gray_frame, scaleFactor=1.05, minSize=(30, 30)
                    )
                if len(detected) and is_recording_enabled:
                    print("Motion Detected")
                    if not recording:
                        writer = self.__record_config(path=self.record_path)
                        recording = True
                        alter_resolution.set()
                    record_init_time = time.time()
                if recording:
                    if (time.time() - record_init_time) < 15:
                        writer.write(frame)
                    else:
                        writer.release()
                        recording = False
                        alter_resolution.set()
                cv2.imshow(self.device_name, frame)
                if cv2.waitKey(10) & 0xFF == ord("q"):
                    stop_event.set()
                    break
            if self.duration != -1:
                track_duration = (time.time() - started_time) / 60
                if track_duration > self.duration:
                    stop_event.set()
                    break
        writer.release()
        cv2.destroyAllWindows()
        print("Writing stopped")

    def start_camera(self) -> None:
        logger.info("Camera: %s started.", self.device_name)
        rtsp_queue = multiprocessing.Queue(maxsize=10)
        stop_event = multiprocessing.Event()
        alter_resolution = multiprocessing.Event()
        cap_strm = multiprocessing.Process(
            target=self.capture_stream,
            args=(
                self.main_stream_channel,
                self.sub_stream_channel,
                self.max_retries,
                rtsp_queue,
                stop_event,
                alter_resolution,
            ),
        )
        cap_strm_proc = multiprocessing.Process(
            target=self.captured_stream_processor,
            args=(
                self.rec_en,
                self.frame_size,
                rtsp_queue,
                stop_event,
                alter_resolution,
            ),
        )
        cap_strm.start()
        cap_strm_proc.start()
        cap_strm.join()
        cap_strm_proc.join()
