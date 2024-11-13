import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from io import BytesIO

# Klasör oluşturma
download_folder = "main7"
os.makedirs(download_folder, exist_ok=True)  # 'main7' klasörü oluşturuluyor

# Mevcut resim sayısını kontrol et
existing_images = os.listdir(download_folder)
image_count = len(existing_images)  # Klasördeki mevcut resim sayısı

# ChromeDriver seçenekleri
chrome_options = Options()
chrome_options.add_argument("--headless")  # Tarayıcıyı başlatmadan çalıştırır (opsiyonel)
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# WebDriver başlat
driver = webdriver.Chrome(service=Service(), options=chrome_options)

# Sayfayı aç
driver.get("https://commons.wikimedia.org/w/index.php?search=psoriasis&title=Special:MediaSearch&go=Go&type=image")

# İndirilen resim URL'lerini saklamak için set
downloaded_images = set()

# Tüm resimleri indirip, "Load more" butonuna basma döngüsü
while True:
    try:
        # Sayfayı aşağı kaydır (lazy loading'i tetiklemek için)
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(3)  # Sayfanın tamamen yüklenmesi için bekle

        # Görsellerin bulunduğu elementleri bul
        image_elements = driver.find_elements(By.XPATH, "//*[@id='cdx-image-0']/div[2]//img")

        # Yeni görselleri kontrol etmek için mevcut URL'leri saklayacağız
        current_image_urls = set()

        for image in image_elements:
            image_url = image.get_attribute("src")
            if image_url:
                current_image_urls.add(image_url)

        # Yeni görselleri indir
        new_images_found = False  # Yeni görsel bulunup bulunmadığını takip et
        for image_url in current_image_urls:
            if image_url not in downloaded_images:
                # Görseli indir
                response = requests.get(image_url)
                if response.status_code == 200:
                    img_data = response.content
                else:
                    print(f"İndirme hatası: {response.status_code} - URL: {image_url}")
                    continue  # Hata varsa sonraki döngüye geç

                # Resmi aç ve yeniden boyutlandır
                try:
                    image = Image.open(BytesIO(img_data))  # Resmi aç
                    image = image.convert("RGB")  # RGBA'dan RGB'ye dönüştür
                    resized_image = image.resize((320, 240))  # 320x240 boyutuna yeniden boyutlandır

                    # Resmin kaydedileceği yol
                    img_path = os.path.join(download_folder, f"{image_count + 1}.jpg")
                    resized_image.save(img_path, "JPEG")  # Resmi kaydet

                    # Dosya yolunu yazdır
                    print(f"{img_path}")

                    downloaded_images.add(image_url)  # İndirilen görseli set'e ekle
                    image_count += 1  # İndirilmiş görsel sayısını arttır
                    new_images_found = True  # Yeni bir görsel bulundu

                except Exception as e:
                    print(f"Resim açılamadı: {e} - URL: {image_url}")
                    continue  # Hata varsa sonraki döngüye geç

        # Eğer yeni bir görsel bulunmadıysa, döngüyü kır
        if not new_images_found:
            print("Yeni resim bulunamadı, döngüden çıkılıyor.")
            break

        # "Load more" butonunu bekleyin ve bulmaya çalışın
        load_more_xpath = "//*[@id='cdx-image-0']/div[2]/div/div/button"

        # Butonu bulmak için 10 saniye bekleyin
        try:
            load_more_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.XPATH, load_more_xpath))
            )
            load_more_button.click()
            time.sleep(5)  # "Load more" işlemi sonrası sayfanın yüklenmesi için daha fazla bekle
        except Exception as e:
            print("Load more butonu bulunamadı veya tıklanamadı, çıkılıyor:")
            break

    except Exception as e:
        print("Hata oluştu:", str(e))
        break

# Tarayıcıyı kapat
driver.quit()
