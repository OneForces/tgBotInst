from db.models import ReelsTask
from db.database import async_session
from datetime import datetime
from sqlalchemy import select, update

from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from time import sleep

INSTAGRAM_PACKAGE = "com.instagram.android"
INSTAGRAM_ACTIVITY = ".activity.MainTabActivity"
CHROME_PACKAGE = "com.android.chrome"
CHROME_ACTIVITY = "com.google.android.apps.chrome.Main"
APPIUM_SERVER_URL = "http://127.0.0.1:4723/wd/hub"

def get_driver():
    desired_caps = {
        "platformName": "Android",
        "deviceName": "emulator-5554",  # ⚙️ ADB device
        "appPackage": INSTAGRAM_PACKAGE,
        "appActivity": INSTAGRAM_ACTIVITY,
        "noReset": True,
        "automationName": "UiAutomator2",
    }
    return webdriver.Remote(APPIUM_SERVER_URL, desired_caps)

async def post_reels_to_stories(task: ReelsTask):
    print(f"[📲] Публикуем Reels: {task.reels_url}")

    try:
        driver = get_driver()

        # 1. Открытие Reels в Chrome
        driver.start_activity(CHROME_PACKAGE, CHROME_ACTIVITY)
        sleep(4)
        driver.get(task.reels_url)
        sleep(5)

        # 2. Кнопка "..."
        try:
            more_btn = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                                           'new UiSelector().descriptionContains("Еще")')
            more_btn.click()
            sleep(2)
        except Exception:
            print("⚠️ Не найдена кнопка 'Еще'")

        # 3. Кнопка "Поделиться в сторис"
        try:
            share_btn = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                                            'new UiSelector().textContains("в сторис")')
            share_btn.click()
            sleep(3)
        except Exception:
            print("⚠️ Не найдена кнопка 'Поделиться в сторис'")

        # 4. Кнопка "Поделиться"
        try:
            post_btn = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                                           'new UiSelector().textContains("Поделиться")')
            post_btn.click()
            sleep(3)
        except Exception:
            print("⚠️ Не найдена кнопка 'Поделиться'")

        # 5. Завершение
        driver.press_keycode(4)  # Назад
        sleep(1)
        driver.press_keycode(3)  # Домой

        print(f"✅ Reels размещён: {task.reels_url}")

    except Exception as e:
        print(f"❌ Ошибка Appium: {e}")
    finally:
        try:
            driver.quit()
        except:
            pass

    # Обновление статуса
    async with async_session() as session:
        await session.execute(
            update(ReelsTask)
            .where(ReelsTask.id == task.id)
            .values(status="posted")
        )
        await session.commit()
