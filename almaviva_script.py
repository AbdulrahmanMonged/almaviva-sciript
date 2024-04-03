from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.wait import WebDriverWait
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions as EC
from awesometkinter.bidirender import render_text
from colors import *


def submit(browser, wait, args):
    window = args[-1]
    window.state_lbl.configure(text=render_text("جاري تحميل البيانات..."), text_color=info)
    try:
        wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "//div[@class='flex flex-col lg:flex-row lg:justify-end']//button[@class='visasys-button w-72 mt-6']"))
        )
    finally:
        submit_btn2 = browser.find_element(
            By.XPATH, "//div[@class='flex flex-col lg:flex-row lg:justify-end']//button[@class='visasys-button w-72 mt-6']")
        submit_btn2.click()
    try:
        wait.until(
            EC.element_to_be_clickable(
                (By.XPATH, "/html[1]/body[1]/app-root[1]/div[1]/app-appointment-page[1]/div[1]/mat-stepper[1]/div[1]/div[2]/div[1]/app-memebers-number[1]/app-visasys-allert-card[1]/div[2]/div[3]/button[1]"))
        )
    except:
        print("error")
        window.state_lbl.configure(text=render_text("تم انتهاء المهمة..."), text_color=success)
    else:
        err_btn = browser.find_element(
            By.XPATH, "/html[1]/body[1]/app-root[1]/div[1]/app-appointment-page[1]/div[1]/mat-stepper[1]/div[1]/div[2]/div[1]/app-memebers-number[1]/app-visasys-allert-card[1]/div[2]/div[3]/button[1]"
        )
        err_btn.click()
        submit(browser, wait, args)


def filling_data(browser, wait, args):
    window = args[-1]
    try:
        browser.get('https://egy.almaviva-visa.it/appointment')
        try:
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, "mat-select#mat-select-0"))
            )
        finally:
            select1 = browser.find_element(
                By.CSS_SELECTOR, "mat-select#mat-select-0")
            select1.click()
            selected_center = 1 if args[3] == "Cairo" else 0
            try:
                wait.until(EC.element_to_be_clickable(
                    (By.ID, f"mat-option-{selected_center}")))
            finally:
                center = browser.find_element(
                    By.ID, f"mat-option-{selected_center}")
                center.click()

            select2 = browser.find_element(
                By.CSS_SELECTOR, "mat-select#mat-select-2")
            select2.click()
            try:
                wait.until(EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "#mat-select-2-panel #mat-option-18")))
            finally:
                visa_type = browser.find_element(
                    By.CSS_SELECTOR, "#mat-select-2-panel #mat-option-18")
                visa_type.click()
            date = browser.find_element(By.XPATH, "//input[@id='pickerInput']")
            date.click()
        try:
            wait.until(
                EC.presence_of_element_located(
                    (By.CSS_SELECTOR, ".mat-calendar-body-cell-content"))
            )
        finally:
            date_box = browser.find_elements(
                By.CSS_SELECTOR, ".mat-calendar-body-cell-content")
            for element in date_box:
                try:
                    if int(args[2]) == int(element.get_attribute("innerText").strip("")):
                        element.click()
                except:
                    continue

        try:
            wait.until(
                EC.presence_of_element_located(
                    (By.XPATH, "//input[@placeholder='Indicate the city of your destination']"))
            )
        finally:
            destination = browser.find_element(
                By.XPATH, "//input[@placeholder='Indicate the city of your destination']")
            destination.send_keys(args[4])

        submit(browser, wait, args)

    except Exception as e:
        print(e)
        filling_data(browser, wait, args)


def start_program(*args):
    options = Options()
    options.add_experimental_option("detach", True)
    browser = webdriver.Chrome(options=options)
    wait = WebDriverWait(browser, 10)
    browser.maximize_window()
    window = args[-1]

    try:
        if 1:
            browser.get('https://egyiam.almaviva-visa.it/realms/oauth2-visaSystem-realm-pkce/protocol/openid-connect/auth?response_type=code&client_id=aa-visasys-public&state=U2I1T2RhOVFDb3lPRDJ6UWFkM0x1TE1EdkVoVTFvfnF1R0tCNWNmQWN-Yn5I&redirect_uri=https%3A%2F%2Fegy.almaviva-visa.it%2F&scope=openid%20profile%20email&code_challenge=L4uaP15WBdRqh766Az3-IkN6i5nk3fg1W-5497pOGN0&code_challenge_method=S256&nonce=U2I1T2RhOVFDb3lPRDJ6UWFkM0x1TE1EdkVoVTFvfnF1R0tCNWNmQWN-Yn5I#')
            try:
                wait.until(
                    EC.presence_of_element_located((By.ID, "username"))
                )
            finally:
                username = browser.find_element(By.ID, "username")
                username.send_keys(args[0])
                password = browser.find_element(By.ID, "password")
                password.send_keys(args[1])
                submit_btn = browser.find_element(By.ID, "kc-login")
                submit_btn.click()

            try:
                wait._timeout = 0.5
                wait.until(
                    EC.presence_of_element_located((By.ID, "input-error"))
                )
            except:
                wait._timeout = 10
                window.state_lbl.configure(text=render_text("تم تسجيل الدخول بنجاح"), text_color=success)
                filling_data(browser, wait, args)
            else:
                window.state_lbl.configure(text=render_text("اسم المستخدم او كلمة المرور غير صحيحة"), text_color=danger)
                browser.quit()
        else:
            filling_data(browser, wait, args)

    except Exception as e:
        window.state_lbl.configure(text=render_text("يوجد خطأ بالموقع حاليا..."), text_color=danger)

        browser.quit()
