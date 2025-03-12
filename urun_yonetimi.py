import sys
import sqlite3
import shutil
from datetime import datetime
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QComboBox, QMessageBox, QTableWidget, QTableWidgetItem,
                            QHeaderView, QGroupBox, QRadioButton, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont, QDoubleValidator

class UrunYonetimi(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ürün Yönetimi")
        self.setGeometry(100, 100, 1200, 800)
        
        # Veritabanı bağlantısı
        self.connect_db()
        
        # Ana widget ve layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QHBoxLayout(main_widget)
        
        # Sol taraf (form ve tablo)
        left_layout = QVBoxLayout()
        
        # Form alanları
        form_layout = QVBoxLayout()
        
        # Barkod
        barkod_layout = QHBoxLayout()
        barkod_label = QLabel("Barkod:")
        barkod_label.setFont(QFont("Arial", 12))
        self.barkod_input = QLineEdit()
        self.barkod_input.setFont(QFont("Arial", 12))
        self.barkod_input.setFixedHeight(40)
        self.barkod_input.returnPressed.connect(self.check_existing_product)
        barkod_layout.addWidget(barkod_label)
        barkod_layout.addWidget(self.barkod_input)
        
        # Ürün Adı
        urun_adi_layout = QHBoxLayout()
        urun_adi_label = QLabel("Ürün Adı:")
        urun_adi_label.setFont(QFont("Arial", 12))
        self.urun_adi_input = QLineEdit()
        self.urun_adi_input.setFont(QFont("Arial", 12))
        self.urun_adi_input.setFixedHeight(40)
        urun_adi_layout.addWidget(urun_adi_label)
        urun_adi_layout.addWidget(self.urun_adi_input)
        
        # Marka
        marka_layout = QHBoxLayout()
        marka_label = QLabel("Marka:")
        marka_label.setFont(QFont("Arial", 12))
        self.marka_input = QLineEdit()
        self.marka_input.setFont(QFont("Arial", 12))
        self.marka_input.setFixedHeight(40)
        marka_layout.addWidget(marka_label)
        marka_layout.addWidget(self.marka_input)
        
        # Fiyat
        fiyat_layout = QHBoxLayout()
        fiyat_label = QLabel("Fiyat (TL):")
        fiyat_label.setFont(QFont("Arial", 12))
        self.fiyat_input = QLineEdit()
        self.fiyat_input.setFont(QFont("Arial", 12))
        self.fiyat_input.setFixedHeight(40)
        self.fiyat_input.setValidator(QDoubleValidator(0.00, 999999.99, 2))
        fiyat_layout.addWidget(fiyat_label)
        fiyat_layout.addWidget(self.fiyat_input)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.kaydet_button = QPushButton("Kaydet")
        self.kaydet_button.setFont(QFont("Arial", 12))
        self.kaydet_button.clicked.connect(self.save_product)
        
        self.temizle_button = QPushButton("Formu Temizle")
        self.temizle_button.setFont(QFont("Arial", 12))
        self.temizle_button.clicked.connect(self.clear_form)
        
        # Veritabanı import/export butonları
        self.import_button = QPushButton("Veritabanı İçe Aktar")
        self.import_button.setFont(QFont("Arial", 12))
        self.import_button.clicked.connect(self.import_database)
        
        self.export_button = QPushButton("Veritabanı Dışa Aktar")
        self.export_button.setFont(QFont("Arial", 12))
        self.export_button.clicked.connect(self.export_database)
        
        button_layout.addWidget(self.kaydet_button)
        button_layout.addWidget(self.temizle_button)
        button_layout.addWidget(self.import_button)
        button_layout.addWidget(self.export_button)
        
        # Arama kutusu
        search_layout = QHBoxLayout()
        search_label = QLabel("Ürün Ara:")
        search_label.setFont(QFont("Arial", 12))
        self.search_input = QLineEdit()
        self.search_input.setFont(QFont("Arial", 12))
        self.search_input.setFixedHeight(40)
        self.search_input.setPlaceholderText("Ürün adına göre ara...")
        self.search_input.textChanged.connect(self.search_products)
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        left_layout.addLayout(search_layout)
        
        # Ürün tablosu
        self.table = QTableWidget()
        self.table.setColumnCount(4)
        self.table.setHorizontalHeaderLabels(["Barkod", "Ürün Adı", "Marka", "Fiyat"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setFont(QFont("Arial", 12))
        self.table.itemClicked.connect(self.load_product_to_form)
        
        # Layout'ları ana layout'a ekle
        form_layout.addLayout(barkod_layout)
        form_layout.addLayout(urun_adi_layout)
        form_layout.addLayout(marka_layout)
        form_layout.addLayout(fiyat_layout)
        form_layout.addLayout(button_layout)
        
        left_layout.addLayout(form_layout)
        left_layout.addWidget(self.table)
        
        # Sağ taraf (toplu zam paneli)
        right_layout = QVBoxLayout()
        right_layout.setContentsMargins(20, 0, 0, 0)
        
        # Toplu Zam Başlığı
        zam_baslik = QLabel("Toplu Zam Paneli")
        zam_baslik.setFont(QFont("Arial", 14, QFont.Weight.Bold))
        zam_baslik.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_layout.addWidget(zam_baslik)
        
        # Zam Yapılacak Alan Seçimi
        zam_alan_group = QGroupBox("Zam Yapılacak Alan")
        zam_alan_layout = QVBoxLayout()
        
        self.tum_urunler_radio = QRadioButton("Tüm Ürünler")
        self.marka_bazli_radio = QRadioButton("Markaya Göre")
        self.tum_urunler_radio.setChecked(True)
        
        zam_alan_layout.addWidget(self.tum_urunler_radio)
        zam_alan_layout.addWidget(self.marka_bazli_radio)
        zam_alan_group.setLayout(zam_alan_layout)
        right_layout.addWidget(zam_alan_group)
        
        # Marka Seçimi
        self.marka_combo = QComboBox()
        self.marka_combo.setFont(QFont("Arial", 12))
        self.marka_combo.setFixedHeight(40)
        self.marka_combo.setEnabled(False)  # Başlangıçta devre dışı
        right_layout.addWidget(self.marka_combo)
        
        # Zam Türü Seçimi
        zam_tur_group = QGroupBox("Zam Türü")
        zam_tur_layout = QVBoxLayout()
        
        self.yuzde_radio = QRadioButton("Yüzdelik (%)")
        self.sabit_radio = QRadioButton("Sabit Tutar (TL)")
        self.yuzde_radio.setChecked(True)
        
        zam_tur_layout.addWidget(self.yuzde_radio)
        zam_tur_layout.addWidget(self.sabit_radio)
        zam_tur_group.setLayout(zam_tur_layout)
        right_layout.addWidget(zam_tur_group)
        
        # Zam Miktarı
        zam_miktar_layout = QHBoxLayout()
        self.zam_miktar_input = QLineEdit()
        self.zam_miktar_input.setFont(QFont("Arial", 12))
        self.zam_miktar_input.setFixedHeight(40)
        self.zam_miktar_input.setValidator(QDoubleValidator(0.00, 999999.99, 2))
        zam_miktar_layout.addWidget(QLabel("Zam Miktarı:"))
        zam_miktar_layout.addWidget(self.zam_miktar_input)
        right_layout.addLayout(zam_miktar_layout)
        
        # Zam Uygula Butonu
        self.zam_button = QPushButton("Zam Uygula")
        self.zam_button.setFont(QFont("Arial", 12))
        self.zam_button.clicked.connect(self.apply_price_increase)
        right_layout.addWidget(self.zam_button)
        
        # Boşluk ekle
        right_layout.addStretch()
        
        # Radio buton değişikliklerini dinle
        self.marka_bazli_radio.toggled.connect(self.update_marka_combo)
        self.tum_urunler_radio.toggled.connect(self.update_marka_combo)
        
        # Layout'ları ana layout'a ekle
        main_layout.addLayout(left_layout, 2)
        main_layout.addLayout(right_layout, 1)
        
        # Stil
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #2c3e50;
            }
            QLineEdit, QComboBox {
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
        
        # Ürünleri yükle
        self.load_products()

    def connect_db(self):
        """Veritabanı bağlantısını oluşturur"""
        self.db = sqlite3.connect('market_urunler.db')
        self.cursor = self.db.cursor()
        
        # Ana tabloyu oluştur
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS urunler (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                urun_adi TEXT NOT NULL,
                fiyat REAL NOT NULL,
                birim_fiyat TEXT,
                marka TEXT,
                barkod TEXT UNIQUE
            )
        """)
        self.db.commit()

    def check_existing_product(self):
        # Veritabanı bağlantısını yenile
        self.connect_db()
        
        barkod = self.barkod_input.text().strip()
        if not barkod:
            return
            
        self.cursor.execute("SELECT * FROM urunler WHERE barkod = ?", (barkod,))
        product = self.cursor.fetchone()
        
        if product:
            # Ürün bulundu, formu doldur
            self.urun_adi_input.setText(product[1])
            self.fiyat_input.setText(str(product[2]))
            self.marka_input.setText(product[4] if product[4] != "Belirtilmemiş" else "")
            
            QMessageBox.information(self, "Bilgi", "Ürün bulundu! Bilgileri düzenleyebilirsiniz.")
        else:
            QMessageBox.information(self, "Bilgi", "Yeni ürün ekleyebilirsiniz.")

    def save_product(self):
        # Veritabanı bağlantısını yenile
        self.connect_db()
        
        # Form verilerini al
        barkod = self.barkod_input.text().strip()
        urun_adi = self.urun_adi_input.text().strip()
        marka = self.marka_input.text().strip() or "Belirtilmemiş"
        fiyat_text = self.fiyat_input.text().replace(",", ".")
        
        # Validasyon
        if not all([barkod, urun_adi, fiyat_text]):
            QMessageBox.warning(self, "Uyarı", "Lütfen gerekli alanları doldurun!")
            return
            
        try:
            fiyat = float(fiyat_text)
        except ValueError:
            QMessageBox.warning(self, "Uyarı", "Geçersiz fiyat!")
            return
            
        try:
            # Ürün var mı kontrol et
            self.cursor.execute("SELECT barkod FROM urunler WHERE barkod = ?", (barkod,))
            existing_product = self.cursor.fetchone()
            
            if existing_product:
                # Güncelle
                self.cursor.execute("""
                    UPDATE urunler 
                    SET urun_adi = ?, fiyat = ?, marka = ?
                    WHERE barkod = ?
                """, (urun_adi, fiyat, marka, barkod))
                message = "Ürün başarıyla güncellendi!"
            else:
                # Yeni ekle
                self.cursor.execute("""
                    INSERT INTO urunler (barkod, urun_adi, fiyat, marka)
                    VALUES (?, ?, ?, ?)
                """, (barkod, urun_adi, fiyat, marka))
                message = "Ürün başarıyla eklendi!"
            
            self.db.commit()
            QMessageBox.information(self, "Başarılı", message)
            
            # Formu temizle ve tabloyu güncelle
            self.clear_form()
            self.load_products()
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Hata", f"Veritabanı hatası: {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Beklenmeyen hata: {str(e)}")

    def search_products(self):
        # Veritabanı bağlantısını yenile
        self.connect_db()
        
        search_text = self.search_input.text().strip().lower()
        
        try:
            if search_text:
                # Arama kriterine göre ürünleri getir
                self.cursor.execute("""
                    SELECT barkod, urun_adi, marka, fiyat 
                    FROM urunler 
                    WHERE LOWER(urun_adi) LIKE ?
                    ORDER BY urun_adi
                """, (f"%{search_text}%",))
            else:
                # Tüm ürünleri getir
                self.cursor.execute("""
                    SELECT barkod, urun_adi, marka, fiyat 
                    FROM urunler 
                    ORDER BY urun_adi
                """)
            
            products = self.cursor.fetchall()
            
            self.table.setRowCount(len(products))
            for row, product in enumerate(products):
                for col, value in enumerate(product):
                    item = QTableWidgetItem(str(value))
                    if col == 3:  # Fiyat kolonuysa
                        item = QTableWidgetItem(f"{float(value):.2f} TL")
                    self.table.setItem(row, col, item)
                    
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Hata", f"Veritabanı hatası: {str(e)}")

    def load_products(self):
        # Veritabanı bağlantısını yenile
        self.connect_db()
        
        # Arama kutusunu temizle
        if hasattr(self, 'search_input'):
            self.search_input.clear()
        
        try:
            # Tüm ürünleri getir
            self.cursor.execute("""
                SELECT barkod, urun_adi, marka, fiyat 
                FROM urunler 
                ORDER BY urun_adi
            """)
            products = self.cursor.fetchall()
            
            self.table.setRowCount(len(products))
            for row, product in enumerate(products):
                for col, value in enumerate(product):
                    item = QTableWidgetItem(str(value))
                    if col == 3:  # Fiyat kolonuysa
                        item = QTableWidgetItem(f"{float(value):.2f} TL")
                    self.table.setItem(row, col, item)
                    
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Hata", f"Veritabanı hatası: {str(e)}")

    def load_product_to_form(self, item):
        row = item.row()
        self.barkod_input.setText(self.table.item(row, 0).text())
        self.urun_adi_input.setText(self.table.item(row, 1).text())
        self.marka_input.setText(self.table.item(row, 2).text())
        fiyat = self.table.item(row, 3).text().replace(" TL", "")
        self.fiyat_input.setText(fiyat)

    def clear_form(self):
        self.barkod_input.clear()
        self.urun_adi_input.clear()
        self.marka_input.clear()
        self.fiyat_input.clear()
        self.barkod_input.setFocus()

    def closeEvent(self, event):
        self.db.close()
        event.accept()

    def update_marka_combo(self):
        # Veritabanı bağlantısını yenile
        self.connect_db()
        
        self.marka_combo.setEnabled(self.marka_bazli_radio.isChecked())
        if self.marka_bazli_radio.isChecked():
            try:
                # Mevcut seçili markayı kaydet
                current_marka = self.marka_combo.currentText()
                
                # Markaları getir
                self.cursor.execute("""
                    SELECT DISTINCT marka 
                    FROM urunler 
                    WHERE marka != 'Belirtilmemiş'
                    ORDER BY marka
                """)
                markalar = [row[0] for row in self.cursor.fetchall()]
                
                # Combo box'ı güncelle
                self.marka_combo.clear()
                self.marka_combo.addItems(markalar)
                
                # Önceki seçili markayı tekrar seç
                index = self.marka_combo.findText(current_marka)
                if index >= 0:
                    self.marka_combo.setCurrentIndex(index)
                
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Hata", f"Markalar yüklenirken hata oluştu: {str(e)}")

    def apply_price_increase(self):
        # Veritabanı bağlantısını yenile
        self.connect_db()
        
        # Seçimleri al
        miktar_text = self.zam_miktar_input.text().replace(",", ".")
        
        # Validasyon
        if not miktar_text:
            QMessageBox.warning(self, "Uyarı", "Lütfen zam miktarını girin!")
            return
            
        try:
            miktar = float(miktar_text)
        except ValueError:
            QMessageBox.warning(self, "Uyarı", "Geçersiz zam miktarı!")
            return
            
        # Marka bazlı zam için validasyon
        if self.marka_bazli_radio.isChecked() and not self.marka_combo.currentText():
            QMessageBox.warning(self, "Uyarı", "Lütfen bir marka seçin!")
            return
            
        # Onay mesajı
        zam_turu = "yüzde" if self.yuzde_radio.isChecked() else "TL"
        if self.marka_bazli_radio.isChecked():
            marka = self.marka_combo.currentText()
            msg = f"{marka} markalı ürünlere {miktar} {zam_turu} zam yapılacak. Onaylıyor musunuz?"
        else:
            msg = f"Tüm ürünlere {miktar} {zam_turu} zam yapılacak. Onaylıyor musunuz?"
        
        reply = QMessageBox.question(self, "Onay", msg, 
                                   QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No)
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # SQL sorgusunu hazırla
                if self.marka_bazli_radio.isChecked():
                    self.cursor.execute("SELECT id, fiyat FROM urunler WHERE marka = ?", 
                                      (self.marka_combo.currentText(),))
                else:
                    self.cursor.execute("SELECT id, fiyat FROM urunler")
                
                products = self.cursor.fetchall()
                
                if not products:
                    QMessageBox.warning(self, "Uyarı", "Seçilen kriterlere uygun ürün bulunamadı!")
                    return
                
                # Her ürüne zam uygula
                for product_id, current_price in products:
                    if self.yuzde_radio.isChecked():
                        # Yüzdelik zam
                        new_price = current_price * (1 + miktar / 100)
                    else:
                        # Sabit zam
                        new_price = current_price + miktar
                    
                    # Fiyatı güncelle
                    self.cursor.execute("""
                        UPDATE urunler 
                        SET fiyat = ? 
                        WHERE id = ?
                    """, (new_price, product_id))
                
                self.db.commit()
                
                # Başarı mesajı
                QMessageBox.information(self, "Başarılı", 
                    f"{len(products)} ürüne zam uygulandı!")
                
                # Tabloyu güncelle
                self.load_products()
                
            except sqlite3.Error as e:
                QMessageBox.critical(self, "Hata", f"Zam uygulanırken hata oluştu: {str(e)}")
                self.db.rollback()

    def import_database(self):
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                "Veritabanı Dosyası Seç",
                "",
                "SQLite Veritabanı (*.db)"
            )
            
            if file_path:
                # Mevcut veritabanı bağlantısını kapat
                self.db.close()
                
                # Yeni veritabanını kopyala
                shutil.copy2(file_path, 'market_urunler.db')
                
                # Veritabanı bağlantısını yeniden aç
                self.db = sqlite3.connect('market_urunler.db')
                self.cursor = self.db.cursor()
                
                # Tabloyu yeniden yükle
                self.load_products()
                
                QMessageBox.information(
                    self,
                    "Başarılı",
                    "Veritabanı başarıyla içe aktarıldı!"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Hata",
                f"Veritabanı içe aktarılırken bir hata oluştu: {str(e)}"
            )
    
    def export_database(self):
        try:
            # Tarih ve saat bilgisini al
            current_time = datetime.now().strftime("%Y%m%d_%H%M%S")
            default_name = f"market_urunler_yedek_{current_time}.db"
            
            file_path, _ = QFileDialog.getSaveFileName(
                self,
                "Veritabanını Kaydet",
                default_name,
                "SQLite Veritabanı (*.db)"
            )
            
            if file_path:
                # Veritabanını kopyala
                shutil.copy2('market_urunler.db', file_path)
                
                QMessageBox.information(
                    self,
                    "Başarılı",
                    "Veritabanı başarıyla dışa aktarıldı!"
                )
        except Exception as e:
            QMessageBox.critical(
                self,
                "Hata",
                f"Veritabanı dışa aktarılırken bir hata oluştu: {str(e)}"
            )

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = UrunYonetimi()
    window.show()
    sys.exit(app.exec()) 