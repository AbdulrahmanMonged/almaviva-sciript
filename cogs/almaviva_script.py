from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from awesometkinter.bidirender import render_text
import threading
from . import sheet_management
from .colors import *


MAIN_PAGE = "https://egy.almaviva-visa.it/"
APPOINTMENT_PAGE = "https://egy.almaviva-visa.it/appointment"
SIGN_IN_PAGE = "https://egyiam.almaviva-visa.it/realms/oauth2-visaSystem-realm-pkce/protocol/openid-connect/auth?response_type=code&client_id=aa-visasys-public&state=U2I1T2RhOVFDb3lPRDJ6UWFkM0x1TE1EdkVoVTFvfnF1R0tCNWNmQWN-Yn5I&redirect_uri=https%3A%2F%2Fegy.almaviva-visa.it%2F&scope=openid%20profile%20email&code_challenge=L4uaP15WBdRqh766Az3-IkN6i5nk3fg1W-5497pOGN0&code_challenge_method=S256&nonce=U2I1T2RhOVFDb3lPRDJ6UWFkM0x1TE1EdkVoVTFvfnF1R0tCNWNmQWN-Yn5I#"
FLAG = 1
PAGES = [MAIN_PAGE, APPOINTMENT_PAGE, SIGN_IN_PAGE]
test_ua = 'Mozilla/5.0 (Windows NT 4.0; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/37.0.2049.0 Safari/537.36'



def filling_data(browser: webdriver.Chrome, wait: WebDriverWait, args):
    global FLAG
    window = args[-1]
    while FLAG:
        try:
            browser.get(APPOINTMENT_PAGE)
            wait.until(
                EC.invisibility_of_element_located(
                    (By.CLASS_NAME, "_ngcontent-bon-c143")
                )
            )
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "mat-select#mat-select-0")
                )
            )
            browser.find_element(By.CSS_SELECTOR, "mat-select#mat-select-0").click()
            selected_center = 1 if args[3] == "Cairo" else 0
            wait.until(
                EC.element_to_be_clickable((By.ID, f"mat-option-{selected_center}"))
            )
            browser.find_element(By.ID, f"mat-option-{selected_center}").click()

            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "mat-select#mat-select-4")
                )
            )

            browser.find_element(By.CSS_SELECTOR, "mat-select#mat-select-4").click()

            services = browser.find_elements(
                By.CLASS_NAME, "mdc-list-item__primary-text"
            )
            for service in services:
                if service.get_attribute("innerText") == "Standard - EGP 1110":
                    service.click()
                    break

            browser.find_element(By.CSS_SELECTOR, "mat-select#mat-select-2").click()
            wait.until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "#mat-select-2-panel #mat-option-18")
                )
            )
            browser.find_element(
                By.CSS_SELECTOR, "#mat-select-2-panel #mat-option-18"
            ).click()
            browser.find_element(By.XPATH, "//input[@id='pickerInput']").click()
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".mat-calendar-body-cell-content")
                )
            )
            date_box = browser.find_elements(
                By.CSS_SELECTOR, ".mat-calendar-body-cell-content"
            )
            for element in date_box:
                try:
                    if int(args[2]) == int(
                        element.get_attribute("innerText").strip("")
                    ):
                        element.click()
                        break
                except:
                    continue
            wait.until(
                EC.presence_of_element_located(
                    (
                        By.XPATH,
                        "//input[@placeholder='Indicate the first city of entry in Italy']",
                    )
                )
            )
            browser.find_element(
                By.XPATH,
                "//input[@placeholder='Indicate the first city of entry in Italy']",
            ).send_keys(args[4])
            window.state_lbl.configure(
                text=render_text("جاري تحميل البيانات..."), text_color=info
            )

            # CHECK_BOX
            browser.execute_script(
                "document.querySelector('#mat-mdc-checkbox-1-input').click()"
            )

            wait.until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "//div[@class='flex flex-col lg:flex-row lg:justify-end']//button[@class='visasys-button w-72 mt-6']",
                    )
                )
            )
                        
            # SUBMIT_BTN
            browser.find_element(
                By.XPATH,
                "//div[@class='flex flex-col lg:flex-row lg:justify-end']//button[@class='visasys-button w-72 mt-6']",
            ).click()
            wait.until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        "button[class='text-white']",
                    )
                )
            )
            button = browser.find_element(
                By.CSS_SELECTOR,
                "button[class='text-white']",
            )
            if "Proceed" in button.get_attribute("innerText").strip():
                button.click()
                browser.switch_to.window(browser.current_window_handle)
                browser.maximize_window()
                threading.Thread(target=(lambda : sheet_management.update_operation_status("Passed"))).start()
                FLAG = 0
                return
        except Exception as e:
            pass


def start_program(*args):
    options = Options()
    options.add_experimental_option("detach", True)
    options.add_argument(f'--user-agent={test_ua}')
    options.add_argument('--no-sandbox')
    options.add_argument("--disable-extensions")
    browser = webdriver.Chrome(options=options)
    wait = WebDriverWait(browser, 5)
    window = args[-1]

    try:
        if 1:
            browser.get(SIGN_IN_PAGE)
            try:
                wait.until(EC.presence_of_element_located((By.ID, "username")))
            finally:
                browser.find_element(By.ID, "username").send_keys(args[0])
                browser.find_element(By.ID, "password").send_keys(args[1])
                browser.find_element(By.ID, "kc-login").click()
            try:
                wait._timeout = 0.5
                wait.until(EC.presence_of_element_located((By.ID, "input-error")))
            except:
                wait._timeout = 5
                window.state_lbl.configure(
                    text=render_text("تم تسجيل الدخول بنجاح"), text_color=success
                )
                threading.Thread(target=(lambda : sheet_management.update_login_status("Success"))).start()
                filling_data(browser, wait, args)
            else:
                window.state_lbl.configure(
                    text=render_text("اسم المستخدم او كلمة المرور غير صحيحة"),
                    text_color=danger,
                )
                threading.Thread(target=(lambda : sheet_management.update_login_status("Failed"))).start()
                browser.quit()
        else:
            filling_data(browser, wait,  args)

    except Exception as e:
        if (
            browser.current_url in PAGES
            or "oauth2-visaSystem-realm-pkce" in browser.current_url
        ):
            browser.quit()
            window.state_lbl.configure(
                text=render_text("يوجد خطأ بالموقع حاليا...\nجاري اعادة المحاولة..."),
                text_color=danger,
            )
            start_program(*args)
        else:
            window.state_lbl.configure(
                text=render_text("يوجد خطأ بالموقع حاليا..."), text_color=danger
            )
