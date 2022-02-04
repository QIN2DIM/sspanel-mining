"""
    - 集爬取、清洗、分类与测试为一体的STAFF采集队列自动化更新组件
    - 需要本机启动系统全局代理，或使用“国外”服务器部署
"""
from .sspanel_checker import SSPanelStaffChecker
from .sspanel_classifier import SSPanelHostsClassifier
from .sspanel_collector import SSPanelHostsCollector

__version__ = 'v0.2.2'

__all__ = ['SSPanelHostsCollector', "SSPanelStaffChecker", "SSPanelHostsClassifier"]
