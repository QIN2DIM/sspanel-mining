# -*- coding: utf-8 -*-
# Time       : 2021/12/17 18:17
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:

import csv
import os.path
import random
import sys
from datetime import datetime

from .config import (
    DIR_OUTPUT_STORE_COLLECTOR,
    DIR_OUTPUT_STORE_CLASSIFIER,
    CHROMEDRIVER_PATH,
    TIME_ZONE_CN,
    logger,

)
from .sspanel_mining.support.sspanel_classifier import SSPanelHostsClassifier
from .sspanel_mining.support.sspanel_collector import SSPanelHostsCollector

__all__ = [
    "create_env", "run_collector",
    "load_sspanel_hosts", "SSPanelHostsClassifier", "SSPanelHostsCollector",
    "output_cleaning_dataset", "PATH_DATASET_TEMPLATE","data_cleaning"

]

# Collector 数据集路径
_FOCUS_SUFFIX = ".txt"
_FOCUS_PREFIX = "dataset"
# 路径模版
PATH_DATASET_TEMPLATE = os.path.join(
    DIR_OUTPUT_STORE_COLLECTOR, _FOCUS_PREFIX + "_{}" + _FOCUS_SUFFIX
)


def create_env(path_file_txt: str) -> bool:
    """
    初始化运行环境

    :param path_file_txt: such as `dataset_2022-01-1.txt`
    :return:
    """
    # 若文件不存在或仅存在空白文件时返回 True
    # 若文件不存在，初始化文件
    if not os.path.exists(path_file_txt):
        with open(path_file_txt, 'w', encoding="utf8"):
            pass
        return True

    # 若文件存在但为空仍返回 True
    with open(path_file_txt, 'r', encoding="utf8") as f:
        return False if f.read() else True


def data_cleaning(path_file_txt: str):
    """
    链接去重

    :param path_file_txt: such as `dataset_2022-01-1.txt`
    :return:
    """

    with open(path_file_txt, "r", encoding="utf8") as f:
        data = {i for i in f.read().split("\n") if i}
    with open(path_file_txt, "w", encoding="utf8") as f:
        for i in data:
            f.write(f"{i}\n")


def run_collector(path_file_txt: str, silence: bool = None, debug: bool = None):
    """

    :param path_file_txt:
    :param silence:
    :param debug:
    :return:
    """

    # 假设的应用场景中，非Windows系统强制无头启动Selenium
    silence_ = bool(silence) if "win" in sys.platform else True

    collector = SSPanelHostsCollector(
        path_file_txt=path_file_txt,
        chromedriver_path=CHROMEDRIVER_PATH,
        silence=silence_,
        debug=bool(debug)
    )

    collector.run()


def load_sspanel_hosts() -> list:
    """
    sspanel-预处理数据集 获取过去X天的历史数据

    :return:
    """
    # 待分类链接
    urls = []

    # 识别并读回 Collector 输出
    for t in os.listdir(DIR_OUTPUT_STORE_COLLECTOR):
        if t.endswith(_FOCUS_SUFFIX) and t.startswith(_FOCUS_PREFIX):
            # 补全路径模版
            path_file_txt = os.path.join(DIR_OUTPUT_STORE_COLLECTOR, t)
            # 读回 Collector 输出
            with open(path_file_txt, "r", encoding="utf8") as f:
                for url in f.read().split("\n"):
                    urls.append(url)

    # 清洗杂质
    urls = {i for i in urls if i}

    # 返回参数
    return list(urls)


def output_cleaning_dataset(dir_output: str, docker: list, path_output: str = None) -> str:
    """
    输出分类/清洗结果

    :param dir_output:
    :param docker:
    :param path_output:
    :return:
    """
    if not docker:
        return ""

    # 规则清洗后导出的数据集路径
    path_output_template = os.path.join(
        DIR_OUTPUT_STORE_CLASSIFIER,
        "mining_{}".format(
            str(datetime.now(TIME_ZONE_CN)).split(".")[0].replace(":", "-")
        )
    )
    path_output_ = f"{path_output_template}.csv" if path_output is None else path_output

    docker = sorted(docker, key=lambda x: x["label"])
    try:
        with open(path_output_, "w", encoding="utf8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["url", "label"])
            for context in docker:
                writer.writerow([context["url"], context["label"]])
        return path_output_
    except PermissionError:
        logger.warning(f"导出文件被占用 - file={path_output_}")
        path_output_ = f"{path_output_template}.{random.randint(1, 10)}.csv"
        return output_cleaning_dataset(dir_output, docker, path_output=path_output_)
