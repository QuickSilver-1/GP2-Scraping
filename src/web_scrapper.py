from regex import B
# from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.remote import webelement
import time
import src.config as config
from structlog import BoundLogger
from selenium_stealth import stealth
from seleniumwire import webdriver
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
        self.driver = driver
                
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
        time.sleep(2 + random.random())
        # WebDriverWait(driver, 10).until(lambda d: d.find_element(By.CSS_SELECTOR, "button[data-e2e-id='cookie-alert-accept']"))

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
        
        time.sleep(random.uniform(1.2, 1.5))
        
        main_tab = driver.current_window_handle
        offset = 0
        count = 1
        while True:
            cards = driver.find_elements(By.CSS_SELECTOR, "a.sQ7Tu")[offset:]
            offset = len(cards)
            for i in range(len(cards)):
                WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a.sQ7Tu"))
                )
                
                card = cards[i]
                
                driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", card)
                time.sleep(random.uniform(0.3, 0.7))
                
                self.__move_mouse_smoothly(card)
                time.sleep(random.uniform(1, 3))
                for handle in driver.window_handles:
                    if handle != main_tab:
                        driver.switch_to.window(handle)
                        driver.close()
                
                driver.switch_to.window(main_tab)
                
            if count%2 == 0:
                button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, "button[data-e2e-id='next-offers-button']"))
                )
                
                button.click()
                time.sleep(random.uniform(1.2, 1.5))
    
            count += 1
        
        driver.quit()
        for request in driver.requests:
            self.logger.debug(f"🔗 {request.method} {request.url}")
            
            self.logger.debug("ЗАГОЛОВКИ ЗАПРОСА:")
            for name, value in request.headers.items():
                self.logger.debug(f"{name}: {value}")

            if request.body:
                self.logger.debug(f"ТЕЛО ЗАПРОСА: {request.body[:500]}")
        
            
    def save_data(self):
        pass

    def __move_mouse_smoothly(self, element: webelement.WebElement) -> None:
        actions = ActionChains(self.driver)
        
        self.driver.execute_script("arguments[0].scrollIntoView({block: 'center'});", element)
        time.sleep(random.uniform(1, 1.2))
        
        actions.move_to_element(element)
        actions.pause(random.uniform(0.1, 0.3))
        actions.click()
        actions.perform()