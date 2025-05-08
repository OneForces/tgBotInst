from db.models import ReelsTask
from db.database import async_session
from sqlalchemy import update

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from time import sleep

INSTAGRAM_PACKAGE = "com.instagram.android"
INSTAGRAM_ACTIVITY = ".activity.MainTabActivity"
CHROME_PACKAGE = "com.android.chrome"
CHROME_ACTIVITY = "com.google.android.apps.chrome.Main"
APPIUM_SERVER_URL = "http://127.0.0.1:4723/wd/hub"

def get_driver():
    caps = {
        "platformName": "Android",
        "deviceName": "emulator-5554",
        "appPackage": INSTAGRAM_PACKAGE,
        "appActivity": INSTAGRAM_ACTIVITY,
        "noReset": False,
        "automationName": "UiAutomator2"
    }
    return webdriver.Remote(APPIUM_SERVER_URL, caps)

def login_to_instagram(driver, username, password):
    try:
        print(f"[🔐] Логинимся как {username}")
        sleep(5)
        driver.find_element(AppiumBy.XPATH, "//android.widget.EditText[1]").send_keys(username)
        driver.find_element(AppiumBy.XPATH, "//android.widget.EditText[2]").send_keys(password)
        driver.find_element(AppiumBy.XPATH, "//android.widget.Button").click()
        sleep(6)
        print("✅ Успешный вход")
    except Exception as e:
        print(f"⚠ Ошибка логина: {e}")

def logout_from_instagram(driver):
    try:
        print("🚪 Выходим из аккаунта")
        driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Профиль").click()
        sleep(2)
        driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Параметры").click()
        sleep(2)
        driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Выйти")').click()
        sleep(1)
        driver.find_element(AppiumBy.ID, "android:id/button1").click()
        sleep(2)
        print("✅ Вышли из аккаунта")
    except Exception as e:
        print(f"⚠ Ошибка выхода: {e}")

async def post_reels_to_stories(task: ReelsTask):
    print(f"[📲] Публикуем Reels: {task.reels_url}")
    driver = webdriver.Remote(account.appium_url + "/wd/hub", caps)

    try:
        # 🔐 Логинимся под нужным аккаунтом
        login_to_instagram(driver, task.instagram_login, task.instagram_password)

        # 🔗 Открытие Reels в Chrome
        driver.start_activity(CHROME_PACKAGE, CHROME_ACTIVITY)
        sleep(4)
        driver.get(task.reels_url)
        sleep(6)

        # 📤 Публикация в сторис
        try:
            driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("Еще")').click()
            sleep(2)
            driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("в сторис")').click()
            sleep(2)
            driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Поделиться")').click()
            sleep(3)
            print("✅ Reels размещён")
        except Exception as e:
            print(f"⚠ Не удалось опубликовать: {e}")

        # 🚪 Логаут
        logout_from_instagram(driver)

    except Exception as e:
        print(f"❌ Ошибка публикации: {e}")
    finally:
        driver.quit()

    # ✅ Обновляем статус в базе
    async with async_session() as session:
        await session.execute(
            update(ReelsTask)
            .where(ReelsTask.id == task.id)
            .values(status="posted")
        )
        await session.commit()
