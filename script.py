from selenium import webdriver
from time import sleep
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import StaleElementReferenceException
from selenium.webdriver.chrome.options import Options
import time
import random
from configuration import phone_number
from generate_message import MessageGemini


class TinderBot():
    def __init__(self):
        options = Options()
        options.add_argument("start-maximized")
        options.add_argument("--disable-blink-features=AutomationControlled")
        options.add_experimental_option("excludeSwitches", ["enable-automation"])
        self.driver = webdriver.Chrome(options=options)
        

    def open_tinder(self):
        time.sleep(random.randint(2, 5))
        self.driver.get('https://tinder.com/pl')
        login_button = WebDriverWait(self.driver, 15).until(EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Zaloguj się")]')))
        login_button.click()
        sleep(15)

        try:
            allow_cookies = self.driver.find_element(By.XPATH, '//button[@class="c1p6lbu0 W(100%) W(a)--ml Mx(4px)--ml My(0)--ml"]')
            allow_cookies.click()
        except:
            print('No cookies popup')
        sleep(5)
        self.sms_login()
        sleep(5)
        try:
            allow_location_button = self.driver.find_element('xpath', '//*[@id="t-1917074667"]/main/div/div/div/div[3]/button[1]')
            allow_location_button.click()
        except:
            print('No location popup')
        sleep(5)
        try:
            notifications_button = self.driver.find_element('xpath', '/html/body/div[2]/main/div/div/div/div[3]/button[2]')
            notifications_button.click()
        except:
            print('No notification popup')


    def sms_login(self):
        # find and click sms login button 
        time.sleep(random.randint(2, 5))
        login_with_sms = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Zaloguj się podając numer telefonu")]')))
        login_with_sms.click()
        # save references to main
        sleep(5)
        base_window = self.driver.window_handles[0]

        try:
            cookies_accept_button = WebDriverWait(self.driver, 5).until(EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Wyrażam zgodę")]')))
            cookies_accept_button.click()
        except:
            print('No cookies')
        sleep(5)
        phone_field = self.driver.find_element(By.NAME, 'phone_number')
        phone_field.send_keys(phone_number)
        phone_field.send_keys(Keys.ENTER)

        print("PROCEED MANUALLY BY ENTERING SMS CODE")
        print('Manual interference is required.')

        # check every second if user has bypassed sms-code barrier
        while not self.is_logged_in():
            time.sleep(9)

        self.driver.switch_to.window(base_window)
        
        try:
            allow_location_button_again = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Zezwól")]')))
            allow_location_button_again.click()
        except:
            print('No location popup')
        try:
            enable_button = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH, '//div[contains(text(), "Na razie nie")]')))
            enable_button.click()
        except:
            print('No notifications popup')


        # checks if user is logged in by checking the url
    def is_logged_in(self):
        return 'app' in self.driver.current_url


        # gather the list of all matches
    def get_matches(self):
        match_profiles = self.driver.find_elements('class name', 'matchListItem')
        print(str(match_profiles))
        message_links = []
        for profile in match_profiles[:3]:
            if profile.get_attribute('href') == 'https://tinder.com/app/my-likes' or profile.get_attribute('href') == 'https://tinder.com/app/likes-you':
                continue
            match_name = profile.find_element(By.CLASS_NAME, 'Ell')
            name = match_name.text
            print(name)
            message_links.append((name, profile.get_attribute('href')))
        return message_links
    

    # send a personalized message to first two match based on bio
    def send_messages_to_matches(self):
        links = self.get_matches()
        for name, link in links:
            self.driver.get(link)
            try:
                bio = WebDriverWait(self.driver, 10).until(EC.presence_of_element_located((By.XPATH,'//*[@id="u-1419960890"]/div/div[1]/div/main/div[1]/div/div/div/div[2]/div/div/div/div/div[2]/div[2]/div'))).text
            except:
                bio = ":)"
            self.send_message(bio, link)


    # generate message based on gemini         
    def send_message(self, bio, link):
        print(bio)
        sleep(5)
        text_area = self.driver.find_element('xpath', '/html/body/div[1]/div/div[1]/div/main/div[1]/div/div/div/div[1]/div/div/div[3]/form/textarea')
        llm = MessageGemini(bio)
        message = llm.model_gemini()
        if not message.strip():
            message = 'Hej. Miło cię poznać :)'
            
        print(message)
        js_code = """
        var elm = arguments[0], txt = arguments[1];
        elm.value += txt;
        elm.dispatchEvent(new Event('change'));
        """
        self.driver.execute_script(js_code, text_area, message)
        text_area.send_keys(" ")
        sleep(10)
        text_area.send_keys(Keys.ENTER)


bot = TinderBot()
bot.open_tinder()
sleep(1)
bot.send_messages_to_matches()