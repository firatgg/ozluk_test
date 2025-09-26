"""
Core modülü için yardımcı fonksiyonlar.
"""
from typing import List

def parse_page_ranges(range_text: str, total_pages: int) -> List[List[int]]:
    """
    Sayfa aralıkları metnini ayrıştırır ve sayfa listesi listesi döndürür.
    
    Args:
        range_text: Sayfa aralıkları metni, örn. "1,3-5,7"
        total_pages: PDF'deki toplam sayfa sayısı
    
    Returns:
        Sayfa numaraları listesi listesi
    """
    result = []
    
    # Metin boş ise boş liste döndür
    if not range_text or range_text.strip() == "":
        return result
        
    # Virgülle ayrılmış parçalara böl
    parts = range_text.split(",")
    
    for part in parts:
        part = part.strip()
        
        # Aralık (örn. 3-5)
        if "-" in part:
            try:
                start, end = part.split("-", 1)
                start = int(start.strip())
                end = int(end.strip())
                
                # 0 tabanlı indeksleme için ayarla (PDF okuyucu 1 tabanlı gösterir)
                start = max(1, start) - 1  # En az 1, sonra 0-tabanlı için -1
                end = min(total_pages, end) - 1  # En fazla toplam sayfa, sonra 0-tabanlı için -1
                
                if start <= end:
                    result.append(list(range(start, end + 1)))
            except:
                # Ayrıştırma hatası, bu parçayı atla
                continue
        
        # Tek sayfa (örn. 3)
        else:
            try:
                page = int(part)
                # 0 tabanlı indeksleme için ayarla
                page = max(1, page) - 1  # En az 1, sonra 0-tabanlı için -1
                
                if 0 <= page < total_pages:
                    result.append([page])
            except:
                # Ayrıştırma hatası, bu parçayı atla
                continue
                
    return result
