import os  # Dosya ve dizin işlemleri yapmak için kullanılır
import requests  # HTTP istekleri yaparak internetten veri çekmek için kullanılır (örneğin, resim indirme)
from selenium import webdriver  # Web tarayıcısını otomatik olarak açmak ve kontrol etmek için kullanılır
from selenium.webdriver.common.by import By  # Selenium'un sayfadaki öğeleri bulmasına yardımcı olan bir modül
from selenium.webdriver.common.keys import Keys  # Klavye işlemleri (örneğin, Enter tuşuna basmak) için kullanılır
from selenium.webdriver.support.ui import WebDriverWait  # Belirli bir süre boyunca öğenin yüklenmesini beklemek için kullanılır
from selenium.webdriver.support import expected_conditions as EC  # Koşullu beklemeleri tanımlamak için kullanılır
import time  # Kodun belirli süre duraklamasını sağlamak için kullanılır (örneğin, sayfanın yüklenmesi için bekleme)
from PIL import Image  # Görüntüleri işlemek için kullanılan bir modül (örneğin, yeniden boyutlandırma)
from io import BytesIO  # Bellekteki byte verilerini dosya benzeri bir nesne olarak kullanmak için kullanılır
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException  # Selenium hata işlemleri için kullanılır

# Chrome tarayıcı ayarları
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')  # Tarayıcıyı tam ekran başlatır
options.add_experimental_option('detach', True)  # Tarayıcı işlemi kapatıldığında açık kalır
driver = webdriver.Chrome(options=options)  # Chrome WebDriver'ı başlatır

# Sayfayı aç
driver.get("https://dermnetnz.org/images")  # DermNetNZ resim sayfasını açar

# "AGREE" butonuna tıklayın
try:
    agree_button = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "css-usek55"))
    )
    agree_button.click()  # Gizlilik onayı için "AGREE" butonuna tıklar
    print("AGREE butonuna tıklandı.")
except Exception as e:
    print(f"AGREE butonuna tıklanamadı: {e}")
    driver.quit()  # Hata varsa tarayıcıyı kapatır

# 'acne' yaz ve Enter tuşuna bas
try:
    search_input = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='search_images']"))
    )
    search_input.send_keys('acne')  # "acne" anahtar kelimesini arama kutusuna yazar
    search_input.send_keys(Keys.RETURN)  # Enter tuşuna basarak arama yapar
    print("'acne' arandı.")
except Exception as e:
    print(f"Hata: {e}")
    driver.quit()  # Hata varsa tarayıcıyı kapatır

# Resimleri ve açıklamaları indirmek için klasör oluştur
output_folder = 'DermNetzAcne'
os.makedirs(output_folder, exist_ok=True)  # Klasör yoksa oluşturur
info_file_path = os.path.join(output_folder, "dermnet_acne.txt")  # Açıklamaların kaydedileceği dosya yolu

# Mevcut dosya sayısını kontrol et
existing_images = len([name for name in os.listdir(output_folder) if os.path.isfile(os.path.join(output_folder, name))])
image_count = existing_images  # İndirilecek yeni resimler için sayaç başlatılır

# Bilgi dosyasını aç (UTF-8 formatında yazma)
with open(info_file_path, "a", encoding="utf-8") as info_file:
    page_number = 1
    while page_number <= 16:
        print(f"Page {page_number} ***")  # Hangi sayfada olduğunu gösterir

        # Sayfadaki tüm resimlerin yüklenmesini bekle
        try:
            images = WebDriverWait(driver, 15).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "gallery__slides__item__image"))
            )
        except TimeoutException as e:
            print(f"Resimler bulunamadı: {e}")
            break  # Hata durumunda döngüden çıkar

        # Her resim için döngü
        for i in range(len(images)):
            for attempt in range(3):  # Her resmi üç kez deneyecek
                try:
                    # Resmi tekrar bulmak için her seferinde yenile
                    images = driver.find_elements(By.CLASS_NAME, "gallery__slides__item__image")
                    img_element = images[i].find_element(By.TAG_NAME, "img")  # Resim elemanını alır
                    img_url = img_element.get_attribute('src')  # Resim URL'sini alır
                    response = requests.get(img_url)  # Resim verisini indirir
                    response.raise_for_status()

                    # Resmi kaydet
                    image_count += 1
                    extension = img_url.split('.')[-1]  # Resim dosya uzantısını alır
                    file_path = f'{output_folder}/{image_count}.{extension}'  # Resim dosya adını oluşturur

                    # Resmi aç, yeniden boyutlandır ve kaydet
                    with Image.open(BytesIO(response.content)) as img:
                        img = img.resize((320, 240))  # 320x240 boyutuna ayarlar
                        img.save(file_path)
                        print(f"{image_count}. resim indiriliyor")

                    # Açıklama metnini tekrar al
                    description_text = "Açıklama bulunamadı"  # Varsayılan açıklama
                    for _ in range(3):  # Açıklama için üç deneme
                        try:
                            images = driver.find_elements(By.CLASS_NAME, "gallery__slides__item__image")
                            description_element = images[i].find_element(By.XPATH, "following-sibling::div/p")  # Açıklama metnini bulur
                            description_text = description_element.text  # Açıklama metnini alır
                            break
                        except StaleElementReferenceException:
                            print("Açıklama alınamadı, tekrar deneniyor...")
                            time.sleep(1)

                    # Açıklamayı kaydet
                    info_file.write(f"{image_count}. resim açıklaması: {description_text}\n")
                    print(f"p etiketinde yazan metin: {description_text}")
                    print(f"{image_count}.jpg olarak kaydedildi.")
                    break  # Başarılıysa döngüden çık
                except (StaleElementReferenceException, TimeoutException, requests.exceptions.HTTPError) as img_error:
                    print(f"Resim indirirken hata, tekrar deneniyor: {img_error}")
                    time.sleep(2)
                    if attempt == 2:
                        print(f"{image_count}. resim kaydedilemedi ve atlandı.")
                    continue

        # Sonraki sayfaya geç
        if page_number < 16:
            try:
                time.sleep(2)  # Geçişten önce kısa bir bekleme
                next_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "images__wrap__grid__pagination__last"))
                )
                next_button.click()  # Sonraki sayfaya geçiş yapar
                print("Sonraki sayfaya geçildi.")
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "gallery__slides__item__image"))
                )
                page_number += 1
            except Exception as e:
                print("Sonraki sayfa bulunamadı veya geçilemedi.")
                break
        else:
            print("16. sayfaya ulaşıldı, indirme işlemi sonlandırılıyor.")
            break

# Tarayıcıyı kapat
driver.quit()  # İşlem tamamlandıktan sonra tarayıcıyı kapatır
