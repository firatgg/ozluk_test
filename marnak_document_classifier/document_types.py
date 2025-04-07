from collections import Counter

"""
Belge tiplerini ve anahtar kelimelerini merkezi bir yapıda tanımlayan modül.
Bu modül, eğitim ve sınıflandırma süreçlerinde tutarlılık sağlar.
"""

# Belge tipleri ve ilgili anahtar kelimeler
DOC_TYPE_KEYWORDS = {
    "kimlik": ["kimlik", "tc", "t.c.", "nüfus cüzdanı", "tc kimlik", "tckn", "vesikalık", "nüfus", "nufus", "kayıt", "kayit", "örneği", "ornegi"],
    "ehliyet": ["ehliyet", "sürücü belgesi", "sürücü", "surucu", "src", "src1", "src2", "src3", "src4", "üdy", "üdy1", "üdy2", "üdy3", "üdy4", "profesyonel", "profesyonel sürücü", "profesyonel surucu"],
    "diploma": ["diploma", "mezuniyet", "okul bitirme", "yüksekokul", "yuksekokul", "lise", "mezun", "öğrenim", "ogrenim", "öğrenci", "ogrenci", "okul", "üniversite", "universite"],
    "ikametgah": ["ikametgah", "ikamet", "gah", "adres", "yerleşim", "yerlesim"],
    "saglik_raporu": [
        "sağlık", "saglik", "rapor", "kan", "hemogram", "göz", "goz", "akciğer", "akciger", 
        "odyometri", "psikoteknik", "tetanoz", "covid", "test", "tahlil", "aşı", "asi",
        "muayene", "checkup", "periyodik", "işe giriş", "ise giris", "işe başlama", "ise baslama",
        "aşı kartı", "asi kartı", "genel sağlık", "genel saglik", "iş göremezlik", "is goremezlik"
    ],
    "sertifika": [
        "sertifika", "katılım", "katilim", "başarı", "basari", "eğitim", "egitim", "belge", "formu",
        "talimat", "yangın", "yangin", "güvenliği", "guvenligi", "isg", "iş güvenliği", "is guvenligi",
        "temel", "liderlik", "etkin", "yönetici", "yonetici", "excel", "oryantasyon", "lojistik", "depo", "forklift", "istifleme"
    ],
    "transkript": ["transkript", "not dökümü", "not dokumu", "not belgesi"],
    "sgk": ["sgk", "hizmet dökümü", "hizmet dokumu", "ssk", "sgk dökümü", "sgk dokumu", "4a", "4b", "emeklilik", "işe giriş", "ise giris", "işten ayrılış", "isten ayrilis", "gelir", "ödeme", "odeme", "aylık", "aylik", "ödenek", "odenek", "talep", "bildirgesi"],
    "sozlesme": ["sözleşme", "sozlesme", "iş sözleşmesi", "is sozlesmesi", "kontrat", "anlaşma", "anlasma", "hizmet sözleşmesi", "hizmet sozlesmesi", "belirli süreli", "belirli sureli", "belirsiz süreli", "belirsiz sureli", "protokol", "değişiklik", "degisiklik"],
    "dilekce": ["dilekçe", "dilekce", "ibraname", "başvuru", "basvuru", "izin talebi", "talep"],
    "referans": ["referans", "öneri mektubu", "oneri mektubu", "tavsiye mektubu"],
    "banka": ["banka", "iban", "hesap bilgisi", "banka bilgisi", "dekont", "banka hesabı", "banka hesabi"],
    "fotoğraf": ["fotoğraf", "fotograf", "vesikalık", "vesikalik", "resim", "photo", "profil"],
    "adli_sicil": ["adli sicil", "adli", "sicil", "sabıka", "sabika", "temiz kağıdı", "temiz kagidi", "sicil belgesi"],
    "ik": ["personel bilgi formu", "özgeçmiş", "ozgecmis", "cv", "kimlik fotokopisi", "nüfus kayıt örneği", "nufus kayit ornegi", "nüfus", "nufus", "iş detay", "is detay", "iş talep", "is talep", "işe başlama", "ise baslama"],
    "aile": ["vukuatlı", "vukuatli", "nüfus kayıt örneği", "nufus kayit ornegi", "aile bireyleri", "aile belgesi", "aile durumu", "aile bildirimi", "asgari", "geçim", "gecim", "indirimi", "indirimi", "agi"],
    "askerlik": ["askerlik", "terhis", "askerlik durumu", "askerlik belgesi", "asker", "vazife", "vazifesi", "askerlik hizmeti"],
    "dijital_imza": ["e-imza", "e-imza", "dijital imza", "mobil imza", "nitelikli", "imza belgesi"],
    "fatura": ["fatura", "ödeme", "odeme", "makbuz", "bedel", "tutar", "ücret", "ucret"],
    "kıdem": ["kıdem", "kidem", "tazminat", "ihbar", "hesap", "bordro", "kıdem tazminatı", "kidem tazminati", "hizmet süresi", "hizmet suresi", "kıdem belgesi", "kidem belgesi"],
    "kkd": ["kkd", "kişisel koruyucu", "kisisel koruyucu", "baret", "eldiven", "koruma ekipmanı", "koruma ekipmani", "donanım", "donanim", "teslim", "tutanak"],
    "lojistik": ["lojistik", "nakliye", "taşıma", "tasima", "depo", "forklift", "istifleme", "yükleme", "yukleme", "boşaltma", "bosaltma", "rota", "güzergah", "guzergah", "sefer", "konteyner"],
    "diger": ["belge", "doküman", "dokuman", "dosya", "ek", "evrak", "form", "talimat", "tutanak", "rapor", "bildirim"]
}

