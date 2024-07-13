import os
import cv2
import time
import queue
import logging
import threading
import multiprocessing
from datetime import datetime

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

    def __stream_reader(
        self,
        main_stream_channel: str,
        sub_stream_channel: str,
        max_retries: int,
        rtsp_queue: multiprocessing.Queue,
        capture_stream_queue: queue.Queue,
        stop_event: multiprocessing.Event,
        high_resolution_cap: multiprocessing.Event,
        low_resolution_cap: multiprocessing.Event,
        recording: multiprocessing.Event,
    ) -> None:
        default_channel = sub_stream_channel
        print("initial channel: " + default_channel)
        capture = cv2.VideoCapture(default_channel)
        retry_counter = 0
        while not stop_event.is_set():
            if high_resolution_cap.is_set() or low_resolution_cap.is_set():
                if high_resolution_cap.is_set() and recording.is_set():
                    default_channel = main_stream_channel
                    high_resolution_cap.clear()
                if low_resolution_cap.is_set() and not recording.is_set():
                    default_channel = sub_stream_channel
                    low_resolution_cap.clear()
                capture.release()
                while capture.isOpened():
                    pass
                capture = cv2.VideoCapture(default_channel)
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
                capture.release()
                time.sleep(1)
                capture = cv2.VideoCapture(default_channel)
                continue
            retry_counter = 0
            if not rtsp_queue.full():
                rtsp_queue.put(frame)
            if not capture_stream_queue.full():
                capture_stream_queue.put(frame)
            time.sleep(0.06)  # This will help to maintain the frame rate at 15fps
        capture.release()
        while not capture_stream_queue.empty():
            capture_stream_queue.get_nowait()
        while not rtsp_queue.empty():
            rtsp_queue.get_nowait()
        time.sleep(1)
        print("__stream_reader stopped")

    def __stream_writer(
        self,
        capture_stream_queue: queue.Queue,
        stop_event: multiprocessing.Event,
        start_recording: multiprocessing.Event,
        high_resolution_cap: multiprocessing.Event,
        low_resolution_cap: multiprocessing.Event,
        recording: multiprocessing.Event,
    ) -> None:
        writer = None
        while not stop_event.is_set():
            time.sleep(0.001)
            if start_recording.is_set():
                if recording.is_set() and writer == None:
                    writer = self.__record_config(path=self.record_path)
                start_recording.clear()
                recording_init_time = time.time()
                while high_resolution_cap.is_set():
                    pass
            if not capture_stream_queue.empty():
                frame = capture_stream_queue.get()
                if recording.is_set() and not start_recording.is_set():
                    if time.time() - recording_init_time < 20:
                        writer.write(frame)
                    else:
                        # print("RECORDING FLAG CLERED")
                        writer.release()
                        while writer.isOpened():
                            pass
                        writer = None
                        recording.clear()
                        # high_resolution_cap.clear()
                        low_resolution_cap.set()
        if writer != None:
            writer.release()
        time.sleep(1)
        print("__stream_writer stopped")

    def capture_stream(
        self,
        main_stream_channel: str,
        sub_stream_channel: str,
        max_retries: int,
        rtsp_queue: multiprocessing.Queue,
        stop_event: multiprocessing.Event,
        high_resolution_cap: multiprocessing.Event,
        low_resolution_cap: multiprocessing.Event,
        start_recording: multiprocessing.Event,
        recording: multiprocessing.Event,
    ):
        capture_stream_queue = queue.Queue(maxsize=10)
        reader_thread = threading.Thread(
            target=self.__stream_reader,
            args=(
                main_stream_channel,
                sub_stream_channel,
                max_retries,
                rtsp_queue,
                capture_stream_queue,
                stop_event,
                high_resolution_cap,
                low_resolution_cap,
                recording,
            ),
        )
        writer_thread = threading.Thread(
            target=self.__stream_writer,
            args=(
                capture_stream_queue,
                stop_event,
                start_recording,
                high_resolution_cap,
                low_resolution_cap,
                recording,
            ),
        )
        reader_thread.start()
        writer_thread.start()
        # reader_thread.join()
        # writer_thread.join()

    def captured_stream_processor(
        self,
        is_recording_enabled: bool,
        rtsp_queue: multiprocessing.Queue,
        stop_event: multiprocessing.Event,
        high_resolution_cap: multiprocessing.Event,
        low_resolution_cap: multiprocessing.Event,
        start_recording: multiprocessing.Event,
        recording: multiprocessing.Event,
    ):
        if self.human_detection:
            human_detector = self.__enable_human_detection()
        # cv2.namedWindow(self.device_name, cv2.WINDOW_NORMAL)
        while not stop_event.is_set():
            if not rtsp_queue.empty():
                frame = rtsp_queue.get()
                custom_window = cv2.resize(frame, (640, 480))
                if self.human_detection and not recording.is_set():
                    gray_frame = cv2.cvtColor(custom_window, cv2.COLOR_BGR2GRAY)
                    detected = human_detector.detectMultiScale(
                        gray_frame, scaleFactor=1.05, minSize=(30, 30)
                    )
                    if len(detected) and is_recording_enabled:
                        recording.set()
                        start_recording.set()
                        high_resolution_cap.set()
                        # print("Motion Detected + " + str(recording.is_set()))
                # cv2.imshow(self.device_name, frame)
                if cv2.waitKey(30) & 0xFF == ord("q"):
                    stop_event.set()
                    time.sleep(1)
                    break
        # cv2.destroyAllWindows()
        print("Video Processor stopped")

    def start_camera(self) -> None:
        logger.info("Camera: %s started.", self.device_name)
        rtsp_queue = multiprocessing.Queue(maxsize=10)
        stop_event = multiprocessing.Event()
        high_resolution_cap = multiprocessing.Event()
        low_resolution_cap = multiprocessing.Event()
        start_recording = multiprocessing.Event()
        recording = multiprocessing.Event()
        cap_strm = multiprocessing.Process(
            target=self.capture_stream,
            args=(
                self.main_stream_channel,
                self.sub_stream_channel,
                self.max_retries,
                rtsp_queue,
                stop_event,
                high_resolution_cap,
                low_resolution_cap,
                start_recording,
                recording,
            ),
        )
        cap_strm_proc = multiprocessing.Process(
            target=self.captured_stream_processor,
            args=(
                self.rec_en,
                rtsp_queue,
                stop_event,
                high_resolution_cap,
                low_resolution_cap,
                start_recording,
                recording,
            ),
        )
        cap_strm.start()
        cap_strm_proc.start()
        # cap_strm.join()
        # cap_strm_proc.join()
