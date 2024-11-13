import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException, WebDriverException
from PIL import Image
from io import BytesIO
import time
from concurrent.futures import ThreadPoolExecutor

# İndirilecek resimlerin kaydedileceği klasörü oluştur
output_folder = 'NLM_Acne'
os.makedirs(output_folder, exist_ok=True)

# Detay URL'lerini kaydetmek için dosya oluştur
detail_url_file = "detail_url_openi_acne.txt"
with open(detail_url_file, "a") as f:
    pass  # Boş dosya oluşturulmuş olur

# Klasördeki mevcut resim sayısını sayarak sayaç başlat
existing_images = len([name for name in os.listdir(output_folder) if os.path.isfile(os.path.join(output_folder, name))])
image_count = existing_images + 1  # Yeni indirilecek resimlerin başlangıç adlandırması
max_images = 469  # İndirilecek maksimum resim sayısı

# Temel URL
base_url = "https://openi.nlm.nih.gov/gridquery?q=acne%20on%20the%20face&m=1&n=100&it=xg"

# Başlatılması gereken Chrome tarayıcı ayarlarını içeren fonksiyon
def start_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")  # Tarayıcıyı arka planda çalıştır
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)

# Tek tek resimleri indirmek için fonksiyon
def download_image(img_url, img_name):
    try:
        img_data = requests.get(img_url, timeout=10).content  # Resim verisini indir
        image = Image.open(BytesIO(img_data))  # İndirilen resmi aç
        resized_image = image.resize((320, 240))  # Resmi yeniden boyutlandır
        resized_image.save(img_name)  # Resmi belirtilen adla kaydet
        print(f"{img_name} indirildi ve yeniden boyutlandırıldı.")
    except Exception as e:
        print(f"{img_name} indirilirken hata oluştu: {e}")

# Resimleri ve detay URL'leri toplu olarak indirip kaydetmek için fonksiyon
def download_images_and_save_urls(driver):
    global image_count
    wait = WebDriverWait(driver, 20)
    try:
        # Resimlerin bulunduğu alanın yüklenmesini bekle
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#grid')))
        image_elements = driver.find_elements(By.CSS_SELECTOR, 'div#grid a')
        futures = []
        with ThreadPoolExecutor() as executor:
            for element in image_elements:
                if image_count > max_images:
                    return  # Maksimum resim sayısına ulaşıldıysa işlemi durdur

                try:
                    # Detay URL'sini al
                    detail_url = element.get_attribute("href")
                    # Resim URL'sini al
                    img_element = element.find_element(By.TAG_NAME, "img")
                    img_url = img_element.get_attribute("src")

                    # Detay URL'yi dosyaya kaydet
                    with open(detail_url_file, "a") as f:
                        f.write(detail_url + "\n")

                    # Resmi asenkron olarak indirin
                    img_name = f"{output_folder}/{image_count}.jpg"
                    futures.append(executor.submit(download_image, img_url, img_name))
                    image_count += 1
                except NoSuchElementException:
                    print("Resim ögesi bulunamadı.")
                except Exception as e:
                    print(f"Resim indirme sırasında hata oluştu: {e}")

            # Tüm indirme işlemlerinin tamamlanmasını bekle
            for future in futures:
                future.result()

    except WebDriverException as e:
        print(f"Resim öğeleri yüklenirken hata oluştu: {e}")
        time.sleep(5)

# Sayfa indeksini başlatma
page_index = 0

while image_count <= max_images:
    # Tarayıcıyı başlat ve her sayfa geçişinde kapat/aç
    driver = start_driver()
    wait = WebDriverWait(driver, 20)

    # Sayfa URL'sini belirle
    m_value = page_index * 100 + 1
    n_value = m_value + 99
    current_url = base_url.format(m_value, n_value)

    for attempt in range(3):  # 3 deneme hakkı
        try:
            driver.get(current_url)
            print(f"{current_url} sayfası yüklendi. Resimler indiriliyor...")
            download_images_and_save_urls(driver)
            break
        except WebDriverException as e:
            print(f"Sayfa yüklenirken hata oluştu: {e}. {attempt + 1}. deneme.")
            time.sleep(5)

    # Tarayıcıyı kapat
    driver.quit()
    print("Tarayıcı kapatıldı.")
    page_index += 1

print("İndirme işlemi tamamlandı.")
