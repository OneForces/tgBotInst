from appium import webdriver
from appium.webdriver.common.appiumby import AppiumBy
from sqlalchemy import select
from db.models import async_session, ViewResult, ViewTask, Subscriber, Account  # предполагаем модель Account
from time import sleep

# Параметры Appium/эмулятора
APPIUM_URL = "http://appium:4723/wd/hub"
CAPS = {
    "platformName": "Android",
    "deviceName": "emulator-5554",
    "automationName": "UiAutomator2",
    # ... остальные capabilities для headless-эмулятора
}

async def perform_view_task(task_id: int, subscriber_id: int, target_profile: str):
    # получить список аккаунтов подписчика
    async with async_session() as session:
        sub = await session.get(Subscriber, subscriber_id)
        accounts = sub.accounts  # list of Account(login, password)

    driver = webdriver.Remote("http://localhost:4723/wd/hub", caps)
    for acc in accounts:
        try:
            # 1. Логин
            login_to_instagram(driver, acc.login, acc.password)
            # 2. Переход на профиль
            open_profile(driver, target_profile)
            # 3. Открыть Stories и пролистать все
            view_all_stories(driver)
            # 4. Записать результат
            async with async_session() as session:
                vr = ViewResult(task_id=task_id, account=acc.login, success=True)
                session.add(vr)
                await session.commit()
        except Exception:
            async with async_session() as session:
                vr = ViewResult(task_id=task_id, account=acc.login, success=False)
                session.add(vr)
                await session.commit()
        finally:
            # очистить сессию Instagram
            driver.reset()
    driver.quit()

def login_to_instagram(driver, username, password):
    # ваше существующее login_to_instagram
    from instagram.publish import login_to_instagram as base_login
    base_login(driver, username, password)

def open_profile(driver, profile_name: str):
    # поиск и переход через поиск Instagram
    search_button = driver.find_element(AppiumBy.ACCESSIBILITY_ID, "Search and explore")
    search_button.click()
    sleep(2)
    input_el = driver.find_element(AppiumBy.CLASS_NAME, "android.widget.EditText")
    input_el.send_keys(profile_name)
    sleep(2)
    driver.find_element(AppiumBy.XPATH, f"//android.widget.TextView[@text='{profile_name}']").click()
    sleep(3)

def view_all_stories(driver):
    # Нажать на аватар, если Stories есть
    try:
        driver.find_element(AppiumBy.XPATH, "//android.widget.ImageView[contains(@content-desc, 'Story')]").click()
    except:
        return  # нет сторис
    sleep(2)
    # Пролистывать, пока есть следующий элемент
    while True:
        try:
            driver.swipe(900, 500, 100, 500, 500)  # координаты можно подогнать
            sleep(2)
        except:
            break
