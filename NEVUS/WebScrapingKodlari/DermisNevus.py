import requests
from bs4 import BeautifulSoup
import os
from PIL import Image
from io import BytesIO

# Başlangıç URL'si (nevus için)
base_url = "https://www.dermis.net/dermisroot/tr/list/nevus/search.htm"

# İndirilecek klasör
download_folder = "DermisNevus"
os.makedirs(download_folder, exist_ok=True)

# Mevcut resim sayısını al ve yeni resimler için başlangıç numarasını ayarla
existing_images_count = len(os.listdir(download_folder))
img_counter = existing_images_count + 1  # Yeni resimlerin adlandırması mevcut sayıdan başlar

# Ana sayfadaki bağlantıları bul ve her bir bağlantıdaki resimleri indir
response = requests.get(base_url)
print(f"Arama sayfası durumu: {response.status_code}")
soup = BeautifulSoup(response.content, 'html.parser')
li_tags = soup.find_all('li')
print(f"Bulunan 'li' etiketleri: {len(li_tags)}")

# Her 'li' etiketi için detay sayfasını çek
for li in li_tags:
    detail_link = li.find('a')
    if detail_link:
        detail_href = detail_link['href']
        detail_url = f"https://www.dermis.net/dermisroot/tr/{detail_href.strip('./')}"
        print(f"Detay URL'si: {detail_url}")

        # Detay sayfasına isteği gönder
        detail_response = requests.get(detail_url)
        if detail_response.status_code == 200:
            detail_soup = BeautifulSoup(detail_response.content, 'html.parser')
            images = detail_soup.find_all('img')
            print(f"Bulunan detay sayfası resim sayısı: {len(images)}")

            # Resimleri indir
            for img in images:
                img_url = img.get('src')
                if img_url:
                    # URL'yi tamamla
                    if img_url.startswith('..'):
                        img_url = f"https://www.dermis.net{img_url[2:]}"
                    elif img_url.startswith('.'):
                        img_url = f"https://www.dermis.net{img_url[1:]}"
                    elif not img_url.startswith('http'):
                        img_url = f"https://www.dermis.net{img_url}"

                    # Resim adı ve yolunu oluştur
                    img_name = os.path.join(download_folder, f"{img_counter}.jpeg")  # Her zaman .jpeg uzantısı ile kaydet

                    # Resmi indirme ve kaydetme işlemi
                    try:
                        img_data = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                        print(f"Detay resim isteği durumu: {img_data.status_code} - {img_url}")
                        img_data.raise_for_status()
                        image = Image.open(BytesIO(img_data.content))
                        image = image.resize((320, 240), Image.LANCZOS)
                        image.save(img_name)  # JPEG formatında kaydet

                        print(f"İndirildi: {img_name}")
                        img_counter += 1  # Resim numarasını artır

                    except Exception as e:
                        print(f"Detay resim indirme hatası: {e} - {img_url}")
                else:
                    print("Geçersiz resim URL'si")
        else:
            print(f"Detay sayfasına erişim hatası: {detail_response.status_code} - {detail_url}")

# Belirtilen ikinci URL için işlem (21372 numaralı detay sayfası)
second_url = "https://www.dermis.net/dermisroot/tr/21372/diagnose.htm"
response = requests.get(second_url)
print(f"İkinci sayfa durumu: {response.status_code}")
soup = BeautifulSoup(response.content, 'html.parser')
images = soup.find_all('img')
print(f"İkinci sayfadaki bulunan resim sayısı: {len(images)}")

# İkinci sayfadaki resimleri indir
for img in images:
    img_url = img.get('src')
    if img_url:
        # URL'yi tamamla
        if img_url.startswith('..'):
            img_url = f"https://www.dermis.net{img_url[2:]}"
        elif img_url.startswith('.'):
            img_url = f"https://www.dermis.net{img_url[1:]}"
        elif not img_url.startswith('http'):
            img_url = f"https://www.dermis.net{img_url}"

        # Resim adı ve yolunu oluştur
        img_name = os.path.join(download_folder, f"{img_counter}.jpeg")  # Her zaman .jpeg uzantısı ile kaydet

        # Resmi indirme ve kaydetme işlemi
        try:
            img_data = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
            print(f"İkinci sayfa resim isteği durumu: {img_data.status_code} - {img_url}")
            img_data.raise_for_status()
            image = Image.open(BytesIO(img_data.content))
            image = image.resize((320, 240), Image.LANCZOS)
            image.save(img_name)  # JPEG formatında kaydet

            print(f"İndirildi: {img_name}")
            img_counter += 1  # Resim numarasını artır
        except Exception as e:
            print(f"İkinci sayfa resim indirme hatası: {e} - {img_url}")
    else:
        print("Geçersiz resim URL'si")

print("İndirme işlemi tamamlandı.")
