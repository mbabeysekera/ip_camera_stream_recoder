import logging
from device import camera
from config import device, arg_read


def main():
    loglevel: str = arg_read.get_log_level()
    ip_cameras: list[str] = arg_read.get_rtsp_uris()
    recording_path: str = arg_read.get_recording_path()
    device_names: list[str] = arg_read.get_device_names()

    if not ip_cameras and not device_names:
        raise Exception(
            "Please set RTSP link for each camera and device name for each camera."
        )
    if len(device_names) != len(ip_cameras):
        raise Exception("Not enough device names for RTSP links or vice versa.")
    if len(recording_path) == 0:
        raise Exception("Please set the stream recording destination path.")

    logging.basicConfig(encoding="utf-8", level=loglevel)
    # device.check_for_environment(environment="local")

    ip_cam_01 = camera.Camera(
        ip_cameras[0],
        max_retries=5,
        duration=-1,
        human_detection=True,
        device_name=device_names[0],
        rec_en=True,
        record_path=recording_path,
        frame_size=(940, 560),
    )
    ip_cam_01.start_camera()


if __name__ == "__main__":
    main()
