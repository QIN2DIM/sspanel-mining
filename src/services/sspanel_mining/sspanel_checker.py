# -*- coding: utf-8 -*-
# Time       : 2021/12/18 14:59
# Author     : QIN2DIM
# Github     : https://github.com/QIN2DIM
# Description:

from typing import Optional, List, Any
from urllib.parse import urlparse

from cloudscraper.exceptions import CloudflareChallengeError
from requests.exceptions import (
    Timeout,
    ConnectionError,
    SSLError, HTTPError,
    ProxyError,
)

from services.settings import logger
from .sspanel_classifier import SSPanelHostsClassifier


class SSPanelStaffChecker(SSPanelHostsClassifier):
    def __init__(self, docker: Optional[List[Any]] = None, debug: Optional[bool] = True):
        super(SSPanelStaffChecker, self).__init__(docker=docker)

        self.path_register = "/auth/register"
        self.path_tos = "/tos"
        self.path_staff = "/staff"

        # 控制日志输出
        self.debug = debug

        # 上下文通信模版
        _CONTEXT_TEMPLATE = {
            "urlparse().netloc": {
                "loss-statement": False,
                "loss-staff": False,
                "loss-tos": False,
                "rookie": False,
            }
        }

    def _fall_staff_page(self, staff_url: str) -> None:
        response, status_code, soup = self.handle_html(staff_url)

        _loss_staff = True if status_code != 200 else False

        if _loss_staff and self.debug:
            logger.info(self.report(
                message="STAFF",
                url=staff_url,
                status_code=status_code
            ))
        self._protocol_hook(staff_url, "loss_staff", _loss_staff)

    def _fall_tos_page(self, tos_url: str) -> None:
        response, status_code, soup = self.handle_html(tos_url)

        _loss_tos = True if status_code != 200 else False

        if _loss_tos and self.debug:
            logger.warning(self.report(
                message="TOS",
                url=tos_url,
                status_code=status_code
            ))

        self._protocol_hook(tos_url, "loss_tos", _loss_tos)

    def _fall_staff_footer(self, register_url: str) -> None:

        context = {}

        response, status_code, soup = self.handle_html(register_url, allow_redirects=True)

        copyright_ = soup.find("div", class_="simple-footer")
        try:
            copyright_text = copyright_.text.strip()
            context.update({"url": register_url, "copyright": copyright_text, "ok": True})
        except AttributeError:
            pass
        if "sspanel" in response.text.lower():
            pass

        # 转发上下文评价数据
        if context.get("ok"):
            logger.success(self.report(
                message="实例正常",
                url=context["url"],
                copyright=context["copyright"]
            ))
        else:
            logger.error(self.report(
                message="脚注异常",
                url=context["url"],
            ))

    def _fall_rookie(self, url: str) -> None:
        response, status_code, soup = self.handle_html(url)

        # 有趣的模版，有趣的灵魂
        _is_rookie = True if (
                "占位符" in soup.text
                or "。素质三连" in soup.text
                or "CXK" in soup.text
        ) else False

        # 打印日志
        if _is_rookie and self.debug:
            logger.warning(self.report(
                message="新手司机",
                url=url,
                rookie=True
            ))

        # 缓存上下文数据
        self._protocol_hook(url, "rookie", _is_rookie)

    def _protocol_hook(self, url: str, cache_key: str, cache_value: bool) -> None:
        """

        :param url:
        :param cache_key: within [rookie loss-statement loss-staff loss tos]
        :param cache_value:
        :return:
        """
        _hook = urlparse(url)
        self.done.put_nowait({
            f"{_hook.scheme}://{_hook.netloc}": {
                cache_key: cache_value
            },
        })

    def preload(self):
        """
        数据增强

        在docker中拷贝一份子页链接用于广度搜素
        :return:
        """
        _docker = []

        # 数据增强
        for url in self.docker:
            _parse_obj = urlparse(url)
            _url = f"{_parse_obj.scheme}://{_parse_obj.netloc}"
            # 添加审查 path
            for suffix_ in [
                self.path_register,
                self.path_tos,
                self.path_staff
            ]:
                _docker.append(_url + suffix_)
            # 添加主页
            _docker.append(_url)
        # 刷新数据容器缓存
        self.docker = _docker

    def control_driver(self, url: str):
        try:
            if "/tos" in url:
                self._fall_tos_page(url)
            elif "/staff" in url:
                self._fall_staff_page(url)
            elif "/register" in url:
                pass
            else:
                self._fall_rookie(url)

        # 站点被动行为，流量无法过墙
        except ConnectionError:
            logger.error(self.report("流量阻断", url=url))
            return False
        # 站点主动行为，拒绝国内IP访问
        except (SSLError, HTTPError, ProxyError):
            logger.error(self.report("代理异常", url=url))
            return False
        # 未授权站点
        except ValueError:
            logger.critical(self.report(
                message="危险通信",
                context={"url": url, "label": "未授权站点"},
                url=url
            ))
            return False
        # <CloudflareDefense>被迫中断且无法跳过
        except CloudflareChallengeError:
            logger.debug(self.report(
                message="检测失败",
                context={"url": url, "label": "CloudflareDefenseV2"},
                url=url,
                error="<CloudflareDefense>被迫中断且无法跳过"
            ))
            return False
        # 站点负载紊乱或主要服务器已瘫痪
        except Timeout:
            logger.error(self.report("响应超时", url=url))
            return False

    def offload(self) -> list:
        _output_docker = []
        _cache_docker = {}
        while not self.done.empty():
            context: dict = self.done.get()
            for hook_netloc, cache_dict in context.items():
                if not _cache_docker.get(hook_netloc):
                    _cache_docker[hook_netloc] = cache_dict
                else:
                    _cache_docker[hook_netloc].update(cache_dict)
        for hook_netloc, labels in _cache_docker.items():
            _output_docker.append({
                "url": hook_netloc,
                "labels": ";".join([label[0] for label in labels.items() if label[-1]])
            })
        return _output_docker
