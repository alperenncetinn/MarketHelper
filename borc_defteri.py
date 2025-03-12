import sys
import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
                            QLabel, QLineEdit, QPushButton, QTableWidget, 
                            QTableWidgetItem, QMessageBox, QHeaderView)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont

class BorcDefteri(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Borç Defteri")
        self.setGeometry(100, 100, 1200, 800)
        
        # Veritabanı bağlantısı
        self.connect_db()
        
        # Ana widget ve layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Sol taraf (borçlu listesi)
        left_layout = QVBoxLayout()
        
        # Borçlu ekleme formu
        form_layout = QVBoxLayout()
        
        # Müşteri Adı
        musteri_layout = QHBoxLayout()
        musteri_label = QLabel("Müşteri Adı:")
        musteri_label.setFont(QFont("Arial", 12))
        self.musteri_input = QLineEdit()
        self.musteri_input.setFont(QFont("Arial", 12))
        self.musteri_input.setFixedHeight(40)
        musteri_layout.addWidget(musteri_label)
        musteri_layout.addWidget(self.musteri_input)
        
        # Telefon
        telefon_layout = QHBoxLayout()
        telefon_label = QLabel("Telefon:")
        telefon_label.setFont(QFont("Arial", 12))
        self.telefon_input = QLineEdit()
        self.telefon_input.setFont(QFont("Arial", 12))
        self.telefon_input.setFixedHeight(40)
        telefon_layout.addWidget(telefon_label)
        telefon_layout.addWidget(self.telefon_input)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.ekle_button = QPushButton("Müşteri Ekle")
        self.ekle_button.setFont(QFont("Arial", 12))
        self.ekle_button.clicked.connect(self.add_customer)
        
        button_layout.addWidget(self.ekle_button)
        
        # Layout'ları form layout'a ekle
        form_layout.addLayout(musteri_layout)
        form_layout.addLayout(telefon_layout)
        form_layout.addLayout(button_layout)
        
        # Borçlu tablosu
        self.customer_table = QTableWidget()
        self.customer_table.setColumnCount(4)
        self.customer_table.setHorizontalHeaderLabels(["ID", "Müşteri Adı", "Telefon", "Toplam Borç"])
        self.customer_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.customer_table.setFont(QFont("Arial", 12))
        self.customer_table.itemClicked.connect(self.load_customer_debts)
        
        # Sol layout'a ekle
        left_layout.addLayout(form_layout)
        left_layout.addWidget(self.customer_table)
        
        # Sağ taraf (borç detayları)
        right_layout = QVBoxLayout()
        
        # Borç detay tablosu
        self.debt_table = QTableWidget()
        self.debt_table.setColumnCount(5)
        self.debt_table.setHorizontalHeaderLabels(["Tarih", "Ürün", "Alış Fiyatı", "Güncel Fiyat", "Durum"])
        self.debt_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.debt_table.setFont(QFont("Arial", 12))
        
        # Ödeme butonu
        self.odeme_button = QPushButton("Seçili Borcu Öde")
        self.odeme_button.setFont(QFont("Arial", 12))
        self.odeme_button.clicked.connect(self.pay_debt)
        
        # Sağ layout'a ekle
        right_layout.addWidget(self.debt_table)
        right_layout.addWidget(self.odeme_button)
        
        # Ana layout'a ekle
        main_layout.addLayout(left_layout, 1)
        main_layout.addLayout(right_layout, 2)
        
        # Stil
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #2c3e50;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #3498db;
                border-radius: 5px;
                background-color: white;
            }
            QPushButton {
                padding: 10px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                min-height: 40px;
                min-width: 150px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
                margin-top: 20px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 8px;
                border: none;
            }
        """)
        
        # Müşterileri yükle
        self.load_customers()
    
    def connect_db(self):
        """Veritabanı bağlantısını oluşturur"""
        self.db = sqlite3.connect('market_urunler.db')
        self.cursor = self.db.cursor()
        
        # Gerekli tabloları oluştur
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS musteriler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                musteri_adi TEXT NOT NULL,
                telefon TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS borclar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                musteri_id INTEGER,
                urun_id INTEGER,
                alis_fiyati REAL NOT NULL,
                odendi INTEGER DEFAULT 0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (musteri_id) REFERENCES musteriler (id),
                FOREIGN KEY (urun_id) REFERENCES urunler (id)
            )
        """)
        
        self.db.commit()
    
    def add_customer(self):
        # Veritabanı bağlantısını yenile
        self.connect_db()
        
        musteri_adi = self.musteri_input.text().strip()
        telefon = self.telefon_input.text().strip()
        
        if not musteri_adi:
            QMessageBox.warning(self, "Uyarı", "Lütfen müşteri adını girin!")
            return
        
        try:
            self.cursor.execute("""
                INSERT INTO musteriler (musteri_adi, telefon)
                VALUES (?, ?)
            """, (musteri_adi, telefon))
            
            self.db.commit()
            QMessageBox.information(self, "Başarılı", "Müşteri başarıyla eklendi!")
            
            # Formu temizle ve tabloyu güncelle
            self.musteri_input.clear()
            self.telefon_input.clear()
            self.load_customers()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Hata", f"Veritabanı hatası: {str(e)}")
    
    def load_customers(self):
        # Veritabanı bağlantısını yenile
        self.connect_db()
        
        try:
            # Müşterileri ve toplam borçlarını getir
            self.cursor.execute("""
                SELECT 
                    m.id,
                    m.musteri_adi,
                    m.telefon,
                    COALESCE(SUM(CASE WHEN b.odendi = 0 THEN b.alis_fiyati ELSE 0 END), 0) as toplam_borc
                FROM musteriler m
                LEFT JOIN borclar b ON m.id = b.musteri_id
                GROUP BY m.id
                ORDER BY m.musteri_adi
            """)
            
            customers = self.cursor.fetchall()
            
            self.customer_table.setRowCount(len(customers))
            for row, customer in enumerate(customers):
                for col, value in enumerate(customer):
                    item = QTableWidgetItem(str(value))
                    if col == 3:  # Toplam borç kolonuysa
                        item = QTableWidgetItem(f"{float(value):.2f} TL")
                    self.customer_table.setItem(row, col, item)
                    
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Hata", f"Veritabanı hatası: {str(e)}")
    
    def load_customer_debts(self, item):
        # Veritabanı bağlantısını yenile
        self.connect_db()
        
        row = item.row()
        musteri_id = int(self.customer_table.item(row, 0).text())
        
        try:
            # Müşterinin borçlarını getir
            self.cursor.execute("""
                SELECT 
                    b.created_at,
                    u.urun_adi,
                    b.alis_fiyati,
                    u.fiyat,
                    b.odendi,
                    b.id
                FROM borclar b
                JOIN urunler u ON b.urun_id = u.id
                WHERE b.musteri_id = ?
                ORDER BY b.created_at DESC
            """, (musteri_id,))
            
            debts = self.cursor.fetchall()
            
            self.debt_table.setRowCount(len(debts))
            for row, debt in enumerate(debts):
                # Tarih
                tarih = datetime.strptime(debt[0], "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y %H:%M")
                self.debt_table.setItem(row, 0, QTableWidgetItem(tarih))
                
                # Ürün adı
                self.debt_table.setItem(row, 1, QTableWidgetItem(debt[1]))
                
                # Alış fiyatı
                self.debt_table.setItem(row, 2, QTableWidgetItem(f"{float(debt[2]):.2f} TL"))
                
                # Güncel fiyat
                self.debt_table.setItem(row, 3, QTableWidgetItem(f"{float(debt[3]):.2f} TL"))
                
                # Durum
                durum = "Ödendi" if debt[4] else "Ödenmedi"
                self.debt_table.setItem(row, 4, QTableWidgetItem(durum))
                
                # Borç ID'sini gizli veri olarak sakla
                self.debt_table.item(row, 0).setData(Qt.ItemDataRole.UserRole, debt[5])
                
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Hata", f"Veritabanı hatası: {str(e)}")
    
    def pay_debt(self):
        # Veritabanı bağlantısını yenile
        self.connect_db()
        
        current_row = self.debt_table.currentRow()
        if current_row < 0:
            QMessageBox.warning(self, "Uyarı", "Lütfen ödenecek borcu seçin!")
            return
        
        # Borç ID'sini al
        borc_id = self.debt_table.item(current_row, 0).data(Qt.ItemDataRole.UserRole)
        
        # Borç durumunu kontrol et
        durum = self.debt_table.item(current_row, 4).text()
        if durum == "Ödendi":
            QMessageBox.warning(self, "Uyarı", "Bu borç zaten ödenmiş!")
            return
        
        try:
            # Borcu ödenmiş olarak işaretle
            self.cursor.execute("""
                UPDATE borclar
                SET odendi = 1
                WHERE id = ?
            """, (borc_id,))
            
            self.db.commit()
            
            # Tabloları güncelle
            self.load_customers()
            self.debt_table.item(current_row, 4).setText("Ödendi")
            
            QMessageBox.information(self, "Başarılı", "Borç başarıyla ödendi!")
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Hata", f"Veritabanı hatası: {str(e)}")
    
    def closeEvent(self, event):
        self.db.close()
        event.accept() 