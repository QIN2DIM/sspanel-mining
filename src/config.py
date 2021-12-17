import os
import sys
from os.path import dirname, join, exists
from sys import platform

import pytz
from loguru import logger

__all__ = [
    "CHROMEDRIVER_PATH", "PROJECT_DATABASE",
    "DIR_OUTPUT_STORE_CLASSIFIER", "DIR_OUTPUT_STORE_COLLECTOR",
    "TIME_ZONE_CN", "TIME_ZONE_NY", "logger"
]
# ---------------------------------------------------
# TODO [√] 项目索引路径定位
# ---------------------------------------------------
# 工程根目录
PROJECT_ROOT = dirname(__file__)

# 定位 chromedriver
CHROMEDRIVER_PATH = join(PROJECT_ROOT, "chromedriver.exe" if "win" in platform else "chromedriver")

# 系统数据库
PROJECT_DATABASE = join(PROJECT_ROOT, "database")

# 运行缓存:采集器输出目录
DIR_OUTPUT_STORE_COLLECTOR = join(PROJECT_DATABASE, "sspanel_hosts")

# 运行缓存:分类器输出目录
DIR_OUTPUT_STORE_CLASSIFIER = join(DIR_OUTPUT_STORE_COLLECTOR, "classifier")
# ---------------------------------------------------
# TODO [√] 运行日志设置
# ---------------------------------------------------
SERVER_DIR_DATABASE_LOG = join(PROJECT_DATABASE, "logs")
event_logger_format = (
    "<g>{time:YYYY-MM-DD HH:mm:ss}</g> | "
    "<lvl>{level}</lvl> - "
    # "<c><u>{name}</u></c> | "
    "{message}"
)
logger.remove()
logger.add(sink=sys.stdout, colorize=True, level="DEBUG", format=event_logger_format)
logger.add(
    sink=join(SERVER_DIR_DATABASE_LOG, "error.log"),
    level="ERROR",
    rotation="1 week",
    encoding="utf8",
)

logger.add(
    sink=join(SERVER_DIR_DATABASE_LOG, "runtime.log"),
    level="DEBUG",
    rotation="1 day",
    retention="20 days",
    encoding="utf8",
)
# ---------------------------------------------------
# TODO [*] 自动调整
# ---------------------------------------------------
# 时区
TIME_ZONE_CN = pytz.timezone("Asia/Shanghai")
TIME_ZONE_NY = pytz.timezone("America/New_York")

# 若chromedriver不在CHROMEDRIVER_PATH指定的路径下 尝试从环境变量中查找路径'
if not exists(CHROMEDRIVER_PATH):
    CHROMEDRIVER_PATH = "chromedriver"

# 目录补全
for _pending in [PROJECT_DATABASE, DIR_OUTPUT_STORE_COLLECTOR, DIR_OUTPUT_STORE_CLASSIFIER]:
    if not exists(_pending):
        os.mkdir(_pending)
