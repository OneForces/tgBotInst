from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from time import sleep

def create_viewer_driver(port=4723):
    caps = {
        "platformName": "Android",
        "deviceName": "Android Device",
        "appPackage": "com.instagram.android",
        "appActivity": ".activity.MainTabActivity",
        "noReset": True,
        "automationName": "UiAutomator2"
    }
    return webdriver.Remote(f"http://localhost:{port}/wd/hub", caps)


def view_stories(driver, usernames: list, view_duration=5):
    report = []

    for username in usernames:
        status = "❌ Не просмотрено"
        try:
            print(f"👁 Открываем сторис @{username}")

            # Нажимаем на иконку поиска
            search_button = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Search")
            search_button.click()
            sleep(2)

            # Вводим имя пользователя
            search_input = driver.find_element(AppiumBy.ID, "com.instagram.android:id/action_bar_search_edit_text")
            search_input.clear()
            search_input.send_keys(username)
            sleep(3)

            # Кликаем по нужному пользователю
            user_result = driver.find_element(
                AppiumBy.XPATH,
                f"//android.widget.TextView[@text='{username}']"
            )
            user_result.click()
            sleep(3)

            # Открываем сторис (если активны)
            story_ring = driver.find_element(
                AppiumBy.ID,
                "com.instagram.android:id/reel_viewer_thumbnail_image_view"
            )
            story_ring.click()
            sleep(view_duration)

            status = "✅ Просмотрено"

        except Exception as e:
            print(f"❌ Ошибка при просмотре @{username}: {e}")
        finally:
            report.append((username, status))
            sleep(2)

    return report
