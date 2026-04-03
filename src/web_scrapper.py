from regex import B
# from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
import time
import src.config as config
from structlog import BoundLogger
from selenium_stealth import stealth
from seleniumwire import webdriver
import datetime
import random

class SeleniumScraper:    
    def __init__(self, cfg: config.Config, logger: BoundLogger):
        self.chrome_option = Options()
        self.chrome_option.add_argument("--disable-blink-features=AutomationControlled")
        # self.chrome_option.add_experimental_option("excludeSwitches", ["enable-automation"])
        # self.chrome_option.add_experimental_option('useAutomationExtension', False)
        self.chrome_option.add_argument("user-agent=" + cfg.scrapper.user_agent)
        self.chrome_option.add_argument("--window-size=1920,1080")
        self.chrome_option.add_argument('--user-data-dir=C:\\temp\\chrome_debug_profile')
        self.chrome_option.add_experimental_option("debuggerAddress", "127.0.0.1:9222")

        self.options = {
            'disable_encoding': True,
            'verify_ssl': False,
        }

        self.logger = logger.bind(service="SeleniumScraper")
        
    def scrape(self):
        logger = self.logger.bind(method="scrape")
        logger.info("Starting scraping...")
        
        driver = webdriver.Chrome(
            options=self.chrome_option,
            seleniumwire_options=self.options
        )
        
        actions = ActionChains(driver)
        
        stealth(
            driver,
            languages=["ru"],
            vendor="Google Inc.",
            platform="Win64",
            webgl_vendor="Intel Inc.",
            renderer="Intel Iris OpenGL Engine",
            fix_hairline=True,
        )

        driver.get("https://domclick.ru")
        time.sleep(4 + random.random())
        # WebDriverWait(driver, 10).until(lambda d: d.find_element(By.CLASS_NAME, "btn-root-119-19-5-4"))


        # button = WebDriverWait(driver, 10).until(
        #    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-e2e-id='cookie-alert-accept']"))
        # )
        # button.click()

        # time.sleep(2 + random.random())
        # button = WebDriverWait(driver, 10).until(
        #     EC.element_to_be_clickable((By.XPATH, "//button[.//span[text()='Да, верно']]"))
        # )
        # button.click()

        
        button = WebDriverWait(driver, 10).until(
           EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-e2e-id='main-search-button']"))
        )
        button.click()
        
        driver.quit()
        for request in driver.requests:
            self.logger.debug(f"🔗 {request.method} {request.url}")
            
            self.logger.debug("ЗАГОЛОВКИ ЗАПРОСА:")
            for name, value in request.headers.items():
                self.logger.debug(f"{name}: {value}")

            if request.body:
                self.logger.debug(f"ТЕЛО ЗАПРОСА: {request.body[:500]}")
        
            
    def save_data(serlf):
        pass