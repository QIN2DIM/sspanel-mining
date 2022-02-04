import random
import sys
import time

from selenium.common.exceptions import (
    NoSuchElementException,
    ElementClickInterceptedException
)
from selenium.webdriver import Chrome
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from tqdm import tqdm

from services.utils import get_ctx
from .exceptions import CollectorSwitchError


class SSPanelHostsCollector:
    def __init__(
            self,
            path_file_txt: str,
            silence: bool = True,
            debug: bool = False,
    ):
        """

        :param path_file_txt:
        :param silence:
        :param debug:
        """
        # 筛选 Malio 站点
        self._QUERY = "由 @editXY 修改适配。"

        # 全量搜集
        # self._QUERY = 'inurl:staff "SSPanel V3 Mod UIM"'

        self.GOOGLE_SEARCH_API = f'https://www.google.com.hk/search?q="{self._QUERY}"&filter=0'
        self.path_file_txt = path_file_txt
        self.debug = debug
        self.silence = silence
        self.page_num = 1

    @staticmethod
    def _down_to_api(api: Chrome, search_query: str):
        """检索关键词并跳转至相关页面"""
        while True:
            try:
                input_tag = api.find_element(By.XPATH, "//input[@name='q']")
                try:
                    input_tag.click()
                # 无头模式运行会引发错误
                except ElementClickInterceptedException:
                    pass
                input_tag.clear()
                input_tag.send_keys(search_query)
                input_tag.send_keys(Keys.ENTER)
                break

            except NoSuchElementException:
                time.sleep(0.5)
                continue

    @staticmethod
    def _page_switcher(api: Chrome, is_home_page: bool = False):
        start_time = time.time()
        # 首页 -> 第二页
        if is_home_page:
            while True:
                try:
                    ActionChains(api).send_keys(Keys.END).perform()
                    time.sleep(0.5)
                    api.find_element(By.XPATH, "//a[@id='pnnext']").click()
                    break
                except NoSuchElementException:
                    # 检测到到流量拦截 主动抛出异常并采取备用方案
                    if "sorry" in api.current_url:
                        raise CollectorSwitchError
                    time.sleep(0.5)
                    api.refresh()
                    continue
        # 第二页 -> 第N页
        else:
            while True:
                try:
                    ActionChains(api).send_keys(Keys.END).perform()
                    time.sleep(0.5)
                    page_switchers = api.find_elements(By.XPATH, "//a[@id='pnnext']")
                    next_page_bottom = page_switchers[-1]
                    next_page_bottom.click()
                    break
                except (NoSuchElementException, IndexError):
                    time.sleep(0.5)
                    # 检测到到流量拦截 主动抛出异常并采取备用方案
                    if "sorry" in api.current_url:
                        raise CollectorSwitchError
                    # 最后一页
                    if time.time() - start_time > 5:
                        break
                    continue

    def _page_tracking(self, api: Chrome, ignore_filter=True):
        next_obj = None
        start_time = time.time()
        while True:
            try:
                ActionChains(api).send_keys(Keys.END).perform()
                time.sleep(0.5)
                next_obj = api.find_element(By.XPATH, "//a[@id='pnnext']")
                break
            except NoSuchElementException:
                time.sleep(0.5)
                # 检测到到流量拦截 主动抛出异常并采取备用方案
                if "sorry" in api.current_url:
                    # windows调试环境中，手动解决 CAPTCHA
                    if 'win' in sys.platform and not self.silence:
                        input("\n--> 遭遇拦截，本开源代码未提供相应解决方案。\n"
                              "--> 请开发者手动处理 reCAPTCHA 并于控制台输入任意键继续执行程序\n"
                              f">>>")
                        continue
                    raise CollectorSwitchError
                # 最后一页
                if time.time() - start_time > 5:
                    break
                continue

        if next_obj:
            next_url = next_obj.get_attribute("href")
            if ignore_filter:
                next_url = next_url + "&filter=0"
            api.get(next_url)
            return True
        else:
            return False

    def _capture_host(self, api: Chrome):
        time.sleep(1)
        hosts = api.find_elements(
            By.XPATH,
            "//div[contains(@class,'NJjxre')]//cite[@class='iUh30 qLRx3b tjvcx']"
        )

        with open(self.path_file_txt, "a", encoding="utf8") as f:
            for host in hosts:
                f.write(f"{host.text.split(' ')[0].strip()}/auth/register\n")

    def reset_page_num(self, api: Chrome):
        try:
            result = api.find_element(By.XPATH, "//div[@id='result-stats']")
            tag_num = result.text.strip().split(" ")[1]
            self.page_num = int(int(tag_num) / 10) + 1 if tag_num else 26
            return self.page_num
        except NoSuchElementException:
            return None

    @staticmethod
    def set_loop_progress(total: int):
        return tqdm(
            total=total,
            desc="SSPanel COLLECTOR",
            ncols=150,
            unit="piece",
            dynamic_ncols=False,
            leave=True,
        )

    def reset_loop_progress(self, api: Chrome, new_status: str = None):
        self.reset_page_num(api=api)
        loop_progress = self.set_loop_progress(self.page_num)
        if new_status:
            loop_progress.set_postfix({"status": new_status})

    def run(self, page_num: int = None, sleep_node: int = 5):
        """

        :param page_num: 期望采集数量
        :param sleep_node: 休眠间隔
        :return:
        """
        self.page_num = 26 if page_num is None else page_num

        loop_progress = self.set_loop_progress(self.page_num)
        loop_progress.set_postfix({"status": "__initialize__"})

        with get_ctx(silence=self.silence) as ctx:
            ctx.get(self.GOOGLE_SEARCH_API)
            self.reset_loop_progress(api=ctx, new_status="__pending__")

            # 获取page_num页的注册链接
            # 正常情况一页10个链接 既共获取page_num * 10个链接
            ack_num = 0
            while True:
                ack_num += 1
                """
                [🛴]采集器
                ___________
                萃取注册链接并保存
                """
                self._capture_host(api=ctx)
                loop_progress.update(1)
                loop_progress.set_postfix({"status": "__collect__"})

                """
                [🛴]翻页控制器
                ___________
                页面追踪
                """
                res = self._page_tracking(api=ctx)
                if ack_num >= self.page_num:
                    self.reset_loop_progress(api=ctx, new_status="__reset__")
                    loop_progress.update(ack_num)
                if not res:
                    return

                """
                [🛴]休眠控制器
                ___________
                每sleep_node页进行一次随机时长的休眠
                """
                if ack_num % sleep_node == 0:
                    tax_ = random.uniform(3, 5)
                    loop_progress.set_postfix({"status": "__sleep__"})
                    time.sleep(tax_)
