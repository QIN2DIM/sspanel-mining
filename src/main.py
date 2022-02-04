# -*- coding: utf-8 -*-
# Time       : 2021/7/19 0:58
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description: 扫描、清洗、分类、存储暴露在公网上的SSPanel-Uim站点
from fire import Fire

from services.scaffold import Scaffold

if __name__ == "__main__":
    Fire(Scaffold)
