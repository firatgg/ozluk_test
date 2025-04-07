"""
Geliştirme modu için hot reload script'i.
"""
import os
import sys
import time
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import subprocess

class CodeChangeHandler(FileSystemEventHandler):
    """Kod değişikliklerini izleyen sınıf."""
    
    def __init__(self):
        self.process = None
        self.restart_app()
        
    def restart_app(self):
        """Uygulamayı yeniden başlatır."""
        if self.process:
            self.process.terminate()
            self.process.wait()
            
        print("\n🔄 Uygulama yeniden başlatılıyor...")
        self.process = subprocess.Popen([sys.executable, "-m", "marnak_pdf_tools"])
        
    def on_modified(self, event):
        """Dosya değişikliklerini izler."""
        if event.src_path.endswith('.py'):
            print(f"\n📝 Değişiklik algılandı: {event.src_path}")
            self.restart_app()

def main():
    """Ana fonksiyon."""
    print("🚀 Geliştirme modu başlatılıyor...")
    print("👀 Kod değişiklikleri izleniyor...")
    
    # İzleyiciyi başlat
    event_handler = CodeChangeHandler()
    observer = Observer()
    observer.schedule(event_handler, path='.', recursive=True)
    observer.start()
    
    try:
        while True:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\n👋 Geliştirme modu kapatılıyor...")
        observer.stop()
        if event_handler.process:
            event_handler.process.terminate()
    observer.join()

if __name__ == "__main__":
    main() 