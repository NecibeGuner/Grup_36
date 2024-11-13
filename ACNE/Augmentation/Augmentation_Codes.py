from PIL import Image, ImageFilter, ImageEnhance
import os

# İşlem yapılacak klasörler
augmentation_folder_Atlas = r'C:\Users\Necibe\PycharmProjects\Grup_36\ACNE\ElenmisArtirilmisGorseller\AtlasAcne'
augmentation_folder_Dermis = r'C:\Users\Necibe\PycharmProjects\Grup_36\ACNE\ElenmisArtirilmisGorseller\DermisAcne'
transform_folder_IStock = r'C:\Users\Necibe\PycharmProjects\Grup_36\ACNE\ElenmisArtirilmisGorseller\final_istock_acne'
transform_folder_DermNetZ = r'C:\Users\Necibe\PycharmProjects\Grup_36\ACNE\ElenmisArtirilmisGorseller\DermNetZAcne'

output_size = (320, 240)

# İşlem uygulanmış kopyaları kaydedecek genel bir fonksiyon
def save_image(img, folder, filename, operation_name):
    name, ext = os.path.splitext(filename)
    new_filename = f"{name}_{operation_name}.jpg"
    new_img_path = os.path.join(folder, new_filename)
    img = img.resize(output_size)
    img.save(new_img_path)
    print(f"{new_filename} dosyası kaydedildi.")

# Veri artırma işlemi
def apply_augmentations(image_folder):
    for filename in os.listdir(image_folder):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            img_path = os.path.join(image_folder, filename)
            img = Image.open(img_path)

            # Grayscale
            grayscale_img = img.convert('L').convert('RGB')
            save_image(grayscale_img, image_folder, filename, "grayscale")

            # Saturation
            saturation_enhancer = ImageEnhance.Color(img)
            saturation_img = saturation_enhancer.enhance(1.5)  # Örnek doygunluk değeri
            save_image(saturation_img, image_folder, filename, "saturation")

            # Brightness
            brightness_enhancer = ImageEnhance.Brightness(img)
            brightness_img = brightness_enhancer.enhance(1.5)  # Örnek parlaklık değeri
            save_image(brightness_img, image_folder, filename, "brightness")

# Dönüşüm işlemleri
def apply_transformations(image_folder):
    for filename in os.listdir(image_folder):
        if filename.endswith(('.jpg', '.jpeg', '.png')):
            img_path = os.path.join(image_folder, filename)
            img = Image.open(img_path)

            # Yansıma işlemi (horizontal flip)
            mirrored_img = img.transpose(method=Image.FLIP_LEFT_RIGHT)
            save_image(mirrored_img, image_folder, filename, "mirror")

            # 90 derece döndürme
            rotated_90 = img.rotate(90, expand=True)
            save_image(rotated_90, image_folder, filename, "rotate_90")

            # 180 derece döndürme
            rotated_180 = img.rotate(180, expand=True)
            save_image(rotated_180, image_folder, filename, "rotate_180")

            # 270 derece döndürme
            rotated_270 = img.rotate(270, expand=True)
            save_image(rotated_270, image_folder, filename, "rotate_270")

            # %50 yakınlaştırma (Zoom)
            zoom_factor = 1.5  # %50 daha büyük olacak şekilde ayarladık
            w, h = img.size
            new_w, new_h = int(w * zoom_factor), int(h * zoom_factor)
            resized_img = img.resize((new_w, new_h), Image.LANCZOS)
            left = (new_w - w) // 2
            top = (new_h - h) // 2
            right = left + w
            bottom = top + h
            zoomed_img = resized_img.crop((left, top, right, bottom))
            save_image(zoomed_img, image_folder, filename, "zoom")

# İşlemleri çalıştır
apply_augmentations(augmentation_folder_Atlas)
apply_augmentations(augmentation_folder_Dermis)
apply_transformations(transform_folder_IStock)
apply_transformations(transform_folder_DermNetZ)
print("Tüm işlemler başarıyla tamamlandı.")
