import logging
from device import camera
from config import device, arg_read


def main():
    loglevel = arg_read.get_loglevel()
    ip_cameras = arg_read.get_rtsp_uris()

    if len(ip_cameras) == 0:
        raise Exception("Please set at least one RTSP link.")

    logging.basicConfig(encoding="utf-8", level=loglevel)
    device.check_for_environment(environment="local")

    ip_cam_01 = camera.Camera(device.get_device("CAM_00"), duration=1)
    ip_cam_01.start_camera()
    ip_cam_01.stop_camera()


if __name__ == "__main__":
    main()