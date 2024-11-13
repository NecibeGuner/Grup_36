import subprocess
import sys
import os

# Çalıştırılacak Python dosyalarının listesi
scripts = [ 'AtlasAcne+.py','DermisAcne+.py','DermNetZAcne+.py','IStockAcne+.py','NLM_Acne+.py','PCDS_Acne+.py'
            ,'SkinSightAcne+.py','WikiMediaAcne+.py']

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
