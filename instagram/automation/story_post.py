from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from time import sleep

def create_poster_driver(port=4723):
    caps = {
        "platformName": "Android",
        "deviceName": "Android Device",
        "appPackage": "com.instagram.android",
        "appActivity": ".activity.MainTabActivity",
        "noReset": True,
        "automationName": "UiAutomator2"
    }
    return webdriver.Remote(f"http://localhost:{port}/wd/hub", caps)

def logout_from_instagram(driver):
    try:
        print("🚪 Выход из Instagram")
        driver.find_element(AppiumBy.XPATH, "//android.widget.ImageView[@content-desc='Profile']").click()
        sleep(2)
        driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Options").click()
        sleep(2)
        driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                            'new UiSelector().textContains("Log Out")').click()
        sleep(2)
        driver.find_element(AppiumBy.ID, "android:id/button1").click()
        print("✅ Вышли из аккаунта")
    except Exception as e:
        print(f"⚠ Ошибка при выходе: {e}")

def post_reels_to_story(driver, reels_url):
    try:
        print(f"📤 Публикуем Reels: {reels_url}")

        # Открытие поиска
        search_button = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Search")
        search_button.click()
        sleep(2)

        # Ввод ссылки
        search_input = driver.find_element(AppiumBy.ID, "com.instagram.android:id/action_bar_search_edit_text")
        search_input.clear()
        search_input.send_keys(reels_url)
        sleep(3)

        # Здесь может быть требование нажать Enter или выбрать ссылку из результатов
        # (можно расширить при необходимости)

        # Поделиться в сторис
        share_button = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                                           'new UiSelector().textContains("Add reel to your story")')
        share_button.click()
        sleep(3)

        send_to_button = driver.find_element(AppiumBy.ANDROID_UIAUTOMATOR,
                                             'new UiSelector().textContains("Share")')
        send_to_button.click()
        sleep(2)

        print("✅ Reels опубликован в сторис")

    except Exception as e:
        print(f"❌ Ошибка публикации: {e}")
    finally:
        logout_from_instagram(driver)
        print("⏹ Завершаем сессию Appium")
        driver.quit()
