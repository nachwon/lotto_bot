import datetime
import os
import time
from typing import NamedTuple, List

import boto3
from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait

from bs4 import BeautifulSoup


def wait_for_element(driver, xpath):
    WebDriverWait(driver, 5).until(
        expected_conditions.visibility_of_element_located((By.XPATH, xpath))
    )


MAIN_URL = "https://dhlottery.co.kr/common.do?method=main"
MOBILE_MAIN_URL = "https://m.dhlottery.co.kr/common.do?method=main"
MY_PAGE_URL = "https://m.dhlottery.co.kr/myPage.do?method=lottoBuyListView"

XPATH_MAP = {
    "login_page_button": "/html/body/div[1]/header/div[2]/div[2]/form/div/ul/li[1]/a",
    "username_input": '//*[@id="userId"]',
    "password_input": '//*[@id="article"]/div[2]/div/form/div/div[1]/fieldset/div[1]/input[2]',
    "login_button": '//*[@id="article"]/div[2]/div/form/div/div[1]/fieldset/div[1]/a',
    "nav_bar": "/html/body/div[2]",
    "lotto_buy_category": '//*[@id="gnb"]/ul/li[1]',
    "yoengeom": '//*[@id="gnb"]/ul/li[1]/div/ul/li[6]/a',
    "lotto_6_45": '//*[@id="gnb"]/ul/li[1]/div/ul/li[1]/a',
    "lotto_buy_iframe": "/html/body/div/iframe",
    "auto_buy_button": '//*[@id="checkNumGroup"]/div[1]/label',
    "num_to_buy_select": '//*[@id="amoundApply"]',
    "confirm_select_button": '//*[@id="btnSelectNum"]',
    "buy_lotto_button": '//*[@id="btnBuy"]',
    "buy_confirm_button": '//*[@id="closeLayer"]',
}

XPATH_MOBILE = {
    "goto_pension_buy": '//*[@id="slick-slide10"]/div[3]/a',
    "buy_pension_button": '//*[@id="wrapper"]/div/a',
    "choose_numbers": '//*[@id="container"]/div[1]/div[1]/div[4]/div/a',
    "auto_numbers": '//*[@id="popup4"]/article/div[1]/ul/li[2]/div/a[2]',
    "confirm_numbers": '//*[@id="popup4"]/article/div[2]/a',
    "final_pension_buy_button": '//*[@id="container"]/div[1]/div[1]/div[5]/div/a',
    "table_iframe": '//*[@id="lottoBuyList"]',
    "result_table": "/html/body/div/div[1]/div/table",
}

USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_5) AppleWebKit/537.36 "
    "(KHTML, like Gecko) Chrome/67.0.3396.87 Safari/537.36"
)


def init_driver():
    options = Options()
    options.add_argument("--no-sandbox")
    options.add_argument("--headless")
    options.add_argument("--single-process")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--window-size=1920,1080")
    options.add_argument(f"user-agent={USER_AGENT}")
    options.binary_location = "./chrome_bins/headless-chromium"
    chrome_driver = webdriver.Chrome("./chrome_bins/chromedriver", options=options)
    chrome_driver.get(MAIN_URL)
    return chrome_driver


def clear_popups(driver):
    target = driver.window_handles[0]
    driver.switch_to.window(target)


def perform_login(driver, username, password):
    login_page_button = driver.find_element_by_xpath(XPATH_MAP["login_page_button"])
    login_page_button.click()

    user_input = driver.find_element_by_xpath(XPATH_MAP["username_input"])
    user_input.send_keys(username)

    password_input = driver.find_element_by_xpath(XPATH_MAP["password_input"])
    password_input.send_keys(password)

    login_button = driver.find_element_by_xpath(XPATH_MAP["login_button"])
    driver.execute_script("arguments[0].click()", login_button)


def goto_lotto_buy(driver):
    wait_for_element(driver, XPATH_MAP["nav_bar"])
    nav_bar = driver.find_element_by_xpath(XPATH_MAP["nav_bar"])
    lotto_buy_category = driver.find_element_by_xpath(XPATH_MAP["lotto_buy_category"])
    lotto_6_45 = driver.find_element_by_xpath(XPATH_MAP["lotto_6_45"])

    ActionChains(driver).move_to_element(nav_bar).move_to_element(
        lotto_buy_category
    ).move_to_element(lotto_6_45).click().perform()
    window_after = driver.window_handles[1]

    driver.switch_to.window(window_after)


