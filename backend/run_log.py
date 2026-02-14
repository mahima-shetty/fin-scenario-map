"""
Run log: one file per app run under backend/logs/.
On next run startup, previous file is removed so only one file exists.
"""
import logging
import os
import glob

RUN_LOG_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "logs")
RUN_LOG_FILE = "run.log"
LOG_NAME = "fin_scenario_map.run"

_run_logger: logging.Logger | None = None
_run_file_handler: logging.FileHandler | None = None


def _ensure_log_dir() -> str:
    os.makedirs(RUN_LOG_DIR, exist_ok=True)
    return RUN_LOG_DIR


def init_run_log() -> None:
    """
    Call once at app startup.
    Removes any existing log files in backend/logs/, then creates the single run log file.
    """
    global _run_file_handler
    _ensure_log_dir()
    pattern = os.path.join(RUN_LOG_DIR, "*")
    for path in glob.glob(pattern):
        try:
            os.remove(path)
        except OSError:
            pass
    log_path = os.path.join(RUN_LOG_DIR, RUN_LOG_FILE)
    logger = get_run_logger()
    if _run_file_handler:
        logger.removeHandler(_run_file_handler)
        _run_file_handler.close()
        _run_file_handler = None
    handler = logging.FileHandler(log_path, encoding="utf-8")
    handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s %(message)s"))
    logger.addHandler(handler)
    _run_file_handler = handler
    logger.info("run log initialized path=%s", log_path)


def get_run_logger() -> logging.Logger:
    """Return the run logger (writes to backend/logs/run.log after init_run_log)."""
    global _run_logger
    if _run_logger is None:
        _run_logger = logging.getLogger(LOG_NAME)
        _run_logger.setLevel(logging.INFO)
    return _run_logger
