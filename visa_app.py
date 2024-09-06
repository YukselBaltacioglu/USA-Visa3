import datetime
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.support.ui import Select
import time
import schedule
import smtplib
from smtplib import SMTP  # simple mail transport protocol demek
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import re
from getpass import getpass
import os
from flask import Flask, request, jsonify, render_template

#from flask_cors import CORS

#app = Flask(__name__)
#CORS(app, resources={r"/login": {"origins": "*"}})  # Sadece /login endpointine izin ver


from flask_cors import CORS
app = Flask(__name__)
CORS(app)

EMAILS = []

# Update the PATH to the correct location of chromedriver.exe
PATH = (
    "C:\\Program Files (x86)\\chrome-win64\\chrome.exe"  # Chrome'un exe dosyasinin yolu
)

# Log dosyası yolu
LOG_FILE_PATH = r"C:\Users\YükselBaltacıoğlu\Desktop\visa common with next pc\USA-Visa\last_fail_time.txt"

# Mapping for months
MONTH_MAPPING = {
    "January": 1, "February": 2, "March": 3, "April": 4, "May": 5, "June": 6,
    "July": 7, "August": 8, "September": 9, "October": 10, "November": 11, "December": 12
}
# Hardcoded kullanıcı bilgileri
users = {
    "pcaglarsahin@gmail.com": "Kel35Bek",
    "anotheruser@example.com": "mypassword"
}


def main(email_to_use, password_to_use, EMAILS):
    chrome_options = Options()
    chrome_options.add_argument("--start-maximized")
    # WebDriver'i başlatma
    driver = webdriver.Chrome(options=chrome_options)

    # Visa sayfasina gitme
    driver.get("https://ais.usvisa-info.com/tr-tr/niv/users/sign_in")
    wait = WebDriverWait(driver, 60)

    email = email_to_use
    password = password_to_use
    # İlk sayfa giriş işlemleri
    first_page(email, password, driver)
    current_appt = second_page(driver)
    third_page(driver)

    # Önce Ankara'yı kontrol et
    ankara_available = date_finder("Ankara", current_appt, driver, EMAILS)

    # Ankara'da uygun tarih bulunamadıysa İstanbul'u kontrol et
    if not ankara_available:
        close_button = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, "//a[@class='button secondary' and contains(text(), 'Kapat')]")
            )
        )
        close_button.click()
        second_page(driver)
        time.sleep(5)
        third_page(driver)
        istanbul_option = WebDriverWait(driver, 60).until(  # takvimi aç
            EC.element_to_be_clickable((By.XPATH, "//option[contains(text(),'Istanbul')]"))
        )
        istanbul_option.click()
        time.sleep(5)
        istanbul_available = date_finder("Istanbul", current_appt, driver, EMAILS)

        # Eğer ne Ankara'da ne de İstanbul'da uygun tarih bulunamadıysa, başarısızlık e-postasını gönder
        if not istanbul_available:
            if should_send_fail_email():
                send_email_fail("Istanbul", "Ankara", EMAILS)
                log_fail_time()
                print("E-posta başarıyla gönderildi!")
            else:
                print("E-posta gönderimi atlandı, çünkü 1 saat geçmedi.")
    else:
        print("Ankara'da uygun bir tarih bulundu, İstanbul kontrol edilmedi.")

    time.sleep(20)


