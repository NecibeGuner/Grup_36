import os  # Dosya ve dizin işlemlerini yapmak için kullanılır (örneğin, klasör oluşturma, dosya listesi alma)
import requests  # HTTP istekleri yaparak internetten veri çekmek için kullanılır (örneğin, resim indirme)
from selenium import webdriver  # Web tarayıcısını otomatik olarak açmak ve kontrol etmek için kullanılır
from selenium.webdriver.chrome.options import Options  # Chrome tarayıcı ayarlarını yapılandırmak için kullanılır
from selenium.webdriver.common.by import By  # Selenium'un sayfadaki öğeleri bulmasına yardımcı olan bir modül
from selenium.webdriver.support import expected_conditions as EC  # Koşullu beklemeleri tanımlamak için kullanılır (örneğin, bir öğe görünene kadar beklemek)
from selenium.webdriver.support.ui import WebDriverWait  # Belirli bir süre boyunca öğenin yüklenmesini beklemek için kullanılır
from PIL import Image  # Python Imaging Library'nin bir parçası olan bu modül, görüntüleri işlemek için kullanılır (örneğin, yeniden boyutlandırma)
from io import BytesIO  # Bellekteki byte verilerini dosya benzeri bir nesne olarak kullanmak için kullanılır
import time  # Kodun belirli süre duraklamasını sağlamak için kullanılır (örneğin, sayfanın yüklenmesi için bekleme)

# Anahtar kelimeler
keywords = ["illüstrasyon", "illustration", "month card", "month cards", "cancer cell", "cancer cells",
            "metastatic melanoma", "before and after", "3d", "three dimensional", "poster", "posters",
            "month concept", "month concepts", "test", "tests", "kanserli hücre", "hücre",
            "infographic", "check", "examine", "analysis", "inspection", "microscope", "microscopic",
            "microscopic view", "dermatoscopy", "animal", "animals", "farkındalık",
            "kiraz anjiyom", "angioma", "game", "games", "surgery", "pathology", "laboratory",
            "monkeypox", "chickhenpox", "exercise", "shirt", "egzersiz", "eye cream", "alışveriş",
            "Çamaşır Makinesi", "sivrisinek", "kaşımak", "psoriasis", "sedef", "egzema", "dermatit",
            "acne", "makine"]

# Anahtar kelimeleri küçük harfe çevir
keywords = [keyword.lower() for keyword in keywords]

# İndirilecek resimlerin kaydedileceği klasörü oluştur
folder_name = "istock_elenecekler_vitiligo"
os.makedirs(folder_name, exist_ok=True)

# Chrome tarayıcı ayarları (headless modda çalıştırmak için)
chrome_options = Options()
chrome_options.add_argument("--headless")  # Gizli modda çalışır
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")

# WebDriver başlat
driver = webdriver.Chrome(options=chrome_options)
driver.set_window_size(1024, 768)  # Tarayıcı penceresi boyutunu ayarla

# requests oturumu başlat (bağlantıları yönetmek için)
session = requests.Session()

# Detay URL listesini aç ve her URL'yi işlemek için bir döngü başlat
with open("detail_url_istockvitiligo.txt", "r") as file:
    detail_urls = file.readlines()

# 1. URL'den başlayarak işlemler yapılacak
for i, url in enumerate(detail_urls, start=1):  # 1. URL’den itibaren işle
    url = url.strip()
    print(f"\n{i}. detay URL : {url}")

    success = False  # Her URL için başarı durumunu takip et
    retries = 3  # Her URL için maksimum 3 deneme

    # Her URL için maksimum 3 deneme yapılacak
    for attempt in range(retries):
        try:
            driver.get(url)  # Detay sayfasını aç

            # h1 başlık elemanını bul ve metni küçülterek anahtar kelime kontrolü yap
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

            # Eğer anahtar kelime bulunamazsa vitiligo kontrolü
            if not found_keyword:
                print("Anahtar kelime bulunamadı.")
                if "vitiligo" in title_text:
                    print("Başlıkta 'vitiligo' bulundu - Resim elenmeyecek.")
                    success = True
                    break  # Sonraki URL'ye geç
                else:
                    print("vitiligo kelimesi de bulunamadı - Resim elenecek klasöre indiriliyor.")
            else:
                print(f"Anahtar kelime bulundu: {found_keyword}")
                print("Resim indiriliyor...")

            # Anahtar kelime bulunursa veya vitiligo yoksa resmi indir
            if found_keyword or "vitiligo" not in title_text:
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
