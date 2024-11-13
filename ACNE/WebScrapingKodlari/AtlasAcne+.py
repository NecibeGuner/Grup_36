import requests  # HTTP istekleri yaparak internetten veri çekmek için kullanılır
from bs4 import BeautifulSoup  # HTML ve XML dosyalarını ayrıştırmak (parse etmek) için kullanılır
import os  # Dosya ve dizin işlemleri yapmak için kullanılan modül
from urllib.parse import urljoin  # Bağlantıları birleştirmek (URL tamamlama) için kullanılır
from PIL import Image  # Görüntüleri işlemek için kullanılan bir modül (örneğin, yeniden boyutlandırma)
from io import BytesIO  # Bellekteki byte verilerini dosya benzeri bir nesne olarak kullanmak için kullanılır

# Başlangıç URL'si
base_url = "https://atlasdermatologico.com.br/search.jsf?q=acne"

# Ana sayfadan hastalık bağlantılarını al
response = requests.get(base_url)  # Ana sayfaya istek gönderir
soup = BeautifulSoup(response.content, 'html.parser')  # Ana sayfanın içeriğini ayrıştırır

# Liste elemanlarını bul
disease_list = soup.find('ul', id='j_idt23_list')  # Hastalıkların listelendiği <ul> öğesini bulur
disease_links = disease_list.find_all('a')  # Her hastalık için bağlantıları alır

# Resimleri indirmek için yeni bir klasör oluştur
download_folder = "AtlasAcne"
os.makedirs(download_folder, exist_ok=True)  # Eğer klasör yoksa oluşturur

# Klasördeki mevcut dosya sayısına göre sayaç başlat
image_counter = len(os.listdir(download_folder)) + 1  # Mevcut dosya sayısını kontrol edip sayaç başlatır

# Her hastalık bağlantısı için döngü
for index, link in enumerate(disease_links):
    disease_url = urljoin(base_url, link['href'])  # Tam URL'yi oluştur

    # Hastalık sayfasına isteği gönder
    disease_response = requests.get(disease_url)  # Her hastalık sayfasına istek gönderir
    disease_soup = BeautifulSoup(disease_response.content, 'html.parser')  # Sayfanın içeriğini ayrıştırır

    # Resimleri bul
    images = disease_soup.find_all('img')  # Sayfadaki tüm resim öğelerini bulur

    # Her resmi indir
    for img in images:
        img_url = img.get('src')  # Resmin URL'sini alır
        if img_url:
            # Tam URL'yi oluştur
            img_url = urljoin(disease_url, img_url)  # Resim URL'sini tam bir URL yapar

            # Resmin adını oluştur (Sıralı numaralarla)
            img_name = os.path.join(download_folder, f"{image_counter}.jpg")  # Resim dosya adı oluşturur

            # Daha önce indirilip indirilmediğini kontrol et
            if os.path.exists(img_name):
                continue  # Eğer dosya varsa, atla

            # Resmi indir
            try:
                img_data = requests.get(img_url).content  # Resim verisini indirir
                image = Image.open(BytesIO(img_data))  # Resmi açar

                # Resmi yeniden boyutlandır
                resized_image = image.resize((320, 240))  # 320x240 boyutuna yeniden boyutlandır

                # Yeniden boyutlandırılmış resmi kaydet
                resized_image.save(img_name)  # Yeniden boyutlandırılmış resmi kaydeder

                # Dosya yolunu ve adını yazdır
                print(img_name)  # "Kaydedildi: " yazmadan sadece dosya yolunu yazdırır
                image_counter += 1  # Sayaç artır
            except Exception as e:
                print(f"Resim indirme hatası: {e}")  # Hata varsa hatayı yazdır

print("Tüm resimler indirildi.")  # İndirme işlemi tamamlandığında bildirim yapar
