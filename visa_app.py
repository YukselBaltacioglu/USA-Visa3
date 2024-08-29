import datetime


from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import schedule
import smtplib
from smtplib import SMTP  # simple mail transport protocol demek
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
from getpass import getpass
import os


def send_email_fail(city):
    host = "smtp-mail.outlook.com"
    port = 587
    user = "deneme.experilabs@outlook.com"
    password = "experilabs123"
    # Birden fazla alıcı
    receivers = ["ykselbaltacioglu@gmail.com", "ercan.gokduman@experilabs.com", "yavuz.sahin@experilabs.com"]


    subject = "Daha Yakin Vize Tarihi Belirlenemedi!"

    body = """
    Sitemizi ziyaret ettiğiniz için teşekkür ederiz. Size bildirmekten üzüntü duyariz ki, {} ili icin daha önce belirlenmiş olan vize tarihiniz yerine daha yakin bir vize tarihi bulunamadi.

    Uygulamamiz sizin icin daha erken bir vize tarihi aramaya devam edecektir.

    İyi günler dileriz.
    Experilabs
    """.format(city)

    # E-posta mesajını oluşturma
    msg = MIMEMultipart()
    msg['From'] = user
    msg['To'] = ", ".join(receivers)  # Alıcıları virgülle ayırarak birleştirme
    msg['Subject'] = subject

    # Mesajın içeriğini ekleme
    msg.attach(MIMEText(body, 'plain'))

    try:
        # SMTP sunucusuna bağlanma
        conn = smtplib.SMTP(host, port)
        conn.ehlo()
        conn.starttls()
        conn.login(user, password)

        # E-postayı gönderme
        conn.sendmail(user, receivers, msg.as_string())

        print("E-posta başarıyla gönderildi!")
    except Exception as e:
        print(f"E-posta gönderilemedi: {e}")
    finally:
        # Bağlantıyı kapatma
        conn.quit()


# -------------------------------------------------

def send_email_success(city, day, month, year):
    host = "smtp-mail.outlook.com"
    port = 587
    user = "deneme.experilabs@outlook.com"
    password = "experilabs123"

    # Birden fazla alıcı
    receivers = ["ykselbaltacioglu@gmail.com", "ercan.gokduman@experilabs.com", "yavuz.sahin@experilabs.com"]

    subject = "Daha Yakin Vize Tarihi Belirlendi!"

    body = """
       Sitemizi ziyaret ettiğiniz için teşekkür ederiz. Size bildirmekten mutluluk duyarız ki, daha önce belirlenmiş olan vize tarihiniz yerine, daha yakın bir tarih için yeni bir vize alabilirsiniz.

       Lütfen "Türkiye Official U.S. Department of State Visa Appointment Service" sitesinden belirtilen tarihler arasında uygun bir tarih seçip, vizenizi almak için gereken adımları takip edin.

       Belirtilen Tarih : {}   {}/{}/{}

       İyi günler dileriz.
       Experilabs
       """.format(city, day, month, year)

    # E-posta mesajını oluşturma
    msg = MIMEMultipart()
    msg['From'] = user
    msg['To'] = ", ".join(receivers)  # Alıcıları virgülle ayırarak birleştirme
    msg['Subject'] = subject

    # Mesajın içeriğini ekleme
    msg.attach(MIMEText(body, 'plain'))

    try:
        # SMTP sunucusuna bağlanma
        conn = smtplib.SMTP(host, port)
        conn.ehlo()
        conn.starttls()
        conn.login(user, password)

        # E-postayı gönderme
        conn.sendmail(user, receivers, msg.as_string())  # Burada da listeyi kullanıyoruz

        print("E-posta başarıyla gönderildi!")
    except Exception as e:
        print(f"E-posta gönderilemedi: {e}")
    finally:
        # Bağlantıyı kapatma
        conn.quit()


# Update the PATH to the correct location of chromedriver.exe
PATH = (
    "C:\\Program Files (x86)\\chrome-win64\\chrome.exe"  # Chrome'un exe dosyasinin yolu
)

chrome_options = Options()
chrome_options.add_argument("--start-maximized")
# WebDriver'i başlatma
driver = webdriver.Chrome(options=chrome_options)

# Visa sayfasina gitme
driver.get("https://ais.usvisa-info.com/tr-tr/niv/users/sign_in")
wait = WebDriverWait(driver, 60)


