import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from PIL import Image
from io import BytesIO

# Anahtar kelimeler (güncellenmiş)
keywords = [
    "illüstrasyon", "illustration", "month card", "month cards", "cancer cell", "cancer cells",
    "metastatic melanoma", "metastatic melanomas", "before and after", "3d", "3-d", "three dimensional",
    "poster", "posters", "month concept", "month concepts", "test", "tests",
    "kanserli hücre", "kanserli hücreleri", "kanser hücresi", "hücre", "hücreler",
    "infographic", "infographics", "check", "checking", "muayene", "muayeneler", "incele",
    "inceleme", "incelemek", "inceleyen", "inceleyerek", "examination", "examine",
    "examining", "analysis", "analyze", "analyses", "inspecting", "inspection",
    "mikroskop", "mikroskob", "mikroskobik", "mikroskobik görüntü", "microscope", "microscopic", "microscopic view",
    "dermoskopi", "dermoskopik", "dermatoscopy", "dermatoscopic", "dermoscopy",
    "hayvan", "hayvanlar", "animal", "animals",
    "avrupa", "europe", "sevimli", "cute", "güzel", "beautiful",
    "kiraz anjiyom", "anjiyom", "cherry angioma", "angioma",
    "oyun", "oyunlar", "game", "games", "ameliyat", "operation", "surgery",
    "pathology", "pathologies", "laboratory", "lab"
]

# Klasör oluştur
folder_name = "elenecekresimler_istock"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Chrome ayarları
chrome_options = Options()
driver = webdriver.Chrome(options=chrome_options)
driver.maximize_window()

# Detay URL listesini aç
with open("detay_url_listesi.txt", "r") as file:
    detail_urls = file.readlines()

# Mevcut resim sayısını al
existing_images_count = len([name for name in os.listdir(folder_name) if os.path.isfile(os.path.join(folder_name, name))])

# Filtreleme işlemi
for i, url in enumerate(detail_urls, start=1):
    url = url.strip()
    print(f"\n{i}. Detay URL: {url}")
    driver.get(url)

    try:
        # Başlık elemanını al
        h1_element = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.XPATH, "//h1"))
        )
        title_text = h1_element.text
        title_text = title_text.lower().replace("i̇", "i").replace("ı", "i")
        print(f"Başlık metni: {title_text}")

        # Anahtar kelimeleri kontrol et
        found_keyword = None
        for keyword in keywords:
            if keyword in title_text:
                found_keyword = keyword
                break

        if found_keyword:
            print(f"Aranan kelime bulundu: '{found_keyword}' - Resim indiriliyor...")

            # Resmi alternatif yollarla bul ve indir
            img_url = None
            try:
                img_element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, "//img[@data-testid='image-asset']"))
                )
                img_url = img_element.get_attribute("src")
            except:
                try:
                    img_element = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, "//div[@class='_StJSx0EdFAmrG6JvZo7']//img"))
                    )
                    img_url = img_element.get_attribute("src")
                except:
                    try:
                        img_element = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.XPATH, "//img[contains(@class, 'yGh0CfFS4AMLWjEE9W7v')]"))
                        )
                        img_url = img_element.get_attribute("src")
                    except Exception as e:
                        print("Resim bulunamadı.")

            # Resmi indir ve kaydet
            if img_url:
                try:
                    img_data = requests.get(img_url).content
                    image = Image.open(BytesIO(img_data)).convert("RGB")
                    resized_image = image.resize((320, 240))
                    image_file_name = os.path.join(folder_name, f"{existing_images_count + i}.jpg")
                    resized_image.save(image_file_name, "JPEG")
                    print(f"{image_file_name} indirildi.")
                except Exception as e:
                    print(f"Resim indirilirken hata oluştu: {e}")
        else:
            print("Aranan kelime bulunamadı - Resim indirilemiyor.")
    except Exception as e:
        print(f"Detay sayfasında hata oluştu: {e}")

# Tarayıcıyı kapat
driver.quit()
