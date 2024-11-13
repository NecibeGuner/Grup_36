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

# Klasör oluşturma
output_folder = 'main6'
os.makedirs(output_folder, exist_ok=True)

# Detay URL'leri kaydetmek için dosya oluşturma
detail_url_file = "detail_url_openi_psoriasis.txt"
with open(detail_url_file, "a") as f:
    pass  # Boş dosya oluşturulmuş olur

# Resim sayaçlarını başlat
existing_images = len([name for name in os.listdir(output_folder) if os.path.isfile(os.path.join(output_folder, name))])
image_count = existing_images + 1  # Yeni resim adlandırması başlangıcı
max_images = 1500

# URL yapılandırmasını anlamaya yönelik base URL ve parametreler
base_url = "https://openi.nlm.nih.gov/gridquery?m={m_value}&n={n_value}&it=xg&q=psoriasis"


# Tarayıcı başlatma fonksiyonu
def start_driver():
    chrome_options = webdriver.ChromeOptions()
    chrome_options.add_argument("--headless")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    return webdriver.Chrome(options=chrome_options)


# Tek tek resim indirme fonksiyonu
def download_image(img_url, img_name):
    try:
        img_data = requests.get(img_url, timeout=10).content
        image = Image.open(BytesIO(img_data))
        resized_image = image.resize((320, 240))
        resized_image.save(img_name)
        print(f"{img_name} indirildi ve yeniden boyutlandırıldı.")
    except Exception as e:
        print(f"{img_name} indirilirken hata oluştu: {e}")


# URL'leri takip eden set oluşturma
downloaded_urls = set()

# Önceden indirilmiş URL'leri yükleme
if os.path.exists(detail_url_file):
    with open(detail_url_file, "r") as f:
        for line in f:
            downloaded_urls.add(line.strip())


# Resimleri ve detay URL'leri topluca indirme fonksiyonu
def download_images_and_save_urls(driver):
    global image_count
    wait = WebDriverWait(driver, 20)
    try:
        wait.until(EC.presence_of_all_elements_located((By.CSS_SELECTOR, 'div#grid')))
        image_elements = driver.find_elements(By.CSS_SELECTOR, 'div#grid a')
        futures = []
        with ThreadPoolExecutor() as executor:
            for element in image_elements:
                if image_count > max_images:
                    return  # Maksimum resim sayısına ulaşıldıysa çıkış yap

                try:
                    # Resim URL'sini ve detay URL'sini al
                    detail_url = element.get_attribute("href")

                    # Eğer URL daha önce indirilmişse atla
                    if detail_url in downloaded_urls:
                        print(f"{detail_url} zaten indirildi, atlanıyor.")
                        continue

                    img_element = element.find_element(By.TAG_NAME, "img")
                    img_url = img_element.get_attribute("src")

                    # Detay URL'yi dosyaya ve sete kaydet
                    with open(detail_url_file, "a") as f:
                        f.write(detail_url + "\n")
                    downloaded_urls.add(detail_url)

                    # Resmi asenkron olarak indirin
                    img_name = f"{output_folder}/{image_count}.jpg"
                    futures.append(executor.submit(download_image, img_url, img_name))
                    image_count += 1
                except NoSuchElementException:
                    print("Resim ögesi bulunamadı.")
                except Exception as e:
                    print(f"Resim indirme sırasında hata oluştu: {e}")

            # Tüm iş parçacıkları tamamlanana kadar bekleyin
            for future in futures:
                future.result()

    except WebDriverException as e:
        print(f"Resim öğeleri yüklenirken hata oluştu: {e}")
        time.sleep(5)


# Sayfa indeksini belirleme ve döngü
page_index = 0

while image_count <= max_images:
    # Tarayıcıyı başlat ve her sayfa geçişinde kapat/aç
    driver = start_driver()
    wait = WebDriverWait(driver, 20)

    # Sayfa URL'sini belirle (100'erlik bloklarla artıyor)
    m_value = page_index * 100 + 1
    n_value = m_value + 99
    current_url = base_url.format(m_value=m_value, n_value=n_value)

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
