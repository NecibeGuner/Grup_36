import os  # Dosya ve dizin işlemleri yapmak için kullanılan modül
import shutil  # Dosya ve dizin kopyalama işlemleri için kullanılan modül

# Klasör yolları
all_images_folder = "C:/Users/Tugce/PycharmProjects/selenium_temelleri/.venv/vitiligo/istockVitiligo"  # Tüm görsellerin bulunduğu klasör
exclude_images_folder = "C:/Users/Tugce/PycharmProjects/selenium_temelleri/.venv/vitiligo/istock_elenecekler_vitiligo"  # Gereksiz görsellerin bulunduğu klasör
final_images_folder = "C:/Users/Tugce/PycharmProjects/selenium_temelleri/.venv/vitiligo/final_istock_vitiligo"  # Filtrelenmiş görsellerin kopyalanacağı sonuç klasörü

# Sonuç klasörü yoksa oluştur
if not os.path.exists(final_images_folder):
    os.makedirs(final_images_folder)  # Klasör yoksa oluşturulur

# Gereksiz dosyaların isimlerini bir set olarak al
exclude_images = set(os.listdir(exclude_images_folder))  # Gereksiz görsellerin isimlerini içeren set

# Kopyalanan dosyaların sayacını başlat (sırayla numaralandırmak için)
file_counter = 1

# Tüm görseller klasöründeki dosyaları kontrol et
for image_file in os.listdir(all_images_folder):
    # Eğer dosya gereksizler setinde değilse final klasörüne kopyala
    if image_file not in exclude_images:
        source_path = os.path.join(all_images_folder, image_file)  # Orijinal dosya yolu

        # Dosya adını sıraya göre adlandır (örneğin, 1.jpg, 2.jpg, ...)
        new_file_name = f"{file_counter}.jpg"
        destination_path = os.path.join(final_images_folder, new_file_name)  # Hedef dosya yolu

        # Dosyayı kopyala ve sayacı artır
        shutil.copy2(source_path, destination_path)  # Dosyayı final klasörüne kopyalar
        print(f"Kopyalandı: {new_file_name}")  # Kopyalanan dosyanın adı yazdırılır
        file_counter += 1  # Sayacı artırarak sıradaki dosya numarasını hazırlar

# İşlem tamamlandığında bilgilendirici mesaj yazdır
print("Gereksiz görseller çıkarıldı ve kalan görseller final klasörüne sırayla kopyalandı.")
