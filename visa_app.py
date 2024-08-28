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



def send_email_fail(city, day, month, year):
    host = "smtp-mail.outlook.com"
    port = 587
    user = "deneme.experilabs@outlook.com"
    password = "experilabs123"
    receiver = "ykselbaltacioglu@gmail.com"
    subject = "Daha Yakin Vize Tarihi Belirlenemedi!"

    body = """
    Sitemizi ziyaret ettiğiniz için teşekkür ederiz. Size bildirmekten üzüntü duyariz ki, daha önce belirlenmiş olan vize tarihiniz yerine daha yakin bir vize tarihi bulunamadi.

    Uygulamamiz sizin icin daha erken bir vize tarihi aramaya devam edecektir.

    İyi günler dileriz.
    Experilabs
    """.format(city, day, month, year)

    # E-posta mesajını oluşturma
    msg = MIMEMultipart()
    msg['From'] = user
    msg['To'] = receiver
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
        conn.sendmail(user, receiver, msg.as_string())

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
    receiver = "ykselbaltacioglu@gmail.com"
    subject = "Daha Yakin Vize Tarihi Belirlendi!"

    body = """
    Sitemizi ziyaret ettiğiniz için teşekkür ederiz. Size bildirmekten mutluluk duyariz ki, daha önce belirlenmiş olan vize tarihiniz yerine, daha yakin bir tarih için yeni bir vize alabilirsiniz.

    Lütfen "Türkiye Official U.S. Department of State Visa Appointment Service" sitesinden belirtilen tarihler arasinda uygun bir tarih seçip, vizenizi almak için gereken adimlari takip edin.

    Belirtilen Tarih : {}   {}/{}/{}

    İyi günler dileriz.
    Experilabs
    """.format(city, day, month, year)

    # E-posta mesajını oluşturma
    msg = MIMEMultipart()
    msg['From'] = user
    msg['To'] = receiver
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
        conn.sendmail(user, receiver, msg.as_string())

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
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa")
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
    print("cleaned text: ")
    print(cleaned_text)
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
from datetime import datetime

def convert_to_date(day, month, year):
    month_mapping = {
        "Ocak": 1, "Şubat": 2, "Mart": 3, "Nisan": 4, "Mayıs": 5, "Haziran": 6, "Temmuz": 7,
        "Ağustos": 8, "Eylül": 9, "Ekim": 10, "Kasım": 11, "Aralık": 12,
        # English months if needed
        "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
        "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
    }

    month_number = month_mapping[month]
    return datetime.strptime(f"{day}/{month_number}/{year}", "%d/%m/%Y")

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
                    break
                else:
                    send_email_fail(city, date_element.text, month_content, year_content)
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
