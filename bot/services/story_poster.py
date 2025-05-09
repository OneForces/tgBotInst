from db.models import ReelsTask
from db.engine import async_session
from sqlalchemy import update
from appium.options.android import UiAutomator2Options
from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from time import sleep

INSTAGRAM_PACKAGE = "com.instagram.android"
INSTAGRAM_ACTIVITY = ".activity.MainTabActivity"
CHROME_PACKAGE = "com.android.chrome"
CHROME_ACTIVITY = "com.google.android.apps.chrome.Main"
APPIUM_SERVER_URL = "http://127.0.0.1:4723/wd/hub"

def get_driver(app_package: str, app_activity: str):
    options = UiAutomator2Options()
    options.set_capability("platformName", "Android")
    options.set_capability("deviceName", "emulator-5554")
    options.set_capability("appPackage", app_package)
    options.set_capability("appActivity", app_activity)
    options.set_capability("noReset", True)
    return webdriver.Remote(command_executor=APPIUM_SERVER_URL, options=options)

def login_to_instagram(driver, username: str, password: str):
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

    # 1. Запуск Instagram и логин
    driver = get_driver(INSTAGRAM_PACKAGE, INSTAGRAM_ACTIVITY)
    try:
        login_to_instagram(driver, task.instagram_login, task.instagram_password)
        driver.quit()
    except Exception as e:
        print(f"❌ Ошибка при логине: {e}")
        driver.quit()
        return

    # 2. Открытие ссылки через Chrome
    driver = get_driver(CHROME_PACKAGE, CHROME_ACTIVITY)
    try:
        sleep(5)
        print(f"[🌐] Открываем ссылку: {task.reels_url}")
        driver.get(task.reels_url)
        sleep(6)

        print("[📤] Пытаемся опубликовать в сторис...")
        driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().descriptionContains("Еще")').click()
        sleep(2)
        driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("в сторис")').click()
        sleep(2)
        driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR, 'new UiSelector().textContains("Поделиться")').click()
        sleep(3)
        print("✅ Reels размещён")
    except Exception as e:
        print(f"⚠ Не удалось опубликовать: {e}")
    finally:
        driver.quit()

    # 3. Логаут из Instagram
    driver = get_driver(INSTAGRAM_PACKAGE, INSTAGRAM_ACTIVITY)
    try:
        logout_from_instagram(driver)
    except Exception as e:
        print(f"⚠ Ошибка при выходе: {e}")
    finally:
        driver.quit()

    # 4. Обновление статуса в базе
    async with async_session() as session:
        await session.execute(
            update(ReelsTask)
            .where(ReelsTask.id == task.id)
            .values(status="posted")
        )
        await session.commit()
