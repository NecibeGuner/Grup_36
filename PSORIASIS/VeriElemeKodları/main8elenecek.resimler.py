import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait
from PIL import Image
from io import BytesIO

# Anahtar kelimeler
keywords = ["illüstrasyon", "illustration", "month card", "month cards", "cancer cell", "cancer cells",
            "metastatic melanoma", "metastatic melanomas", "before and after", "3d", "3-d", "three dimensional",
            "poster", "posters", "month concept", "month concepts", "test", "tests",
            "kanserli hücre", "kanserli hücreleri", "kanser hücresi", "hücre", "hücreler",
            "infographic", "infographics", "check", "checking", "muayene", "muayeneler", "incele",
            "inceleme", "incelemek", "inceleyen", "inceleyerek", "examination", "examine",
            "examining", "analysis", "analyze", "analyses", "inspecting", "inspection",
            "mikroskop", "mikroskob", "mikroskobik", "mikroskobik görüntü", "microscope", "microscopic",
            "microscopic view", "dermoskopi", "dermoskopik", "dermatoscopy", "dermatoscopic", "dermoscopy",
            "hayvan", "hayvanlar", "animal", "animals", "farkındalık", "farkindalik", "avrupa", "europe",
            "sevimli", "cute", "güzel", "beautiful", "kiraz anjiyom", "anjiyom", "cherry angioma", "angioma",
            "oyun", "oyunlar", "game", "games", "ameliyat", "operation", "surgery", "pathology", "pathologies",
            "laboratory", "lab", "vitiligo", "monkeypox", "chickhenpox", "exercise", "bakım", "shirt", "egzersiz",
            "bel fıtığı", "desen", "eye cream", "alışveriş", "bilgisayar", "Çamaşır Makinesi", "Sivrisinek",
            "sivrisinek", "mantar", "kaşıdı", "kaşımak","kaşidi", "kaşıyor", "kaşıma", "Kaşıdı", "Kaşımak", "Kaşıyor",
            "Kaşıma", "Kaşidi", "kaşidi", "bakim", "Gül Hastalığı"]

# Klasör oluştur
folder_name = "elenecekresimler_istock_psoriasis"
if not os.path.exists(folder_name):
    os.makedirs(folder_name)

# Chrome ayarları
chrome_options = Options()
chrome_options.add_argument("--headless")  # Gizli mod
driver = webdriver.Chrome(options=chrome_options)
driver.set_window_size(1024, 768)  # Küçük bir pencere boyutu belirleyin

# Detay URL listesini aç
with open("detay_url_listesi_istockpsoriasis.txt", "r") as file:
    detail_urls = file.readlines()

# Mevcut resim sayısını al
existing_images_count = len([name for name in os.listdir(folder_name) if os.path.isfile(os.path.join(folder_name, name))])

# Oturum başlatma
session = requests.Session()

# Filtreleme işlemi
for i, url in enumerate(detail_urls, start=1):
    url = url.strip()
    print(f"\n{i}. Detay URL: {url}")
    driver.get(url)

    try:
        # Başlık elemanını al
        h1_element = WebDriverWait(driver, 5).until(
            EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/section/div/main/div/div/div/div[2]/section/div/h1"))
        )
        title_text = h1_element.text.lower().replace("i̇", "i").replace("ı", "i")
        print(f"Başlık metni (h1): {title_text}")

        # Anahtar kelimeleri h1 başlığında kontrol et
        found_keyword = None
        for keyword in keywords:
            if keyword in title_text:
                found_keyword = keyword
                break

        # Eğer h1 başlığında anahtar kelime bulunamazsa h2 başlığını kontrol et
        if not found_keyword:
            try:
                button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.XPATH, "/html/body/div[2]/section/div/main/div/div/div/div[2]/section/div/h1/button"))
                )
                button.click()  # Düğmeye tıkla

                # h2 başlığını al ve anahtar kelimeleri kontrol et
                h2_element = WebDriverWait(driver, 5).until(
                    EC.presence_of_element_located((By.XPATH, "/html/body/div[2]/section/div/main/div/div/div/div[2]/section/div[2]/h2"))
                )
                title_text = h2_element.text.lower().replace("i̇", "i").replace("ı", "i")
                print(f"Başlık metni (h2): {title_text}")

                for keyword in keywords:
                    if keyword in title_text:
                        found_keyword = keyword
                        break
            except Exception:
                print("Düğmeye tıklanamadı veya h2 başlığı bulunamadı.")

        if found_keyword:
            print(f"Anahtar kelime bulundu: '{found_keyword}' - Resim indiriliyor...")

            # Resmi indir
            img_element = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.XPATH, "//img[@data-testid='image-asset']"))
            )
            img_url = img_element.get_attribute("src")

            if img_url:
                try:
                    img_data = session.get(img_url, timeout=5).content
                    image = Image.open(BytesIO(img_data)).convert("RGB")
                    resized_image = image.resize((320, 240))
                    image_file_name = os.path.join(folder_name, f"{existing_images_count + i}.jpg")
                    resized_image.save(image_file_name, "JPEG")
                    print(f"{image_file_name} indirildi.")
                except Exception as e:
                    print(f"Resim indirilirken hata oluştu: {e}")
        else:
            print("Anahtar kelime bulunamadı - Resim indirilemiyor.")
    except Exception as e:
        print(f"Detay sayfasında hata oluştu: {e}")

# Tarayıcıyı ve oturumu kapat
driver.quit()
session.close()
