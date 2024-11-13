import os
import requests
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
from PIL import Image
from io import BytesIO
from selenium.common.exceptions import StaleElementReferenceException, TimeoutException

# Chrome tarayıcı ayarları
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_experimental_option('detach', True)
driver = webdriver.Chrome(options=options)

# Sayfayı aç
driver.get("https://dermnetnz.org/images")

# "AGREE" butonuna tıklayın
try:
    for attempt in range(3):  # AGREE butonuna üç kez deneme yapılacak
        try:
            agree_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "css-usek55"))
            )
            agree_button.click()
            print("AGREE butonuna tıklandı.")
            break  # Tıklama başarılıysa döngüden çık
        except StaleElementReferenceException:
            print("AGREE butonu referansı geçersiz, yeniden deneniyor...")
            time.sleep(1)
except Exception as e:
    print(f"AGREE butonuna tıklanamadı: {e}")
    driver.quit()

# 'melanoma' kelimesini arama çubuğuna yaz ve Enter tuşuna bas
try:
    search_input = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='search_images']"))
    )
    search_input.send_keys('melanoma')
    search_input.send_keys(Keys.RETURN)
    print("'melanoma' arandı.")
except Exception as e:
    print(f"Hata: {e}")
    driver.quit()

# Resimleri ve açıklamaları indirmek için klasör oluştur
output_folder = 'DermNetZNevus'
os.makedirs(output_folder, exist_ok=True)
info_file_path = os.path.join(output_folder, "dermnet_melanoma.txt")

# Mevcut dosya sayısını kontrol et
existing_images = len([name for name in os.listdir(output_folder) if os.path.isfile(os.path.join(output_folder, name))])
image_count = existing_images

# Bilgi dosyasını aç (UTF-8 formatında yazma)
with open(info_file_path, "a", encoding="utf-8") as info_file:
    page_number = 1
    while page_number <= 21:
        print(f"Sayfa {page_number} ***")

        # Sayfanın sonuna kadar kaydırarak tüm resimlerin yüklenmesini sağla
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # İçeriğin yüklenmesi için bekle
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # Yükleme tamamlandı
            last_height = new_height

        try:
            # Resimlerin tamamının yüklenip yüklenmediğini kontrol et
            images = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "gallery__slides__item__image"))
            )
        except TimeoutException as e:
            print(f"Resimler bulunamadı: {e}")
            break

        # Resimleri indir
        for i in range(len(images)):
            for attempt in range(3):  # Her resmi üç kez deneyecek
                try:
                    # Resmi tekrar bulmak için her seferinde yenile
                    images = driver.find_elements(By.CLASS_NAME, "gallery__slides__item__image")
                    img_element = images[i].find_element(By.TAG_NAME, "img")
                    img_url = img_element.get_attribute('src')
                    response = requests.get(img_url)
                    response.raise_for_status()

                    # Resmi kaydet
                    image_count += 1
                    extension = img_url.split('.')[-1]
                    file_path = f'{output_folder}/{image_count}.{extension}'

                    with Image.open(BytesIO(response.content)) as img:
                        img = img.resize((320, 240))
                        img.save(file_path)
                        print(f"{image_count}. resim indiriliyor")

                    # Açıklama metnini tekrar al
                    description_text = "Açıklama bulunamadı"
                    for _ in range(3):  # Açıklama için üç deneme yapılacak
                        try:
                            images = driver.find_elements(By.CLASS_NAME, "gallery__slides__item__image")
                            description_element = images[i].find_element(By.XPATH, "following-sibling::div/p")
                            description_text = description_element.text
                            break
                        except StaleElementReferenceException:
                            print("Açıklama alınamadı, tekrar deneniyor...")
                            time.sleep(1)

                    # Açıklamayı kaydet
                    info_file.write(f"{image_count}. resim açıklaması: {description_text}\n")
                    print(f"Açıklama: {description_text}")
                    print(f"{image_count}.jpg olarak kaydedildi.")
                    break  # Başarılıysa döngüden çık
                except (StaleElementReferenceException, TimeoutException, requests.exceptions.HTTPError) as img_error:
                    print(f"Resim indirirken hata, tekrar deneniyor: {img_error}")
                    time.sleep(2)
                    if attempt == 2:
                        print(f"{image_count}. resim kaydedilemedi ve atlandı.")
                    continue

        # Sayfadaki tüm resimler indirildikten sonra sonraki sayfaya geç
        if page_number < 21:
            try:
                time.sleep(2)
                next_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "images__wrap__grid__pagination__last"))
                )
                next_button.click()
                print("Sonraki sayfaya geçildi.")
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "gallery__slides__item__image"))
                )
                page_number += 1
            except Exception as e:
                print("Sonraki sayfa bulunamadı veya geçilemedi.")
                break
        else:
            print("21. sayfaya ulaşıldı, indirme işlemi sonlandırılıyor.")
            break

# Tarayıcıyı kapat
driver.quit()
