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
        rtsp_link: str,
        max_retries: int = 5,
        device_name: str = "Camera",
        rec_en: bool = False,
        duration: int = 1,
        human_detection: bool = False,
        frame_size: cv2.typing.Size = (640, 480),
        record_path: str = "",
    ) -> None:
        logger.info("Camera initialized as: %s", device_name)
        self.rtsp_link = rtsp_link
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
            filename=record_name, fourcc=rec_format, fps=20.0, frameSize=self.frame_size
        )

    def __enable_human_detection(self) -> cv2.CascadeClassifier:
        self.human_detection = True
        cascade_classifire = cv2.CascadeClassifier("haarcascade_fullbody.xml")
        return cascade_classifire

    def __any_motion_detection(
        self, opt_frame: cv2.typing.MatLike, previous_mean: float
    ) -> tuple[float, float]:
        mean_value = np.mean(opt_frame)
        detection_level = np.abs(mean_value - previous_mean)
        # print(detection_level)
        return (detection_level, mean_value)

    def capture_stream(
        self,
        rtsp_link: str,
        max_retries: int,
        rtsp_queue: multiprocessing.Queue,
        stop_event: multiprocessing.Event,
    ):
        # logger.info("RTSP stream initialized for %s", self.device_name)
        capture = cv2.VideoCapture(rtsp_link)
        # capture = cv2.VideoCapture(0)
        retry_counter = 0
        while not stop_event.is_set():
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
                capture = cv2.VideoCapture(rtsp_link)
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
    ):
        # logger.info("RTSP stream processor initialized for %s", self.device_name)
        # self.stop_stream_capture = True
        started_time = time.time()
        # if self.human_detection:
        #     human_detector = self.__enable_human_detection()
        # logger.info("Human detection enabled for camera: %s", self.device_name)
        previous_mean = 0.0
        # cv2.namedWindow(self.device_name, cv2.WINDOW_NORMAL)
        record_init_time = 0
        recording = False
        while not stop_event.is_set():
            if not rtsp_queue.empty():
                custom_window = cv2.resize(rtsp_queue.get(), frame_size)
                gray_frame = cv2.cvtColor(custom_window, cv2.COLOR_BGR2GRAY)
                detection_level, previous_mean = self.__any_motion_detection(
                    gray_frame, previous_mean
                )
                if detection_level > 0.7 and is_recording_enabled:
                    # print("Motion Detected")
                    if not recording:
                        writer = self.__record_config(path=self.record_path)
                        recording = True
                    record_init_time = time.time()
                if recording:
                    if (time.time() - record_init_time) < 15:
                        writer.write(custom_window)
                    else:
                        writer.release()
                        recording = False
                        record_init_time = 0
                # cv2.imshow(self.device_name, custom_window)
                # cv2.waitKey(10)
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
        cap_strm = multiprocessing.Process(
            target=self.capture_stream,
            args=(
                self.rtsp_link,
                self.max_retries,
                rtsp_queue,
                stop_event,
            ),
        )
        cap_strm_proc = multiprocessing.Process(
            target=self.captured_stream_processor,
            args=(
                self.rec_en,
                self.frame_size,
                rtsp_queue,
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