def buy_lotto(driver):
    lotto_buy_iframe = driver.find_element_by_xpath(XPATH_MAP["lotto_buy_iframe"])
    driver.switch_to.frame(lotto_buy_iframe)

    auto_buy_button = driver.find_element_by_xpath(XPATH_MAP["auto_buy_button"])
    auto_buy_button.click()

    selector = Select(driver.find_element_by_xpath(XPATH_MAP["num_to_buy_select"]))
    selector.select_by_value("5")

    confirm_button = driver.find_element_by_xpath(XPATH_MAP["confirm_select_button"])
    confirm_button.click()

    buy_lotto_button = driver.find_element_by_xpath(XPATH_MAP["buy_lotto_button"])
    buy_lotto_button.click()

    alert = driver.switch_to.alert
    alert.accept()

    try:
        buy_confirm_button = driver.find_element_by_xpath(
            XPATH_MAP["buy_confirm_button"]
        )
        buy_confirm_button.click()
    except ElementNotInteractableException:
        print("???????????? ???????????????.")


def go_mobile(driver):
    driver.get(MOBILE_MAIN_URL)


def buy_pension_lotto(driver):
    goto_pension_buy = driver.find_element_by_xpath(XPATH_MOBILE["goto_pension_buy"])
    goto_pension_buy.click()

    buy_pension_button = driver.find_element_by_xpath(
        XPATH_MOBILE["buy_pension_button"]
    )
    buy_pension_button.click()

    choose_numbers = driver.find_element_by_xpath(XPATH_MOBILE["choose_numbers"])
    choose_numbers.click()

    auto_numbers = driver.find_element_by_xpath(XPATH_MOBILE["auto_numbers"])
    auto_numbers.click()

    time.sleep(3)

    confirm_numbers = driver.find_element_by_xpath(XPATH_MOBILE["confirm_numbers"])
    confirm_numbers.click()

    time.sleep(3)

    final_pension_buy_button = driver.find_element_by_xpath(
        XPATH_MOBILE["final_pension_buy_button"]
    )
    final_pension_buy_button.click()

    time.sleep(3)

    alert = driver.switch_to.alert
    alert.accept()

    time.sleep(3)


def get_result_table(driver):
    driver.get(MY_PAGE_URL)

    table_iframe = driver.find_element_by_xpath(XPATH_MOBILE["table_iframe"])
    driver.switch_to.frame(table_iframe)

    result_table = driver.find_element_by_xpath(XPATH_MOBILE["result_table"])
    return result_table.get_attribute("outerHTML")


class WinResult:
    def __init__(self, buy_date, round_num, lotto_type, quantity, result, win_amount, open_date):
        self.buy_date = buy_date
        self.round_num = round_num
        self.lotto_type = lotto_type
        self.quantity = quantity
        self.result = result
        self.win_amount = win_amount
        self.open_date = open_date

    def __repr__(self):
        return f"{self.open_date} {self.round_num} ?????? {self.lotto_type} ??????: {self.result} ??????: {self.win_amount}"

    @classmethod
    def parse_tds(cls, tds) -> "WinResult":
        return cls(*[td.text.strip() for td in tds])

    @property
    def is_win(self):
        return (
            self.open_date == datetime.date.today().strftime("%y-%m-%d")
            and self.result == "??????"
        )

    def to_message(self):
        return str(self)


class WinResultSet:
    def __init__(self, win_results: List[WinResult]):
        self._win_results = win_results
        self._is_win = False

    def __repr__(self):
        return "\n".join([win_result.to_message() for win_result in self._win_results])

    @property
    def is_win(self) -> bool:
        self._is_win = all([win_result.is_win for win_result in self._win_results])
        return self._is_win

    def to_message(self) -> str:
        return str(self)


def parse_table(table) -> WinResultSet:
    soup = BeautifulSoup(table, "html.parser")
    trs = soup.find_all("tr")[1:]
    return WinResultSet([WinResult.parse_tds(tr.find_all("td")) for tr in trs])


def publish_result(message):
    sns = boto3.client("sns")
    sns.publish(
        TopicArn=os.environ["TopicArn"],
        Message=message,
    )


class ChromeDriver:
    def __enter__(self):
        self.driver = init_driver()
        return self.driver

    def __exit__(self, exc_type, exc_val, exc_tb):
        self.driver.quit()


def buy_pensions(*args, **kwargs):
    chrome_driver = init_driver()

    try:
        print("Init")
        perform_login(
            chrome_driver,
            os.environ["DH_LOTTO_USERNAME"],
            os.environ["DH_LOTTO_PASSWORD"],
        )
        print("Login Done...")
        go_mobile(chrome_driver)
        print("In Lotto Buy Window...")
        buy_pension_lotto(chrome_driver)
        print("Task Done")

    finally:
        chrome_driver.quit()


def check_pension_wins():
    with ChromeDriver() as driver:
        clear_popups(driver)
        perform_login(
            driver,
            os.environ["DH_LOTTO_USERNAME"],
            os.environ["DH_LOTTO_PASSWORD"],
        )
        go_mobile(driver)
        result_table = get_result_table(driver)
        win_result_set = parse_table(result_table)

    publish_result(win_result_set.to_message())


def lambda_handler(*args, **kwargs):
    check_pension_wins()