# Fotoğraf belgelerinde genellikle bulunmayan kelimeler
NON_PHOTO_KEYWORDS = [
    "tarih", "imza", "numara", "adres", "telefon", "e-posta", "email",
    "tc kimlik", "kimlik no", "doğum", "anne", "baba", "medeni",
    "uyruk", "meslek", "işyeri", "firma", "şirket", "vergi", "sgk",
    "sağlık", "hastane", "doktor", "muayene", "rapor", "tedavi",
    "okul", "üniversite", "fakülte", "bölüm", "öğrenci", "öğretmen",
    "diploma", "sertifika", "belge", "evrak", "dilekçe", "form",
    "banka", "hesap", "kredi", "ödeme", "fatura", "makbuz", "fiş",
    "askerlik", "terhis", "rütbe", "birlik", "nizamiye", "kamu",
    "devlet", "kurum", "kuruluş", "resmi", "özel", "ticari"
]

# Fotoğraf belgelerinde bulunabilecek kelimeler
PHOTO_KEYWORDS = [
    "fotoğraf", "fotograf", "resim", "görüntü", "çekim", "portre",
    "vesikalık", "pasaport", "ehliyet", "kimlik", "kart", "belge"
]

# Az örnekli sınıflar (eğitim sırasında "diger" sınıfına birleştirilecek)
RARE_CLASSES = ['fotoğraf', 'aile', 'askerlik', 'kkd', 'kıdem', 'fatura', 'lojistik', 'dijital_imza', 'referans']

# Belge tipine göre detaylı isimler
DOC_TYPE_DETAILS = {
    'kimlik': 'kimlik',
    'ehliyet': 'ehliyet',
    'diploma': 'diploma',
    'adli_sicil': 'adli sicil kaydı',
    'ikametgah': 'ikametgah',
    'saglik_raporu': 'sağlık raporu',
    'kan_testi': 'sağlık [kan testi]',
    'akciger_grafisi': 'sağlık [akciğer grafisi]',
    'odyometri': 'sağlık [odyometri raporu]',
    'is_sozlesmesi': 'belirsiz süreli iş sözleşmesi',
    'sgk_bildirgesi': 'sgk işe giriş bildirgesi',
    'sertifika': 'sertifika',
    'transkript': 'transkript',
    'sozlesme': 'sözleşme',
    'dilekce': 'dilekçe',
    'referans': 'referans mektubu',
    'banka': 'banka bilgileri',
    'fotoğraf': 'fotoğraf',
    'ik': 'personel bilgi formu',
    'aile': 'aile durumu',
    'askerlik': 'askerlik belgesi',
    'dijital_imza': 'dijital imza',
    'fatura': 'fatura',
    'kıdem': 'kıdem tazminatı',
    'kkd': 'kişisel koruyucu donanım',
    'lojistik': 'lojistik belgesi',
    'diger': 'diger'
}

def get_doc_type_from_filename(filename):
    """Dosya adından belge tipini belirle"""
    # Dosya adını küçük harfe çevir ve .pdf uzantısını kaldır
    filename_lower = filename.lower().replace('.pdf', '')
    
    # Belge tipini belirle
    for doc_type_name, keywords in DOC_TYPE_KEYWORDS.items():
        if any(keyword in filename_lower for keyword in keywords):
            return doc_type_name
    
    # Eğer hiçbir sınıfa uymuyorsa 'diger' olarak işaretle
    return "diger"

def is_photo_document(text):
    """Metin içeriğine göre belgenin fotoğraf olup olmadığını kontrol et"""
    if not text or len(text.strip()) < 10:  # 10 karakterden az metin varsa
        return True
        
    # Metni küçük harfe çevir
    text = text.lower()
    
    # Fotoğraf anahtar kelimelerini kontrol et
    photo_count = sum(1 for keyword in PHOTO_KEYWORDS if keyword in text)
    
    # Fotoğraf olmayan anahtar kelimeleri kontrol et
    non_photo_count = sum(1 for keyword in NON_PHOTO_KEYWORDS if keyword in text)
    
    # Eğer fotoğraf anahtar kelimeleri varsa ve fotoğraf olmayan anahtar kelimeleri yoksa
    if photo_count > 0 and non_photo_count == 0:
        return True
        
    # Eğer fotoğraf olmayan anahtar kelimeleri varsa
    if non_photo_count > 0:
        return False
        
    # Eğer hiç anahtar kelime yoksa ve metin çok kısaysa
    if len(text.split()) < 5:
        return True
        
    return False

def get_detailed_doc_name(doc_type):
    """Belge tipine göre detaylı isim döndür"""
    return DOC_TYPE_DETAILS.get(doc_type, f"[{doc_type}]")

def merge_rare_classes(labels, threshold=5):
    """Az örnekli sınıfları birleştir"""
    # Önce RARE_CLASSES listesindeki sınıfları "diger" olarak işaretle
    labels = ['diger' if label in RARE_CLASSES else label for label in labels]
    
    # Sonra threshold'a göre az örnekli sınıfları birleştir
    label_counts = Counter(labels)
    rare_labels = [label for label, count in label_counts.items() if count < threshold]
    return ['diger' if label in rare_labels else label for label in labels] 