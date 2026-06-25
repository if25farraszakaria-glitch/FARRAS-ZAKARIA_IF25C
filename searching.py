def linear_search(items, query, field="Nama_Barang"):
    """
    Algoritma Linear Search.
    Mencari kecocokan sebagian (partial match) secara case-insensitive.
    Bisa mencari berdasarkan ID_Barang atau Nama_Barang.
    """
    results = []
    query_lower = str(query).lower().strip()
    
    for item in items:
        # Mengambil nilai field (misal Nama_Barang atau ID_Barang)
        val = str(item.get(field, "")).lower()
        if query_lower in val:
            results.append(item)
            
    return results


def binary_search(items, query, field="ID_Barang"):
    """
    Algoritma Binary Search.
    Melakukan pencarian nilai yang sama persis (exact match) secara case-insensitive.
    CATATAN: Sebelum melakukan Binary Search, list harus diurutkan berdasarkan field pencarian.
    """
    query_lower = str(query).lower().strip()
    
    # Langkah 1: Urutkan items berdasarkan field yang dicari (karena Binary Search wajib terurut)
    # Kita mengurutkan list salinan agar tidak merusak list asli
    sorted_items = sorted(items, key=lambda x: str(x.get(field, "")).lower())
    
    low = 0
    high = len(sorted_items) - 1
    results = []
    
    while low <= high:
        mid = (low + high) // 2
        mid_val = str(sorted_items[mid].get(field, "")).lower()
        
        if mid_val == query_lower:
            # Ditemukan kecocokan. Karena mungkin ada item dengan nilai yang sama,
            # kita telusuri ke kiri dan ke kanan untuk mengambil semua item yang cocok.
            results.append(sorted_items[mid])
            
            # Cari ke kiri
            left = mid - 1
            while left >= 0 and str(sorted_items[left].get(field, "")).lower() == query_lower:
                results.append(sorted_items[left])
                left -= 1
                
            # Cari ke kanan
            right = mid + 1
            while right < len(sorted_items) and str(sorted_items[right].get(field, "")).lower() == query_lower:
                results.append(sorted_items[right])
                right += 1
                
            break
        elif mid_val < query_lower:
            low = mid + 1
        else:
            high = mid - 1
            
    return results
