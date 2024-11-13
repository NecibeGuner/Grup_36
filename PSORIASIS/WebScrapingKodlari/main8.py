import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from PIL import Image
from io import BytesIO

# Klasör oluştur
folder_name = "istockPsoriasis"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Mevcut resim sayısını al
existing_images_count = len(os.listdir(folder_name))
images_downloaded = 0  # İndirilmiş resim sayısını başlat

# Hedef resim sayısı
target_images_count = 2000

# Chrome ayarları
chrome_options = Options()
driver = webdriver.Chrome(options=chrome_options)

base_url = "https://www.istockphoto.com/tr/search/2/image"
search_query = "psoriasis"
page_number = 1  # Sayfa numarasını başlat

# Daha önce indirilen resim URL'lerini saklamak için bir set oluştur
downloaded_urls = set()

# URL'leri kaydetmek için dosya aç
url_file_path = "detay_url_listesi_istockpsoriasis.txt"
with open(url_file_path, "a") as url_file:

    # Toplam resim sayısını hesapla
    total_images_needed = existing_images_count + target_images_count

    while images_downloaded < target_images_count:
        # URL'yi oluştur ve aç
        url = f"{base_url}?page={page_number}&phrase={search_query.replace(' ', '%20')}"
        driver.get(url)

        try:
            # Resimlerin bulunduğu elementin yüklenmesini bekle
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "/html/body/div[2]/section/div/main/div/div/div[2]/div/div[3]//article/a"))
            )
        except Exception as e:
            print(f"Hata: {e}")
            break

        # Sayfanın yüklenmesi için bekle
        time.sleep(3)

        # Belirtilen article içindeki resimleri bul
        image_elements = driver.find_elements(By.XPATH, "/html/body/div[2]/section/div/main/div/div/div[2]/div/div[3]//article")

        if not image_elements:
            print("Hiçbir resim bulunamadı.")
            break

        for article in image_elements:
            try:
                # Detay URL'sini al
                detail_url = article.find_element(By.XPATH, "./a").get_attribute("href")
                if detail_url:
                    url_file.write(detail_url + "\n")  # Detay URL'yi dosyaya kaydet

                # Resim URL'sini al
                img = article.find_element(By.TAG_NAME, "img")
                img_url = img.get_attribute("src")
                if img_url and "http" in img_url:  # Resim URL'sinin geçerli olduğunu kontrol et
                    # Daha önce indirildi mi kontrol et
                    if img_url in downloaded_urls:
                        continue  # Daha önce indirilmişse devam et

                    # Resmi indir
                    img_data = requests.get(img_url).content
                    # Resmi aç ve yeniden boyutlandır
                    image = Image.open(BytesIO(img_data))
                    image = image.convert("RGB")  # RGBA'dan RGB'ye dönüştür
                    resized_image = image.resize((320, 240))  # 320x240 boyutuna yeniden boyutlandır

                    # Dosya adı mevcut sayıya göre ayarlanacak
                    image_file_name = os.path.join(folder_name, f"{existing_images_count + images_downloaded + 1}.jpg")
                    resized_image.save(image_file_name, "JPEG")  # Resmi kaydet

                    # Dosya yolunu yazdır
                    print(image_file_name)

                    # URL'yi kaydet
                    downloaded_urls.add(img_url)

                    images_downloaded += 1
            except Exception as e:
                print(f"Resim veya detay URL alınırken hata oluştu: {e}")
                continue

            if images_downloaded >= target_images_count:
                break

        # Bir sonraki sayfaya geç
        page_number += 1

# Tarayıcıyı kapat
driver.quit()

# Son durumu bildir
if images_downloaded >= target_images_count:
    print("Tüm 3000 resim indirildi.")
else:
    print(f"{images_downloaded} adet resim indirildi.")
