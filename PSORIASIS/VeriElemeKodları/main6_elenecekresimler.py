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

# Klasör oluşturma
os.makedirs("main6_elenecekler", exist_ok=True)

# Anahtar kelimeler listesi
keywords = [
    "%", "(%)", "üç boyutlu", "histopatolojik", "şiddet indeksi", "fareler", "fare", "fareleri",
    "radyografik", "görüntüleme", "sitometre", "sitometresi", "biyopsi", "biyopsisi",
    "histolojik", "bitki", "bitkiler", "hayvan", "hayvanlar", "tomogrofi", "karşılaştırma",
    "grafik", "çalışma", "çalışması", "mri", "hedefleri", "sunumu", "hipergranülozis",
    "histoloji", "fotomikrografi", "turba", "vakuolizasyon", "infiltrat", "röntgen", "kitle",
    "3d", "histopathological", "severity index", "mice", "mouse", "rays", "radiographic", "imaging",
    "cytometer", "cytometry", "biopsy", "histological", "plant", "plants", "animal", "animals",
    "tomography", "comparison", "graph", "study", "research", "presentation", "hypergranulosis",
    "histology", "photomicrograph", "peat", "vacuolization", "infiltrate", "x-ray", "mass", "target", "MRI",
    "istatistik", "istatistiği", "istatistiksel", "statistics", "statistical",
    "olasılık", "olasılık dağılımı", "probability", "probability distribution", "distribution",
    "dağılım", "dağılımı", "distribution", "distributions",
    "hücresel", "cellular", "cell-based", "before and after", "önce ve sonra", "öncesi ve sonrası",
    "ekspresyon", "ekspresyonu", "ekspresyonlar", "expression", "expressions",
    "varyasyon", "varyasyonu", "varyasyonlar", "variation", "variations",
    "fotomikrograf", "fotomikrografi", "mikrograf", "micrograph", "photomicrograph",
    "yaygınlık", "incidence", "prevalence", "biyomedikal", "biomedical", "histopatoloji", "histopathology",
    "konsantrasyon", "concentration", "analiz", "analizi", "analysis", "analyses", "mikroskobik", "microscopic",
    "microscopy", "epidemioloji", "epidemiology", "epidemiolojik", "epidemiological", "görsel analiz",
    "visual analysis", "quantitative", "optik", "optics", "spektrometre", "spectrometry", "spektrum", "spectrum",
    "örnekleme", "sample", "sampling", "örnekler", "samples", "patolojik", "pathological", "patoloji", "pathology",
    "moleküler", "molecular", "molecule", "molecules", "biyokimya", "biochemistry", "biyokimyasal",
    "biochemical", "difüzyon", "diffusion", "solution", "çözeltisi", "solüsyon", "mutasyon", "mutation",
    "genetik", "genetic", "genetics","models","model"
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
                output += f"Anahtar kelime bulundu: {', '.join(found_keywords)}\nResim indiriliyor...\n"
                img_url = driver.find_element(By.XPATH,
                                              '//*[@id="content"]/app-detailedresult/div[1]/div/div[1]/div[3]/div[1]/div/img').get_attribute(
                    "src")
                img_data = requests.get(img_url).content
                image = Image.open(BytesIO(img_data))
                resized_image = image.resize((320, 240))
                img_name = f"main6_elenecekler/{index}.jpg"
                resized_image.save(img_name)
                output += f"Resim {img_name} olarak kaydedildi.\n"
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
                        output += f"Anahtar kelime bulundu: {', '.join(found_keywords)}\nResim indiriliyor...\n"
                        img_url = driver.find_element(By.XPATH,
                                                      '//*[@id="content"]/app-detailedresult/div[1]/div/div[1]/div[3]/div[1]/div/img').get_attribute(
                            "src")
                        img_data = requests.get(img_url).content
                        image = Image.open(BytesIO(img_data))
                        resized_image = image.resize((320, 240))
                        img_name = f"main6_elenecekler/{index}.jpg"
                        resized_image.save(img_name)
                        output += f"Resim {img_name} olarak kaydedildi.\n"
                    else:
                        output += "Anahtar kelime bulunamadı.\n"
                except NoSuchElementException:
                    output += "2. başlık bulunamadı.\n"
        except NoSuchElementException:
            output += "1. başlık bulunamadı.\n"

    except (TimeoutException, NoSuchElementException) as e:
        output += f"İçerik veya resim bulunamadı: {e}\n"
    finally:
        driver.quit()

    print(output)


# Detay URL dosyasını açma ve çoklu iş parçacığında URL'leri işleme
with open("detail_url_openi_psoriasis.txt", "r") as url_file:
    urls = url_file.readlines()

# Çoklu iş parçacığı ile URL'leri eş zamanlı olarak işleme
with ThreadPoolExecutor(max_workers=3) as executor:
    for index, url in enumerate(urls, start=1):
        executor.submit(process_url, index, url)
