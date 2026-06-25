def bubble_sort(items, key, reverse=False):
    """
    Algoritma Bubble Sort.
    Mengurutkan salinan data agar tidak merusak data utama.
    Mendukung pengurutan berdasarkan Nama_Barang, Stok, atau Harga (Ascending / Descending).
    """
    # Buat salinan list agar tidak merubah data asli
    arr = list(items)
    n = len(arr)
    
    # Fungsi pembantu untuk membandingkan secara case-insensitive jika string
    def get_val(item):
        val = item.get(key)
        if isinstance(val, str):
            return val.lower()
        return val

    for i in range(n):
        for j in range(0, n - i - 1):
            val1 = get_val(arr[j])
            val2 = get_val(arr[j+1])
            
            # Pengkondisian untuk ascending vs descending
            if not reverse:
                if val1 > val2:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
            else:
                if val1 < val2:
                    arr[j], arr[j+1] = arr[j+1], arr[j]
    return arr


def quick_sort(items, key, reverse=False):
    """
    Algoritma Quick Sort (Divide and Conquer).
    Mendukung pengurutan berdasarkan Nama_Barang, Stok, atau Harga (Ascending / Descending).
    """
    arr = list(items)
    if len(arr) <= 1:
        return arr
    
    # Fungsi pembantu untuk membandingkan secara case-insensitive jika string
    def get_val(item):
        val = item.get(key)
        if isinstance(val, str):
            return val.lower()
        return val

    pivot = arr[len(arr) // 2]
    pivot_val = get_val(pivot)
    
    left = []
    middle = []
    right = []
    
    for item in arr:
        item_val = get_val(item)
        if item_val < pivot_val:
            left.append(item)
        elif item_val > pivot_val:
            right.append(item)
        else:
            middle.append(item)
            
    # Rekursi
    if not reverse:
        return quick_sort(left, key, reverse) + middle + quick_sort(right, key, reverse)
    else:
        return quick_sort(right, key, reverse) + middle + quick_sort(left, key, reverse)
