import sys
import os
import time
import subprocess
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

class CodeChangeHandler(FileSystemEventHandler):
    def __init__(self):
        self.last_modified = time.time()
        self.process = None
        self.start_app()
    
    def start_app(self):
        """Uygulamayı başlat"""
        if self.process:
            self.process.terminate()
            self.process.wait()
        
        print("\n🔄 Uygulama yeniden başlatılıyor...")
        self.process = subprocess.Popen([sys.executable, "pdf_gui.py"])
    
    def on_modified(self, event):
        """Dosya değişikliğini yakala"""
        if event.src_path.endswith('.py'):
            current_time = time.time()
            if current_time - self.last_modified > 1:  # Çoklu tetiklemeyi önle
                self.last_modified = current_time
                print(f"\n📝 Değişiklik algılandı: {os.path.basename(event.src_path)}")
                self.start_app()

def main():
    # İzlenecek dizin
    path = os.path.dirname(os.path.abspath(__file__))
    
    # Değişiklik izleyiciyi başlat
    event_handler = CodeChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path, recursive=False)
    observer.start()
    
    print("👀 Hot Reload aktif - Kod değişiklikleri izleniyor...")
    print("❌ Çıkmak için Ctrl+C'ye basın")
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n🛑 Hot Reload durduruluyor...")
        if event_handler.process:
            event_handler.process.terminate()
        observer.stop()
    observer.join()

if __name__ == "__main__":
    main() 