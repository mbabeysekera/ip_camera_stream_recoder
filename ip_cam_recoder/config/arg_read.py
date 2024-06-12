import argparse
import logging

logger = logging.getLogger(__name__)

parser = argparse.ArgumentParser()
# -log LOGLEVEL -uri CAM_RTSP_URI
parser.add_argument(
    "-log",
    "--loglevel",
    help="Log levels are - INFO, DEBUG, WARNING",
    default="DEBUG",
)
parser.add_argument(
    "-uri",
    "--uri",
    action="extend",
    nargs="+",
    help="Log levels are - INFO, DEBUG, WARNING",
)

args = parser.parse_args()


def get_loglevel() -> str:
    logger.info("Application log level set to: %s", args.loglevel)
    return str(args.loglevel).upper()


def get_rtsp_uris() -> list[str]:
    logger.info("Available RTSP URIs: %s", str(args.uri))
    return args.uri