# ---------------------------------FIRST PAGE--------------------------------------
def first_page(email, password):
    email_input = driver.find_element(By.ID, "user_email")
    email_input.send_keys(email)  # Inputa metin yazin

    password_input = driver.find_element(By.ID, "user_password")
    password_input.send_keys(password)

    # Gizlilik politakasini check etme
    checkbox = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//input[@id='policy_confirmed']/parent::div")
        )
    )
    checkbox.click()

    submit_button = driver.find_element(By.XPATH, "//input[@value='Oturum Aç']")
    submit_button.click()


# ---------------------------------SECOND PAGE--------------------------------------
def second_page():
    date_span = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, "consular-appt"))
    )
    date_content = date_span.text

    current_appt = extract_date(date_content)
    print(current_appt)  # Çıktı: 28 Mayıs 2025
    continue_button = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[@href='/tr-tr/niv/schedule/56640483/continue_actions']")
        )
    )
    continue_button.click()
    return  current_appt


def extract_date(text):
    cleaned_text = re.sub(r"[^\w\s]", "", text)  # Özel karakterleri temizler
    cleaned_text = re.sub(r"\s+", " ", cleaned_text)  # Fazla boşlukları tek boşluğa indirir
    # Tarih formatını bulmak için düzenli ifade
    pattern = r"\d{1,2} \w+ \d{4}"
    # Düzenli ifadeyi kullanarak tarihi ayır
    match = re.search(pattern, cleaned_text)

    if match:
        return match.group()
    else:
        return "Tarih bulunamadı"


# -------------------------------THIRD PAGE------------------------------------------
def third_page():
    list_items = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='forms']/ul/li[3]"))
    )
    list_items.click()  # 3. listeyi aç

    reschedule_appointment = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[@href='/tr-tr/niv/schedule/56640483/appointment']")
        )
    )
    reschedule_appointment.click()


# ---------------------------------FOURTH PAGE------------------------------------------
# It is default Ankara city
# from datetime import datetime

def convert_to_date(day, month, year):
    month_mapping = {
        "Ocak": 1, "Şubat": 2, "Mart": 3, "Nisan": 4, "Mayıs": 5, "Haziran": 6, "Temmuz": 7,
        "Ağustos": 8, "Eylül": 9, "Ekim": 10, "Kasım": 11, "Aralık": 12,
        # English months if needed
        "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
        "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
    }

    month_number = month_mapping[month]
    return datetime.datetime.strptime(f"{day}/{month_number}/{year}", "%d/%m/%Y")

# Log dosyası yolu
LOG_FILE_PATH = r"C:\Users\YükselBaltacıoğlu\Desktop\visa common with next pc\USA-Visa\last_fail_time.txt"



def should_send_fail_email():
    if os.path.exists(LOG_FILE_PATH):
        with open(LOG_FILE_PATH, "r") as file:
            last_fail_time_str = file.read().strip()
            if last_fail_time_str:
                last_fail_time = datetime.datetime.fromisoformat(last_fail_time_str)
                if datetime.datetime.now() - last_fail_time < datetime.timedelta(hours=1):
                    return False
    return True

def log_fail_time():
    with open(LOG_FILE_PATH, "w") as file:
        file.write(datetime.datetime.now().isoformat())


