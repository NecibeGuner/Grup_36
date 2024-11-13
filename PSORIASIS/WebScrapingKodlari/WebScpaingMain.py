import subprocess
import sys
import os

# Çalıştırılacak Python dosyalarının listesi
scripts = [ 'main.py','main2.py','main3.py','main4.py','main5.py','main6.py','main7.py','main8.py']

# Her bir scripti çalıştır
for script in scripts:
    # Dosya yolunu alarak çalıştırma
    script_path = os.path.join(os.getcwd(), script)  # Dosyanın tam yolunu oluşturur
    print(f"{script} dosyası çalıştırılıyor.")

    try:
        # Python yorumlayıcısını sys.executable kullanarak çalıştırma
        result = subprocess.run(
            [sys.executable, script_path],
            check=True
        )
        print(f"{script} başarıyla çalıştırıldı.")
    except subprocess.CalledProcessError as e:
        # Hata durumunda standart hata (stderr) mesajını göster
        print(f"{script} çalıştırılırken bir hata oluştu:\nHata Mesajı:\n{e}")

print("Tüm görüntüler ilgili klasörlere indirildi.")
