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

# İndirilen resimleri kaydetmek için klasör oluştur
folder_name = "istockVitiligo"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Mevcut klasördeki resim sayısını al
existing_images_count = len(os.listdir(folder_name))
images_downloaded = 0  # İndirilen resim sayısını başlat

# İndirilecek hedef resim sayısı
target_images_count = 4000

# Chrome ayarları (Chrome tarayıcısını başlatmak için seçenekler ayarlanır)
chrome_options = Options()
driver = webdriver.Chrome(options=chrome_options)

# Arama URL'si ve sorgu ayarları
base_url = "https://www.istockphoto.com/tr/search/2/image"
search_query = "vitiligo"
page_number = 1  # Sayfa numarasını başlat

# Daha önce indirilen resim URL'lerini saklamak için bir set oluştur
downloaded_urls = set()

# Detay URL'leri kaydetmek için dosya aç
#veri eleme işlemi için txt lere kaydediyoruz
url_file_path = "detail_url_istockvitiligo.txt"
with open(url_file_path, "a") as url_file:
    # Toplam indirilmesi gereken resim sayısını hesapla
    total_images_needed = existing_images_count + target_images_count

    # İndirilecek hedef sayıya ulaşana kadar döngüye devam et
    while images_downloaded < target_images_count:
        # Her sayfanın URL'sini oluştur ve tarayıcıda aç
        url = f"{base_url}?page={page_number}&phrase={search_query.replace(' ', '%20')}"
        driver.get(url)

        try:
            # Resimlerin bulunduğu elementlerin yüklenmesini bekle
            WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located(
                    (By.XPATH, "/html/body/div[2]/section/div/main/div/div/div[2]/div/div[3]//article/a"))
            )
        except Exception as e:
            print(f"Hata: {e}")
            break  # Hata durumunda döngüden çık

        # Sayfanın tam yüklenmesi için bekle
        time.sleep(3)

        # Belirtilen alanda bulunan tüm resim etiketlerini bul
        image_elements = driver.find_elements(By.XPATH,
                                              "/html/body/div[2]/section/div/main/div/div/div[2]/div/div[3]//article")

        if not image_elements:
            print("Hiçbir resim bulunamadı.")
            break  # Eğer resim bulunamazsa döngüyü kır

        # Her bir resim etiketleri üzerinde döngü
        for article in image_elements:
            try:
                # Detay URL'sini al
                detail_url = article.find_element(By.XPATH, "./a").get_attribute("href")
                if detail_url:
                    url_file.write(detail_url + "\n")  # Detay URL'yi dosyaya kaydet

                # Resim URL'sini al
                img = article.find_element(By.TAG_NAME, "img")
                img_url = img.get_attribute("src")

                # Resim URL'sinin geçerli olup olmadığını kontrol et
                if img_url and "http" in img_url:
                    # Daha önce indirilen URL'lerden mi kontrol et
                    if img_url in downloaded_urls:
                        continue  # URL daha önce indirilmişse döngüye devam et

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

                    # URL'yi kaydet (tekrar indirilmesini önlemek için)
                    downloaded_urls.add(img_url)

                    # İndirilen resim sayacını artır
                    images_downloaded += 1
            except Exception as e:
                print(f"Resim veya detay URL alınırken hata oluştu: {e}")
                continue  # Hata durumunda döngüye devam et

            # İndirilen resim sayısı hedefe ulaştıysa döngüyü kır
            if images_downloaded >= target_images_count:
                break

        # Bir sonraki sayfaya geçmek için sayfa numarasını artır
        page_number += 1

# Tarayıcıyı kapat
driver.quit()

# İndirme işleminin tamamlanma durumunu bildir
if images_downloaded >= target_images_count:
    print("Tüm 4000 resim indirildi.")
else:
    print(f"{images_downloaded} adet resim indirildi.")
