import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from concurrent.futures import ThreadPoolExecutor
from PIL import Image

# Klasör oluşturma (resimlerin kaydedileceği klasör)
output_folder = 'ben'
os.makedirs(output_folder, exist_ok=True)

# Klasördeki mevcut dosya sayısına göre sayaç başlat
existing_images = len([name for name in os.listdir(output_folder) if os.path.isfile(os.path.join(output_folder, name))])
image_count = existing_images + 1  # Yeni resimler için sayaç
max_images = 3250  # İndirilecek maksimum resim sayısı

# Daha önce indirilen resim URL'lerini takip etmek için bir set oluştur
downloaded_images = set()

# Selenium ile Chrome tarayıcısını başlatma
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()

# Hedef URL'ye git
driver.get("https://gallery.isic-archive.com/#!/topWithHeader/onlyHeaderTop/gallery?filter=%5B%5D")

# Kabul butonuna tıklama işlemi
try:
    print("Kabul butonuna tıklanıyor...")
    accept_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//button[text()='I Accept']"))
    )
    accept_button.click()
    time.sleep(12)  # Sayfanın tamamen yüklenmesi için bekleme
    print("Sayfa tamamen yüklendi.")
except Exception as e:
    print("Kabul butonuna tıklanamadı:", str(e))

# Oturum oluşturma
session = requests.Session()

# Resim indirme fonksiyonu
def download_image(img_url, image_count, retries=3):
    # Aynı resmin tekrar indirilmesini engelle
    if img_url in downloaded_images:
        return False

    # İndirme işlemi için belirli sayıda deneme yap
    for attempt in range(retries):
        try:
            # Resmi indir ve kaydet
            img_data = session.get(img_url, timeout=10).content
            img_name = os.path.join(output_folder, f"{image_count}.jpg")

            # Resmi kaydet ve boyutlandır
            with open(img_name, "wb") as file:
                file.write(img_data)

            with Image.open(img_name) as img:
                img = img.resize((320, 240))
                img.save(img_name)

            # İndirilen URL'yi sete ekle ve indirme başarılı mesajı
            downloaded_images.add(img_url)
            print(f"İndirildi ve yeniden boyutlandırıldı: {img_name}")
            return True
        except requests.exceptions.RequestException as e:
            print(f"Resim indirme hatası: {e} - {attempt + 1}. deneme")
            time.sleep(5)

    return False  # İndirme işlemi başarısızsa False döndür

try:
    while image_count <= max_images:
        print("Resim indirme işlemi başlıyor...")

        try:
            # Sayfadaki resimleri içeren div'leri bul
            image_divs = WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "/html/body/div[2]/div/div/div[2]/div/div/div/div[2]/div[3]/div[1]/div")
                )
            )
        except Exception as e:
            print(f"Resim divleri yüklenirken hata oluştu: {e}")
            continue

        # Resimleri indirmek için çoklu iş parçacığı kullan
        with ThreadPoolExecutor() as executor:
            future_to_url = {}
            for image_div in image_divs:
                try:
                    img_elements = image_div.find_elements(By.TAG_NAME, "img")
                except Exception as e:
                    print(f"Resim ögeleri bulunurken hata oluştu: {e}")
                    continue

                for img_element in img_elements:
                    try:
                        img_url = img_element.get_attribute("src")
                        if img_url and img_url not in downloaded_images:
                            future_to_url[executor.submit(download_image, img_url, image_count)] = img_url
                            image_count += 1
                            if image_count > max_images:
                                break
                    except Exception as e:
                        print(f"Resim URL'si alınırken hata oluştu: {e}")
                        continue

                if image_count > max_images:
                    break

            # Tüm indirmelerin tamamlanmasını bekleyin
            for future in future_to_url:
                try:
                    future.result()
                except Exception as e:
                    print(f"İndirme sırasında bir hata oluştu: {e}")

        # "Next" butonuna tıklama işlemi
        retry_attempts = 3
        for attempt in range(retry_attempts):
            try:
                WebDriverWait(driver, 7).until(EC.invisibility_of_element_located((By.CLASS_NAME, "webix_progress_icon")))
                next_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "//button[@aria-label='Next page']"))
                )
                next_button.click()
                print("Next butonuna tıklandı.")
                time.sleep(7)
                break  # Başarılı olduysa döngüden çık
            except Exception as e:
                print(f"Next butonuna tıklanamadı, {attempt + 1}. deneme: {e}")
                time.sleep(5)
                if attempt == retry_attempts - 1:
                    print("Next butonuna tıklama denemeleri başarısız oldu. Yeniden deneniyor...")

finally:
    driver.quit()
    print("İndirme işlemi tamamlandı ve tarayıcı kapatıldı.")