def send_email_approved(city, day, month, year, EMAILS):
    host = "smtp-mail.outlook.com"
    port = 587
    user = "deneme.experilabs@outlook.com"
    password = "experilabs123"

    # Birden fazla alıcı
    receivers = EMAILS
    subject = "Daha Yakin Yeni Vize Tarihi Onaylandi!"

    body = """
    Sitemizi ziyaret ettiğiniz için teşekkür ederiz. Size bildirmekten mutluluk duyarız ki, daha önce belirlenmiş olan vize tarihiniz yerine, daha yakın bir tarih bulunmus olup belirtilen bu yeni tarih onaylanmistir.

    Lütfen "Türkiye Official U.S. Department of State Visa Appointment Service" sitesine gidip alinmis olan randevuyu kontrol ediniz.

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


def send_email_fail(city1, city2, EMAILS):
    host = "smtp-mail.outlook.com"
    port = 587
    user = "deneme.experilabs@outlook.com"
    password = "experilabs123"
    # Birden fazla alıcı
    receivers = EMAILS
    subject = "Daha Yakin Vize Tarihi Belirlenemedi!"

    print(EMAILS)
    print("###########################")
    print(receivers)
    body = """
    Sitemizi ziyaret ettiğiniz için teşekkür ederiz. Size bildirmekten üzüntü duyariz ki, {} ve {} illeri icin daha önce belirlenmiş olan vize tarihiniz yerine daha yakin bir vize tarihi bulunamadi.

    Uygulamamiz sizin icin daha erken bir vize tarihi aramaya devam edecektir.

    İyi günler dileriz.
    Experilabs
    """.format(city1, city2)

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

def send_email_success(city, day, month, year, EMAILS):
    host = "smtp-mail.outlook.com"
    port = 587
    user = "deneme.experilabs@outlook.com"
    password = "experilabs123"

    # Birden fazla alıcı
    receivers = EMAILS

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


# ---------------------------------FIRST PAGE--------------------------------------
def first_page(email, password, driver):
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
def second_page(driver):
    date_span = WebDriverWait(driver, 60).until(
        EC.presence_of_element_located((By.CLASS_NAME, "consular-appt"))
    )
    date_content = date_span.text

    current_appt = extract_date(date_content)
    print(current_appt)  # Çıktı: 28 Mayıs 2025
    continue_button = WebDriverWait(driver, 60).until(
        EC.element_to_be_clickable(
            (By.XPATH, "//a[@href='/tr-tr/niv/schedule/56640483/continue_actions']")
        )  # //*[@id="main"]/div[2]/div[2]/div[1]/div/div/div[1]/div[2]/ul/li/a
    )
    continue_button.click()
    return current_appt


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
def third_page(driver):
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


def get_month_number(month_name):
    return MONTH_MAPPING.get(month_name, None)  # Ay ismi bulunamazsa None döner


def date_picker(city, day, month, year, driver, EMAILS):
    # Tarih seçildikten sonra saat seçimi
    time.sleep(5)
    time_hours = WebDriverWait(driver, 60).until(  # Saat takvimini aç
        EC.element_to_be_clickable((By.ID, "appointments_consulate_appointment_time_input"))
    )
    time.sleep(5)
    time_hours.click()
    time.sleep(5)
    hour_pick = time_hours.find_elements(By.TAG_NAME, "option")
    time.sleep(5)

    # İlk saat seçeneğini seçmek
    if len(hour_pick) != 0:  # Eğer saat seçenekleri varsa
        hour_pick[1].click()  # İlk seçeneği seç
        print(f"İlk saat seçeneği seçildi: {hour_pick[1].text}")
    else:
        print("Hiçbir saat seçeneği bulunamadı.")

    time.sleep(8)
    submit_button = WebDriverWait(driver, 60).until(EC.element_to_be_clickable(
        (By.ID, "appointments_submit")))
    submit_button.click()
    time.sleep(10)

    # Dikkatli ol, deneme yaparken yorum satirina almayi unutma!!!!!!!!!!!!!!!!!!!!!
    approve_button = WebDriverWait(driver, 60).until(EC.element_to_be_clickable(
        (By.CLASS_NAME, "button alert")))
    approve_button.click()
    time.sleep(60)
    send_email_approved(city, day, month, year, EMAILS)


def date_finder(city, current_appointment, driver, EMAILS):
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
                time.sleep(3)
                new_date_string = f"{date_element.text} {month_content} {year_content}"
                new_appointment_date = convert_to_date(date_element.text, month_content, year_content)

                # Dikkatli ol, yanlislikla True kalmasin !!!!!!!!!!!!!!!!!!!
                if new_appointment_date < current_appointment_date:
                    send_email_success(city, date_element.text, month_content, year_content, EMAILS)
                    found_clickable_date = True
                    date_element.click()  # Günü seçer
                    date_picker(city, date_element.text, month_content, year_content, EMAILS)  # Saat seçimini yap
                    return True  # Uygun tarih bulundu
                else:
                    print(f"No earlier date found for {city}. Moving to next date.")
                    return False

        next_button = driver.find_element(By.CLASS_NAME, "ui-datepicker-next")
        next_button.click()

    return False  # Uygun tarih bulunamadı

EMAIL = ""
PASSWORD = ""
@app.route('/login', methods=['POST'])
def login():

    global EMAIL
    global PASSWORD
    print("AAAAA")
    # İstekten gelen email ve şifreyi alıyoruz
    data = request.json
    EMAIL = data.get('email')
    PASSWORD = data.get('password')
    print("You are in.")
    # Kullanıcının hardcoded listede olup olmadığını kontrol et
    if EMAIL in users and users[EMAIL] == PASSWORD:
        print("SUCCESS")
        return jsonify({'message': 'Login successful!'}), 200
    else:
        return jsonify({'message': 'Invalid credentials'}), 401


@app.route('/emails', methods=['POST'])
def emails():
    print("AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAa")
    global EMAILS
    global EMAIL
    global PASSWORD
    print("Also in.")
    data = request.json
    EMAILS = data.get('emails')
    if emails:
        print("Received emails:", EMAILS)  # Gelen e-posta adreslerini işleme
        main(EMAIL, PASSWORD, EMAILS)
        return jsonify({'message': 'Emails received successfully!'}), 200
    else:
        return jsonify({'message': 'No emails provided'}), 400




if __name__ == "__main__":
    app.run(debug=True)

# email = "pcaglarsahin@gmail.com"
# password = "Kel35Bek"


