import os
import time
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from PIL import Image
from io import BytesIO

# İndirilen resimleri kaydetmek için klasör oluşturma
folder_name = "vitiligomain2"
os.makedirs(folder_name, exist_ok=True)

# Detay URL'leri kaydetmek için dosya aç (veri eleme amacıyla URL'leri saklar)
url_file_path = "detail_url_openi_vitiligo.txt"
with open(url_file_path, "a") as url_file:

    # ChromeDriver seçenekleri
    chrome_options = Options()
    chrome_options.add_argument("--headless")  # Tarayıcı arka planda çalışır
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")

    # WebDriver başlat
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 10)  # Öğelerin yüklenmesini beklemek için 10 saniyelik süre

    # İlk sayfa URL'si (her sayfa için 'm' parametresi değişiyor)
    base_url = "https://openi.nlm.nih.gov/gridquery?q=vitiligo&m={}&n=1000&it=xg"

    # Global resim sayacını başlatma
    image_counter = len(os.listdir(folder_name))  # Klasördeki mevcut dosya sayısı kadar başlat
    max_images_to_download = 750  # İndirilecek maksimum resim sayısı

    # Resim indirme fonksiyonu
    def download_images():
        global image_counter
        try:
            # 'grid' içeren öğenin görünmesini bekleyin (sayfanın yüklendiğini anlamak için)
            wait.until(EC.visibility_of_element_located((By.CSS_SELECTOR, 'div#grid')))
            image_elements = driver.find_elements(By.CSS_SELECTOR, 'div#grid a')  # Tüm resim bağlantılarını al

            # Her bir resim bağlantısı üzerinde işlem yap
            for element in image_elements:
                if image_counter >= max_images_to_download:
                    print("Maksimum indirme sayısına ulaşıldı, indirme işlemi durduruldu.")
                    return  # Maksimum resim sayısına ulaşıldıysa işlemi sonlandır

                # Detay URL'sini al ve dosyaya kaydet (veri eleme amacıyla URL'leri saklar)
                detail_url = element.get_attribute("href")
                url_file.write(detail_url + "\n")  # Detay URL'sini dosyaya ekle
                print(f"Detay URL kaydedildi: {detail_url}")

                # Resim URL'sini al
                img = element.find_element(By.TAG_NAME, "img")
                img_url = img.get_attribute("src")  # Resim kaynağını al
                if img_url:
                    # Resmi indir
                    img_data = requests.get(img_url).content
                    image = Image.open(BytesIO(img_data))
                    resized_image = image.resize((320, 240))  # Resmi 320x240 boyutuna getir

                    # Resmin adını oluştur ve kaydet
                    img_name = os.path.join(folder_name, f"{image_counter + 1}.jpg")
                    resized_image.save(img_name)  # Resmi kaydet
                    print(f"{img_name} indirildi.")  # Kaydedilen dosyanın adıyla mesaj yazdır
                    image_counter += 1  # Resim sayacını artır
                else:
                    print("Resim URL'si bulunamadı.")  # Eğer resim URL'si yoksa uyarı mesajı
        except Exception as e:
            print(f"Resim indirme sırasında hata oluştu: {e}")  # Genel bir hata oluşursa hata mesajı yazdır

    # Sayfa sayısını belirleme (her 100 resimde bir yeni sayfa açmak için)
    page_count = 17

    # Belirtilen sayfa sayısı kadar döngüyle işlem yap
    for page_index in range(page_count):
        # Maksimum resim sayısına ulaşıldığında döngüyü kır
        if image_counter >= max_images_to_download:
            break

        # 'm' parametresini sayfa indeksine göre ayarla ve URL oluştur
        m_value = page_index * 100 + 1  # Her sayfa için başlangıç değeri değişir
        current_url = base_url.format(m_value)
        driver.get(current_url)  # Güncellenen URL'yi tarayıcıda aç
        download_images()  # Resim indirme fonksiyonunu çağır

    # WebDriver'ı kapatma
    driver.quit()
