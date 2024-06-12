import cv2
import time


class Camera:
    def __init__(self, rtsp_link, rec_en=False, duration=1):
        self.rtsp_link = rtsp_link
        self.rec_en = rec_en
        self.duration = duration
        self.video = cv2.VideoCapture(self.rtsp_link)
        self.stop_stream_capture = False

    def start_camera(self, device_name="Camera"):
        self.stop_stream_capture = True
        started_time = time.time()
        while True:
            _, frame = self.video.read()
            cv2.namedWindow(device_name, cv2.WINDOW_NORMAL)
            custom_window = cv2.resize(frame, (960, 540))
            cv2.imshow(device_name, custom_window)
            cv2.waitKey(1)
            track_duration = (time.time() - started_time) / 60
            if (track_duration > self.duration) or (self.stop_stream_capture == False):
                break

    def stop_camera(self):
        self.stop_stream_capture = False
        self.video.release()
        cv2.destroyAllWindows()
