import requests
from bs4 import BeautifulSoup
import os
import time
import cv2
import numpy as np

# Başlangıç URL'si
base_url = "https://www.dermis.net/dermisroot/tr/list/psoriasis/search.htm"

# İsteği gönder
response = requests.get(base_url)

# BeautifulSoup ile sayfayı parse et
soup = BeautifulSoup(response.content, 'html.parser')

# 'li' etiketlerini bul
li_tags = soup.find_all('li')

# Yeni klasör oluştur (resimler bu klasöre indirilecek)
download_folder = "main2"
os.makedirs(download_folder, exist_ok=True)

# Klasördeki mevcut dosya sayısına göre sayaç başlat
image_counter = len(os.listdir(download_folder)) + 1

# Her 'li' etiketi için detay sayfasını çek
for li in li_tags:
    detail_link = li.find('a')
    if detail_link:
        detail_href = detail_link['href']

        # URL'yi doğru oluştur
        detail_url = f"https://www.dermis.net/dermisroot/tr/{detail_href.strip('./')}"

        # Detay sayfasına isteği gönder
        detail_response = requests.get(detail_url)
        if detail_response.status_code == 200:
            detail_soup = BeautifulSoup(detail_response.content, 'html.parser')

            # Resimleri bul
            images = detail_soup.find_all('img')

            # Resimleri indir
            for img in images:
                img_url = img.get('src')
                if img_url:
                    # Eğer URL tam değilse, tamamla
                    if img_url.startswith('..'):
                        img_url = f"https://www.dermis.net{img_url[2:]}"  # '..' kısmını temizle
                    elif img_url.startswith('.'):
                        img_url = f"https://www.dermis.net{img_url[1:]}"  # '.' kısmını temizle
                    elif not img_url.startswith('http'):
                        img_url = f"https://www.dermis.net{img_url}"

                    # Resim adı ve yolunu oluştur (sıralı numaralarla)
                    img_name = os.path.join(download_folder, f"{image_counter}.jpg")

                    # Aynı resmin tekrar indirilmesini engelle
                    if os.path.exists(img_name):
                        continue  # Dosya zaten mevcut, indirme atlanıyor

                    # Resmi indirme
                    try:
                        img_data = requests.get(img_url).content
                        with open(img_name, 'wb') as handler:
                            handler.write(img_data)

                        # Resmi OpenCV ile netleştir
                        img_cv = cv2.imread(img_name)

                        # Renk dengesini artırmak için histogram eşitleme
                        img_yuv = cv2.cvtColor(img_cv, cv2.COLOR_BGR2YUV)
                        img_yuv[:,:,0] = cv2.equalizeHist(img_yuv[:,:,0])
                        img_cv = cv2.cvtColor(img_yuv, cv2.COLOR_YUV2BGR)

                        # Daha hafif bir keskinleştirme uygula
                        kernel = np.array([[0, -1, 0], [-1, 5, -1], [0, -1, 0]])  # Keskinleştirme filtresi
                        sharpened = cv2.filter2D(img_cv, -1, kernel)

                        # Yeniden boyutlandırma (DPI'yi dikkate alarak)
                        sharpened_resized = cv2.resize(sharpened, (320, 240), interpolation=cv2.INTER_LANCZOS4)

                        # Netleştirilmiş resmi kaydet
                        cv2.imwrite(img_name, sharpened_resized)

                        # Dosya yolunu ve adını ekrana yazdır
                        print(f"{img_name}")

                        image_counter += 1  # Resim sayacını artır
                        time.sleep(1)  # Sunucuya nazik olmak için kısa bir bekleme süresi ekle
                    except Exception as e:
                        print(f"İndirme hatası: {e}")  # Hata olursa göster
                else:
                    continue  # Geçersiz resim URL'si varsa, döngü devam etsin
        else:
            continue  # Hata varsa döngü devam etsin
