import os
import shutil

# Klasör adları
input_folder = "DermNetZNevus"  # Resimlerin kaydedildiği ana klasör
output_folder = "DermNetZ_Nevus_elenecekler"  # "Acne" geçmeyen açıklamalara sahip resimlerin kaydedileceği klasör

# Hedef klasörü oluştur
os.makedirs(output_folder, exist_ok=True)
#Melanomia
# Açıklamaların bulunduğu dosya yolu
info_file_path = os.path.join(input_folder, "dermnet_melonoma.txt")

# Açıklamaları oku ve filtrele
try:
    with open(info_file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
except FileNotFoundError:
    print(f"{info_file_path} dosyası bulunamadı.")
    exit()

# Açıklamaları resim numarası ile eşleştir
for line in lines:
    line = line.strip()

    # Her satırın "resim açıklaması:" ifadesiyle başladığını kontrol et
    if "resim açıklaması:" in line:
        # Resim numarasını çıkar ve açıklama metnini ayır
        parts = line.split(":", 1)
        image_number = parts[0].split(".")[0].strip()  # "590" gibi
        description = parts[1].strip()  # Açıklama metni

        # "acne" veya "Acne" kelimesi geçmiyorsa, resmi başka klasöre kopyala
        if "melanoma" not in description.lower() and "melanomia" not in description.lower():  # Küçük/büyük harf duyarlılığını kaldırarak kontrol et
            input_image_path = os.path.join(input_folder, f"{image_number}.jpg")
            output_image_path = os.path.join(output_folder, f"{image_number}.jpg")

            # Resmi hedef klasöre kopyala
            if os.path.exists(input_image_path):
                shutil.copy(input_image_path, output_image_path)
                print(
                    f"{image_number}.jpg 'melanoma' veya 'melanomia' içermiyor ve {output_folder} klasörüne kopyalandı. Açıklama: {description}")
            else:
                print(f"{image_number}.jpg dosyası bulunamadı.")
        else:
            print(f"Beklenmeyen formatta satır atlandı: {line}")
