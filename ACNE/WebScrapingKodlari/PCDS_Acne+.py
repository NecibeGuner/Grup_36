import requests
from bs4 import BeautifulSoup
import os
from PIL import Image
from io import BytesIO

# Ana URL (PCDS sitesinde "a" harfiyle başlayan klinik listesinin URL'si)
base_url = "https://www.pcds.org.uk"
main_url = f"{base_url}/clinical-a-z-list/a"

# Ana sayfayı al ve durumunu kontrol et
response = requests.get(main_url)
if response.status_code != 200:
    print(f"Sayfa alınamadı: {main_url} - Hata Kodu: {response.status_code}")
    exit()

# BeautifulSoup ile sayfanın içeriğini parse et
soup = BeautifulSoup(response.text, 'html.parser')

# "Acne" ile alakalı bağlantıları bul
acne_links = [a['href'] for a in soup.find_all('a', href=True) if 'acne' in a['href'].lower()]

# Resimlerin indirileceği klasörü oluştur
folder_name = 'PcdsAcne'
os.makedirs(folder_name, exist_ok=True)

# Klasördeki mevcut dosya sayısını belirleyerek sayaç başlat
existing_files_count = len([name for name in os.listdir(folder_name) if os.path.isfile(os.path.join(folder_name, name))])
image_counter = existing_files_count + 1

# Her bir "acne" bağlantısını işlemeye başla
for link in acne_links:
    # Tam URL'yi oluştur
    full_url = link if link.startswith("http") else f"{base_url}{link}"
    print(f"İşleniyor: {full_url}")

    try:
        # Bağlantıyı al ve durumunu kontrol et
        response = requests.get(full_url)
        if response.status_code != 200:
            print(f"Sayfa alınamadı: {full_url} - Hata Kodu: {response.status_code}")
            continue

        # Sayfanın içeriğini BeautifulSoup ile parse et
        soup = BeautifulSoup(response.text, 'html.parser')
        images = soup.find_all('img')  # Sayfadaki tüm resimleri bul

        for img_tag in images:
            if img_tag.has_attr('src'):
                # Resim URL'sini al ve tam URL'yi oluştur
                image_url = img_tag['src']
                if image_url.startswith("//"):
                    image_url = "https:" + image_url
                elif not image_url.startswith("http"):
                    image_url = base_url + image_url

                # Dosya adını belirle (mevcut resim sayısına göre)
                image_name = os.path.join(folder_name, f"{image_counter}.jpg")

                # Aynı dosya mevcutsa indirmeyi atla
                if os.path.exists(image_name):
                    print(f"Dosya zaten mevcut: {image_name}. İndirme atlanıyor.")
                    continue

                try:
                    # Resim verisini indir ve durumunu kontrol et
                    img_data = requests.get(image_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                    img_data.raise_for_status()  # İndirme hatası varsa hata fırlat
                    image = Image.open(BytesIO(img_data.content))  # Resmi bellekte aç
                    resized_image = image.resize((320, 240))  # Resmi yeniden boyutlandır

                    # Resmi belirtilen klasöre kaydet
                    resized_image.save(image_name)
                    print(f"{image_name} indirildi.")
                    image_counter += 1  # Sayaç artır

                except Exception as e:
                    print(f"Resim indirme hatası: {e} - {image_url}")

    except Exception as e:
        print(f"Sayfa işlenirken hata oluştu: {e} - {full_url}")

# Toplam indirilen yeni resim sayısını bildir
print(f"İndirme tamamlandı. Toplam indirilen yeni resim sayısı: {image_counter - existing_files_count}")
