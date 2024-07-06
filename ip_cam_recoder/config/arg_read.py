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
    "-ms",
    "--mainStreamChannel",
    action="extend",
    nargs="+",
    help="Add main stream channel endpoint",
)

parser.add_argument(
    "-ss",
    "--subStreamChannel",
    action="extend",
    nargs="+",
    help="Add sub stream channel endpoint",
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


def get_main_stream_channels() -> list[str]:
    return args.mainStreamChannel


def get_sub_stream_channels() -> list[str]:
    return args.subStreamChannel


def get_formatted_camera_urls() -> list[list[str]]:
    camera_urls = get_rtsp_uris()
    main_stream_channels = get_main_stream_channels()
    sub_stream_channels = get_sub_stream_channels()
    if len(camera_urls) != len(main_stream_channels) and len(camera_urls) != len(
        sub_stream_channels
    ):
        raise Exception(
            "Mismatch in given camera urls and channels. Please check and restart the application."
        )
    formatted_urls: list[list[str]] = []
    for camera_url, main_channel, sub_channel in zip(
        camera_urls,
        main_stream_channels,
        sub_stream_channels,
    ):
        formatted_urls.append([camera_url + main_channel, camera_url + sub_channel])
    return formatted_urls


def get_recording_path() -> str:
    return args.recordingPath


def get_device_names() -> list[str]:
    return args.deviceNames
