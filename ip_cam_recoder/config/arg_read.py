import argparse
import logging

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
# -log LOGLEVEL -uri CAM_RTSP_URI
parser.add_argument(
    "-ll",
    "--logLevel",
    help="Log levels are - INFO, DEBUG, WARNING",
    default="DEBUG",
)
parser.add_argument(
    "-cu",
    "--cameraURLs",
    action="extend",
    nargs="+",
    help="Add IP camera URLs",
)

parser.add_argument(
    "-rp",
    "--recordingPath",
    help="Set the recording destination for camera streams",
    default="/home",
)

parser.add_argument(
    "-dn",
    "--deviceNames",
    action="extend",
    help="Add device name for each IP camera respectively",
    nargs="+",
)

args = parser.parse_args()


def get_log_level() -> str:
    logger.info("Application log level set to: %s", args.logLevel)
    return str(args.logLevel).upper()


def get_rtsp_uris() -> list[str]:
    return args.cameraURLs


def get_recording_path() -> str:
    return args.recordingPath


def get_device_names() -> list[str]:
    return args.deviceNames
