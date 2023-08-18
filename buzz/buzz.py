import faulthandler
import logging
import multiprocessing
import os
import platform
import sys
from typing import TextIO

from appdirs import user_log_dir

# Check for segfaults if not running in frozen mode
if getattr(sys, "frozen", False) is False:
    faulthandler.enable()

# Sets stderr to no-op TextIO when None (run as Windows GUI).
# Resolves https://github.com/chidiwilliams/buzz/issues/221
if sys.stderr is None:
    sys.stderr = TextIO()

# Adds the current directory to the PATH, so the ffmpeg binary get picked up:
# https://stackoverflow.com/a/44352931/9830227
app_dir = getattr(sys, "_MEIPASS", os.path.dirname(os.path.abspath(__file__)))
os.environ["PATH"] += os.pathsep + app_dir

# Add the app directory to the DLL list: https://stackoverflow.com/a/64303856
if platform.system() == "Windows":
    os.add_dll_directory(app_dir)


def main():
    if platform.system() == "Linux":
        multiprocessing.set_start_method("spawn")

    # Fixes opening new window when app has been frozen on Windows:
    # https://stackoverflow.com/a/33979091
    multiprocessing.freeze_support()

    log_dir = user_log_dir(appname="Buzz")
    os.makedirs(log_dir, exist_ok=True)

    log_format = (
        "[%(asctime)s] %(module)s.%(funcName)s:%(lineno)d %(levelname)s -> %(message)s"
    )
    logging.basicConfig(
        filename=os.path.join(log_dir, "logs.txt"),
        level=logging.DEBUG,
        format=log_format,
    )

    if getattr(sys, "frozen", False) is False:
        stdout_handler = logging.StreamHandler(sys.stdout)
        stdout_handler.setLevel(logging.DEBUG)
        stdout_handler.setFormatter(logging.Formatter(log_format))
        logging.getLogger().addHandler(stdout_handler)

    from buzz.cli import parse_command_line
    from buzz.gui import Application

    app = Application()
    parse_command_line(app)
    sys.exit(app.exec())
