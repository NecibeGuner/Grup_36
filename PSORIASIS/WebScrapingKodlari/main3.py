import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from io import BytesIO

# Klasör oluştur (Tüm resimler bu klasöre indirilecek)
download_folder = "main3"
os.makedirs(download_folder, exist_ok=True)

# Klasördeki mevcut dosya sayısına göre sayaç başlat
image_counter = len(os.listdir(download_folder)) + 1  # Mevcut dosya sayısını alarak sayacı başlat

# Tarayıcı ayarları
options = webdriver.ChromeOptions()
options.add_argument('--headless')  # Tarayıcıyı arka planda çalıştırır
options.add_argument('--no-sandbox')
options.add_argument('--disable-dev-shm-usage')

# Tarayıcıyı başlat
driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)

# Sayfayı aç
url = "https://psoriasisclinics.com.au/gallery/"
driver.get(url)

# İndirilen resimlerin URL'lerini saklamak için set
downloaded_images = set()

# Sayfa başına resim çekme döngüsü
while True:
    time.sleep(3)  # Sayfanın yüklenmesini bekle

    # Resimleri bul
    images = driver.find_elements(By.TAG_NAME, "img")
    page_images = []  # Geçerli sayfadaki resimlerin listesi

    for img in images:
        img_url = img.get_attribute("src")
        if img_url and "logop.png" not in img_url and img_url not in downloaded_images:  # Logo resmini ve daha önce indirilenleri kontrol et
            page_images.append(img_url)
            downloaded_images.add(img_url)  # İndirilen resmi kaydet

    # Geçerli sayfadaki resimleri indir
    for img_url in page_images:
        try:
            # Resmi indir
            img_data = requests.get(img_url).content
            image = Image.open(BytesIO(img_data))

            # Resmi kes
            cropped_image = image.crop((0, 0, 400, 225))  # (sol, üst, sağ, alt) koordinatları ile kes

            # Resmi yeniden boyutlandır
            resized_image = cropped_image.resize((320, 240))  # 320x240 boyutuna yeniden boyutlandır

            # Her zaman JPEG formatında ve .jpeg uzantısıyla kaydet
            img_name = os.path.join(download_folder, f"{image_counter}.jpeg")  # Dosya adını her zaman .jpeg ile ayarla
            resized_image.convert('RGB').save(img_name, 'JPEG')  # JPEG formatında kaydet
            print(f"{img_name} olarak kaydedildi.")  # Kaydedilen dosya yolunu yazdır

            image_counter += 1  # Resim sayacını artır
        except Exception as e:
            print(f"Resim indirme hatası: {e} - {img_url}")

    # "Next" butonuna tıklama
    try:
        next_button = driver.find_element(By.CLASS_NAME, "page-next")
        if "disabled" in next_button.get_attribute("class"):
            break  # "Next" butonu devre dışıysa döngüyü kır
        next_button.click()
    except Exception as e:
        print("Next butonu bulunamadı veya tıklanamadı.")
        break

# Tarayıcıyı kapat
driver.quit()
