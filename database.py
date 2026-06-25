import os
import csv
from linkedlist import BarangLinkedList, BarangNode

class DatabaseController:
    """
    Mengelola sinkronisasi antara file CSV (Database),
    Linked List (In-memory Storage), dan Dictionary (Hash Map untuk fast O(1) lookup).
    """
    def __init__(self, filepath="data_barang.csv"):
        self.filepath = filepath
        self.linked_list = BarangLinkedList()
        self.hash_map = {}  # ID_Barang -> BarangNode
        self.load_data()

    def load_data(self):
        """
        Membaca data dari data_barang.csv dan memasukkannya ke
        dalam Linked List serta Hash Map (Dictionary).
        """
        self.linked_list.clear()
        self.hash_map.clear()

        # Jika file belum ada, buat file baru dengan header
        if not os.path.exists(self.filepath):
            with open(self.filepath, mode='w', newline='', encoding='utf-8') as f:
                writer = csv.writer(f)
                writer.writerow(["ID_Barang", "Nama_Barang", "Kategori", "Stok", "Harga", "Supplier"])
            return

        with open(self.filepath, mode='r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                id_barang = row["ID_Barang"].strip()
                nama_barang = row["Nama_Barang"].strip()
                kategori = row["Kategori"].strip()
                try:
                    stok = int(row["Stok"])
                except ValueError:
                    stok = 0
                try:
                    harga = float(row["Harga"])
                except ValueError:
                    harga = 0.0
                supplier = row["Supplier"].strip()

                # Tambahkan ke Linked List
                node = self.linked_list.append(id_barang, nama_barang, kategori, stok, harga, supplier)
                
                # Tambahkan ke Hash Map (Dictionary) untuk O(1) lookup
                self.hash_map[id_barang] = node

    def save_data(self):
        """
        Menulis seluruh data dari Linked List kembali ke file CSV.
        """
        items = self.linked_list.to_list()
        with open(self.filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(["ID_Barang", "Nama_Barang", "Kategori", "Stok", "Harga", "Supplier"])
            for item in items:
                writer.writerow([
                    item["ID_Barang"],
                    item["Nama_Barang"],
                    item["Kategori"],
                    item["Stok"],
                    int(item["Harga"]), # Harga dalam integer agar lebih rapi di CSV jika tidak ada desimal
                    item["Supplier"]
                ])

    def add_item(self, id_barang, nama_barang, kategori, stok, harga, supplier):
        """
        CREATE: Menambahkan barang baru.
        Mengecek keunikan ID menggunakan Hash Map dalam O(1).
        """
        id_str = str(id_barang).strip()
        if id_str in self.hash_map:
            raise ValueError(f"Barang dengan ID {id_str} sudah terdaftar!")

        # 1. Tambahkan ke Linked List
        node = self.linked_list.append(id_str, nama_barang, kategori, stok, harga, supplier)
        
        # 2. Tambahkan ke Hash Map
        self.hash_map[id_str] = node
        
        # 3. Simpan perubahan ke CSV
        self.save_data()
        return True

    def get_item(self, id_barang):
        """
        READ: Mengambil barang tertentu berdasarkan ID menggunakan Hash Map (O(1)).
        """
        id_str = str(id_barang).strip()
        node = self.hash_map.get(id_str)
        return node.to_dict() if node else None

    def get_all_items(self):
        """
        READ: Mengembalikan seluruh data barang dalam bentuk list of dict.
        """
        return self.linked_list.to_list()

    def update_item(self, id_barang, nama_barang=None, kategori=None, stok=None, harga=None, supplier=None):
        """
        UPDATE: Mengubah informasi barang berdasarkan ID.
        Mengakses node langsung secara O(1) melalui Hash Map.
        """
        id_str = str(id_barang).strip()
        if id_str not in self.hash_map:
            raise KeyError(f"Barang dengan ID {id_str} tidak ditemukan!")

        node = self.hash_map[id_str]
        
        if nama_barang is not None:
            node.nama_barang = str(nama_barang).strip()
        if kategori is not None:
            node.kategori = str(kategori).strip()
        if stok is not None:
            node.stok = int(stok)
        if harga is not None:
            node.harga = float(harga)
        if supplier is not None:
            node.supplier = str(supplier).strip()

        # Simpan perubahan ke CSV
        self.save_data()
        return True

    def delete_item(self, id_barang):
        """
        DELETE: Menghapus barang berdasarkan ID.
        """
        id_str = str(id_barang).strip()
        if id_str not in self.hash_map:
            raise KeyError(f"Barang dengan ID {id_str} tidak ditemukan!")

        # 1. Hapus dari Linked List
        self.linked_list.remove(id_str)
        
        # 2. Hapus dari Hash Map
        self.hash_map.pop(id_str)
        
        # 3. Simpan ke CSV
        self.save_data()
        return True

    def add_stock(self, id_barang, quantity):
        """
        Fitur Tambahan: Menambahkan stok barang masuk.
        """
        id_str = str(id_barang).strip()
        if id_str not in self.hash_map:
            raise KeyError(f"Barang dengan ID {id_str} tidak ditemukan!")

        if quantity <= 0:
            raise ValueError("Jumlah barang masuk harus lebih besar dari 0!")

        node = self.hash_map[id_str]
        node.stok += quantity
        
        self.save_data()
        return True

    def reduce_stock(self, id_barang, quantity):
        """
        Fitur Tambahan: Mengurangi stok barang keluar dengan validasi.
        """
        id_str = str(id_barang).strip()
        if id_str not in self.hash_map:
            raise KeyError(f"Barang dengan ID {id_str} tidak ditemukan!")

        if quantity <= 0:
            raise ValueError("Jumlah barang keluar harus lebih besar dari 0!")

        node = self.hash_map[id_str]
        if node.stok < quantity:
            raise ValueError(f"Stok tidak mencukupi! Stok saat ini: {node.stok}, diminta: {quantity}")

        node.stok -= quantity
        
        self.save_data()
        return True

    def get_statistics(self):
        """
        Fitur Tambahan: Laporan Gudang.
        Menghitung statistik inventory berdasarkan Linked List.
        """
        items = self.linked_list.to_list()
        
        total_jenis = len(items)
        total_stok = sum(item["Stok"] for item in items)
        
        stok_terbanyak = None
        stok_tersedikit = None
        
        if items:
            # Cari barang dengan stok terbanyak & tersedikit
            stok_terbanyak = max(items, key=lambda x: x["Stok"])
            stok_tersedikit = min(items, key=lambda x: x["Stok"])

        return {
            "total_jenis": total_jenis,
            "total_stok": total_stok,
            "stok_terbanyak": stok_terbanyak,
            "stok_tersedikit": stok_tersedikit
        }

    def export_report_to_csv(self, filepath):
        """
        Mengekspor laporan gudang yang mencakup ringkasan statistik,
        stok ekstrim, dan sebaran kategori ke file CSV.
        """
        stats = self.get_statistics()
        items = self.get_all_items()
        total_aset = sum(item["Stok"] * item["Harga"] for item in items)
        
        category_counts = {}
        for item in items:
            cat = item["Kategori"]
            category_counts[cat] = category_counts.get(cat, 0) + item["Stok"]

        with open(filepath, mode='w', newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            
            # 1. Ringkasan
            writer.writerow(["=== LAPORAN RINGKASAN GUDANG ==="])
            writer.writerow(["Parameter", "Nilai"])
            writer.writerow(["Total Jenis Barang", f"{stats['total_jenis']} Jenis"])
            writer.writerow(["Total Jumlah Stok", f"{stats['total_stok']} Unit"])
            writer.writerow(["Total Nilai Investasi Aset", f"Rp {int(total_aset):,}"])
            writer.writerow([])
            
            # 2. Barang Ekstrim
            writer.writerow(["=== ANALISIS STOK EKSTRIM ==="])
            writer.writerow(["Kondisi", "ID Barang", "Nama Barang", "Kategori", "Stok", "Supplier"])
            max_item = stats["stok_terbanyak"]
            if max_item:
                writer.writerow(["Stok Terbanyak", max_item["ID_Barang"], max_item["Nama_Barang"], max_item["Kategori"], max_item["Stok"], max_item["Supplier"]])
            else:
                writer.writerow(["Stok Terbanyak", "-", "-", "-", "-", "-"])
                
            min_item = stats["stok_tersedikit"]
            if min_item:
                writer.writerow(["Stok Tersedikit", min_item["ID_Barang"], min_item["Nama_Barang"], min_item["Kategori"], min_item["Stok"], min_item["Supplier"]])
            else:
                writer.writerow(["Stok Tersedikit", "-", "-", "-", "-", "-"])
            writer.writerow([])
            
            # 3. Distribusi per Kategori
            writer.writerow(["=== DISTRIBUSI STOK PER KATEGORI ==="])
            writer.writerow(["Kategori", "Jumlah Stok"])
            for cat, count in sorted(category_counts.items(), key=lambda x: x[1], reverse=True):
                writer.writerow([cat, f"{count} Unit"])

