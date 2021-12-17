# -*- coding: utf-8 -*-
# Time       : 2021/7/19 0:58
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:
#       - 扫描、清洗、分类、存储暴露在公网上的sspanel-uim站点
#       - 本项目部分流量需要过墙 请开启系统代理
#       - 检索过程若被人机验证拦截，请手动更换IP
from fire import Fire

from examples import demo

if __name__ == "__main__":
    # TODO 本项目部分流量需要过墙 请开启系统代理
    Fire(demo)
