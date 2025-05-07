from appium import webdriver
from time import sleep

def create_driver(device_name="Android Emulator", port=4723):
    caps = {
        "platformName": "Android",
        "deviceName": device_name,
        "appPackage": "com.instagram.android",
        "appActivity": ".activity.MainTabActivity",
        "noReset": True,
        "automationName": "UiAutomator2"
    }

    return webdriver.Remote(f"http://localhost:{port}/wd/hub", caps)

def post_story_from_reels(driver, reels_url: str):
    # Открытие reels по ссылке (допустим, через встроенный веб-браузер Instagram)
    sleep(5)
    driver.get(reels_url)
    sleep(5)

    # UI-логика зависит от версии Instagram!
    # Ниже — псевдологика (потребуется отладка через Appium Inspector)

    try:
        share_button = driver.find_element_by_accessibility_id("Поделиться")
        share_button.click()
        sleep(2)

        story_option = driver.find_element_by_xpath("//android.widget.TextView[@text='Add reel to your story']")
        story_option.click()
        sleep(3)

        post_button = driver.find_element_by_id("com.instagram.android:id/button_share")
        post_button.click()
        print("✅ Reels опубликован в сторис.")
    except Exception as e:
        print("❌ Ошибка при публикации:", e)
