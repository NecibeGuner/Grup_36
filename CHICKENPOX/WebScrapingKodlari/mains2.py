import os
import requests
from bs4 import BeautifulSoup
from PIL import Image
from io import BytesIO

# Hedef URL
url = "https://www.immunize.org/clinical/image-library/varicella/"

# Klasör adı
folder_name = "mains2"

# Klasörü oluştur
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Mevcut resim sayısını kontrol et
existing_images = len(os.listdir(folder_name))

# Sayfayı iste
response = requests.get(url)
print(f"HTTP Durum Kodu: {response.status_code}")  # HTTP durum kodunu yazdır

# Sayfa içeriğini kontrol et
if response.status_code == 200:
    soup = BeautifulSoup(response.content, 'html.parser')

    # Tüm img etiketlerini al
    all_images = soup.find_all('img')

    # Resimlerin bulunduğu alanı kontrol et
    image_elements = [img for img in all_images if img.find_parent("li")]

    print(f"Bulunan img etiketlerinin sayısı: {len(image_elements)}")  # Bulunan img sayısını yazdır

    # Resimleri indir
    for index, img in enumerate(image_elements, start=existing_images + 1):
        img_url = img['src']  # Resim URL'si
        # Tam URL'yi kontrol et
        if not img_url.startswith("http"):
            img_url = "https://www.immunize.org" + img_url  # URL eksikse düzelt

        # Resim dosyasının kaydedileceği yolu oluştur
        img_filename = os.path.join(folder_name, f"{index}.jpg")

        # Eğer resim zaten varsa, atla
        if os.path.exists(img_filename):
            print(f"Zaten var: {img_filename}")
            continue

        try:
            img_data = requests.get(img_url).content  # Resim verisi
            # Resmi aç ve yeniden boyutlandır
            image = Image.open(BytesIO(img_data)).convert("RGB")
            resized_image = image.resize((320, 240))  # Resmi 320x240 boyutuna yeniden boyutlandır

            # Resmi kaydet
            resized_image.save(img_filename, "JPEG")
            print(f"Kaydedildi: {img_filename}")
        except Exception as e:
            print(f"Resim indirilemedi: {img_url}, hata: {e}")

    print("Tüm resimler indirildi.")
else:
    print("Sayfa alınamadı.")
