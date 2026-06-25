import datetime
import tkinter as tk
from tkinter import ttk, messagebox
import customtkinter as ctk

from database import DatabaseController
from searching import linear_search, binary_search
from sorting import bubble_sort, quick_sort

# Set up CustomTkinter appearance and default theme
ctk.set_appearance_mode("Dark")  # Options: "System", "Dark", "Light"
ctk.set_default_color_theme("blue")  # Themes: "blue", "green", "dark-blue"

class WarehouseApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        # Inisialisasi Database Controller
        self.db = DatabaseController()

        # Konfigurasi Window Utama
        self.title("Sistem Manajemen Gudang Enterprise - UAS Struktur Data")
        self.geometry("1220x760")
        self.minsize(1120, 720)
        
        # Center window di layar
        self.center_window()

        # Konfigurasi Skema Warna Premium Modern (Deep Space & Slate Theme)
        # Format: (Light Mode, Dark Mode)
        self.bg_color = ("#f1f5f9", "#0b0f19")        # Slate 100 / Deep Navy 950
        self.card_color = ("#ffffff", "#151b2c")      # White / Slate-Navy 900
        self.border_color = ("#e2e8f0", "#1f293d")    # Slate 200 / Slate-Navy 800
        self.text_primary = ("#0f172a", "#f8fafc")    # Slate 900 / Slate 50
        self.text_secondary = ("#64748b", "#94a3b8")  # Slate 500 / Slate 400
        self.accent_color = ("#3b82f6", "#3b82f6")    # Indigo-Blue Accent

        self.configure(fg_color=self.bg_color)

        # Kapasitas maksimal gudang untuk indikator kapasitas dashboard
        self.max_gudang_capacity = 600

        # Simpan riwayat transaksi sesi ini untuk Dashboard (Barang Masuk / Keluar)
        self.transactions = []

        # Setup Layout Grid (1 row, 2 columns: Sidebar & Main Content)
        self.grid_rowconfigure(0, weight=1)
        self.grid_columnconfigure(1, weight=1)

        # Variabel Penanda Frame Aktif
        self.active_frame = None
        self.active_button = None

        # Build Sidebar & Pages
        self.create_sidebar()
        self.show_page("Dashboard")

    def center_window(self):
        self.update_idletasks()
        width = self.winfo_width()
        height = self.winfo_height()
        x = (self.winfo_screenwidth() // 2) - (width // 2)
        y = (self.winfo_screenheight() // 2) - (height // 2)
        self.geometry(f"+{x}+{y}")

    # =========================================================================
    # SIDEBAR
    # =========================================================================
    def create_sidebar(self):
        # Frame Sidebar dengan Border Tipis Modern
        self.sidebar_frame = ctk.CTkFrame(
            self, 
            width=240, 
            corner_radius=0,
            fg_color=self.card_color,
            border_width=1,
            border_color=self.border_color
        )
        self.sidebar_frame.grid(row=0, column=0, sticky="nsew")
        self.sidebar_frame.grid_rowconfigure(9, weight=1)  # Spacer di bawah menu

        # Logo / Judul Aplikasi
        self.logo_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="📦 GUDANGKU", 
            font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"),
            text_color=self.text_primary
        )
        self.logo_label.grid(row=0, column=0, padx=20, pady=(25, 3))
        
        self.subtitle_label = ctk.CTkLabel(
            self.sidebar_frame, 
            text="Warehouse Dashboard v1.2", 
            font=ctk.CTkFont(family="Segoe UI", size=12, slant="italic"),
            text_color=self.text_secondary
        )
        self.subtitle_label.grid(row=1, column=0, padx=20, pady=(0, 25))

        # Menu Buttons Dictionary untuk memudahkan manipulasi active state
        self.menu_buttons = {}
        
        menu_items = [
            ("Dashboard", "📊  Dashboard"),
            ("Data Barang", "📦  Data Barang"),
            ("Barang Masuk", "📥  Barang Masuk"),
            ("Barang Keluar", "📤  Barang Keluar"),
            ("Searching", "🔍  Pencarian"),
            ("Sorting", "🔀  Pengurutan"),
            ("Laporan", "📋  Laporan Gudang"),
        ]

        row_idx = 2
        for key, text in menu_items:
            btn = ctk.CTkButton(
                self.sidebar_frame,
                text=text,
                anchor="w",
                font=ctk.CTkFont(family="Segoe UI", size=14, weight="normal"),
                height=42,
                corner_radius=8,
                fg_color="transparent",
                text_color=self.text_secondary,
                hover_color=("#f1f5f9", "#1e293d"),
                command=lambda k=key: self.show_page(k)
            )
            btn.grid(row=row_idx, column=0, padx=15, pady=4, sticky="ew")
            self.menu_buttons[key] = btn
            row_idx += 1

        # Indikator Operator di Sidebar (Bottom Card)
        self.op_card = ctk.CTkFrame(
            self.sidebar_frame,
            corner_radius=10,
            fg_color=self.bg_color,
            border_width=1,
            border_color=self.border_color
        )
        self.op_card.grid(row=10, column=0, padx=15, pady=(15, 5), sticky="ew")
        
        op_dot = ctk.CTkLabel(self.op_card, text="🟢", font=ctk.CTkFont(size=10))
        op_dot.grid(row=0, column=0, padx=(12, 5), pady=8)
        
        op_text = ctk.CTkLabel(
            self.op_card, 
            text="SYSTEM ONLINE", 
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            text_color="#10b981"
        )
        op_text.grid(row=0, column=1, padx=(0, 10), pady=8, sticky="w")
        
        op_role = ctk.CTkLabel(
            self.op_card,
            text="Operator: Admin Gudang",
            font=ctk.CTkFont(family="Segoe UI", size=10),
            text_color=self.text_secondary
        )
        op_role.grid(row=1, column=0, columnspan=2, padx=12, pady=(0, 8), sticky="w")

        # Tombol Keluar (ditempatkan terpisah)
        self.exit_button = ctk.CTkButton(
            self.sidebar_frame,
            text="❌  Keluar Aplikasi",
            anchor="w",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            height=42,
            corner_radius=8,
            fg_color="#ef4444",
            hover_color="#dc2626",
            text_color="white",
            command=self.confirm_exit
        )
        self.exit_button.grid(row=11, column=0, padx=15, pady=10, sticky="ew")

        # Switch Mode Gelap / Terang
        self.appearance_switch = ctk.CTkSwitch(
            self.sidebar_frame, 
            text="Mode Gelap", 
            command=self.toggle_appearance_mode,
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.text_secondary
        )
        self.appearance_switch.grid(row=12, column=0, padx=20, pady=(5, 20), sticky="s")
        self.appearance_switch.select()

    def toggle_appearance_mode(self):
        if self.appearance_switch.get() == 1:
            ctk.set_appearance_mode("Dark")
        else:
            ctk.set_appearance_mode("Light")
        
        # Beri jeda sebentar lalu update styling Treeview agar sinkron
        self.after(50, self.update_treeview_styles)

    def confirm_exit(self):
        answer = messagebox.askyesno("Konfirmasi Keluar", "Apakah Anda yakin ingin keluar dari aplikasi?")
        if answer:
            self.destroy()

    # =========================================================================
    # FRAME SWITCHER LOGIC
    # =========================================================================
    def show_page(self, page_name):
        # 1. Bersihkan frame aktif sebelumnya
        if self.active_frame is not None:
            self.active_frame.destroy()

        # 2. Reset status tombol sidebar sebelumnya
        if self.active_button is not None:
            self.active_button.configure(fg_color="transparent", text_color=self.text_secondary)

        # 3. Highlight tombol sidebar aktif yang baru
        if page_name in self.menu_buttons:
            self.active_button = self.menu_buttons[page_name]
            self.active_button.configure(fg_color=self.accent_color, text_color="white")

        # 4. Buat Container Utama baru untuk halaman terpilih
        self.active_frame = ctk.CTkFrame(self, corner_radius=0, fg_color="transparent")
        self.active_frame.grid(row=0, column=1, sticky="nsew", padx=25, pady=25)

        # 5. Render halaman spesifik
        if page_name == "Dashboard":
            self.render_dashboard_page()
        elif page_name == "Data Barang":
            self.render_data_barang_page()
        elif page_name == "Barang Masuk":
            self.render_barang_masuk_page()
        elif page_name == "Barang Keluar":
            self.render_barang_keluar_page()
        elif page_name == "Searching":
            self.render_searching_page()
        elif page_name == "Sorting":
            self.render_sorting_page()
        elif page_name == "Laporan":
            self.render_laporan_page()

    # =========================================================================
    # VIEW: DASHBOARD PAGE
    # =========================================================================
    def render_dashboard_page(self):
        stats = self.db.get_statistics()
        
        bm_sesi = sum(tx["qty"] for tx in self.transactions if tx["type"] == "Barang Masuk")
        bk_sesi = sum(tx["qty"] for tx in self.transactions if tx["type"] == "Barang Keluar")

        # Header Halaman dengan Salam Admin
        header_frame = ctk.CTkFrame(self.active_frame, fg_color="transparent")
        header_frame.grid(row=0, column=0, columnspan=4, sticky="ew", pady=(0, 20))
        
        lbl_welcome = ctk.CTkLabel(
            header_frame, 
            text="Selamat Datang, Admin! 👋", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=self.text_primary
        )
        lbl_welcome.pack(anchor="w")

        lbl_desc = ctk.CTkLabel(
            header_frame, 
            text="Ringkasan kontrol aktivitas inventaris dan kapasitas gudang utama terpusat.", 
            font=ctk.CTkFont(family="Segoe UI", size=13),
            text_color=self.text_secondary
        )
        lbl_desc.pack(anchor="w", pady=(2, 0))

        # Cards Statistik Utama (Dengan Circular Badge Emojis yang Sangat Modern)
        card_data = [
            ("Total Varian Barang", f"{stats['total_jenis']} Jenis", ("#dbeafe", "#1e3a8a"), "#3b82f6", "📊"),  # Blue Badge
            ("Total Jumlah Stok", f"{stats['total_stok']} Unit", ("#d1fae5", "#064e3b"), "#10b981", "📦"),   # Emerald Badge
            ("Stok Masuk (Sesi)", f"+{bm_sesi} Unit", ("#fef3c7", "#78350f"), "#f59e0b", "📥"),               # Amber Badge
            ("Stok Keluar (Sesi)", f"-{bk_sesi} Unit", ("#ffe4e6", "#4c0519"), "#ef4444", "📤")               # Rose Badge
        ]

        self.active_frame.grid_columnconfigure((0, 1, 2, 3), weight=1)

        for i, (title, value, badge_bg, theme_col, emoji) in enumerate(card_data):
            card = ctk.CTkFrame(
                self.active_frame, 
                height=110, 
                corner_radius=16,
                fg_color=self.card_color,
                border_width=1,
                border_color=self.border_color
            )
            card.grid(row=1, column=i, padx=6, pady=5, sticky="nsew")
            card.grid_propagate(False)
            
            # Left Column inside Card: Circular Emoji Badge
            badge = ctk.CTkLabel(
                card, 
                text=emoji, 
                width=46, 
                height=46, 
                corner_radius=23, 
                fg_color=badge_bg, 
                text_color=theme_col, 
                font=ctk.CTkFont(size=20)
            )
            badge.pack(side="left", padx=(15, 10), pady=15)
            
            # Right Column inside Card: Text info
            text_box = ctk.CTkFrame(card, fg_color="transparent")
            text_box.pack(side="left", fill="both", expand=True, padx=(5, 15), pady=18)
            
            title_lbl = ctk.CTkLabel(
                text_box, 
                text=title, 
                font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), 
                text_color=self.text_secondary
            )
            title_lbl.pack(anchor="w")
            
            val_lbl = ctk.CTkLabel(
                text_box, 
                text=value, 
                font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
                text_color=self.text_primary
            )
            val_lbl.pack(anchor="w", pady=(2, 0))

        # Row 2: Grid Layout untuk Progress Kapasitas & Recent Activity
        self.active_frame.grid_rowconfigure(2, weight=1)

        # Left Column Frame: Kapasitas Gudang & Riwayat Aktivitas
        left_column = ctk.CTkFrame(self.active_frame, fg_color="transparent")
        left_column.grid(row=2, column=0, columnspan=2, padx=6, pady=(20, 0), sticky="nsew")
        left_column.grid_rowconfigure(1, weight=1)
        left_column.grid_columnconfigure(0, weight=1)

        # 1. Card Kapasitas Gudang (Visual Meter)
        cap_card = ctk.CTkFrame(
            left_column, 
            corner_radius=16, 
            fg_color=self.card_color,
            border_width=1,
            border_color=self.border_color
        )
        cap_card.grid(row=0, column=0, sticky="ew", pady=(0, 15))
        
        cap_header = ctk.CTkFrame(cap_card, fg_color="transparent")
        cap_header.pack(fill="x", padx=20, pady=(15, 5))
        
        cap_title = ctk.CTkLabel(
            cap_header, 
            text="📈 Utilitas Kapasitas Gudang", 
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=self.text_primary
        )
        cap_title.pack(side="left")

        # Kalkulasi persentase utilitas gudang
        total_stok = stats['total_stok']
        percent_used = min(total_stok / self.max_gudang_capacity, 1.0)
        percent_str = f"{int(percent_used * 100)}%"
        
        # Warnai Badge Status Kapasitas
        status_text = "Aman 🟢"
        status_bg = ("#d1fae5", "#064e3b")
        status_fg = "#10b981"
        if percent_used > 0.85:
            status_text = "Penuh 🔴"
            status_bg = ("#ffe4e6", "#4c0519")
            status_fg = "#ef4444"
        elif percent_used > 0.60:
            status_text = "Peringatan 🟡"
            status_bg = ("#fef3c7", "#78350f")
            status_fg = "#f59e0b"

        cap_badge = ctk.CTkLabel(
            cap_header,
            text=status_text,
            font=ctk.CTkFont(family="Segoe UI", size=11, weight="bold"),
            fg_color=status_bg,
            text_color=status_fg,
            corner_radius=10,
            padx=10,
            pady=3
        )
        cap_badge.pack(side="right")

        meter_frame = ctk.CTkFrame(cap_card, fg_color="transparent")
        meter_frame.pack(fill="x", padx=20, pady=(0, 20))

        lbl_meter = ctk.CTkLabel(
            meter_frame, 
            text=f"{total_stok} / {self.max_gudang_capacity} Unit Terisi ({percent_str})",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color=self.text_secondary
        )
        lbl_meter.pack(anchor="w", pady=(0, 8))

        progress_bar = ctk.CTkProgressBar(meter_frame, height=12, corner_radius=6)
        progress_bar.pack(fill="x")
        progress_bar.set(percent_used)
        progress_bar.configure(progress_color=status_fg, fg_color=self.bg_color)

        # 2. Card Aktivitas Terbaru
        act_card = ctk.CTkFrame(
            left_column, 
            corner_radius=16, 
            fg_color=self.card_color,
            border_width=1,
            border_color=self.border_color
        )
        act_card.grid(row=1, column=0, sticky="nsew")
        act_card.grid_rowconfigure(1, weight=1)
        act_card.grid_columnconfigure(0, weight=1)

        act_title = ctk.CTkLabel(
            act_card, 
            text="🔔 Aktivitas Transaksi Sesi Ini", 
            font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
            text_color=self.text_primary
        )
        act_title.pack(anchor="w", padx=20, pady=(15, 8))

        log_scroll = ctk.CTkScrollableFrame(act_card, fg_color="transparent")
        log_scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        if not self.transactions:
            no_act_lbl = ctk.CTkLabel(
                log_scroll, 
                text="Belum ada transaksi di sesi ini.", 
                text_color=self.text_secondary, 
                font=ctk.CTkFont(family="Segoe UI", size=13, slant="italic")
            )
            no_act_lbl.pack(pady=50)
        else:
            for tx in reversed(self.transactions):
                tx_color = "#10b981" if tx["type"] == "Barang Masuk" else "#ef4444"
                arrow = "📥" if tx["type"] == "Barang Masuk" else "📤"
                
                item_details = self.db.get_item(tx["id"])
                nama_item = item_details["Nama_Barang"] if item_details else tx["id"]
                
                row_str = f"[{tx['time']}]  {arrow}  {tx['type']}: {nama_item} (ID: {tx['id']}) sejumlah {tx['qty']} unit"
                
                log_row = ctk.CTkFrame(log_scroll, height=40, corner_radius=10, fg_color=self.bg_color)
                log_row.pack(fill="x", pady=4, padx=2)
                
                indicator = ctk.CTkFrame(log_row, width=5, fg_color=tx_color, corner_radius=0)
                indicator.pack(side="left", fill="y")
                
                lbl = ctk.CTkLabel(log_row, text=row_str, font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=self.text_primary)
                lbl.pack(side="left", padx=12, fill="both")

        # Right Column Frame: Academic / Project Info Box
        info_frame = ctk.CTkFrame(
            self.active_frame, 
            corner_radius=16,
            fg_color=self.card_color,
            border_width=1,
            border_color=self.border_color
        )
        info_frame.grid(row=2, column=2, columnspan=2, padx=6, pady=(20, 0), sticky="nsew")
        
        info_title = ctk.CTkLabel(
            info_frame, 
            text="🎓 Informasi Proyek UAS", 
            font=ctk.CTkFont(family="Segoe UI", size=16, weight="bold"),
            text_color=self.text_primary
        )
        info_title.pack(anchor="w", padx=20, pady=(15, 10))
        
        desc_text = (
            "Aplikasi ini didesain khusus untuk memenuhi standar nilai akademis UAS Struktur Data.\n\n"
            "Struktur Data yang Diimplementasikan:\n"
            "• Linked List (linkedlist.py): Representasi memori sekuensial dinamis untuk data barang.\n"
            "• Hash Map / Dictionary: Memetakan ID_Barang langsung ke node memori untuk lookup instan O(1).\n\n"
            "Algoritma yang Diimplementasikan:\n"
            "• Searching: Linear Search & Binary Search.\n"
            "• Sorting: Quick Sort & Bubble Sort.\n\n"
            "Database:\n"
            "• data_barang.csv: Sinkronisasi penyimpanan persisten otomatis."
        )
        
        desc_lbl = ctk.CTkLabel(
            info_frame, 
            text=desc_text, 
            justify="left", 
            anchor="nw", 
            wraplength=420, 
            font=ctk.CTkFont(family="Segoe UI", size=12),
            text_color=self.text_primary
        )
        desc_lbl.pack(fill="both", expand=True, padx=20, pady=10)

    # =========================================================================
    # VIEW: DATA BARANG PAGE (CRUD)
    # =========================================================================
    def render_data_barang_page(self):
        # Header Halaman
        header_lbl = ctk.CTkLabel(
            self.active_frame, 
            text="Manajemen Data Barang", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=self.text_primary
        )
        header_lbl.grid(row=0, column=0, sticky="w", pady=(0, 10))

        # Frame Tabel (Treeview)
        table_frame = ctk.CTkFrame(
            self.active_frame,
            fg_color=self.card_color,
            border_width=1,
            border_color=self.border_color,
            corner_radius=16
        )
        table_frame.grid(row=1, column=0, columnspan=2, sticky="nsew", pady=10)
        
        self.active_frame.grid_rowconfigure(1, weight=1)
        self.active_frame.grid_columnconfigure(0, weight=1)

        # Scrollbar untuk Treeview
        tree_scroll_y = ttk.Scrollbar(table_frame, orient="vertical")
        tree_scroll_y.pack(side="right", fill="y", pady=12, padx=(0, 4))
        
        tree_scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x", padx=12, pady=(0, 4))

        # Treeview Table
        cols = ("ID Barang", "Nama Barang", "Kategori", "Stok", "Harga", "Supplier")
        self.tree = ttk.Treeview(
            table_frame, 
            columns=cols, 
            show="headings", 
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set
        )
        self.tree.pack(fill="both", expand=True, padx=12, pady=12)
        
        tree_scroll_y.config(command=self.tree.yview)
        tree_scroll_x.config(command=self.tree.xview)

        # Konfigurasi Header Kolom
        for col in cols:
            self.tree.heading(col, text=col)

        # Format Kolom
        self.tree.column("ID Barang", anchor="center", width=95)
        self.tree.column("Nama Barang", anchor="w", width=230)
        self.tree.column("Kategori", anchor="w", width=150)
        self.tree.column("Stok", anchor="center", width=85)
        self.tree.column("Harga", anchor="e", width=140)
        self.tree.column("Supplier", anchor="w", width=160)

        # Action Buttons Frame
        btn_frame = ctk.CTkFrame(self.active_frame, fg_color="transparent")
        btn_frame.grid(row=2, column=0, columnspan=2, sticky="ew", pady=(10, 0))

        buttons = [
            ("➕ Tambah Barang", self.open_add_dialog, "#3b82f6", "#2563eb"),
            ("✏️ Edit Barang", self.open_edit_dialog, "#f59e0b", "#d97706"),
            ("🗑️ Hapus Barang", self.delete_selected_item, "#ef4444", "#dc2626"),
            ("🔍 Cari Halaman", lambda: self.show_page("Searching"), "#64748b", "#475569"),
            ("🔄 Refresh Tabel", self.refresh_table, "#64748b", "#475569")
        ]

        for i, (text, cmd, color, hover) in enumerate(buttons):
            btn = ctk.CTkButton(
                btn_frame, 
                text=text, 
                command=cmd, 
                fg_color=color, 
                hover_color=hover,
                font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
                height=38,
                corner_radius=8
            )
            btn.pack(side="left", padx=4)

        # Terapkan Tema Warna di Treeview
        self.update_treeview_styles()
        
        # Load Data ke Tabel
        self.refresh_table()

    def update_treeview_styles(self):
        if not hasattr(self, 'tree') or self.tree is None:
            return

        is_dark = ctk.get_appearance_mode() == "Dark"
        bg_color = "#151b2c" if is_dark else "#ffffff"
        fg_color = "#f8fafc" if is_dark else "#0f172a"
        field_bg = "#151b2c" if is_dark else "#ffffff"
        heading_bg = "#0b0f19" if is_dark else "#e2e8f0"
        heading_fg = "#94a3b8" if is_dark else "#475569"
        selected_bg = "#3b82f6"

        style = ttk.Style()
        style.theme_use("default")
        
        # Borderless design
        style.layout("Treeview", [('Treeview.treearea', {'sticky': 'nswe'})])
        
        style.configure("Treeview", 
                        background=bg_color, 
                        foreground=fg_color, 
                        rowheight=35, 
                        fieldbackground=field_bg,
                        font=("Segoe UI", 11))
        
        style.map('Treeview', background=[('selected', selected_bg)], foreground=[('selected', 'white')])
        
        style.configure("Treeview.Heading", 
                        background=heading_bg, 
                        foreground=heading_fg, 
                        relief="flat",
                        font=("Segoe UI", 11, "bold"))
        
        style.map("Treeview.Heading",
                  background=[('active', selected_bg)],
                  foreground=[('active', 'white')])

        # Striping
        if is_dark:
            self.tree.tag_configure('evenrow', background="#151b2c", foreground="#f8fafc")
            self.tree.tag_configure('oddrow', background="#0b0f19", foreground="#f8fafc")
        else:
            self.tree.tag_configure('evenrow', background="#ffffff", foreground="#0f172a")
            self.tree.tag_configure('oddrow', background="#f8fafc", foreground="#0f172a")

    def refresh_table(self):
        for row in self.tree.get_children():
            self.tree.delete(row)

        items = self.db.get_all_items()
        
        for idx, item in enumerate(items):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.tree.insert("", "end", values=(
                item["ID_Barang"],
                item["Nama_Barang"],
                item["Kategori"],
                item["Stok"],
                f"{int(item['Harga']):,}",
                item["Supplier"]
            ), tags=(tag,))

    # =========================================================================
    # DIALOGS (CREATE & UPDATE POPUPS)
    # =========================================================================
    def open_add_dialog(self):
        self.dialog = ctk.CTkToplevel(self)
        self.dialog.title("Tambah Data Barang")
        self.dialog.geometry("420x470")
        self.dialog.resizable(False, False)
        self.dialog.configure(fg_color=self.bg_color)
        self.dialog.transient(self)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (420 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (470 // 2)
        self.dialog.geometry(f"+{x}+{y}")

        # Label Judul
        lbl_title = ctk.CTkLabel(
            self.dialog, 
            text="➕ Tambah Barang Baru", 
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=self.text_primary
        )
        lbl_title.pack(pady=(20, 15))

        # Dialog frame
        d_frame = ctk.CTkFrame(
            self.dialog,
            fg_color=self.card_color,
            border_width=1,
            border_color=self.border_color,
            corner_radius=14
        )
        d_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Form fields
        self.add_entries = {}
        fields = [
            ("ID Barang", "Contoh: 006"),
            ("Nama Barang", "Contoh: Keyboard"),
            ("Kategori", "Contoh: Elektronik"),
            ("Stok", "Contoh: 15"),
            ("Harga", "Contoh: 150000"),
            ("Supplier", "Contoh: Asus")
        ]

        for field, placeholder in fields:
            frame = ctk.CTkFrame(d_frame, fg_color="transparent")
            frame.pack(fill="x", padx=20, pady=6)
            
            lbl = ctk.CTkLabel(frame, text=field, width=110, anchor="w", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=self.text_primary)
            lbl.pack(side="left")
            
            entry = ctk.CTkEntry(frame, placeholder_text=placeholder, width=190, corner_radius=8, border_width=2, border_color=self.border_color, fg_color=self.bg_color)
            entry.pack(side="right", fill="x", expand=True)
            self.add_entries[field] = entry

        # Action Buttons
        btn_frame = ctk.CTkFrame(d_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(15, 15))

        btn_cancel = ctk.CTkButton(btn_frame, text="Batal", fg_color="#64748b", hover_color="#475569", command=self.dialog.destroy, corner_radius=8)
        btn_cancel.pack(side="left", padx=(0, 5), expand=True, fill="x")

        btn_save = ctk.CTkButton(btn_frame, text="Simpan", fg_color="#3b82f6", hover_color="#2563eb", command=self.save_new_item, corner_radius=8)
        btn_save.pack(side="right", padx=(5, 0), expand=True, fill="x")

    def save_new_item(self):
        try:
            id_b = self.add_entries["ID Barang"].get().strip()
            nama = self.add_entries["Nama Barang"].get().strip()
            kat = self.add_entries["Kategori"].get().strip()
            stok_str = self.add_entries["Stok"].get().strip()
            harga_str = self.add_entries["Harga"].get().strip()
            sup = self.add_entries["Supplier"].get().strip()

            if not (id_b and nama and kat and stok_str and harga_str and sup):
                messagebox.showerror("Error Validasi", "Semua kolom input harus diisi!", parent=self.dialog)
                return

            try:
                stok = int(stok_str)
                if stok < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error Validasi", "Stok harus berupa bilangan bulat positif!", parent=self.dialog)
                return

            try:
                harga = float(harga_str)
                if harga < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error Validasi", "Harga harus berupa angka positif!", parent=self.dialog)
                return

            self.db.add_item(id_b, nama, kat, stok, harga, sup)
            
            now = datetime.datetime.now().strftime("%H:%M:%S")
            self.transactions.append({
                "type": "Barang Masuk",
                "id": id_b,
                "qty": stok,
                "time": now
            })

            messagebox.showinfo("Sukses", f"Barang '{nama}' berhasil ditambahkan ke database gudang!", parent=self.dialog)
            self.dialog.destroy()
            self.refresh_table()

        except ValueError as err:
            messagebox.showerror("Error Database", str(err), parent=self.dialog)

    def open_edit_dialog(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Pilih Data", "Silakan pilih baris data barang yang ingin diedit!")
            return

        values = self.tree.item(selected[0], "values")
        id_barang = values[0]
        
        item = self.db.get_item(id_barang)
        if not item:
            messagebox.showerror("Error", "Data barang tidak ditemukan di memori!")
            return

        self.dialog = ctk.CTkToplevel(self)
        self.dialog.title("Edit Data Barang")
        self.dialog.geometry("420x470")
        self.dialog.resizable(False, False)
        self.dialog.configure(fg_color=self.bg_color)
        self.dialog.transient(self)
        self.dialog.grab_set()
        
        # Center dialog
        self.dialog.update_idletasks()
        x = self.winfo_x() + (self.winfo_width() // 2) - (420 // 2)
        y = self.winfo_y() + (self.winfo_height() // 2) - (470 // 2)
        self.dialog.geometry(f"+{x}+{y}")

        # Label Judul
        lbl_title = ctk.CTkLabel(
            self.dialog, 
            text="✏️ Edit Data Barang", 
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=self.text_primary
        )
        lbl_title.pack(pady=(20, 15))

        # Dialog frame
        d_frame = ctk.CTkFrame(
            self.dialog,
            fg_color=self.card_color,
            border_width=1,
            border_color=self.border_color,
            corner_radius=14
        )
        d_frame.pack(fill="both", expand=True, padx=20, pady=(0, 20))

        # Form fields
        self.edit_entries = {}
        fields = [
            ("ID Barang (Kunci)", item["ID_Barang"]),
            ("Nama Barang", item["Nama_Barang"]),
            ("Kategori", item["Kategori"]),
            ("Stok", str(item["Stok"])),
            ("Harga", str(int(item["Harga"]))),
            ("Supplier", item["Supplier"])
        ]

        for field, current_val in fields:
            frame = ctk.CTkFrame(d_frame, fg_color="transparent")
            frame.pack(fill="x", padx=20, pady=6)
            
            lbl = ctk.CTkLabel(frame, text=field, width=120, anchor="w", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=self.text_primary)
            lbl.pack(side="left")
            
            if field.startswith("ID Barang"):
                entry = ctk.CTkEntry(frame, placeholder_text=current_val, width=180, state="disabled", corner_radius=8, border_width=2, border_color=self.border_color, fg_color=self.bg_color)
            else:
                entry = ctk.CTkEntry(frame, width=180, corner_radius=8, border_width=2, border_color=self.border_color, fg_color=self.bg_color)
                entry.insert(0, current_val)
            
            entry.pack(side="right", fill="x", expand=True)
            self.edit_entries[field] = entry

        self.editing_id = id_barang

        # Action Buttons
        btn_frame = ctk.CTkFrame(d_frame, fg_color="transparent")
        btn_frame.pack(fill="x", padx=20, pady=(15, 15))

        btn_cancel = ctk.CTkButton(btn_frame, text="Batal", fg_color="#64748b", hover_color="#475569", command=self.dialog.destroy, corner_radius=8)
        btn_cancel.pack(side="left", padx=(0, 5), expand=True, fill="x")

        btn_save = ctk.CTkButton(btn_frame, text="Simpan", fg_color="#f59e0b", hover_color="#d97706", command=self.save_edited_item, corner_radius=8)
        btn_save.pack(side="right", padx=(5, 0), expand=True, fill="x")

    def save_edited_item(self):
        try:
            nama = self.edit_entries["Nama Barang"].get().strip()
            kat = self.edit_entries["Kategori"].get().strip()
            stok_str = self.edit_entries["Stok"].get().strip()
            harga_str = self.edit_entries["Harga"].get().strip()
            sup = self.edit_entries["Supplier"].get().strip()

            if not (nama and kat and stok_str and harga_str and sup):
                messagebox.showerror("Error Validasi", "Semua kolom input harus diisi!", parent=self.dialog)
                return

            try:
                stok = int(stok_str)
                if stok < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error Validasi", "Stok harus berupa bilangan bulat positif!", parent=self.dialog)
                return

            try:
                harga = float(harga_str)
                if harga < 0:
                    raise ValueError
            except ValueError:
                messagebox.showerror("Error Validasi", "Harga harus berupa angka positif!", parent=self.dialog)
                return

            self.db.update_item(self.editing_id, nama_barang=nama, kategori=kat, stok=stok, harga=harga, supplier=sup)

            messagebox.showinfo("Sukses", f"Data Barang ID {self.editing_id} berhasil diupdate!", parent=self.dialog)
            self.dialog.destroy()
            self.refresh_table()

        except Exception as err:
            messagebox.showerror("Error Database", str(err), parent=self.dialog)

    def delete_selected_item(self):
        selected = self.tree.selection()
        if not selected:
            messagebox.showwarning("Pilih Data", "Silakan pilih baris data barang yang ingin dihapus!")
            return

        values = self.tree.item(selected[0], "values")
        id_barang = values[0]
        nama_barang = values[1]

        answer = messagebox.askyesno(
            "Konfirmasi Hapus", 
            f"Apakah Anda yakin ingin menghapus barang '{nama_barang}' (ID: {id_barang})?"
        )
        if answer:
            try:
                self.db.delete_item(id_barang)
                messagebox.showinfo("Sukses", f"Barang '{nama_barang}' berhasil dihapus.")
                self.refresh_table()
            except Exception as err:
                messagebox.showerror("Error Database", str(err))

    # =========================================================================
    # VIEW: BARANG MASUK PAGE (TAMBAH STOK CONSOLE)
    # =========================================================================
    def render_barang_masuk_page(self):
        header_lbl = ctk.CTkLabel(
            self.active_frame, 
            text="Proses Barang Masuk", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=self.text_primary
        )
        header_lbl.pack(anchor="w", pady=(0, 20))

        # Centered Transaction Console Card
        card = ctk.CTkFrame(
            self.active_frame, 
            corner_radius=16,
            fg_color=self.card_color,
            border_width=1,
            border_color=self.border_color
        )
        card.pack(pady=20, padx=100, fill="both", expand=True)
        card.pack_propagate(False)

        # Header Strip Hijau Zamrud ala Console
        strip = ctk.CTkFrame(card, height=45, fg_color="#10b981", corner_radius=0)
        strip.pack(side="top", fill="x")
        strip.pack_propagate(False)
        
        lbl_strip = ctk.CTkLabel(
            strip, 
            text="📥  SISTEM TRANSMISI BARANG MASUK (TAMBAH STOK)", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="white"
        )
        lbl_strip.pack(side="left", padx=20)

        inner_frame = ctk.CTkFrame(card, fg_color="transparent")
        inner_frame.pack(pady=30, padx=50, fill="both", expand=True)

        # Input ID Barang
        ctk.CTkLabel(
            inner_frame, 
            text="Pilih Barang (ID - Nama):", 
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.text_primary
        ).pack(anchor="w", pady=(0, 5))
        
        items = self.db.get_all_items()
        item_options = [f"{item['ID_Barang']} - {item['Nama_Barang']}" for item in items]
        
        if not item_options:
            item_options = ["Belum ada data barang di database"]
            
        self.bm_combobox = ctk.CTkComboBox(inner_frame, values=item_options, width=400, height=38, corner_radius=8, border_width=2, border_color=self.border_color, fg_color=self.bg_color)
        self.bm_combobox.pack(pady=(0, 20))

        # Input Jumlah Stok Masuk
        ctk.CTkLabel(
            inner_frame, 
            text="Jumlah Barang Masuk:", 
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.text_primary
        ).pack(anchor="w", pady=(0, 5))
        
        self.bm_qty_entry = ctk.CTkEntry(
            inner_frame, 
            placeholder_text="Masukkan jumlah (Contoh: 10)", 
            width=400, 
            height=38, 
            corner_radius=8,
            border_width=2,
            border_color=self.border_color,
            fg_color=self.bg_color
        )
        self.bm_qty_entry.pack(pady=(0, 25))

        # Button
        btn_save = ctk.CTkButton(
            inner_frame, 
            text="📥  EKSEKUSI PENAMBAHAN STOK", 
            fg_color="#10b981", 
            hover_color="#059669",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            height=42,
            corner_radius=8,
            command=self.process_barang_masuk
        )
        btn_save.pack(fill="x")

    def process_barang_masuk(self):
        selection = self.bm_combobox.get()
        qty_str = self.bm_qty_entry.get().strip()

        if selection.startswith("Belum ada") or not selection:
            messagebox.showerror("Error", "Data barang kosong! Silakan tambah data barang terlebih dahulu di halaman Data Barang.")
            return

        id_barang = selection.split(" - ")[0].strip()

        try:
            qty = int(qty_str)
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error Validasi", "Jumlah barang masuk harus berupa bilangan bulat positif!")
            return

        try:
            self.db.add_stock(id_barang, qty)
            
            now = datetime.datetime.now().strftime("%H:%M:%S")
            self.transactions.append({
                "type": "Barang Masuk",
                "id": id_barang,
                "qty": qty,
                "time": now
            })

            item = self.db.get_item(id_barang)
            messagebox.showinfo("Sukses", f"Stok berhasil ditambahkan!\n\nBarang: {item['Nama_Barang']}\nTambahan: +{qty} unit\nTotal Stok Baru: {item['Stok']} unit.")
            
            self.bm_qty_entry.delete(0, "end")
            self.show_page("Barang Masuk")

        except Exception as err:
            messagebox.showerror("Error Database", str(err))

    # =========================================================================
    # VIEW: BARANG KELUAR PAGE (KURANGI STOK CONSOLE)
    # =========================================================================
    def render_barang_keluar_page(self):
        # Header Halaman
        header_lbl = ctk.CTkLabel(
            self.active_frame, 
            text="Proses Barang Keluar", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=self.text_primary
        )
        header_lbl.pack(anchor="w", pady=(0, 20))

        # Centered Transaction Console Card
        card = ctk.CTkFrame(
            self.active_frame, 
            corner_radius=16,
            fg_color=self.card_color,
            border_width=1,
            border_color=self.border_color
        )
        card.pack(pady=20, padx=100, fill="both", expand=True)
        card.pack_propagate(False)

        # Header Strip Merah Mawar ala Console
        strip = ctk.CTkFrame(card, height=45, fg_color="#ef4444", corner_radius=0)
        strip.pack(side="top", fill="x")
        strip.pack_propagate(False)
        
        lbl_strip = ctk.CTkLabel(
            strip, 
            text="📤  SISTEM TRANSMISI BARANG KELUAR (PENGURANGAN STOK)", 
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            text_color="white"
        )
        lbl_strip.pack(side="left", padx=20)

        inner_frame = ctk.CTkFrame(card, fg_color="transparent")
        inner_frame.pack(pady=30, padx=50, fill="both", expand=True)

        # Input ID Barang
        ctk.CTkLabel(
            inner_frame, 
            text="Pilih Barang (ID - Nama - Stok Aktif):", 
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.text_primary
        ).pack(anchor="w", pady=(0, 5))
        
        items = self.db.get_all_items()
        item_options = [f"{item['ID_Barang']} - {item['Nama_Barang']} (Stok: {item['Stok']})" for item in items]
        
        if not item_options:
            item_options = ["Belum ada data barang di database"]
            
        self.bk_combobox = ctk.CTkComboBox(inner_frame, values=item_options, width=400, height=38, corner_radius=8, border_width=2, border_color=self.border_color, fg_color=self.bg_color)
        self.bk_combobox.pack(pady=(0, 20))

        # Input Jumlah Stok Keluar
        ctk.CTkLabel(
            inner_frame, 
            text="Jumlah Barang Keluar:", 
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            text_color=self.text_primary
        ).pack(anchor="w", pady=(0, 5))
        
        self.bk_qty_entry = ctk.CTkEntry(
            inner_frame, 
            placeholder_text="Masukkan jumlah (Contoh: 5)", 
            width=400, 
            height=38, 
            corner_radius=8,
            border_width=2,
            border_color=self.border_color,
            fg_color=self.bg_color
        )
        self.bk_qty_entry.pack(pady=(0, 25))

        # Button
        btn_save = ctk.CTkButton(
            inner_frame, 
            text="📤  EKSEKUSI PENGURANGAN STOK", 
            fg_color="#ef4444", 
            hover_color="#dc2626",
            font=ctk.CTkFont(family="Segoe UI", size=14, weight="bold"),
            height=42,
            corner_radius=8,
            command=self.process_barang_keluar
        )
        btn_save.pack(fill="x")

    def process_barang_keluar(self):
        selection = self.bk_combobox.get()
        qty_str = self.bk_qty_entry.get().strip()

        if selection.startswith("Belum ada") or not selection:
            messagebox.showerror("Error", "Data barang kosong! Silakan tambah data barang terlebih dahulu di halaman Data Barang.")
            return

        id_barang = selection.split(" - ")[0].strip()

        try:
            qty = int(qty_str)
            if qty <= 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Error Validasi", "Jumlah barang keluar harus berupa bilangan bulat positif!")
            return

        try:
            self.db.reduce_stock(id_barang, qty)
            
            now = datetime.datetime.now().strftime("%H:%M:%S")
            self.transactions.append({
                "type": "Barang Keluar",
                "id": id_barang,
                "qty": qty,
                "time": now
            })

            item = self.db.get_item(id_barang)
            messagebox.showinfo("Sukses", f"Stok berhasil dikurangi!\n\nBarang: {item['Nama_Barang']}\nPengurangan: -{qty} unit\nTotal Stok Baru: {item['Stok']} unit.")
            
            self.bk_qty_entry.delete(0, "end")
            self.show_page("Barang Keluar")

        except Exception as err:
            messagebox.showerror("Peringatan Stok Gudang", str(err))

    # =========================================================================
    # VIEW: SEARCHING PAGE
    # =========================================================================
    def render_searching_page(self):
        # Header Halaman
        header_lbl = ctk.CTkLabel(
            self.active_frame, 
            text="Fitur Pencarian Barang", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=self.text_primary
        )
        header_lbl.grid(row=0, column=0, sticky="w", pady=(0, 15))

        # Panel Filter Pencarian (Card Style)
        search_filter_frame = ctk.CTkFrame(
            self.active_frame,
            fg_color=self.card_color,
            border_width=1,
            border_color=self.border_color,
            corner_radius=14
        )
        search_filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.active_frame.grid_columnconfigure(0, weight=1)

        # Dropdown Kriteria Cari
        ctk.CTkLabel(search_filter_frame, text="Cari Berdasarkan:", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=self.text_primary).pack(side="left", padx=(20, 5), pady=15)
        self.search_field_cb = ctk.CTkComboBox(search_filter_frame, values=["Nama_Barang", "ID_Barang"], width=130, corner_radius=8, border_width=2, border_color=self.border_color, fg_color=self.bg_color)
        self.search_field_cb.pack(side="left", padx=5)

        # Dropdown Algoritma Cari
        ctk.CTkLabel(search_filter_frame, text="Algoritma:", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=self.text_primary).pack(side="left", padx=(15, 5))
        self.search_algo_cb = ctk.CTkComboBox(search_filter_frame, values=["Linear Search", "Binary Search"], width=130, corner_radius=8, border_width=2, border_color=self.border_color, fg_color=self.bg_color)
        self.search_algo_cb.pack(side="left", padx=5)

        # Entry Keyword
        ctk.CTkLabel(search_filter_frame, text="Keyword:", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=self.text_primary).pack(side="left", padx=(15, 5))
        self.search_entry = ctk.CTkEntry(search_filter_frame, placeholder_text="Masukkan kata kunci...", width=180, corner_radius=8, border_width=2, border_color=self.border_color, fg_color=self.bg_color)
        self.search_entry.pack(side="left", padx=5)
        
        self.search_entry.bind("<Return>", lambda event: self.run_search())

        # Buttons Cari & Reset
        btn_search = ctk.CTkButton(search_filter_frame, text="🔍 Cari", width=80, fg_color="#3b82f6", hover_color="#2563eb", font=ctk.CTkFont(family="Segoe UI", weight="bold"), command=self.run_search, corner_radius=8)
        btn_search.pack(side="left", padx=(10, 3))

        btn_reset = ctk.CTkButton(search_filter_frame, text="🔄 Reset", width=80, fg_color="#64748b", hover_color="#475569", font=ctk.CTkFont(family="Segoe UI", weight="bold"), command=self.reset_search, corner_radius=8)
        btn_reset.pack(side="left", padx=3)

        # Panel Hasil Pencarian
        table_frame = ctk.CTkFrame(
            self.active_frame,
            fg_color=self.card_color,
            border_width=1,
            border_color=self.border_color,
            corner_radius=16
        )
        table_frame.grid(row=2, column=0, sticky="nsew")
        self.active_frame.grid_rowconfigure(2, weight=1)

        tree_scroll_y = ttk.Scrollbar(table_frame, orient="vertical")
        tree_scroll_y.pack(side="right", fill="y", pady=12, padx=(0, 4))
        
        tree_scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x", padx=12, pady=(0, 4))

        cols = ("ID Barang", "Nama Barang", "Kategori", "Stok", "Harga", "Supplier")
        self.search_tree = ttk.Treeview(
            table_frame, 
            columns=cols, 
            show="headings", 
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set
        )
        self.search_tree.pack(fill="both", expand=True, padx=12, pady=12)

        tree_scroll_y.config(command=self.search_tree.yview)
        tree_scroll_x.config(command=self.search_tree.xview)

        # Konfigurasi Header
        for col in cols:
            self.search_tree.heading(col, text=col)
        
        self.search_tree.column("ID Barang", anchor="center", width=95)
        self.search_tree.column("Nama Barang", anchor="w", width=230)
        self.search_tree.column("Kategori", anchor="w", width=150)
        self.search_tree.column("Stok", anchor="center", width=85)
        self.search_tree.column("Harga", anchor="e", width=140)
        self.search_tree.column("Supplier", anchor="w", width=160)

        # Style Sync
        self.tree = self.search_tree
        self.update_treeview_styles()
        self.tree = None

        self.reset_search()

    def run_search(self):
        query = self.search_entry.get().strip()
        field = self.search_field_cb.get()
        algo = self.search_algo_cb.get()

        if not query:
            messagebox.showwarning("Peringatan", "Masukkan kata kunci terlebih dahulu untuk mencari!")
            return

        items = self.db.get_all_items()
        
        if algo == "Linear Search":
            results = linear_search(items, query, field=field)
        else:
            results = binary_search(items, query, field=field)

        for row in self.search_tree.get_children():
            self.search_tree.delete(row)

        if not results:
            messagebox.showinfo("Informasi", f"Barang tidak ditemukan untuk pencarian '{query}' menggunakan {algo}.")
            return

        for idx, item in enumerate(results):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.search_tree.insert("", "end", values=(
                item["ID_Barang"],
                item["Nama_Barang"],
                item["Kategori"],
                item["Stok"],
                f"{int(item['Harga']):,}",
                item["Supplier"]
            ), tags=(tag,))

    def reset_search(self):
        self.search_entry.delete(0, "end")
        
        for row in self.search_tree.get_children():
            self.search_tree.delete(row)
            
        items = self.db.get_all_items()
        for idx, item in enumerate(items):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.search_tree.insert("", "end", values=(
                item["ID_Barang"],
                item["Nama_Barang"],
                item["Kategori"],
                item["Stok"],
                f"{int(item['Harga']):,}",
                item["Supplier"]
            ), tags=(tag,))

    # =========================================================================
    # VIEW: SORTING PAGE
    # =========================================================================
    def render_sorting_page(self):
        # Header Halaman
        header_lbl = ctk.CTkLabel(
            self.active_frame, 
            text="Fitur Pengurutan Data Barang", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=self.text_primary
        )
        header_lbl.grid(row=0, column=0, sticky="w", pady=(0, 15))

        # Panel Filter Pengurutan (Card Style)
        sort_filter_frame = ctk.CTkFrame(
            self.active_frame,
            fg_color=self.card_color,
            border_width=1,
            border_color=self.border_color,
            corner_radius=14
        )
        sort_filter_frame.grid(row=1, column=0, sticky="ew", pady=(0, 15))
        self.active_frame.grid_columnconfigure(0, weight=1)

        # Dropdown Kolom Kunci Pengurutan
        ctk.CTkLabel(sort_filter_frame, text="Urutkan Berdasarkan:", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=self.text_primary).pack(side="left", padx=(20, 5), pady=15)
        self.sort_key_cb = ctk.CTkComboBox(sort_filter_frame, values=["Nama_Barang", "Stok", "Harga"], width=130, corner_radius=8, border_width=2, border_color=self.border_color, fg_color=self.bg_color)
        self.sort_key_cb.pack(side="left", padx=5)

        # Dropdown Arah Pengurutan
        ctk.CTkLabel(sort_filter_frame, text="Arah Urutan:", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=self.text_primary).pack(side="left", padx=(15, 5))
        self.sort_order_cb = ctk.CTkComboBox(sort_filter_frame, values=["Ascending (Kecil - Besar)", "Descending (Besar - Kecil)"], width=190, corner_radius=8, border_width=2, border_color=self.border_color, fg_color=self.bg_color)
        self.sort_order_cb.pack(side="left", padx=5)

        # Dropdown Algoritma Pengurutan
        ctk.CTkLabel(sort_filter_frame, text="Algoritma:", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=self.text_primary).pack(side="left", padx=(15, 5))
        self.sort_algo_cb = ctk.CTkComboBox(sort_filter_frame, values=["Quick Sort", "Bubble Sort"], width=130, corner_radius=8, border_width=2, border_color=self.border_color, fg_color=self.bg_color)
        self.sort_algo_cb.pack(side="left", padx=5)

        # Button Sortir
        btn_sort = ctk.CTkButton(sort_filter_frame, text="🔀 Urutkan", width=90, fg_color="#f59e0b", hover_color="#d97706", font=ctk.CTkFont(family="Segoe UI", weight="bold"), command=self.run_sorting, corner_radius=8)
        btn_sort.pack(side="left", padx=15)

        # Panel Hasil Pengurutan
        table_frame = ctk.CTkFrame(
            self.active_frame,
            fg_color=self.card_color,
            border_width=1,
            border_color=self.border_color,
            corner_radius=16
        )
        table_frame.grid(row=2, column=0, sticky="nsew")
        self.active_frame.grid_rowconfigure(2, weight=1)

        tree_scroll_y = ttk.Scrollbar(table_frame, orient="vertical")
        tree_scroll_y.pack(side="right", fill="y", pady=12, padx=(0, 4))
        
        tree_scroll_x = ttk.Scrollbar(table_frame, orient="horizontal")
        tree_scroll_x.pack(side="bottom", fill="x", padx=12, pady=(0, 4))

        cols = ("ID Barang", "Nama Barang", "Kategori", "Stok", "Harga", "Supplier")
        self.sort_tree = ttk.Treeview(
            table_frame, 
            columns=cols, 
            show="headings", 
            yscrollcommand=tree_scroll_y.set,
            xscrollcommand=tree_scroll_x.set
        )
        self.sort_tree.pack(fill="both", expand=True, padx=12, pady=12)

        tree_scroll_y.config(command=self.sort_tree.yview)
        tree_scroll_x.config(command=self.sort_tree.xview)

        # Konfigurasi Header
        for col in cols:
            self.sort_tree.heading(col, text=col)
        
        self.sort_tree.column("ID Barang", anchor="center", width=95)
        self.sort_tree.column("Nama Barang", anchor="w", width=230)
        self.sort_tree.column("Kategori", anchor="w", width=150)
        self.sort_tree.column("Stok", anchor="center", width=85)
        self.sort_tree.column("Harga", anchor="e", width=140)
        self.sort_tree.column("Supplier", anchor="w", width=160)

        # Style Sync
        self.tree = self.sort_tree
        self.update_treeview_styles()
        self.tree = None

        self.run_sorting()

    def run_sorting(self):
        key = self.sort_key_cb.get()
        order_str = self.sort_order_cb.get()
        algo = self.sort_algo_cb.get()

        reverse = True if "Descending" in order_str else False
        items = self.db.get_all_items()

        if algo == "Quick Sort":
            sorted_items = quick_sort(items, key, reverse=reverse)
        else:
            sorted_items = bubble_sort(items, key, reverse=reverse)

        for row in self.sort_tree.get_children():
            self.sort_tree.delete(row)

        for idx, item in enumerate(sorted_items):
            tag = 'evenrow' if idx % 2 == 0 else 'oddrow'
            self.sort_tree.insert("", "end", values=(
                item["ID_Barang"],
                item["Nama_Barang"],
                item["Kategori"],
                item["Stok"],
                f"{int(item['Harga']):,}",
                item["Supplier"]
            ), tags=(tag,))

    # =========================================================================
    # VIEW: LAPORAN GUDANG
    # =========================================================================
    def render_laporan_page(self):
        # Header Halaman
        header_lbl = ctk.CTkLabel(
            self.active_frame, 
            text="Laporan & Statistik Gudang", 
            font=ctk.CTkFont(family="Segoe UI", size=24, weight="bold"),
            text_color=self.text_primary
        )
        header_lbl.grid(row=0, column=0, columnspan=2, sticky="w", pady=(0, 20))

        self.active_frame.grid_columnconfigure((0, 1), weight=1)
        self.active_frame.grid_rowconfigure(1, weight=1)

        stats = self.db.get_statistics()
        items = self.db.get_all_items()
        total_aset = sum(item["Stok"] * item["Harga"] for item in items)

        # Left Column Frame: Detail Ringkasan
        left_frame = ctk.CTkFrame(
            self.active_frame, 
            corner_radius=16,
            fg_color=self.card_color,
            border_width=1,
            border_color=self.border_color
        )
        left_frame.grid(row=1, column=0, padx=6, pady=5, sticky="nsew")
        left_frame.pack_propagate(False)
        
        left_scroll = ctk.CTkScrollableFrame(left_frame, fg_color="transparent")
        left_scroll.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            left_scroll, 
            text="📈 Ringkasan Statistik", 
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=self.text_primary
        ).pack(anchor="w", pady=(0, 15))

        stats_list = [
            ("Total Varian Jenis Barang", f"{stats['total_jenis']} Varian", "#3b82f6"),
            ("Total Stok Unit Gudang", f"{stats['total_stok']} Unit", "#10b981"),
            ("Total Nilai Investasi Aset", f"Rp {int(total_aset):,}", "#6366f1")
        ]

        for title, value, label_color in stats_list:
            item_frame = ctk.CTkFrame(left_scroll, fg_color="transparent")
            item_frame.pack(fill="x", pady=8)
            
            ctk.CTkLabel(item_frame, text=title, font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=self.text_secondary).pack(anchor="w")
            ctk.CTkLabel(item_frame, text=value, font=ctk.CTkFont(family="Segoe UI", size=22, weight="bold"), text_color=label_color).pack(anchor="w", pady=(2, 0))
            
            ctk.CTkFrame(left_scroll, height=1, fg_color=self.border_color).pack(fill="x", pady=6)

        # Tombol Ekspor Laporan ke CSV
        btn_export = ctk.CTkButton(
            left_scroll, 
            text="💾  Ekspor Laporan ke CSV", 
            fg_color="#6366f1", 
            hover_color="#4f46e5",
            font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"),
            height=38,
            corner_radius=8,
            command=self.export_report
        )
        btn_export.pack(fill="x", pady=(10, 20))

        # Kategori Breakdown Infographics Chart
        category_counts = {}
        for item in items:
            cat = item["Kategori"]
            category_counts[cat] = category_counts.get(cat, 0) + item["Stok"]

        if category_counts:
            ctk.CTkLabel(
                left_scroll, 
                text="📊 Distribusi Stok per Kategori", 
                font=ctk.CTkFont(family="Segoe UI", size=15, weight="bold"),
                text_color=self.text_primary
            ).pack(anchor="w", pady=(15, 10))

            max_cat_stock = max(category_counts.values()) if category_counts.values() else 1
            cat_colors = ["#3b82f6", "#10b981", "#6366f1", "#f59e0b", "#ec4899", "#8b5cf6"]
            
            for idx, (cat_name, cat_stok) in enumerate(sorted(category_counts.items(), key=lambda x: x[1], reverse=True)):
                cat_row = ctk.CTkFrame(left_scroll, fg_color="transparent")
                cat_row.pack(fill="x", pady=5)
                
                lbl_name = ctk.CTkLabel(cat_row, text=f"{cat_name} ({cat_stok} Unit)", font=ctk.CTkFont(family="Segoe UI", size=12, weight="bold"), text_color=self.text_primary)
                lbl_name.pack(anchor="w")

                ratio = cat_stok / max_cat_stock
                pbar = ctk.CTkProgressBar(cat_row, height=8, corner_radius=4)
                pbar.pack(fill="x", pady=(3, 0))
                pbar.set(ratio)
                
                color_idx = idx % len(cat_colors)
                pbar.configure(progress_color=cat_colors[color_idx], fg_color=self.bg_color)

        # Right Column Frame: Barang Ekstrim
        right_frame = ctk.CTkFrame(
            self.active_frame, 
            corner_radius=16,
            fg_color=self.card_color,
            border_width=1,
            border_color=self.border_color
        )
        right_frame.grid(row=1, column=1, padx=6, pady=5, sticky="nsew")
        right_frame.pack_propagate(False)
        
        right_scroll = ctk.CTkScrollableFrame(right_frame, fg_color="transparent")
        right_scroll.pack(fill="both", expand=True, padx=15, pady=15)

        ctk.CTkLabel(
            right_scroll, 
            text="📊 Analisis Stok Ekstrim", 
            font=ctk.CTkFont(family="Segoe UI", size=18, weight="bold"),
            text_color=self.text_primary
        ).pack(anchor="w", pady=(0, 15))

        # Stok Terbanyak Card
        max_item = stats["stok_terbanyak"]
        ctk.CTkLabel(right_scroll, text="📦 Barang Stok Terbanyak:", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=self.text_secondary).pack(anchor="w")
        
        max_sub = ctk.CTkFrame(right_scroll, fg_color=self.bg_color, corner_radius=12, border_width=1, border_color=self.border_color)
        max_sub.pack(fill="x", pady=(5, 20), padx=2)
        
        if max_item:
            max_desc = f"🏷️  {max_item['Nama_Barang']} (ID: {max_item['ID_Barang']})\n📂  Kategori: {max_item['Kategori']}\n📈  Jumlah Stok: {max_item['Stok']} Unit\n🏢  Supplier: {max_item['Supplier']}"
            max_lbl = ctk.CTkLabel(max_sub, text=max_desc, font=ctk.CTkFont(family="Segoe UI", size=13), justify="left", anchor="w", text_color=self.text_primary)
            max_lbl.pack(anchor="w", padx=18, pady=14)
        else:
            ctk.CTkLabel(max_sub, text="Belum ada data barang.", font=ctk.CTkFont(family="Segoe UI", size=13, slant="italic"), text_color=self.text_secondary).pack(anchor="w", padx=18, pady=14)

        # Stok Tersedikit Card
        min_item = stats["stok_tersedikit"]
        ctk.CTkLabel(right_scroll, text="⚠️ Barang Stok Tersedikit:", font=ctk.CTkFont(family="Segoe UI", size=13, weight="bold"), text_color=self.text_secondary).pack(anchor="w")
        
        min_sub = ctk.CTkFrame(right_scroll, fg_color=self.bg_color, corner_radius=12, border_width=1, border_color=self.border_color)
        min_sub.pack(fill="x", pady=(5, 10), padx=2)
        
        if min_item:
            min_desc = f"🏷️  {min_item['Nama_Barang']} (ID: {min_item['ID_Barang']})\n📂  Kategori: {min_item['Kategori']}\n⚠️  Jumlah Stok: {min_item['Stok']} Unit\n🏢  Supplier: {min_item['Supplier']}"
            min_lbl = ctk.CTkLabel(min_sub, text=min_desc, font=ctk.CTkFont(family="Segoe UI", size=13), justify="left", anchor="w", text_color=self.text_primary)
            min_lbl.pack(anchor="w", padx=18, pady=14)
        else:
            ctk.CTkLabel(min_sub, text="Belum ada data barang.", font=ctk.CTkFont(family="Segoe UI", size=13, slant="italic"), text_color=self.text_secondary).pack(anchor="w", padx=18, pady=14)

    def export_report(self):
        """
        Membuka file dialog untuk mengekspor laporan statistik gudang ke file CSV.
        """
        from tkinter import filedialog
        
        # Format default file name: laporan_gudang_YYYYMMDD_HHMMSS.csv
        default_filename = f"laporan_gudang_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
        filepath = filedialog.asksaveasfilename(
            defaultextension=".csv",
            filetypes=[("CSV Files", "*.csv"), ("All Files", "*.*")],
            title="Ekspor Laporan Gudang",
            initialfile=default_filename
        )
        
        if filepath:
            try:
                self.db.export_report_to_csv(filepath)
                messagebox.showinfo(
                    "Ekspor Sukses", 
                    f"Laporan gudang berhasil disimpan di:\n{filepath}\n\nAnda dapat membuka file ini menggunakan Microsoft Excel atau Notepad untuk melihat isi laporan."
                )
            except Exception as e:
                messagebox.showerror("Error Ekspor", f"Gagal mengekspor laporan:\n{str(e)}")

if __name__ == "__main__":
    app = WarehouseApp()
    app.mainloop()
