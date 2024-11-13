import requests
from bs4 import BeautifulSoup
import os
from PIL import Image
from io import BytesIO

# Başlangıç URL'si (acne ile ilgili liste sayfasının URL'si)
base_url = "https://www.dermis.net/dermisroot/tr/list/acne/search.htm"

# Arama sayfasına GET isteği gönder ve durumunu yazdır
response = requests.get(base_url)
print(f"Arama sayfası durumu: {response.status_code}")

# BeautifulSoup ile sayfanın HTML içeriğini parse et
soup = BeautifulSoup(response.content, 'html.parser')

# 'li' etiketlerini bul (liste öğeleri olarak resim detay linklerini içeriyor)
li_tags = soup.find_all('li')
print(f"Bulunan 'li' etiketleri: {len(li_tags)}")

# Resimlerin indirileceği klasörün adını belirle ve varsa klasörü oluştur
download_folder = "DermisAcne"
os.makedirs(download_folder, exist_ok=True)

# Klasördeki mevcut dosya sayısını sayarak sayaç başlat (yeniden başlatmada kaldığı yerden devam eder)
existing_files = len([name for name in os.listdir(download_folder) if os.path.isfile(os.path.join(download_folder, name))])
image_counter = existing_files + 1  # Yeni resim için dosya numarası başlat

# Her 'li' etiketi içindeki detay sayfası linkine git
for li in li_tags:
    # Detay sayfasının linkini al
    detail_link = li.find('a')
    if detail_link:
        detail_href = detail_link['href']
        detail_url = f"https://www.dermis.net/dermisroot/tr/{detail_href.strip('./')}"  # URL'yi tamamla
        print(f"Detay URL'si: {detail_url}")

        # Detay sayfasına GET isteği gönder
        detail_response = requests.get(detail_url)
        if detail_response.status_code == 200:
            detail_soup = BeautifulSoup(detail_response.content, 'html.parser')

            # Sayfada bulunan resimleri seç
            images = detail_soup.find_all('img')
            print(f"Bulunan resim sayısı: {len(images)}")

            # Her bir resim etiketi için işlem yap
            for img in images:
                # Resim URL'sini al
                img_url = img.get('src')
                if img_url:
                    # URL'yi tam haline getirmek için gerekli dönüşümleri yap
                    if img_url.startswith('..'):
                        img_url = f"https://www.dermis.net{img_url[2:]}"
                    elif img_url.startswith('.'):
                        img_url = f"https://www.dermis.net{img_url[1:]}"
                    elif not img_url.startswith('http'):
                        img_url = f"https://www.dermis.net{img_url}"

                    # Resmin kaydedileceği dosya adını oluştur
                    img_name = os.path.join(download_folder, f"{image_counter}.jpg")

                    # Aynı dosyanın mevcut olup olmadığını kontrol et ve tekrar indirme
                    if os.path.exists(img_name):
                        print(f"Dosya zaten mevcut: {img_name}. İndirme atlanıyor.")
                        continue

                    # Resmi indirme işlemi
                    try:
                        img_data = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                        print(f"İstek durumu: {img_data.status_code} - {img_url}")
                        img_data.raise_for_status()  # Hata durumunda istisna fırlat

                        # Resmi bellekte aç
                        image = Image.open(BytesIO(img_data.content))

                        # Resmi yeniden boyutlandır (320x240 piksel)
                        image = image.resize((320, 240), Image.LANCZOS)

                        # Resmi diske kaydet
                        image.save(img_name)
                        print(f"İndirildi: {img_name}")
                        image_counter += 1  # Resim sayacını bir artır
                    except Exception as e:
                        print(f"Resim indirme hatası: {e} - {img_url}")
                else:
                    print("Geçersiz resim URL'si")
        else:
            print(f"Detay sayfasına erişim hatası: {detail_response.status_code} - {detail_url}")
