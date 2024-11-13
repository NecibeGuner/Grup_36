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
options.add_argument('--start-maximized')  # Tarayıcıyı tam ekran başlat
options.add_experimental_option('detach', True)  # Tarayıcı işlemi kod çalışmayı durdurduğunda kapanmaz
driver = webdriver.Chrome(options=options)

# Web sitesini aç
driver.get("https://dermnetnz.org/images")

# "AGREE" butonuna tıklayın
try:
    for attempt in range(3):  # AGREE butonuna üç kez deneme yapılacak
        try:
            # AGREE butonunun tıklanabilir hale gelmesini bekle
            agree_button = WebDriverWait(driver, 15).until(
                EC.element_to_be_clickable((By.CLASS_NAME, "css-usek55"))
            )
            agree_button.click()  # Butona tıkla
            print("AGREE butonuna tıklandı.")
            break  # Tıklama başarılıysa döngüden çık
        except StaleElementReferenceException:
            print("AGREE butonu referansı geçersiz, yeniden deneniyor...")
            time.sleep(1)  # 1 saniye bekle ve tekrar dene
except Exception as e:
    print(f"AGREE butonuna tıklanamadı: {e}")
    driver.quit()  # Hata durumunda tarayıcıyı kapat ve işlemi sonlandır

# Arama alanına 'vitiligo' yaz ve Enter tuşuna bas
try:
    # Arama çubuğunun tıklanabilir hale gelmesini bekle
    search_input = WebDriverWait(driver, 15).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='search_images']"))
    )
    search_input.send_keys('vitiligo')  # Arama terimini yaz
    search_input.send_keys(Keys.RETURN)  # Enter tuşuna bas
    print("'vitiligo' arandı.")
except Exception as e:
    print(f"Hata: {e}")
    driver.quit()  # Hata durumunda tarayıcıyı kapat ve işlemi sonlandır

# Resimleri ve açıklamaları indirmek için klasör oluştur
output_folder = 'vitiligomain1'
os.makedirs(output_folder, exist_ok=True)  # Klasör yoksa oluştur
info_file_path = os.path.join(output_folder, "dermnet_vitiligo.txt")
#veri eleme kolaylaştırmak için açıklamaları txt ye kaydediyoruz

# Mevcut dosya sayısını kontrol et
existing_images = len([name for name in os.listdir(output_folder) if os.path.isfile(os.path.join(output_folder, name))])
image_count = existing_images  # İndirilen resim sayısını mevcut dosya sayısına göre başlat

# Bilgi dosyasını aç (UTF-8 formatında yazma)

with open(info_file_path, "a", encoding="utf-8") as info_file:
    page_number = 1
    while page_number <= 3:  # En fazla 3 sayfa işlenecek
        print(f"Page {page_number} ***")

        # Sayfanın sonuna kadar kaydırarak tüm resimlerin yüklenmesini sağla
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")  # Sayfanın sonuna kadar kaydır
            time.sleep(2)  # İçeriğin yüklenmesi için bekle
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break  # Yükleme tamamlandıysa döngüden çık
            last_height = new_height  # Yeni yüksekliği eski yükseklik olarak kaydet

        try:
            # Resimlerin tamamının yüklenip yüklenmediğini kontrol et
            images = WebDriverWait(driver, 30).until(
                EC.presence_of_all_elements_located((By.CLASS_NAME, "gallery__slides__item__image"))
            )
        except TimeoutException as e:
            print(f"Resimler bulunamadı: {e}")
            break  # Eğer resimler yüklenmezse işlemi sonlandır

        # Resimleri indir
        for i in range(len(images)):
            for attempt in range(3):  # Her resmi üç kez deneyecek
                try:
                    # Resmi tekrar bulmak için her seferinde yenile
                    images = driver.find_elements(By.CLASS_NAME, "gallery__slides__item__image")
                    img_element = images[i].find_element(By.TAG_NAME, "img")
                    img_url = img_element.get_attribute('src')
                    response = requests.get(img_url)  # Resmi indir
                    response.raise_for_status()

                    # Resmi kaydet
                    image_count += 1
                    extension = img_url.split('.')[-1]
                    file_path = f'{output_folder}/{image_count}.{extension}'

                    # Resmi 320x240 boyutunda kaydet
                    with Image.open(BytesIO(response.content)) as img:
                        img = img.resize((320, 240))
                        img.save(file_path)
                        print(f"{image_count}. resim indiriliyor")

                    # Açıklama metnini tekrar al
                    description_text = "Açıklama bulunamadı"  # Varsayılan açıklama
                    for _ in range(3):  # Açıklama için üç deneme
                        try:
                            images = driver.find_elements(By.CLASS_NAME, "gallery__slides__item__image")
                            description_element = images[i].find_element(By.XPATH, "following-sibling::div/p")
                            description_text = description_element.text  # Açıklamayı al
                            break
                        except StaleElementReferenceException:
                            print("Açıklama alınamadı, tekrar deneniyor...")
                            time.sleep(1)  # Bekleyip tekrar dene

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
                    continue  # Hata durumunda tekrar dene

        # Sayfadaki tüm resimler indirildikten sonra sonraki sayfaya geç
        if page_number < 3:
            try:
                time.sleep(2)
                # Sonraki sayfa butonunu bul ve tıkla
                next_button = WebDriverWait(driver, 15).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "images__wrap__grid__pagination__last"))
                )
                next_button.click()  # Sonraki sayfaya geç
                print("Sonraki sayfaya geçildi.")

                # Yeni sayfanın yüklendiğinden emin olmak için bekle
                WebDriverWait(driver, 15).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "gallery__slides__item__image"))
                )
                page_number += 1  # Sayfa numarasını artır
            except Exception as e:
                print("Sonraki sayfa bulunamadı veya geçilemedi.")
                break
        else:
            print("3. sayfaya ulaşıldı, indirme işlemi sonlandırılıyor.")
            break

# Tarayıcıyı kapat
driver.quit()
