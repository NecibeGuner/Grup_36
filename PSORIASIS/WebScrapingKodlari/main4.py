import requests
from bs4 import BeautifulSoup
import os
from PIL import Image
from io import BytesIO

# Hedef URL
url = "https://www.pcds.org.uk/clinical-guidance/psoriasis-an-overview"

# Sayfayı al
response = requests.get(url)
soup = BeautifulSoup(response.text, 'html.parser')

# Resimleri bul
images = soup.find_all('div', class_='item item-1-8 image')

# Klasör adı (Tüm resimler bu klasöre indirilecek)
folder_name = 'main4'

# Klasörü oluştur (mevcut değilse oluştur)
os.makedirs(folder_name, exist_ok=True)

# Klasördeki mevcut dosya sayısına göre sayaç başlat
image_counter = len(os.listdir(folder_name)) + 1

# Resim URL'lerini ve kaydetme işlemini yap
for img_div in images:
    img_tag = img_div.find('img')
    if img_tag and img_tag['src']:
        image_url = f"https:{img_tag['src']}"  # Protokol ekle
        image_name = os.path.join(folder_name, f"{image_counter}.jpeg")  # Dosya adını .jpeg ile belirle

        # Daha önce indirilip indirilmediğini kontrol et
        if os.path.exists(image_name):
            print(f"Dosya zaten mevcut: {image_name}. İndirme atlanıyor.")
        else:
            try:
                # Resmi indir
                img_data = requests.get(image_url).content
                image = Image.open(BytesIO(img_data))  # Resmi aç

                # Resmi yeniden boyutlandır
                resized_image = image.resize((320, 240))  # 320x240 boyutuna yeniden boyutlandır

                # Resmi her zaman JPEG formatında ve .jpeg uzantısıyla kaydet
                resized_image.convert('RGB').save(image_name, 'JPEG')  # JPEG formatında kaydet

                print(f"{image_name} olarak kaydedildi.")  # Kaydedilen dosya yolunu yazdır
                image_counter += 1  # Resim sayacını artır

            except Exception as e:
                print(f"Resim indirme hatası: {e} - {image_url}")