def select_date(year_to_select, month_to_select, day_to_select):
    # Tarih seçici açma
    print("YYYYYYYYYYYYYYYYYYYYYYYYYYY")
    month_to_select = get_month_number(month_to_select)
    calendar = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable((By.ID, "appointments_consulate_appointment_date"))
    )
    time.sleep(15)
    driver.execute_script("arguments[0].click();", calendar)


    print("XXXXXXXXXXXXXXXXXXXXXXXXX")
    # Ay ve yıl seçim bölümünü bulma
    while True:
        print("ZZZZZZZZZZZZZZZZZZZZZZ")
        # Mevcut yıl ve ayı kontrol etme
        current_year_span = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ui-datepicker-year"))
        )
        current_year = current_year_span.text
        current_month_span = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ui-datepicker-month"))
        )
        current_month = current_month_span.text

        print("Current Year:", current_year)
        print("Current Month:", current_month)
        print("Year to Select:", year_to_select)
        print("Month to Select:", month_to_select)


        if current_year == year_to_select:
            if int(get_month_number(current_month)) < month_to_select:
                next_button = WebDriverWait(driver, 60).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "ui-datepicker-next"))
                )
                next_button.click()
            elif int(get_month_number(current_month)) > month_to_select:
                prev_button = WebDriverWait(driver, 60).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "ui-datepicker-prev"))
                )
                prev_button.click()
            else:
                break
        # Yıl ve ay seçme işlemi
        elif int(current_year) < int(year_to_select):
            next_button = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "ui-datepicker-next"))
            )
            next_button.click()
        else:
            prev_button = WebDriverWait(driver, 60).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "ui-datepicker-prev"))
            )
            prev_button.click()
    print("RRRRRRRRRRRRRRRRRRRRRR")
    # Gün seçme
    date_picker_div = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.XPATH, "//div[@class='ui-datepicker-calendar']"))
    )
    print("IIIIIIIIIIIIIIIIIIIIIIIIII")
    date_elements = date_picker_div.find_elements(By.TAG_NAME, "td")
    day_to_select = day_to_select
    print("HHHHHHHHHHHHHHHHHHHHHHHHHHHHH")
    for date_element in date_elements:
        print("OOOOOOOOOOOOOOOOOOOOOOOOOOOOOOOO")
        if date_element.text == day_to_select:
            date_element.click()
            print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA")
            break


month_mapping = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
}


def get_month_number(month_name):
    return month_mapping.get(month_name, None)  # Ay ismi bulunamazsa None döner


def date_finder(city, current_appointment):
    current_appointment_date = convert_to_date(*current_appointment.split())

    calendar = WebDriverWait(driver, 60).until(  # Takvimi aç
        EC.element_to_be_clickable((By.ID, "appointments_consulate_appointment_date"))
    )
    calendar.click()

    found_clickable_date = False
    not_gonna_find = False
    while not found_clickable_date and not not_gonna_find:
        date_picker_div = driver.find_element(
            By.XPATH,
            "//div[@class='ui-datepicker-group ui-datepicker-group-first']",
        )

        year_span = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ui-datepicker-year"))
        )
        year_content = year_span.text

        month_span = WebDriverWait(driver, 60).until(
            EC.presence_of_element_located((By.CLASS_NAME, "ui-datepicker-month"))
        )
        month_content = month_span.text
        print("Month and year content:", year_content, month_content)

        date_elements = date_picker_div.find_elements(By.TAG_NAME, "td")

        for date_element in date_elements:
            if "ui-datepicker-unselectable" not in date_element.get_attribute("class"):
                print(
                    "Clickable date:",
                    date_element.text,
                    month_content,
                    year_content,
                )
                new_date_string = f"{date_element.text} {month_content} {year_content}"
                new_appointment_date = convert_to_date(date_element.text, month_content, year_content)

                if new_appointment_date < current_appointment_date:
                    send_email_success(city, date_element.text, month_content, year_content)
                    found_clickable_date = True
                    select_date(year_content, month_content, date_element.text)
                    break
                else:
                    print("UUUUUUUUUUUUUUUUUUUUUUUU")
                    print(month_content)
                    select_date(year_content, month_content, date_element.text)
                    if should_send_fail_email():
                        send_email_fail(city)
                        log_fail_time()
                        print("E-posta başarıyla gönderildi!")
                    else:
                        print("E-posta gönderimi atlandı, çünkü 1 saat geçmedi.")
                    not_gonna_find = True
                    print("Sorry Mate!! Couldn't find it in " + city + ".")
                    break

        next_button = driver.find_element(By.CLASS_NAME, "ui-datepicker-next")
        next_button.click()




email ="pcaglarsahin@gmail.com"
password = "Kel35Bek"
# date = document.get("date")

first_page(email, password)
current_appt = second_page()
third_page()
date_finder("Ankara", current_appt)  # default it finds in Ankara firstly

close_button = WebDriverWait(driver, 10).until(
    EC.element_to_be_clickable(
        (By.XPATH, "//a[@class='button secondary' and contains(text(), 'Kapat')]")
    )
)
close_button.click()
second_page()
third_page()
istanbul_option = WebDriverWait(driver, 60).until(  # takvimi aç
    EC.element_to_be_clickable((By.XPATH, "//option[contains(text(),'Istanbul')]"))
)
istanbul_option.click()

date_finder("Istanbul", current_appt)  # for Istanbul



time.sleep(20)
