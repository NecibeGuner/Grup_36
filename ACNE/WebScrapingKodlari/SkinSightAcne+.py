from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
import os
import requests
from io import BytesIO

# Chrome tarayıcı ayarları
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
driver = webdriver.Chrome(options=options)

# İndirilecek resimlerin kaydedileceği klasör
download_folder = "SkinSightAcne"
os.makedirs(download_folder, exist_ok=True)

# Klasördeki mevcut dosya sayısını belirleyerek sayaç başlat
existing_images_count = len([name for name in os.listdir(download_folder) if os.path.isfile(os.path.join(download_folder, name))])
image_counter = existing_images_count + 1  # Yeni resim adlandırması başlangıcı

# İndirmek istediğiniz sayfaların URL'leri
urls = [
    "https://skinsight.com/skin-conditions/acne-vulgaris/child/",
    "https://skinsight.com/skin-conditions/acne-vulgaris/teen/",
    "https://skinsight.com/skin-conditions/acne-vulgaris/"
]

# Toplam indirilen resim sayısını başlat
total_images_downloaded = 0

# Her URL için resimleri indir
for url in urls:
    # Sayfayı aç
    driver.get(url)

    # Resimlerin yüklenmesi için bekle
    WebDriverWait(driver, 15).until(EC.presence_of_all_elements_located((By.TAG_NAME, "img")))

    # Sayfadaki tüm resimleri bul
    images = driver.find_elements(By.TAG_NAME, "img")
    print(f"{len(images)} resim bulundu.")

    # Her bir resim için işlem yap
    for img in images:
        # Resim URL'sini al
        img_url = img.get_attribute("src")
        if img_url and not img_url.startswith('data:'):  # "data:" ile başlayan base64 resim URL'lerini atla
            # Resmi indir
            try:
                response = requests.get(img_url, headers={"User-Agent": "Mozilla/5.0"}, timeout=10)
                if response.status_code == 200:
                    # Resmi aç ve yeniden boyutlandır
                    img_data = Image.open(BytesIO(response.content))
                    img_data = img_data.resize((320, 240))  # Resmi 320x240 olarak yeniden boyutlandır

                    # Resim adını ayarla, mevcut resim sayısına göre adlandır
                    img_name = os.path.join(download_folder, f"{image_counter}.jpg")
                    img_data.save(img_name, "JPEG")  # Yeniden boyutlandırılan resmi kaydet
                    print(f"{img_name} indirildi.")  # Başarılı indirme mesajı

                    # Sayaçları artır
                    image_counter += 1  # İsimlendirme sayacını artır
                    total_images_downloaded += 1  # İndirilen toplam resim sayısını artır
            except Exception as e:
                print(f"Resim indirilirken hata oluştu: {e}")

# İndirme işlemi tamamlandı mesajı
print(f"İndirme tamamlandı. Toplam indirilen yeni resim sayısı: {total_images_downloaded}")

# Tarayıcıyı kapat
driver.quit()
