import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from PIL import Image
from io import BytesIO
import time

# Anahtar kelimeler
keywords = [
    "illüstrasyon", "illustration", "cancer cell", "metastatic melanoma", "before and after", "3d",
    "poster", "month concept", "test", "kanser hücre", "infographic", "check", "muayene",
    "incele", "inceleme", "examination", "analysis", "inspection", "mikroskop",
    "mikroskobik", "microscope", "microscopic view", "dermoskopi", "dermatoscopy",
    "animal", "farkındalık", "cherry angioma", "oyun", "operation", "surgery", "pathology",
    "laboratory", "monkeypox", "exercise", "eye cream", "alışveriş", "sivrisinek", "mantar",
    "kaşıma", "gül hastalığı", "psoriasis", "sedef", "egzema", "dermatit", "machine", "makine"
]

# Klasör oluştur
folder_name = "acne_istock_elenecekler"
os.makedirs(folder_name, exist_ok=True)

# Chrome ayarları
chrome_options = Options()
chrome_options.add_argument("--headless")  # Gizli mod
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
driver = webdriver.Chrome(options=chrome_options)
driver.set_window_size(1024, 768)

# Detay URL listesini aç
with open("detail_url_istockacne.txt", "r") as file:
    detail_urls = file.readlines()

# Başlangıç URL'si
start_index = 1039
detail_urls = detail_urls[start_index - 1:]  # İlk 1020 URL'yi atla

# Oturum başlatma
session = requests.Session()

# Filtreleme işlemi
for i, url in enumerate(detail_urls, start=start_index):
    url = url.strip()
    print(f"\n{i}. detay URL : {url}")

    success = False  # Her URL için başarı durumunu takip et
    retries = 3  # Her URL için maksimum 3 deneme

    for attempt in range(retries):
        try:
            driver.get(url)

            # h1 başlık elemanını bul
            h1_element = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, "/html/body/div[2]/section/div/main/div/div/div/div[2]/section/div/h1"))
            )
            title_text = h1_element.text.lower()
            print(f"Anahtar kelime aranacak metin:\n1. başlık: {title_text}")

            # Anahtar kelime kontrolü
            found_keyword = next((keyword for keyword in keywords if keyword in title_text), None)

            # Eğer h1'de anahtar kelime bulunmazsa, h2 başlığını kontrol et
            if not found_keyword:
                try:
                    button = WebDriverWait(driver, 10).until(
                        EC.element_to_be_clickable(
                            (By.XPATH, "/html/body/div[2]/section/div/main/div/div/div/div[2]/section/div/h1/button"))
                    )
                    button.click()

                    h2_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located(
                            (By.XPATH, "/html/body/div[2]/section/div/main/div/div/div/div[2]/section/div[2]/h2"))
                    )
                    title_text = h2_element.text.lower()
                    print(f"Anahtar kelime aranacak metin:\n2. başlık: {title_text}")

                    found_keyword = next((keyword for keyword in keywords if keyword in title_text), None)
                except Exception:
                    print("Düğmeye tıklanamadı veya h2 başlığı bulunamadı.")

            # Eğer anahtar kelime bulunamazsa 'acne' veya 'akne' kontrolü yap
            if not found_keyword:
                print("Anahtar kelime bulunamadı.")
                if "acne" in title_text or "akne" in title_text:
                    print("Başlıkta 'acne' veya 'akne' bulundu - Resim elenmeyecek.")
                    success = True
                    break  # Sonraki URL'ye geç
                else:
                    print("Acne veya akne kelimeleri de bulunamadı - Resim elenecek klasöre indiriliyor.")
            else:
                print(f"Anahtar kelime bulundu: {found_keyword}")
                print("Resim indiriliyor...")

            # Anahtar kelime bulunursa veya "acne" veya "akne" yoksa resmi indir
            if found_keyword or ("acne" not in title_text and "akne" not in title_text):
                img_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//img[@data-testid='image-asset']"))
                )
                img_url = img_element.get_attribute("src")

                if img_url:
                    try:
                        img_data = session.get(img_url, timeout=10).content
                        image = Image.open(BytesIO(img_data)).convert("RGB")
                        resized_image = image.resize((320, 240))
                        # Dosya adını detay URL numarası ile kaydet
                        image_file_name = os.path.join(folder_name, f"{i}.jpg")
                        resized_image.save(image_file_name, "JPEG")
                        print(f"Resim {image_file_name} olarak kaydedildi.")
                        success = True
                        break  # İndirme başarılı olursa döngüden çık
                    except Exception as e:
                        print(f"Resim indirilirken hata oluştu: {e}")

        except Exception as e:
            print(f"Detay sayfasında hata oluştu, {attempt + 1}. deneme...: {e}")
            time.sleep(5)  # Yeniden denemeden önce bekle

        if success:
            break

# Tarayıcıyı ve oturumu kapat
driver.quit()
session.close()
