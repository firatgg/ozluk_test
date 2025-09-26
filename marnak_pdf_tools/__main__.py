"""
Ana modül - GUI uygulamasını veya CLI komutlarını başlatır.
"""
import sys
import argparse
import os
from pathlib import Path

def setup_cli_parser():
    """CLI argüman parser'ını oluşturur."""
    parser = argparse.ArgumentParser(
        description="Marnak PDF Araçları - PDF dosyalarını işlemek için araçlar",
        prog="python -m marnak_pdf_tools"
    )
    
    subparsers = parser.add_subparsers(dest='command', help='Kullanılabilir komutlar')
    
    # Merge komutu
    merge_parser = subparsers.add_parser('merge', help='PDF dosyalarını birleştir')
    merge_parser.add_argument('files', nargs='+', help='Birleştirilecek PDF dosyaları')
    merge_parser.add_argument('-o', '--output', required=True, help='Çıktı dosyası yolu')
    
    # Split komutu
    split_parser = subparsers.add_parser('split', help='PDF dosyasını böl')
    split_parser.add_argument('file', help='Bölünecek PDF dosyası')
    split_parser.add_argument('-o', '--output', required=True, help='Çıktı klasörü')
    split_parser.add_argument('-m', '--mode', choices=['all', 'range', 'every'], 
                             default='all', help='Bölme modu (all: tüm sayfalar, range: aralık, every: her N sayfa)')
    split_parser.add_argument('-r', '--range', help='Sayfa aralığı (örn: 1,3-5,7)')
    split_parser.add_argument('-n', '--number', type=int, help='Her N sayfada bir böl (every modu için)')
    
    # Extract komutu
    extract_parser = subparsers.add_parser('extract', help='PDF sayfalarını çıkar')
    extract_parser.add_argument('file', help='PDF dosyası')
    extract_parser.add_argument('-o', '--output', required=True, help='Çıktı klasörü')
    extract_parser.add_argument('-a', '--all', action='store_true', help='Tüm sayfaları çıkar')
    extract_parser.add_argument('-r', '--range', help='Sayfa aralığı (örn: 1,3-5,7)')
    extract_parser.add_argument('-p', '--prefix', default='', help='Dosya adı öneki')
    
    # Rename komutu
    rename_parser = subparsers.add_parser('rename', help='PDF dosyalarını yeniden adlandır')
    rename_parser.add_argument('files', nargs='+', help='Yeniden adlandırılacak PDF dosyaları')
    rename_parser.add_argument('-o', '--output', required=True, help='Çıktı klasörü')
    rename_parser.add_argument('-n', '--name', help='Yeni dosya adı (opsiyonel)')
    rename_parser.add_argument('--keep-originals', action='store_true', help='Orijinal dosyaları koru')
    
    return parser

def run_cli_command(args):
    """CLI komutunu çalıştırır."""
    try:
        from .services.pdf_service import PdfService
        from .core import PdfSplitter, PdfMerger, PdfExtractor, PdfRenamer
        
        pdf_service = PdfService()
        
        if args.command == 'merge':
            # Dosya varlığını kontrol et
            for file_path in args.files:
                if not os.path.exists(file_path):
                    print(f"Hata: Dosya bulunamadı: {file_path}")
                    return 1
            
            print(f"PDF dosyaları birleştiriliyor...")
            print(f"Giriş dosyaları: {', '.join(args.files)}")
            print(f"Çıktı dosyası: {args.output}")
            
            merger = PdfMerger()
            success, message, _ = merger.merge_pdfs(args.files, args.output)
            
            if success:
                print(f"✅ Başarılı: {message}")
                return 0
            else:
                print(f"❌ Hata: {message}")
                return 1
                
        elif args.command == 'split':
            if not os.path.exists(args.file):
                print(f"Hata: Dosya bulunamadı: {args.file}")
                return 1
            
            print(f"PDF dosyası bölünüyor...")
            print(f"Giriş dosyası: {args.file}")
            print(f"Çıktı klasörü: {args.output}")
            
            # Çıktı klasörünü oluştur
            os.makedirs(args.output, exist_ok=True)
            
            options = {'mode': args.mode}
            if args.mode == 'range' and args.range:
                options['page_range'] = args.range
            elif args.mode == 'every' and args.number:
                options['pages_per_split'] = args.number
            
            splitter = PdfSplitter()
            success, message, output_files = splitter.split_pdf(args.file, args.output, options)
            
            if success:
                print(f"✅ Başarılı: {message}")
                print(f"Oluşturulan dosyalar: {len(output_files)}")
                for file in output_files:
                    print(f"  - {file}")
                return 0
            else:
                print(f"❌ Hata: {message}")
                return 1
                
        elif args.command == 'extract':
            if not os.path.exists(args.file):
                print(f"Hata: Dosya bulunamadı: {args.file}")
                return 1
            
            print(f"PDF sayfaları çıkarılıyor...")
            print(f"Giriş dosyası: {args.file}")
            print(f"Çıktı klasörü: {args.output}")
            
            # Çıktı klasörünü oluştur
            os.makedirs(args.output, exist_ok=True)
            
            options = {
                'extract_all': args.all,
                'page_range': args.range or '',
                'file_prefix': args.prefix
            }
            
            extractor = PdfExtractor()
            success, message, output_files = extractor.extract_pages(args.file, args.output, options)
            
            if success:
                print(f"✅ Başarılı: {message}")
                print(f"Çıkarılan dosyalar: {len(output_files)}")
                for file in output_files:
                    print(f"  - {file}")
                return 0
            else:
                print(f"❌ Hata: {message}")
                return 1
                
        elif args.command == 'rename':
            # Dosya varlığını kontrol et
            for file_path in args.files:
                if not os.path.exists(file_path):
                    print(f"Hata: Dosya bulunamadı: {file_path}")
                    return 1
            
            print(f"PDF dosyaları yeniden adlandırılıyor...")
            print(f"Giriş dosyaları: {', '.join(args.files)}")
            print(f"Çıktı klasörü: {args.output}")
            
            # Çıktı klasörünü oluştur
            os.makedirs(args.output, exist_ok=True)
            
            options = {
                'new_name': args.name or '',
                'keep_originals': args.keep_originals
            }
            
            renamer = PdfRenamer()
            success, message, output_files = renamer.rename_pdfs(args.files, args.output, options)
            
            if success:
                print(f"✅ Başarılı: {message}")
                print(f"İşlenen dosyalar: {len(output_files)}")
                for file in output_files:
                    print(f"  - {file}")
                return 0
            else:
                print(f"❌ Hata: {message}")
                return 1
                
    except Exception as e:
        print(f"❌ Beklenmeyen hata: {str(e)}")
        return 1

def main():
    """Ana fonksiyon - CLI veya GUI'yi başlatır."""
    # Eğer argüman yoksa GUI'yi başlat
    if len(sys.argv) == 1:
        from .app import main as gui_main
        return gui_main()
    
    # CLI argümanlarını işle
    parser = setup_cli_parser()
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    return run_cli_command(args)

if __name__ == "__main__":
    sys.exit(main()) 