import os
import shutil

# Klasör yolları
# Tüm görsellerin bulunduğu klasör
all_images_folder = "C:/Users/Tugce/PycharmProjects/selenium_temelleri/.venv/vitiligo/vitiligomain2"
# Gereksiz görsellerin bulunduğu klasör
exclude_images_folder = "C:/Users/Tugce/PycharmProjects/selenium_temelleri/.venv/vitiligo/vitiligo_openi_elenecekler"
# Sonuç klasörü - gereksiz olmayan görsellerin kaydedileceği klasör
final_images_folder = "C:/Users/Tugce/PycharmProjects/selenium_temelleri/.venv/vitiligo/final_openi_vitiligo"

# Sonuç klasörü yoksa oluştur
if not os.path.exists(final_images_folder):
    os.makedirs(final_images_folder)

# Gereksiz dosyaların isimlerini bir set olarak al
# Bu dosyalar final klasörüne kopyalanmayacak
exclude_images = set(os.listdir(exclude_images_folder))

# Kopyalanan dosyaların sayacını başlat (sırayla isimlendirme için)
file_counter = 1

# Tüm görseller klasöründeki dosyaları kontrol et
for image_file in os.listdir(all_images_folder):
    # Eğer dosya gereksizler arasında değilse final klasörüne kopyala
    if image_file not in exclude_images:
        source_path = os.path.join(all_images_folder, image_file)  # Orijinal dosya yolu

        # Dosya adını sıraya göre adlandır (örneğin, 1.jpg, 2.jpg, ...)
        new_file_name = f"{file_counter}.jpg"
        destination_path = os.path.join(final_images_folder, new_file_name)  # Hedef dosya yolu

        # Dosyayı kopyala ve sayacı artır
        shutil.copy2(source_path, destination_path)  # Dosyayı final klasörüne kopyalar
        print(f"Kopyalandı: {new_file_name}")  # Kopyalanan dosyanın adını yazdır
        file_counter += 1  # Sayacı artırarak sıradaki dosya adını ayarla

print("Gereksiz görseller çıkarıldı ve kalan görseller final klasörüne sırayla kopyalandı.")
