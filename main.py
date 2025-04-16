import typing
import sys
import argparse
import logging

__APP_DESCRIPTION__ = "A simple CLI tool."

if __name__ == "__main__":

    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(levelname)s - %(message)s",
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler("app.log"),
        ],
    )

    parser = argparse.ArgumentParser(description=__APP_DESCRIPTION__)

    parser.add_argument(
        "--debug",
        action="store_true",
        help="Enable debug mode",
    )
    parser.add_argument(
        "-n", "notification", action="store_true", help="Enable notification"
    )
    parser.add_argument(
        "-p", "--production", action="store_true", help="Enable production mode"
    )

    args = parser.parse_args()

    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        logging.debug("Debug mode enabled")

    if args.production:
        logging.info("Production mode enabled")
