import os
import shutil

# Klasör yolları
all_images_folder = "C:/Users/Tugce/PycharmProjects/selenium_temelleri/.venv/Nevus/IstockNevus"  # Tüm görsellerin bulunduğu klasör
exclude_images_folder = "C:/Users/Tugce/PycharmProjects/selenium_temelleri/.venv/Nevus/elenecekresimler_istock"  # Gereksiz görsellerin bulunduğu klasör
final_images_folder = "C:/Users/Tugce/PycharmProjects/selenium_temelleri/.venv/Nevus/final_istock"  # Sonuç klasörü

# Sonuç klasörü yoksa oluştur
if not os.path.exists(final_images_folder):
    os.makedirs(final_images_folder)

# Gereksiz dosyaların isimlerini bir set olarak al
exclude_images = set(os.listdir(exclude_images_folder))

# Kopyalanan dosyaların sayacını başlat
file_counter = 1

# Tüm görseller klasöründeki dosyaları kontrol et
for image_file in os.listdir(all_images_folder):
    # Dosya gereksizler arasında değilse final klasörüne kopyala
    if image_file not in exclude_images:
        source_path = os.path.join(all_images_folder, image_file)

        # Dosya adını sıraya göre adlandır
        new_file_name = f"{file_counter}.jpg"
        destination_path = os.path.join(final_images_folder, new_file_name)

        # Dosyayı kopyala ve sayacı artır
        shutil.copy2(source_path, destination_path)
        print(f"Kopyalandı: {new_file_name}")
        file_counter += 1

print("Gereksiz görseller çıkarıldı ve kalan görseller final klasörüne sırayla kopyalandı.")
