import os

from selenium import webdriver
from selenium.common.exceptions import ElementNotInteractableException
from selenium.webdriver import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.select import Select
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait


def wait_for_element(driver, xpath):
    WebDriverWait(driver, 5).until(
        expected_conditions.visibility_of_element_located((By.XPATH, xpath))
    )


MAIN_URL = "https://dhlottery.co.kr/common.do?method=main"

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
    options.add_argument(f"user-agent={USER_AGENT}")
    options.binary_location = "./chrome_bins/headless-chromium"
    chrome_driver = webdriver.Chrome("./chrome_bins/chromedriver", options=options)
    chrome_driver.get(MAIN_URL)
    return chrome_driver


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
        print("구매한도 초과입니다.")


def lambda_handler(*args, **kwargs):
    chrome_driver = init_driver()

    try:
        print("Init")
        perform_login(
            chrome_driver,
            os.environ["DH_LOTTO_USERNAME"],
            os.environ["DH_LOTTO_PASSWORD"],
        )
        print("Login Done...")
        goto_lotto_buy(chrome_driver)
        print("In Lotto Buy Window...")
        buy_lotto(chrome_driver)
        print("Task Done")
    finally:
        chrome_driver.quit()
