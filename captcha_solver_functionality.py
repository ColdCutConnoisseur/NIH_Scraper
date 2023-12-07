

import os
import time
import random

import requests
import assemblyai as aai
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementNotInteractableException
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as ec
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.keys import Keys



aai.settings.api_key = os.environ['AAI_KEY']

transcriber = aai.Transcriber()

AUDIO_LOC = './audio/audio_file.mp3'


class ReCaptchaSolveFail(Exception):
    pass

def random_sleep(low_end, high_end):
    stdzr = 10_000
    low_end *= stdzr
    high_end *= stdzr

    chosen_int = random.randint(low_end, high_end)

    time.sleep(chosen_int / stdzr)

def switch_to_first_recaptcha_iframe(driver):
    #Wait for recaptcha popup
    wait = WebDriverWait(driver, 10)

    try:
        captcha_iframe = wait.until(ec.visibility_of_element_located((By.XPATH, "//iframe[@title='reCAPTCHA']")))
        driver.switch_to.frame(captcha_iframe)
        print("Switched to initial recaptcha iframe!")
    
    except TimeoutException:
        print("Timeout on attempt to switch to recaptcha iframe")
        raise ReCaptchaSolveFail
    
def switch_to_second_recaptcha_iframe(driver):
    wait = WebDriverWait(driver, 10)

    try:
        captcha_iframe = wait.until(ec.visibility_of_element_located((By.XPATH,
                                    "//iframe[@title='recaptcha challenge expires in two minutes']")))
        driver.switch_to.frame(captcha_iframe)
        print("Switched to second captcha iframe!")

    except TimeoutException:
        print("Timeout on attempt to switch to second recaptcha iframe")
        raise ReCaptchaSolveFail

def click_audio_option_button(driver):
    wait = WebDriverWait(driver, 10)

    try:
        audio_button = wait.until(ec.visibility_of_element_located((By.XPATH,
                                    "//button[@class='rc-button goog-inline-block rc-button-audio']")))
        print("Sleeping before clicking 'audio' option...")
        time.sleep(3)
        print("Clicking audio option...")
        driver.execute_script("arguments[0].click();", audio_button)
        #audio_button.click()
        print("Audio option clicked!")
        time.sleep(8)

    except TimeoutException:
        print("Timeout in trying to click audio option of recaptcha")
        raise ReCaptchaSolveFail

def get_audio_source(driver):
    wait = WebDriverWait(driver, 10)

    try:
        audio_element = wait.until(ec.presence_of_element_located((By.XPATH, "//audio[@id='audio-source']")))
        audio_source = audio_element.get_attribute('src')
        return audio_source

    except TimeoutException:
        print("Timeout in attempt to get audio source")
        raise ReCaptchaSolveFail

def download_audio(source):
    """Download audio source for recaptcha solving"""
    print("Downloading audio source...")
    r = requests.get(source)
    
    with open(AUDIO_LOC, 'wb') as f:
        f.write(r.content)
    print("Audio source downloaded!")

def get_audio_source_translate_and_enter(driver):
    """Emulate user sleeps because ReCaptcha flags if you move too quickly"""
    audio_source = get_audio_source(driver)
    download_audio(audio_source)
    
    #Play audio challenge
    wait = WebDriverWait(driver, 10)

    try:
        play_challenge_button = wait.until(ec.visibility_of_element_located((By.XPATH, "//div[@class='rc-audiochallenge-play-button']")))
        print("Sleeping before clicking 'play'...")
        random_sleep(2, 3)
        print("sleep exited")
        play_challenge_button.click()

    except TimeoutException:
        print("Timeout in attempt to find 'play audio challenge button'")
        raise ReCaptchaSolveFail

    print("Getting speech --> text....")
    try:
        as_text = get_text_from_audio(AUDIO_LOC)

    except IndexError:
        print("No solution found for audio file.  Raising Fail...")
        raise ReCaptchaSolveFail
    print("Got text. Sleeping...")

    #User-emulated recognition of speech  
    random_sleep(3, 4)

    try:
        text_box = driver.find_element(By.XPATH, "//input[@id='audio-response']")

    except NoSuchElementException:
        print("NoSuchElement caught in attempt to find Captcha text entry box")
        raise ReCaptchaSolveFail

    try:
        #User-emulated typing
        for char in as_text:
            text_box.send_keys(char)
            random_sleep(0.1, 0.2)

    except ElementNotInteractableException:
        print("Element not Interactable error in call to 'get_audio_source_translate_and_enter' call")
        raise ReCaptchaSolveFail

    print("Clicking 'verify'...")
    wait = WebDriverWait(driver, 10)
    try:
        verify_button = wait.until(ec.visibility_of_element_located((By.XPATH, "//button[@id='recaptcha-verify-button']")))
        driver.execute_script("arguments[0].click();", verify_button)
        print("'Verify' clicked!")

    except TimeoutException:
        print("Timeout in attempt to find 'verify' button in call to 'get_audio_source_translate_and_enter'")
        raise ReCaptchaSolveFail

    driver.switch_to.default_content()

def get_text_from_audio(audio_file_path):
    transcript = transcriber.transcribe(audio_file_path)

    if transcript.error:
        print(transcript.error)

    else:
        print(transcript.text)
        return transcript.text

def solve_captcha(driver, manual_solve=False):
    """Main"""
    if manual_solve:
        user_in = input("Solve captcha then continue")
        if user_in:
            return 0
    
    

    try:
        #Depending on Captcha test you might need this first function
        #switch_to_first_recaptcha_iframe(driver)
        switch_to_second_recaptcha_iframe(driver)
        click_audio_option_button(driver)
        get_audio_source_translate_and_enter(driver)

    except:
        input()