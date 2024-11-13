import os
import requests
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import NoSuchElementException, TimeoutException
from PIL import Image
from io import BytesIO
from concurrent.futures import ThreadPoolExecutor

# Klasör oluşturma (resimlerin kaydedileceği klasör)
os.makedirs("acne_openi_elenecekler", exist_ok=True)

# Anahtar kelimeler listesi (her kelime küçük harf)
keywords = [
    "%", "(%)", "üç boyutlu", "histopatolojik", "şiddet indeksi", "fareler", "fare", "radyografik",
    "görüntüleme", "sitometre", "biyopsi", "histolojik", "bitki", "hayvan", "tomografi", "karşılaştırma",
    "grafik", "çalışma", "mri", "sunumu", "hipergranülozis", "histoloji", "fotomikrografi", "vakuolizasyon",
    "infiltrat", "röntgen", "3d", "biopsy", "plant", "animal", "comparison", "study", "research",
    "statistics", "dağılım", "hücresel", "expression", "varyasyon", "micrograph", "incidence",
    "prevalence", "concentration", "epidemioloji", "optik", "patoloji", "moleküler", "biochemistry",
    "diffusion", "solution", "mutation", "genetik", "molecular", "models", "micro", "report", "pathology"
]

# ChromeDriver seçenekleri
chrome_options = Options()
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")

# Çoklu işlem fonksiyonu
def process_url(index, url):
    driver = webdriver.Chrome(options=chrome_options)
    wait = WebDriverWait(driver, 15)
    url = url.strip()
    output = f"{index}. detay URL : {url}\nAnahtar kelime aranacak metin:\n"

    try:
        driver.get(url)

        # İlk başlıkta anahtar kelimeleri arama
        try:
            content_element1 = wait.until(EC.visibility_of_element_located(
                (By.XPATH, '//*[@id="content"]/app-detailedresult/div[1]/div/div[1]/div[1]')))
            content_text1 = content_element1.text
            output += f"1. başlık: {content_text1}\n"

            # İlk başlıkta anahtar kelimeleri kontrol et
            found_keywords = {keyword for keyword in keywords if keyword.casefold() in content_text1.casefold()}
            if found_keywords:
                output += f"Anahtar kelime bulundu: {', '.join(found_keywords)} - Resim indiriliyor...\n"
                download_image(driver, index)
            else:
                output += "Anahtar kelime 1. başlıkta bulunamadı, 2. başlıkta aranıyor...\n"

                # 2. başlıkta anahtar kelimeleri arama
                try:
                    content_element2 = driver.find_element(By.XPATH,
                                                           '//*[@id="content"]/app-detailedresult/div[1]/div/div[1]/div[4]/span')
                    content_text2 = content_element2.text
                    output += f"2. başlık: {content_text2}\n"

                    found_keywords = {keyword for keyword in keywords if keyword.casefold() in content_text2.casefold()}
                    if found_keywords:
                        output += f"Anahtar kelime bulundu: {', '.join(found_keywords)} - Resim indiriliyor...\n"
                        download_image(driver, index)
                    elif "acne" not in content_text1.casefold() and "acne" not in content_text2.casefold():
                        output += "2. başlıkta da anahtar kelime bulunamadı. 'acne' anahtar kelimesi de yok. Resim eleniyor...\n"
                        download_image(driver, index)
                    else:
                        output += "'acne' anahtar kelimesi mevcut, resim elenmeyecek.\n"
                except NoSuchElementException:
                    output += "2. başlık bulunamadı. 2. başlıkta da anahtar kelime bulunamadı.\n"
        except NoSuchElementException:
            output += "1. başlık bulunamadı.\n"

    except (TimeoutException, NoSuchElementException) as e:
        output += f"İçerik veya resim bulunamadı: {e}\n"
    finally:
        driver.quit()

    print(output)

# Resim indirme fonksiyonu
def download_image(driver, index):
    try:
        img_url = driver.find_element(By.XPATH,
                                      '//*[@id="content"]/app-detailedresult/div[1]/div/div[1]/div[3]/div[1]/div/img').get_attribute(
            "src")
        img_data = requests.get(img_url).content
        image = Image.open(BytesIO(img_data))
        resized_image = image.resize((320, 240))
        img_name = f"acne_openi_elenecekler/{index}.jpg"
        resized_image.save(img_name)
        print(f"Resim {img_name} olarak kaydedildi.")
    except Exception as e:
        print(f"Resim indirilirken hata oluştu: {e}")

# Detay URL dosyasını açma ve çoklu iş parçacığında URL'leri işleme
with open("detail_url_openi_acne.txt", "r") as url_file:
    urls = url_file.readlines()

# Çoklu iş parçacığı ile URL'leri eş zamanlı olarak işleme
with ThreadPoolExecutor(max_workers=3) as executor:
    for index, url in enumerate(urls, start=1):
        executor.submit(process_url, index, url)
