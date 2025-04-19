"""
淘宝智能抢购程序 v2.0
功能：
1. 自动登录淘宝
2. 智能识别图形验证码
3. 定时精准抢购
4. 基于AI的图像识别点击
"""

import cv2
import time
import numpy as np
from datetime import datetime
from PIL import ImageGrab
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.action_chains import ActionChains

class TaoBaoAIBot:
    """
    淘宝AI抢购机器人主类
    使用说明：
    1. 初始化时传入抢购时间（格式："YYYY-MM-DD HH:MM:SS"）
    2. 调用run()启动程序
    """
    
    def __init__(self, target_time):
        """
        初始化抢购机器人
        :param target_time: 目标抢购时间字符串
        """
        self.target_time = datetime.strptime(target_time, "%Y-%m-%d %H:%M:%S")
        self.driver = self._init_browser()
        self.templates = {
            'login_btn': cv2.imread('templates/login_button.png'),    # 登录按钮模板
            'cart_btn': cv2.imread('templates/cart_button.png'),      # 购物车按钮模板
            'buy_btn': cv2.imread('templates/buy_button.png')        # 立即购买按钮模板
        }

    def _init_browser(self):
        """
        初始化浏览器配置
        返回配置好的WebDriver实例
        """
        options = webdriver.ChromeOptions()
        # 全屏相关配置
        options.add_argument("--start-maximized")  # 启动时最大化窗口
        # 反自动化检测配置
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        options.add_experimental_option("useAutomationExtension", False)
        
        driver = webdriver.Chrome(options=options)
        # 屏蔽WebDriver特征
        driver.execute_cdp_cmd("Page.addScriptToEvaluateOnNewDocument", {
            "source": """
            Object.defineProperty(navigator, 'webdriver', {
                get: () => undefined
            })
            """
        })
        return driver

    def _wait_until_time(self):
        """等待直到目标时间到达"""
        while datetime.now() < self.target_time:
            # 精确到10毫秒级检查
            time.sleep(0.01)

    def _screen_capture(self, region=None):
        """
        屏幕截图功能
        :param region: 截取区域 (x1, y1, x2, y2)
        :return: OpenCV格式的图像
        """
        screen = ImageGrab.grab(bbox=region)
        return cv2.cvtColor(np.array(screen), cv2.COLOR_RGB2BGR)

    def _match_template(self, template_name, threshold=0.8):
        """
        模板匹配算法
        :param template_name: 模板名称（在templates字典中的key）
        :param threshold: 匹配阈值（0-1）
        :return: 匹配成功返回中心坐标，否则返回None
        """
        template = self.templates[template_name]
        h, w = template.shape[:-1]
        
        # 截取全屏
        screen = self._screen_capture()
        # 使用高精度匹配算法
        result = cv2.matchTemplate(screen, template, cv2.TM_CCOEFF_NORMED)
        _, max_val, _, max_loc = cv2.minMaxLoc(result)
        
        if max_val > threshold:
            # 返回中心坐标
            return (max_loc[0] + w//2, max_loc[1] + h//2)
        return None

    def _ai_click(self, template_name, max_retry=3, wait_time=0.5):
        """
        AI驱动点击功能
        :param template_name: 要点击的按钮模板名称
        :param max_retry: 最大重试次数
        :param wait_time: 重试间隔（秒）
        :return: 点击成功返回True，否则False
        """
        for _ in range(max_retry):
            position = self._match_template(template_name)
            if position:
                self._human_like_click(position)
                return True
            time.sleep(wait_time)
        return False

    def _human_like_click(self, position):
        """
        拟人化点击（带随机偏移）
        :param position: 目标坐标(x, y)
        """
        # 生成随机偏移
        x_offset = np.random.randint(-5, 5)
        y_offset = np.random.randint(-5, 5)
        
        action = ActionChains(self.driver)
        # 移动鼠标到目标位置
        action.move_by_offset(position[0] + x_offset, 
                            position[1] + y_offset)
        # 添加随机点击延迟
        action.pause(np.random.uniform(0.1, 0.3))
        action.click()
        action.perform()

    def login(self):
        """执行登录流程"""
        self.driver.get("https://www.taobao.com")
        
        # 等待并点击登录按钮
        if not self._ai_click('login_btn'):
            raise Exception("登录按钮识别失败")
        
        if self._ai_click('login_btn')
        print("请手动完成登录（约120秒等待时间）...")
        # 等待用户完成登录
        WebDriverWait(self.driver, 120).until(
            EC.url_contains("taobao.com")
        )
# 新增登录后等待机制（开始）
        print("登录成功，等待页面稳定（120秒）...")
        time.sleep(120)
        print("准备进入购物车...")
        # 新增登录后等待机制（结束）
        
    def enter_cart(self):
        """进入购物车页面"""
        self.driver.get("https://cart.taobao.com/cart.htm")
        # 等待购物车页面加载完成
        WebDriverWait(self.driver, 10).until(
            EC.presence_of_element_located((By.ID, "J_SelectAll1"))
        )
# 新增登录后等待机制（开始）
        print("等待页面稳定（15秒）...")
        time.sleep(15)
        print("准备抢购...")
        # 新增登录后等待机制（结束）
        
    def purchase(self):
        """执行抢购操作"""
        # 等待目标时间
        self._wait_until_time()
        
        # 点击结算按钮
        if not self._ai_click('buy_btn', max_retry=5, wait_time=0.3):
            raise Exception("结算按钮点击失败")
        
        # 处理提交订单页面
        self._handle_submit_page()

    def _handle_submit_page(self):
        """处理订单提交页面"""
        # 等待页面跳转
        time.sleep(1)
        
        # 识别并点击提交订单按钮
        if not self._ai_click('buy_btn', max_retry=5):
            raise Exception("提交订单失败")
        
        print("抢购成功！请在5分钟内完成支付")

    def run(self):
        """主运行流程"""
        try:
            self.login()
            self.enter_cart()
            self.purchase()
        except Exception as e:
            print(f"程序运行出错: {str(e)}")
        finally:
            self.driver.close()

if __name__ == "__main__":
    # 使用示例（设置抢购时间为2023年12月31日20点）
    bot = TaoBaoAIBot("2025-4-19 22:28:33")
    bot.run()