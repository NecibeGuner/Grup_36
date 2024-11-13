import requests
from bs4 import BeautifulSoup
import os
from urllib.parse import urljoin
from PIL import Image
from io import BytesIO
import time

# Başlangıç URL'si (melanoma için)
base_url = "https://atlasdermatologico.com.br/search.jsf?q=melanoma"

# Ana sayfadan hastalık bağlantılarını al
response = requests.get(base_url)
soup = BeautifulSoup(response.content, 'html.parser')

# Liste elemanlarını bul
disease_list = soup.find('ul', id='j_idt23_list')
disease_links = disease_list.find_all('a')

# Resimleri indirmek için yeni bir klasör oluştur
download_folder = "AtlasMelanoma"
os.makedirs(download_folder, exist_ok=True)

# Klasördeki mevcut dosya sayısına göre sayaç başlat
image_counter = len([name for name in os.listdir(download_folder) if os.path.isfile(os.path.join(download_folder, name))]) + 1

# Her hastalık bağlantısı için döngü
for index, link in enumerate(disease_links):
    disease_url = urljoin(base_url, link['href'])  # Tam URL'yi oluştur

    # Hastalık sayfasına isteği gönder
    disease_response = requests.get(disease_url)
    disease_soup = BeautifulSoup(disease_response.content, 'html.parser')

    # Resimleri bul
    images = disease_soup.find_all('img')

    # Her resmi indir
    for img in images:
        img_url = img.get('src')
        if img_url:
            # Tam URL'yi oluştur
            img_url = urljoin(disease_url, img_url)

            # Resmin adını oluştur (Sıralı numaralarla)
            img_name = os.path.join(download_folder, f"{image_counter}.jpg")

            # Daha önce indirilip indirilmediğini kontrol et
            if os.path.exists(img_name):
                print(f"Dosya zaten mevcut, atlanıyor: {img_name}")
                continue

            # Resmi indir
            try:
                img_data = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                img_data.raise_for_status()  # Talep başarılı olmazsa hata fırlat
                image = Image.open(BytesIO(img_data.content))  # Resmi aç

                # Resmi yeniden boyutlandır
                resized_image = image.resize((320, 240))  # 320x240 boyutuna yeniden boyutlandır

                # Yeniden boyutlandırılmış resmi kaydet
                resized_image.save(img_name)

                # Dosya yolunu ve adını yazdır
                print(img_name)  # "Kaydedildi: " yazmadan sadece dosya yolunu yazdır
                image_counter += 1  # Sayaç artır
                time.sleep(1)  # Her indirme arasında kısa bir bekleme süresi

            except Exception as e:
                print(f"Resim indirme hatası: {e} - URL: {img_url}")

print("Tüm resimler indirildi.")
