from PIL import Image, ImageFilter, ImageEnhance
import os
import random

# İşlem yapılacak klasörler
zoom_folder = r'C:\Users\Necibe\PycharmProjects\Grup_36\NEVUS\ElenmisArtirilmisGorseller\IstockNevus'
sharpen_folder = r'C:\Users\Necibe\PycharmProjects\Grup_36\NEVUS\ElenmisArtirilmisGorseller\DermisNevus'
augmentation_folder = r'C:\Users\Necibe\PycharmProjects\Grup_36\NEVUS\ElenmisArtirilmisGorseller\ben'

# Yakınlaştırma parametreleri
zoom_factor = 1.5

# Netleştirme parametreleri
radius = 1.5  # Etki alanı yarıçapı
percent = 100  # Netleştirme yüzdesi
threshold = 5  # Gürültü seviyesini kontrol eden eşik

# Veri artırma için dosya ve işlem parametreleri
start_index = 1
end_index = 1500
initial_image_count = 3250

# Yakınlaştırma işlemi
for filename in os.listdir(zoom_folder):
    if filename.endswith(('.jpg', '.jpeg', '.png')):
        img_path = os.path.join(zoom_folder, filename)
        img = Image.open(img_path)

        # Resim boyutlarını al ve yakınlaştır
        w, h = img.size
        new_w, new_h = int(w * zoom_factor), int(h * zoom_factor)
        resized_img = img.resize((new_w, new_h), Image.LANCZOS)

        # Merkezden kırp ve orijinal boyutuna getir
        left = (new_w - w) // 2
        top = (new_h - h) // 2
        right = left + w
        bottom = top + h
        zoomed_img = resized_img.crop((left, top, right, bottom))

        # Yeni dosya adıyla kaydet
        name, ext = os.path.splitext(filename)
        zoomed_img_name = f"{name}_zoom{ext}"
        zoomed_img_path = os.path.join(zoom_folder, zoomed_img_name)
        zoomed_img.save(zoomed_img_path)

print("Yakınlaştırma işlemi tamamlandı ve resimler kaydedildi.")

# Netleştirme işlemi
for filename in os.listdir(sharpen_folder):
    if filename.endswith(('.jpg', '.jpeg', '.png')):
        img_path = os.path.join(sharpen_folder, filename)
        img = Image.open(img_path)

        # UnsharpMask filtresi ile netleştir
        sharpened_img = img.filter(ImageFilter.UnsharpMask(radius=radius, percent=percent, threshold=threshold))

        # Yeni dosya adıyla kaydet
        name, ext = os.path.splitext(filename)
        sharpened_img_name = f"{name}_sharpened{ext}"
        sharpened_img_path = os.path.join(sharpen_folder, sharpened_img_name)
        sharpened_img.save(sharpened_img_path)

print("Daha düşük ayarlarla netleştirme işlemi tamamlandı ve resimler kaydedildi.")

# Veri artırma işlemi
counter = 1
for filename in sorted(os.listdir(augmentation_folder)):
    if counter > end_index:
        break
    if start_index <= counter <= end_index and filename.endswith(('.jpg', '.jpeg', '.png')):
        img_path = os.path.join(augmentation_folder, filename)
        img = Image.open(img_path)

        # Rastgele bir işlem seç: Grayscale, Saturation, veya Brightness
        operation = random.choice(['grayscale', 'saturation', 'brightness'])

        if operation == 'grayscale':
            processed_img = img.convert('L').convert('RGB')
            operation_name = 'grayscale'

        elif operation == 'saturation':
            enhancer = ImageEnhance.Color(img)
            saturation_factor = random.uniform(0.5, 1.5)
            processed_img = enhancer.enhance(saturation_factor)
            operation_name = f'saturation_{saturation_factor:.2f}'

        elif operation == 'brightness':
            enhancer = ImageEnhance.Brightness(img)
            brightness_factor = random.uniform(0.5, 1.5)
            processed_img = enhancer.enhance(brightness_factor)
            operation_name = f'brightness_{brightness_factor:.2f}'

        # Yeni dosya adıyla kaydet
        new_filename = f"{initial_image_count + counter}_{operation_name}.jpg"
        new_img_path = os.path.join(augmentation_folder, new_filename)
        processed_img.save(new_img_path)

        print(f"{new_filename} dosyası kaydedildi.")

    counter += 1

print(f"{end_index - start_index + 1} resim başarıyla işlendi ve kaydedildi.")
