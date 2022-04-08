# -*- coding: utf-8 -*-
# Time       : 2022/1/16 0:27
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
import sys
from typing import Optional

from loguru import logger
from selenium.webdriver import ChromeOptions, Chrome
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager


class InitLog:
    @staticmethod
    def init_log(**sink_path):
        event_logger_format = (
            "<g>{time:YYYY-MM-DD HH:mm:ss}</g> | "
            "<lvl>{level}</lvl> - "
            # "<c><u>{name}</u></c> | "
            "{message}"
        )
        logger.remove()
        logger.add(
            sink=sys.stdout,
            colorize=True,
            level="DEBUG",
            format=event_logger_format,
            diagnose=False,
        )
        if sink_path.get("error"):
            logger.add(
                sink=sink_path.get("error"),
                level="ERROR",
                rotation="1 week",
                encoding="utf8",
                diagnose=False,
            )
        if sink_path.get("runtime"):
            logger.add(
                sink=sink_path.get("runtime"),
                level="DEBUG",
                rotation="20 MB",
                retention="20 days",
                encoding="utf8",
                diagnose=False,
            )
        return logger


def _set_ctx() -> ChromeOptions:
    options = ChromeOptions()
    options.add_argument("--log-level=3")
    options.add_argument("--lang=zh-CN")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--incognito")
    options.add_argument("--disk-cache")
    return options


def get_ctx(silence: Optional[bool] = None):
    options = ChromeOptions()
    options.add_argument("--log-level=3")
    options.add_argument("--lang=zh-CN")
    if "linux" in sys.platform:
        silence = True
        options.add_argument("--no-sandbox")
        options.add_argument("--disable-dev-shm-usage")
    if silence:
        options.add_argument("--headless")

    # 使用 ChromeDriverManager 托管服务，自动适配浏览器驱动
    service = Service(ChromeDriverManager(log_level=0).install())
    return Chrome(options=options, service=service)  # noqa
