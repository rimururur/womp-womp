"""
The solvecaptcha module contains functions for automating CAPTCHA(s) solving.
"""
# Built-in 
import os
import time
# Externally packed
import requests
import discord
#GUI automation 
import pyautogui
import undetected_chromedriver as uc
#Selenium modules
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.keys import Keys
from selenium.common.exceptions import TimeoutException

def SolveCaptcha(url: str) -> bool:
    chrome_options = uc.ChromeOptions()

    chrome_options.add_argument(
        '--disable-blink-features=AutomationControlled')
    chrome_options.add_argument('--disable-extensions')

    path = str

    if os.path.exists("C:\Program Files\Google\Chrome\Application\chrome.exe"):
        path = "C:\Program Files\Google\Chrome\Application\chrome.exe"

    elif os.path.exists("C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"):
        path = "C:\Program Files (x86)\Google\Chrome\Application\chrome.exe"

    else:
        print("[?] Could not find chrome installed on the system.")
        return False

    chrome = uc.Chrome(browser_executable_path=path,
                       use_subprocess=True, options=chrome_options)

    # redirecting to URL
    chrome.get(url)

    try:
        captcha_selector = '#recaptcha-anchor > div.recaptcha-checkbox-border'
        audio_selector = '#recaptcha-audio-button'
        download_selector = '#rc-audio > div.rc-audiochallenge-tdownload > a'

        chrome.switch_to.default_content()

        # wait for captcha iframe to be visible
        WebDriverWait(chrome, 20).until(EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, "iframe[title='reCAPTCHA']")))
        captcha = WebDriverWait(chrome, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, captcha_selector)))

        time.sleep(2)
        captcha.click()

        chrome.switch_to.default_content()

        # wait for challenge to be visible
        WebDriverWait(chrome, 20).until(EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, "iframe[title='recaptcha challenge expires in two minutes']")))
        audio_btn = WebDriverWait(chrome, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, audio_selector)))

        time.sleep(2)
        audio_btn.click()

        chrome.switch_to.default_content()

        # wait for audio challenge to be visible
        WebDriverWait(chrome, 20).until(EC.frame_to_be_available_and_switch_to_it(
            (By.CSS_SELECTOR, "iframe[title='recaptcha challenge expires in two minutes']")))
        WebDriverWait(chrome, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, download_selector)))

        time.sleep(2)
        # get audio download link
        download_link = chrome.find_element(
            By.CSS_SELECTOR, download_selector).get_attribute("href")

        # save the audio to disk as an MP3
        r = requests.get(download_link)
        with open('sound.mp3', 'wb') as f:
            f.write(r.content)

        # convert audio to WAV and save to disk
        # ffmpeg must be a PATH variable for this operation
        sound = AudioSegment.from_mp3("sound.mp3")
        sound.export("sound.wav", format="wav")

        sample_audio = sr.AudioFile('sound.wav')

        # comprehend the audio
        recognizer = sr.Recognizer()
        audio = None

        with sample_audio as source:
            audio = recognizer.record(source)

        text = recognizer.recognize_google(audio)

        # input the text from speech
        input_box = chrome.find_element(By.ID, 'audio-response')

        time.sleep(2)

        input_box.send_keys(text.lower())
        input_box.send_keys(Keys.ENTER)

    except Exception as e:
        # checking if captcha has already been solved
        try:
            # wait for captcha checkmark to be visible
            chrome.switch_to.default_content()

            WebDriverWait(chrome, 20).until(EC.frame_to_be_available_and_switch_to_it(
                (By.CSS_SELECTOR, "iframe[title='reCAPTCHA']")))
            WebDriverWait(chrome, 10).until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, '#recaptcha-anchor > div.recaptcha-checkbox-checkmark')))

            chrome.switch_to.default_content()

            verify_btn = chrome.find_element(By.TAG_NAME, "button")

            if verify_btn.is_enabled() == False:
                chrome.quit()
                return False

            # captcha was solved
            time.sleep(2)
            verify_btn.click()

            time.sleep(5)
            chrome.quit()

            return True

        except Exception as e:
            chrome.quit()
            return False

    # get fail text; successful operation otherwise
    try:
        # wait for fail text
        WebDriverWait(chrome, 10).until(
            EC.element_to_be_clickable((By.CSS_SELECTOR, '#rc-audio > div.rc-audiochallenge-error-message')))

        fail_text = chrome.find_element(
            By.CSS_SELECTOR, '#rc-audio > div.rc-audiochallenge-error-message').text

        if len(fail_text) > 0:
            chrome.quit()
            return False

    except TimeoutException:
        # captcha was solved
        chrome.switch_to.default_content()

        verify_btn = chrome.find_element(By.TAG_NAME, "button")

        time.sleep(2)
        verify_btn.click()

        time.sleep(5)
        chrome.quit()

        return True


def getAllWindows() -> str:
    processes = []

    for window in pyautogui.getAllWindows():
        if len(window.title) > 0:
            processes.append(window.title)

    return processes


def determineSolving() -> bool:
    processes = getAllWindows()
    combined = '\t'.join(processes)

    condition = "New Tab" in combined or "verify.poketwo.net" in combined or "Just a moment" in combined

    while condition == True:
        processes = getAllWindows()
        combined = '\t'.join(processes)

        condition = "New Tab" in combined or "verify.poketwo.net" in combined or "Just a moment" in combined

        time.sleep(1)

    return False


def solve(url: str) -> None:
    solving = True

    while solving == True:
        solving = determineSolving()

    solved = False

    while solved == False:
        solved = SolveCaptcha(url)
    print("Successfully solved the captcha!")
    return
    
#
