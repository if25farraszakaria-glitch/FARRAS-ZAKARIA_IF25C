import os
from database import DatabaseController
from searching import linear_search, binary_search
from sorting import bubble_sort, quick_sort

def run_tests():
    temp_csv = "temp_verify.csv"
    
    # 1. Hapus jika sisa test sebelumnya ada
    if os.path.exists(temp_csv):
        os.remove(temp_csv)
        
    print("=== Memulai Pengujian Backend Sistem Gudang ===")
    
    # 2. Inisialisasi Database
    db = DatabaseController(filepath=temp_csv)
    print("[OK] Database inisialisasi berhasil.")
    
    # 3. Pengujian CREATE
    db.add_item("001", "Laptop Gaming", "Elektronik", 10, 15000000.0, "Asus")
    db.add_item("002", "Keyboard Mechanical", "Elektronik", 25, 850000.0, "Logitech")
    db.add_item("003", "Kursi Gaming", "Furnitur", 5, 2500000.0, "Secretlab")
    db.add_item("004", "Meja Kayu", "Furnitur", 12, 1200000.0, "Olympic")
    
    # Cek duplicate ID
    try:
        db.add_item("001", "Laptop Duplikat", "Elektronik", 5, 12000000.0, "Asus")
        print("[FAIL] Seharusnya mendeteksi duplicate ID!")
    except ValueError as e:
        print(f"[OK] Deteksi duplicate ID berhasil: '{e}'")
        
    # Cek jumlah item
    items = db.get_all_items()
    assert len(items) == 4, f"Jumlah item salah, seharusnya 4 tetapi {len(items)}"
    print("[OK] Pengujian Tambah Item (CREATE) berhasil.")
    
    # 4. Pengujian READ & O(1) Dictionary Lookup
    item_002 = db.get_item("002")
    assert item_002 is not None, "Item 002 tidak ditemukan di dictionary!"
    assert item_002["Nama_Barang"] == "Keyboard Mechanical", "Nama item 002 tidak cocok!"
    print("[OK] Pengujian lookup O(1) Dictionary berhasil.")
    
    # 5. Pengujian UPDATE
    db.update_item("002", nama_barang="Keyboard Mechanical RGB", stok=20)
    item_002_updated = db.get_item("002")
    assert item_002_updated["Nama_Barang"] == "Keyboard Mechanical RGB", "Gagal update Nama_Barang!"
    assert item_002_updated["Stok"] == 20, "Gagal update Stok!"
    print("[OK] Pengujian update item (UPDATE) berhasil.")
    
    # 6. Pengujian Barang Masuk & Barang Keluar
    db.add_stock("001", 5) # 10 + 5 = 15
    assert db.get_item("001")["Stok"] == 15, "Gagal menambah stok!"
    print("[OK] Pengujian tambah stok (Barang Masuk) berhasil.")
    
    db.reduce_stock("001", 3) # 15 - 3 = 12
    assert db.get_item("001")["Stok"] == 12, "Gagal mengurangi stok!"
    
    # Validasi stok tidak cukup
    try:
        db.reduce_stock("001", 20)
        print("[FAIL] Seharusnya mendeteksi stok tidak cukup!")
    except ValueError as e:
        print(f"[OK] Deteksi stok kurang berhasil: '{e}'")
    print("[OK] Pengujian kurangi stok (Barang Keluar) berhasil.")
    
    # 7. Pengujian Searching
    items_to_search = db.get_all_items()
    
    # Linear Search
    lin_results = linear_search(items_to_search, "gaming", field="Nama_Barang")
    assert len(lin_results) == 2, f"Hasil linear search salah, seharusnya 2 tetapi {len(lin_results)}"
    print("[OK] Pengujian Linear Search (Nama_Barang berisi 'gaming') berhasil.")
    
    # Binary Search (wajib exact match dan sorted)
    bin_results = binary_search(items_to_search, "Furnitur", field="Kategori")
    assert len(bin_results) == 2, f"Hasil binary search salah, seharusnya 2 tetapi {len(bin_results)}"
    print("[OK] Pengujian Binary Search (Kategori exact 'Furnitur') berhasil.")
    
    # 8. Pengujian Sorting
    # Quick Sort - Berdasarkan Stok Ascending
    sorted_quick_stok = quick_sort(items_to_search, key="Stok", reverse=False)
    assert sorted_quick_stok[0]["Stok"] <= sorted_quick_stok[-1]["Stok"], "Quick Sort Stok Ascending gagal!"
    print("[OK] Pengujian Quick Sort (Stok Ascending) berhasil.")
    
    # Bubble Sort - Berdasarkan Harga Descending
    sorted_bubble_harga = bubble_sort(items_to_search, key="Harga", reverse=True)
    assert sorted_bubble_harga[0]["Harga"] >= sorted_bubble_harga[-1]["Harga"], "Bubble Sort Harga Descending gagal!"
    print("[OK] Pengujian Bubble Sort (Harga Descending) berhasil.")
    
    # 9. Pengujian DELETE
    db.delete_item("003")
    assert db.get_item("003") is None, "Gagal menghapus item dari dictionary!"
    assert len(db.get_all_items()) == 3, "Gagal menghapus item dari Linked List!"
    print("[OK] Pengujian hapus item (DELETE) berhasil.")
    
    # Bersihkan file temp
    if os.path.exists(temp_csv):
        os.remove(temp_csv)
    print("=== Semua Pengujian Berhasil Dilalui! ===")

if __name__ == "__main__":
    run_tests()
