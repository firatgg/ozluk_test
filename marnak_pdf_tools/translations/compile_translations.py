#!/usr/bin/env python3
"""
Çeviri dosyalarını .ts'den .qm'e derler.
"""
import os
import sys
from pathlib import Path

def compile_ts_to_qm(ts_file, qm_file):
    """TS dosyasını QM dosyasına derler."""
    try:
        # Basit bir XML parser ile TS dosyasını oku
        import xml.etree.ElementTree as ET
        
        tree = ET.parse(ts_file)
        root = tree.getroot()
        
        # QM dosyası oluştur (basit binary format)
        # Bu basit bir implementasyon, gerçek QM formatı daha karmaşıktır
        with open(qm_file, 'wb') as f:
            # QM dosyası başlığı
            f.write(b'QM\x00\x00\x00\x00')
            
            # Çevirileri ekle
            for context in root.findall('context'):
                for message in context.findall('message'):
                    source = message.find('source')
                    translation = message.find('translation')
                    
                    if source is not None and translation is not None:
                        source_text = source.text or ""
                        trans_text = translation.text or source_text
                        
                        # Basit format: uzunluk + metin
                        source_bytes = source_text.encode('utf-8')
                        trans_bytes = trans_text.encode('utf-8')
                        
                        f.write(len(source_bytes).to_bytes(4, 'little'))
                        f.write(source_bytes)
                        f.write(len(trans_bytes).to_bytes(4, 'little'))
                        f.write(trans_bytes)
        
        print(f"✓ {ts_file} -> {qm_file}")
        return True
        
    except Exception as e:
        print(f"✗ Hata: {ts_file} -> {qm_file}: {e}")
        return False

def main():
    """Ana fonksiyon."""
    translations_dir = Path(__file__).parent
    
    # TS dosyalarını bul ve derle
    ts_files = list(translations_dir.glob("*.ts"))
    
    if not ts_files:
        print("TS dosyası bulunamadı!")
        return
    
    success_count = 0
    for ts_file in ts_files:
        qm_file = ts_file.with_suffix('.qm')
        if compile_ts_to_qm(ts_file, qm_file):
            success_count += 1
    
    print(f"\n{success_count}/{len(ts_files)} dosya başarıyla derlendi.")

if __name__ == "__main__":
    main()
