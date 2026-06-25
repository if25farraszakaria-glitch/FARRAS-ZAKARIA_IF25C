class BarangNode:
    """
    Representasi sebuah node dalam Linked List yang menyimpan data barang.
    """
    def __init__(self, id_barang, nama_barang, kategori, stok, harga, supplier):
        self.id_barang = str(id_barang)
        self.nama_barang = str(nama_barang)
        self.kategori = str(kategori)
        self.stok = int(stok)
        self.harga = float(harga)
        self.supplier = str(supplier)
        self.next = None  # Pointer ke node selanjutnya

    def to_dict(self):
        """
        Mengonversi data node menjadi dictionary.
        """
        return {
            "ID_Barang": self.id_barang,
            "Nama_Barang": self.nama_barang,
            "Kategori": self.kategori,
            "Stok": self.stok,
            "Harga": self.harga,
            "Supplier": self.supplier
        }


class BarangLinkedList:
    """
    Struktur data Linked List untuk mengelola node Barang.
    """
    def __init__(self):
        self.head = None

    def is_empty(self):
        return self.head is None

    def append(self, id_barang, nama_barang, kategori, stok, harga, supplier):
        """
        Menambahkan node barang baru di akhir Linked List.
        """
        new_node = BarangNode(id_barang, nama_barang, kategori, stok, harga, supplier)
        if self.is_empty():
            self.head = new_node
            return new_node

        current = self.head
        while current.next:
            current = current.next
        current.next = new_node
        return new_node

    def find(self, id_barang):
        """
        Mencari node barang berdasarkan ID_Barang.
        Mengembalikan BarangNode jika ditemukan, jika tidak mengembalikan None.
        """
        id_search = str(id_barang)
        current = self.head
        while current:
            if current.id_barang == id_search:
                return current
            current = current.next
        return None

    def remove(self, id_barang):
        """
        Menghapus node barang berdasarkan ID_Barang.
        Mengembalikan True jika berhasil dihapus, False jika tidak ditemukan.
        """
        id_search = str(id_barang)
        if self.is_empty():
            return False

        # Jika node yang akan dihapus berada di head
        if self.head.id_barang == id_search:
            self.head = self.head.next
            return True

        current = self.head
        while current.next:
            if current.next.id_barang == id_search:
                current.next = current.next.next
                return True
            current = current.next
        return False

    def update(self, id_barang, nama_barang=None, kategori=None, stok=None, harga=None, supplier=None):
        """
        Mengubah data node barang berdasarkan ID_Barang.
        """
        node = self.find(id_barang)
        if not node:
            return False

        if nama_barang is not None:
            node.nama_barang = str(nama_barang)
        if kategori is not None:
            node.kategori = str(kategori)
        if stok is not None:
            node.stok = int(stok)
        if harga is not None:
            node.harga = float(harga)
        if supplier is not None:
            node.supplier = str(supplier)
        return True

    def to_list(self):
        """
        Mengonversi Linked List menjadi standard Python list of dictionaries.
        Sangat berguna untuk proses searching, sorting, dan penampilan di GUI.
        """
        items_list = []
        current = self.head
        while current:
            items_list.append(current.to_dict())
            current = current.next
        return items_list

    def clear(self):
        """
        Mengosongkan Linked List.
        """
        self.head = None
