import sys
import sqlite3
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHeaderView, QDialog, QMessageBox,
                            QInputDialog)
from PyQt6.QtCore import Qt, QTimer, QSizeF
from PyQt6.QtGui import QFont, QColor, QDoubleValidator, QPainter, QPageSize
from PyQt6.QtPrintSupport import QPrinter, QPrintDialog

class MarketSatis(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Market Satış Sistemi")
        self.setGeometry(100, 100, 1200, 800)
        
        # Veritabanı bağlantısı
        self.connect_db()
        
        # Ürün listesi (binary search için sıralı)
        self.urunler = self.get_sorted_products()
        
        # Ana widget ve layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Üst kısım (Barkod girişi ve toplam)
        top_layout = QHBoxLayout()
        
        # Sol taraf (Barkod girişi)
        barkod_layout = QVBoxLayout()
        barkod_label = QLabel("Barkod:")
        barkod_label.setFont(QFont("Arial", 14))
        self.barkod_input = QLineEdit()
        self.barkod_input.setFont(QFont("Arial", 16))
        self.barkod_input.setFixedHeight(50)
        self.barkod_input.returnPressed.connect(self.process_barcode)
        barkod_layout.addWidget(barkod_label)
        barkod_layout.addWidget(self.barkod_input)
        
        # Sağ taraf (Toplam tutar)
        toplam_layout = QVBoxLayout()
        toplam_label = QLabel("Toplam Tutar:")
        toplam_label.setFont(QFont("Arial", 14))
        self.toplam_display = QLabel("0.00 TL")
        self.toplam_display.setFont(QFont("Arial", 36, QFont.Weight.Bold))
        self.toplam_display.setAlignment(Qt.AlignmentFlag.AlignRight)
        toplam_layout.addWidget(toplam_label)
        toplam_layout.addWidget(self.toplam_display)
        
        top_layout.addLayout(barkod_layout, 2)
        top_layout.addLayout(toplam_layout, 1)
        
        # Ürün tablosu
        self.table = QTableWidget()
        self.table.setColumnCount(5)
        self.table.setHorizontalHeaderLabels(["Barkod", "Ürün Adı", "Birim Fiyat", "Adet", "Toplam"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setFont(QFont("Arial", 12))
        
        # Alt kısım (Butonlar)
        button_layout = QHBoxLayout()
        
        self.sil_button = QPushButton("Seçili Ürünü Sil")
        self.sil_button.setFont(QFont("Arial", 12))
        self.sil_button.clicked.connect(self.remove_selected_item)
        
        self.iptal_button = QPushButton("Satışı İptal Et")
        self.iptal_button.setFont(QFont("Arial", 12))
        self.iptal_button.clicked.connect(self.clear_sale)
        
        self.tamamla_button = QPushButton("Ürünleri Yazdır")
        self.tamamla_button.setFont(QFont("Arial", 12))
        self.tamamla_button.clicked.connect(self.complete_sale)
        
        button_layout.addWidget(self.sil_button)
        button_layout.addWidget(self.iptal_button)
        button_layout.addWidget(self.tamamla_button)
        
        # Toplam ve ödeme alanı
        total_layout = QHBoxLayout()
        
        # Toplam tutar
        total_label = QLabel("Toplam:")
        total_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        self.total_display = QLabel("0.00 TL")
        self.total_display.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        total_layout.addWidget(total_label)
        total_layout.addWidget(self.total_display)
        
        # Ödeme butonları
        payment_layout = QHBoxLayout()
        
        self.cash_button = QPushButton("Nakit Ödeme")
        self.cash_button.setFont(QFont("Arial", 12))
        self.cash_button.clicked.connect(self.process_cash_payment)
        
        self.credit_button = QPushButton("Kredi Kartı")
        self.credit_button.setFont(QFont("Arial", 12))
        self.credit_button.clicked.connect(self.process_credit_payment)
        
        self.debt_button = QPushButton("Borca Ver")
        self.debt_button.setFont(QFont("Arial", 12))
        self.debt_button.clicked.connect(self.process_debt_payment)
        
        payment_layout.addWidget(self.cash_button)
        payment_layout.addWidget(self.credit_button)
        payment_layout.addWidget(self.debt_button)
        
        # Layout'ları ana layout'a ekle
        layout.addLayout(top_layout)
        layout.addWidget(self.table)
        layout.addLayout(button_layout)
        layout.addLayout(total_layout)
        layout.addLayout(payment_layout)
        
        # Değişkenler
        self.toplam_tutar = 0.0
        self.urun_adetleri = {}
        
        # Barkod input'una fokuslan
        self.barkod_input.setFocus()
        
        # Otomatik fokus için timer
        self.focus_timer = QTimer()
        self.focus_timer.timeout.connect(lambda: self.barkod_input.setFocus())
        self.focus_timer.start(500)  # Her 500ms'de bir kontrol et
        
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
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QTableWidget {
                background-color: white;
                border: 1px solid #bdc3c7;
                border-radius: 5px;
            }
            QHeaderView::section {
                background-color: #3498db;
                color: white;
                padding: 8px;
                border: none;
            }
        """)

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
                marka TEXT,
                barkod TEXT UNIQUE
            )
        """)
        self.db.commit()

    def get_sorted_products(self):
        # Veritabanı bağlantısını yenile
        self.connect_db()
        
        # Veritabanından ürünleri çek ve barkoda göre sırala
        self.cursor.execute("SELECT barkod, urun_adi, fiyat FROM urunler ORDER BY barkod")
        return self.cursor.fetchall()

    def binary_search(self, barkod):
        # Ürün listesini güncelle
        self.urunler = self.get_sorted_products()
        
        left = 0
        right = len(self.urunler) - 1
        
        while left <= right:
            mid = (left + right) // 2
            current_barkod = self.urunler[mid][0]
            
            if current_barkod == barkod:
                return self.urunler[mid]
            elif current_barkod < barkod:
                left = mid + 1
            else:
                right = mid - 1
        
        return None

    def process_barcode(self):
        barkod = self.barkod_input.text().strip()
        if not barkod:
            return
        
        # Binary search ile ürünü bul
        urun = self.binary_search(barkod)
        if urun:
            self.add_product_to_table(urun)
        else:
            # Ürün bulunamadı bildirimi
            self.barkod_input.setStyleSheet("background-color: #ffebee;")
            QTimer.singleShot(1000, lambda: self.barkod_input.setStyleSheet("background-color: white;"))
        
        self.barkod_input.clear()

    def add_product_to_table(self, urun):
        barkod, urun_adi, fiyat = urun
        
        # Ürün zaten tabloda var mı kontrol et
        if barkod in self.urun_adetleri:
            row = self.urun_adetleri[barkod]["row"]
            adet = self.urun_adetleri[barkod]["adet"] + 1
            toplam = adet * fiyat
            
            # Adet ve toplam güncelle
            self.table.item(row, 3).setText(str(adet))
            self.table.item(row, 4).setText(f"{toplam:.2f} TL")
            self.urun_adetleri[barkod]["adet"] = adet
        else:
            # Yeni ürün ekle
            row = self.table.rowCount()
            self.table.insertRow(row)
            
            self.table.setItem(row, 0, QTableWidgetItem(barkod))
            self.table.setItem(row, 1, QTableWidgetItem(urun_adi))
            self.table.setItem(row, 2, QTableWidgetItem(f"{fiyat:.2f} TL"))
            self.table.setItem(row, 3, QTableWidgetItem("1"))
            self.table.setItem(row, 4, QTableWidgetItem(f"{fiyat:.2f} TL"))
            
            self.urun_adetleri[barkod] = {
                "row": row,
                "adet": 1,
                "fiyat": fiyat  # Fiyatı da saklayalım
            }
        
        # Toplam tutarı güncelle
        self.toplam_tutar += fiyat
        self.toplam_display.setText(f"{self.toplam_tutar:.2f} TL")
        
        # Yeni eklenen satırı vurgula
        for col in range(self.table.columnCount()):
            item = self.table.item(row, col)
            item.setBackground(QColor("#e3f2fd"))
            QTimer.singleShot(500, lambda item=item: item.setBackground(QColor("white")))

    def remove_selected_item(self):
        current_row = self.table.currentRow()
        if current_row >= 0:
            barkod = self.table.item(current_row, 0).text()
            fiyat = float(self.table.item(current_row, 2).text().replace(" TL", ""))
            adet = int(self.table.item(current_row, 3).text())
            
            self.toplam_tutar -= (fiyat * adet)
            self.toplam_display.setText(f"{self.toplam_tutar:.2f} TL")
            
            del self.urun_adetleri[barkod]
            self.table.removeRow(current_row)

    def clear_sale(self):
        self.table.setRowCount(0)
        self.urun_adetleri.clear()
        self.toplam_tutar = 0.0
        self.toplam_display.setText("0.00 TL")

    def complete_sale(self):
        # İşletme adını al
        isletme_adi, ok = QInputDialog.getText(self, 'İşletme Adı', 
                                             'İşletme adını giriniz:')
        if not ok:
            return
            
        # PDF oluştur
        printer = QPrinter()
        printer.setPageSize(QPageSize(QSizeF(79.5, 297), QPageSize.Unit.Millimeter))
        printer.setOutputFormat(QPrinter.OutputFormat.PdfFormat)
        
        # Yazdırma diyaloğunu aç
        dialog = QPrintDialog(printer, self)
        if dialog.exec() != QDialog.DialogCode.Accepted:
            return
            
        # PDF içeriğini oluştur
        painter = QPainter()
        painter.begin(printer)
        
        # Font ayarları
        font = QFont("Arial", 8)
        painter.setFont(font)
        
        # Başlık
        painter.drawText(0, 100, printer.width(), 50,
                        Qt.AlignmentFlag.AlignHCenter, "*** FİŞ ***")
        
        # Ürünleri yazdır
        y = 200
        for barkod, bilgi in self.urun_adetleri.items():
            row = bilgi["row"]
            urun = self.table.item(row, 1).text()
            fiyat = self.table.item(row, 2).text()
            adet = self.table.item(row, 3).text()
            toplam = self.table.item(row, 4).text()
            
            painter.drawText(50, y, f"{urun}")
            painter.drawText(50, y+20, f"{adet} x {fiyat} = {toplam}")
            y += 50
            
        # Toplam tutar
        painter.drawText(50, y+50, f"TOPLAM: {self.toplam_tutar:.2f} TL")
        
        # İşletme adı
        painter.drawText(0, y+100, printer.width(), 50,
                        Qt.AlignmentFlag.AlignHCenter, isletme_adi)
        
        painter.end()
        
        # Satışı temizle
        self.clear_sale()

    def process_cash_payment(self):
        if not self.urun_adetleri:
            QMessageBox.warning(self, "Uyarı", "Sepet boş!")
            return
        
        # Nakit ödeme dialog'u
        dialog = QDialog(self)
        dialog.setWindowTitle("Nakit Ödeme")
        dialog.setModal(True)
        dialog_layout = QVBoxLayout(dialog)
        
        # Toplam tutar gösterimi
        toplam_label = QLabel(f"Toplam Tutar: {self.toplam_tutar:.2f} TL")
        toplam_label.setFont(QFont("Arial", 16, QFont.Weight.Bold))
        dialog_layout.addWidget(toplam_label)
        
        # Alınan para girişi
        alinan_layout = QHBoxLayout()
        alinan_label = QLabel("Alınan Tutar (TL):")
        alinan_label.setFont(QFont("Arial", 12))
        alinan_input = QLineEdit()
        alinan_input.setFont(QFont("Arial", 16))
        alinan_input.setValidator(QDoubleValidator(0.00, 999999.99, 2))
        alinan_layout.addWidget(alinan_label)
        alinan_layout.addWidget(alinan_input)
        dialog_layout.addLayout(alinan_layout)
        
        # Para üstü gösterimi
        para_ustu_label = QLabel("Para Üstü: 0.00 TL")
        para_ustu_label.setFont(QFont("Arial", 16))
        dialog_layout.addWidget(para_ustu_label)
        
        # Para üstü hesaplama fonksiyonu
        def hesapla_para_ustu():
            try:
                alinan = float(alinan_input.text().replace(",", "."))
                para_ustu = alinan - self.toplam_tutar
                if para_ustu >= 0:
                    para_ustu_label.setText(f"Para Üstü: {para_ustu:.2f} TL")
                    para_ustu_label.setStyleSheet("color: #2ecc71;")  # Yeşil
                    self.tamamla_button.setEnabled(True)
                else:
                    para_ustu_label.setText(f"Eksik Ödeme: {abs(para_ustu):.2f} TL")
                    para_ustu_label.setStyleSheet("color: #e74c3c;")  # Kırmızı
                    self.tamamla_button.setEnabled(False)
            except ValueError:
                para_ustu_label.setText("Para Üstü: 0.00 TL")
                para_ustu_label.setStyleSheet("")
                self.tamamla_button.setEnabled(False)
        
        # Alınan para değiştiğinde para üstünü hesapla
        alinan_input.textChanged.connect(hesapla_para_ustu)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        self.tamamla_button = QPushButton("Ürünleri Yazdır")
        self.tamamla_button.setFont(QFont("Arial", 12))
        self.tamamla_button.setEnabled(False)
        self.tamamla_button.clicked.connect(dialog.accept)
        
        self.iptal_button = QPushButton("İptal")
        self.iptal_button.setFont(QFont("Arial", 12))
        self.iptal_button.clicked.connect(dialog.reject)
        
        button_layout.addWidget(self.tamamla_button)
        button_layout.addWidget(self.iptal_button)
        dialog_layout.addLayout(button_layout)
        
        # Dialog'a stil ekle
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f0f0f0;
            }
            QLabel {
                color: #2c3e50;
                margin: 10px 0;
            }
            QLineEdit {
                padding: 8px;
                border: 2px solid #3498db;
                border-radius: 5px;
                background-color: white;
                margin: 10px 0;
            }
            QPushButton {
                padding: 10px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                min-height: 40px;
                min-width: 150px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
            }
        """)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            try:
                alinan = float(alinan_input.text().replace(",", "."))
                para_ustu = alinan - self.toplam_tutar
                
                # Satışları kaydet
                try:
                    for barkod, detay in self.urun_adetleri.items():
                        # Ürün ID'sini al
                        self.cursor.execute("SELECT id FROM urunler WHERE barkod = ?", (barkod,))
                        urun_id = self.cursor.fetchone()[0]
                        
                        # Satış kaydı oluştur
                        self.cursor.execute("""
                            INSERT INTO satislar (urun_id, adet, fiyat, toplam_fiyat, odeme_turu)
                            VALUES (?, ?, ?, ?, ?)
                        """, (urun_id, detay["adet"], detay["fiyat"], detay["adet"] * detay["fiyat"], "Nakit"))
                    
                    self.db.commit()
                    
                    # Satışı tamamla
                    QMessageBox.information(self, "Başarılı", 
                        f"Satış tamamlandı!\nAlınan: {alinan:.2f} TL\nPara Üstü: {para_ustu:.2f} TL")
                    
                    # Sepeti temizle
                    self.clear_sale()
                    
                except sqlite3.Error as e:
                    self.db.rollback()
                    QMessageBox.critical(self, "Hata", f"Veritabanı hatası: {str(e)}")
                
            except ValueError:
                QMessageBox.warning(self, "Hata", "Geçersiz tutar!")

    def process_credit_payment(self):
        if not self.urun_adetleri:
            QMessageBox.warning(self, "Uyarı", "Sepet boş!")
            return
            
        try:
            # Satışları kaydet
            for barkod, detay in self.urun_adetleri.items():
                # Ürün ID'sini al
                self.cursor.execute("SELECT id FROM urunler WHERE barkod = ?", (barkod,))
                urun_id = self.cursor.fetchone()[0]
                
                # Satış kaydı oluştur
                self.cursor.execute("""
                    INSERT INTO satislar (urun_id, adet, fiyat, toplam_fiyat, odeme_turu)
                    VALUES (?, ?, ?, ?, ?)
                """, (urun_id, detay["adet"], detay["fiyat"], detay["adet"] * detay["fiyat"], "Kredi Kartı"))
            
            self.db.commit()
            
            # Satışı tamamla
            QMessageBox.information(self, "Başarılı", "Kredi kartı ile satış tamamlandı!")
            
            # Sepeti temizle
            self.clear_sale()
            
        except sqlite3.Error as e:
            self.db.rollback()
            QMessageBox.critical(self, "Hata", f"Veritabanı hatası: {str(e)}")

    def process_debt_payment(self):
        if not self.urun_adetleri:
            QMessageBox.warning(self, "Uyarı", "Sepet boş!")
            return
        
        # Veritabanı bağlantısını yenile
        self.connect_db()
        
        # Müşteri seçim dialog'u
        dialog = QDialog(self)
        dialog.setWindowTitle("Müşteri Seçimi")
        dialog.setModal(True)
        dialog_layout = QVBoxLayout(dialog)
        
        # Müşteri seçim tablosu
        customer_table = QTableWidget()
        customer_table.setColumnCount(4)
        customer_table.setHorizontalHeaderLabels(["ID", "Müşteri Adı", "Telefon", "Toplam Borç"])
        customer_table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        
        # Müşterileri getir
        try:
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
            
            customer_table.setRowCount(len(customers))
            for row, customer in enumerate(customers):
                for col, value in enumerate(customer):
                    item = QTableWidgetItem(str(value))
                    if col == 3:  # Toplam borç kolonuysa
                        item = QTableWidgetItem(f"{float(value):.2f} TL")
                    customer_table.setItem(row, col, item)
            
            dialog_layout.addWidget(customer_table)
            
            # Butonlar
            button_layout = QHBoxLayout()
            
            select_button = QPushButton("Seç")
            select_button.clicked.connect(dialog.accept)
            
            cancel_button = QPushButton("İptal")
            cancel_button.clicked.connect(dialog.reject)
            
            button_layout.addWidget(select_button)
            button_layout.addWidget(cancel_button)
            
            dialog_layout.addLayout(button_layout)
            
            if dialog.exec() == QDialog.DialogCode.Accepted:
                current_row = customer_table.currentRow()
                if current_row >= 0:
                    musteri_id = int(customer_table.item(current_row, 0).text())
                    musteri_adi = customer_table.item(current_row, 1).text()
                    
                    try:
                        # Her ürün için borç kaydı oluştur
                        for barkod, detay in self.urun_adetleri.items():
                            # Ürün ID'sini al
                            self.cursor.execute("SELECT id FROM urunler WHERE barkod = ?", (barkod,))
                            urun_id = self.cursor.fetchone()[0]
                            
                            # Satış kaydı oluştur
                            self.cursor.execute("""
                                INSERT INTO satislar (urun_id, adet, fiyat, toplam_fiyat, odeme_turu)
                                VALUES (?, ?, ?, ?, ?)
                            """, (urun_id, detay["adet"], detay["fiyat"], detay["adet"] * detay["fiyat"], "Borç"))
                            
                            # Borç kaydı oluştur
                            for _ in range(detay["adet"]):  # Her adet için ayrı kayıt
                                self.cursor.execute("""
                                    INSERT INTO borclar (musteri_id, urun_id, alis_fiyati)
                                    VALUES (?, ?, ?)
                                """, (musteri_id, urun_id, detay["fiyat"]))
                        
                        self.db.commit()
                        
                        QMessageBox.information(self, "Başarılı", 
                            f"Ürünler {musteri_adi} adına borç olarak kaydedildi!")
                        
                        # Sepeti temizle
                        self.clear_sale()
                        
                    except sqlite3.Error as e:
                        self.db.rollback()
                        QMessageBox.critical(self, "Hata", f"Veritabanı hatası: {str(e)}")
                else:
                    QMessageBox.warning(self, "Uyarı", "Lütfen bir müşteri seçin!")
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Hata", f"Veritabanı hatası: {str(e)}")

    def closeEvent(self, event):
        try:
            if self.db:
                self.db.close()
        except:
            pass
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MarketSatis()
    window.show()
    sys.exit(app.exec()) 