from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import requests
import os
import time
from PIL import Image
from io import BytesIO

# Chrome tarayıcı ayarları
options = webdriver.ChromeOptions()
options.add_argument('--start-maximized')
options.add_experimental_option('detach', True)
driver = webdriver.Chrome(options=options)

# Sayfayı aç
driver.get("https://dermnetnz.org/images")

# Sayfanın yüklenmesini bekleyin ve "AGREE" butonuna tıklayın
try:
    agree_button = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.CLASS_NAME, "css-usek55"))
    )
    agree_button.click()  # AGREE butonuna tıkla
    print("AGREE butonuna tıklandı.")

    # AGREE butonundan sonra sayfanın yüklenmesini bekleyin
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, "//*[@id='search_images']"))
    )
except Exception as e:
    print(f"AGREE butonuna tıklanamadı: {e}")
    driver.quit()  # Hata durumunda tarayıcıyı kapat

# 'chickenpox' yaz ve Enter tuşuna bas
try:
    search_input = WebDriverWait(driver, 10).until(
        EC.element_to_be_clickable((By.XPATH, "//*[@id='search_images']"))
    )
    search_input.send_keys('chickenpox')
    search_input.send_keys(Keys.RETURN)
    print("chickenpox arandı.")
except Exception as e:
    print(f"Hata: {e}")
    driver.quit()  # Hata durumunda tarayıcıyı kapat

# Sayfanın sonuçları yüklemesini bekleyin
try:
    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.CLASS_NAME, "gallery__slides__item__image"))
    )
except Exception as e:
    print(f"Resimlerin yüklenmesi beklenirken hata oluştu: {e}")
    driver.quit()  # Hata durumunda tarayıcıyı kapat

# Resimleri indirmek için klasör oluştur
output_folder = 'mains1'
if not os.path.exists(output_folder):
    os.makedirs(output_folder)

# Mevcut dosya sayısını kontrol et
existing_images = len([name for name in os.listdir(output_folder) if os.path.isfile(os.path.join(output_folder, name))])
image_count = existing_images  # Mevcut dosya sayısını başlangıç sayısı olarak kullan

# Sayfa sayfalarını döngüye al
page_number = 1  # Sayfa numarasını başlat

while page_number <=2:  # 31. sayfaya kadar döngü
    print(f"Page {page_number} ***")  # Sayfa numarasını yazdır

    try:
        # Sayfayı kaydırarak tüm resimlerin yüklenmesini sağla
        last_height = driver.execute_script("return document.body.scrollHeight")
        while True:
            # Sayfayı en aşağı kaydır
            driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
            time.sleep(2)  # Sayfanın yüklenmesi için bekleyin

            # Sayfa yüklenme durumunu kontrol et
            new_height = driver.execute_script("return document.body.scrollHeight")
            if new_height == last_height:
                break
            last_height = new_height

        # Tüm img elemanlarını bulmak için tekrar WebDriverWait kullan
        images = WebDriverWait(driver, 10).until(
            EC.presence_of_all_elements_located((By.CLASS_NAME, "gallery__slides__item__image"))
        )

        # Resimleri indirin
        for i, image in enumerate(images):
            try:
                img_element = image.find_element(By.TAG_NAME, "img")  # img tag'ini al
                img_url = img_element.get_attribute('src')  # Resmin URL'sini al
                response = requests.get(img_url)
                response.raise_for_status()  # İndirme hatası varsa bir hata fırlat

                # Dosya uzantısını belirle
                content_type = response.headers['Content-Type']
                extension = content_type.split('/')[-1]  # Uzantıyı al

                # Dosya yolunu belirle
                image_count += 1  # Her bir resim için sayıyı artır
                file_path = f'{output_folder}/{image_count}.{extension}'  # Dosya uzantısını ekle

                # Resmi yeniden boyutlandır ve kaydet
                with Image.open(BytesIO(response.content)) as img:
                    img = img.resize((320, 240))  # Boyutu 320x240 yap
                    img.save(file_path)  # Yeniden boyutlandırılmış resmi kaydet
                    print(f"{file_path} indirildi.")  # Başarılı indirme mesajı

            except Exception as img_error:
                print(f"Resim indirirken hata: {img_error}")

        # Sonraki sayfaya git
        if page_number < 2:  # 2. sayfadan önce geç
            try:
                # Sonraki sayfa butonunu bulmadan önce sayfanın tam yüklenmesini bekleyin
                time.sleep(2)  # Tüm resimlerin işlenmesi için 2 saniye bekle

                # "Sonraki Sayfa" butonunu bul ve tıkla
                next_button = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CLASS_NAME, "images__wrap__grid__pagination__last"))
                )
                next_button.click()
                print("Sonraki sayfaya geçildi.")

                # Yeni sayfanın yüklenmesini bekleyin
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CLASS_NAME, "gallery__slides__item__image"))
                )
                time.sleep(2)  # 2 saniye bekleyin

                # Sayfa numarasını artır
                page_number += 1

            except Exception as e:
                print("Sonraki sayfa bulunamadı veya geçilemedi.")
                break  # Sonraki sayfa yoksa döngüden çık
        else:
            print("2. sayfaya ulaşıldı, indirme işlemi sonlandırılıyor.")
            break  # 31. sayfaya ulaşıldığında döngüden çık

    except Exception as e:
        print(f"Bir hata oluştu: {e}")
        break  # Hata oluşursa döngüden çık

# Tarayıcıyı kapat
driver.quit()