from device import camera
from config import device

device.check_for_environment(environment="local")

ip_cam_01 = camera.Camera(device.get_device("CAM_00"), duration=1)
ip_cam_01.start_camera()
ip_cam_01.stop_camera()
