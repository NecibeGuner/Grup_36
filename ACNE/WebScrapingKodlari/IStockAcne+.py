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

# Resimlerin indirileceği klasörü oluştur
folder_name = "IStockAcne"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Klasörde mevcut olan resim sayısını belirle
existing_images_count = len(os.listdir(folder_name))
images_downloaded = 0  # İndirilen resim sayısını başlat

# Hedeflenen toplam resim sayısı
target_images_count = 3000

# Chrome tarayıcı ayarları
chrome_options = Options()
driver = webdriver.Chrome(options=chrome_options)

# İstek yapılan sayfanın temel URL'si ve arama sorgusu
base_url = "https://www.istockphoto.com/tr/search/2/image"
search_query = "acne"
page_number = 1  # Sayfa numarasını başlat

# Daha önce indirilen resim URL'lerini saklamak için bir set
downloaded_urls = set()

# Resim detay URL'lerini saklamak için bir dosya aç
url_file_path = "detail_url_istockacne.txt"
with open(url_file_path, "a") as url_file:
    # Toplamda ihtiyaç duyulan resim sayısını belirle
    total_images_needed = existing_images_count + target_images_count

    while images_downloaded < target_images_count:
        # Arama URL'sini oluştur ve sayfayı aç
        url = f"{base_url}?page={page_number}&phrase={search_query.replace(' ', '%20')}"
        driver.get(url)

        try:
            # Resimlerin bulunduğu alanın yüklenmesini bekle
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "/html/body/div[2]/section/div/main/div/div/div[2]/div/div[3]//article/a"))
            )
        except Exception as e:
            print(f"Hata: {e}")
            break

        # Sayfanın yüklenmesi için ek süre bekle
        time.sleep(3)

        # Sayfadaki article etiketlerinden resimleri bul
        image_elements = driver.find_elements(By.XPATH,
                                              "/html/body/div[2]/section/div/main/div/div/div[2]/div/div[3]//article")

        # Resim yoksa döngüyü kır
        if not image_elements:
            print("Hiçbir resim bulunamadı.")
            break

        # Bulunan her bir article için işlem yap
        for article in image_elements:
            try:
                # Detay URL'sini al
                detail_url = article.find_element(By.XPATH, "./a").get_attribute("href")
                if detail_url:
                    url_file.write(detail_url + "\n")  # Detay URL'yi dosyaya kaydet

                # Resim URL'sini al
                img = article.find_element(By.TAG_NAME, "img")
                img_url = img.get_attribute("src")

                # Resim URL'sinin geçerli olduğunu kontrol et
                if img_url and "http" in img_url:
                    # Resmin daha önce indirilip indirilmediğini kontrol et
                    if img_url in downloaded_urls:
                        continue  # İndirildiyse devam et

                    # Resmi indir ve bellekte aç
                    img_data = requests.get(img_url).content
                    image = Image.open(BytesIO(img_data))

                    # Resmi RGB formatına dönüştür
                    image = image.convert("RGB")

                    # Resmi 320x240 boyutuna yeniden boyutlandır
                    resized_image = image.resize((320, 240))

                    # Dosya adı oluştur, mevcut resim sayısına göre adlandır
                    image_file_name = os.path.join(folder_name, f"{existing_images_count + images_downloaded + 1}.jpg")
                    resized_image.save(image_file_name, "JPEG")  # Resmi JPEG formatında kaydet

                    # Dosya yolunu yazdır (kontrol amaçlı)
                    print(image_file_name)

                    # URL'yi kaydedip indirilen resimler setine ekle
                    downloaded_urls.add(img_url)

                    # İndirilen resim sayısını bir artır
                    images_downloaded += 1
            except Exception as e:
                print(f"Resim veya detay URL alınırken hata oluştu: {e}")
                continue

            # İndirilen resim sayısı hedefe ulaştığında döngüden çık
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
