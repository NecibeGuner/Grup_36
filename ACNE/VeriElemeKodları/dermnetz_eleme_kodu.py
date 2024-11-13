import os
import shutil

# Klasör adları
input_folder = "acnemain1"  # Resimlerin kaydedildiği ana klasör
output_folder = "acnemain1_elenecekresimler"  # Filtreye uymayan açıklamalara sahip resimlerin kaydedileceği klasör

# Hedef klasörü oluştur
os.makedirs(output_folder, exist_ok=True)

# Açıklamaların bulunduğu dosya yolu
info_file_path = os.path.join(input_folder, "dermnet_acne.txt")

# Açıklamaları oku ve filtrele
try:
    with open(info_file_path, "r", encoding="utf-8") as file:
        lines = file.readlines()
except FileNotFoundError:
    print(f"{info_file_path} dosyası bulunamadı.")
    exit()

# Filtreleme kelimeleri
keywords = ["acne", "comedones", "cyst"]

# Açıklamaları resim numarası ile eşleştir
for line in lines:
    line = line.strip()

    # Her satırın "resim açıklaması:" ifadesiyle başladığını kontrol et
    if "resim açıklaması:" in line:
        # Resim numarasını çıkar ve açıklama metnini ayır
        parts = line.split(":", 1)
        image_number = parts[0].split(".")[0].strip()  # "590" gibi
        description = parts[1].strip()  # Açıklama metni

        # "acne", "COMEDONES" veya "Cyst" kelimelerinden hiçbiri geçmiyorsa, resmi başka klasöre kopyala
        if not any(keyword in description.lower() for keyword in keywords):
            input_image_path = os.path.join(input_folder, f"{image_number}.jpg")
            output_image_path = os.path.join(output_folder, f"{image_number}.jpg")

            # Resmi hedef klasöre kopyala
            if os.path.exists(input_image_path):
                shutil.copy(input_image_path, output_image_path)
                print(
                    f"{image_number}.jpg belirtilen kelimeleri içermiyor ve {output_folder} klasörüne kopyalandı. Açıklama: {description}")
            else:
                print(f"{image_number}.jpg dosyası bulunamadı.")
    else:
        print(f"Beklenmeyen formatta satır atlandı: {line}")
