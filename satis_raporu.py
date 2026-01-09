import sys
import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QComboBox, QTableWidget, 
                            QTableWidgetItem, QHeaderView, QPushButton, QDateEdit, 
                            QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont

from styles import Styles

class SatisRaporu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Satış Raporu")
        self.setGeometry(100, 100, 1200, 800)
        
        # Veritabanı bağlantısı
        self.connect_db()
        
        # Ana widget ve layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Logo ekle
        Styles.add_logo(main_layout, 80)
        
        # Tarih seçimi
        date_layout = QHBoxLayout()
        
        baslangic_label = QLabel("Başlangıç Tarihi:")
        baslangic_label.setFont(QFont("Arial", 12))
        self.baslangic_date = QDateEdit()
        self.baslangic_date.setFont(QFont("Arial", 12))
        self.baslangic_date.setDate(QDate.currentDate())
        self.baslangic_date.setCalendarPopup(True)
        
        bitis_label = QLabel("Bitiş Tarihi:")
        bitis_label.setFont(QFont("Arial", 12))
        self.bitis_date = QDateEdit()
        self.bitis_date.setFont(QFont("Arial", 12))
        self.bitis_date.setDate(QDate.currentDate())
        self.bitis_date.setCalendarPopup(True)
        
        self.listele_button = QPushButton("Listele")
        self.listele_button.setObjectName("SuccessButton")
        self.listele_button.clicked.connect(self.load_sales)
        
        date_layout.addWidget(baslangic_label)
        date_layout.addWidget(self.baslangic_date)
        date_layout.addWidget(bitis_label)
        date_layout.addWidget(self.bitis_date)
        date_layout.addWidget(self.listele_button)
        date_layout.addStretch()
        
        # Özet bilgiler
        summary_layout = QHBoxLayout()
        
        # Toplam Satış Özeti
        total_group = QGroupBox("Toplam Satış")
        total_group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        total_layout = QVBoxLayout()
        
        self.total_amount_label = QLabel("Toplam Tutar: 0.00 TL")
        self.total_count_label = QLabel("Toplam Satış Adedi: 0")
        self.avg_sale_label = QLabel("Ortalama Satış Tutarı: 0.00 TL")
        
        for label in [self.total_amount_label, self.total_count_label, self.avg_sale_label]:
            label.setFont(QFont("Arial", 12))
            total_layout.addWidget(label)
        
        total_group.setLayout(total_layout)
        
        # Ödeme Türü Dağılımı
        payment_group = QGroupBox("Ödeme Türü Dağılımı")
        payment_group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        payment_layout = QVBoxLayout()
        
        self.cash_label = QLabel("Nakit: %0 (0.00 TL)")
        self.credit_label = QLabel("Kredi Kartı: %0 (0.00 TL)")
        self.debt_label = QLabel("Borç: %0 (0.00 TL)")
        
        for label in [self.cash_label, self.credit_label, self.debt_label]:
            label.setFont(QFont("Arial", 12))
            payment_layout.addWidget(label)
        
        payment_group.setLayout(payment_layout)
        
        # Günlük Özet
        daily_group = QGroupBox("Günlük Özet")
        daily_group.setFont(QFont("Arial", 12, QFont.Weight.Bold))
        daily_layout = QVBoxLayout()
        
        self.daily_amount_label = QLabel("Günlük Ortalama Satış: 0.00 TL")
        self.daily_count_label = QLabel("Günlük Ortalama İşlem: 0")
        self.best_day_label = QLabel("En Yüksek Satış Günü: -")
        
        for label in [self.daily_amount_label, self.daily_count_label, self.best_day_label]:
            label.setFont(QFont("Arial", 12))
            daily_layout.addWidget(label)
        
        daily_group.setLayout(daily_layout)
        
        summary_layout.addWidget(total_group)
        summary_layout.addWidget(payment_group)
        summary_layout.addWidget(daily_group)
        
        # Satış tablosu
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Tarih", "Ürün", "Adet", "Fiyat", "Toplam", "Ödeme Türü"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setFont(QFont("Arial", 12))
        
        # Layout'ları ana layout'a ekle
        main_layout.addLayout(date_layout)
        main_layout.addLayout(summary_layout)
        main_layout.addWidget(self.table)
        
        # Stil - Global stylesheet kullanılıyor
        pass
        
        # İlk yükleme
        self.load_sales()

    def connect_db(self):
        """Veritabanı bağlantısını oluşturur"""
        self.db = sqlite3.connect('market_urunler.db')
        self.cursor = self.db.cursor()
        
        # Satışlar tablosunu oluştur
        self.cursor.execute("""
            CREATE TABLE IF NOT EXISTS satislar (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                urun_id INTEGER,
                adet INTEGER,
                fiyat REAL,
                toplam_fiyat REAL,
                odeme_turu TEXT,
                tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (urun_id) REFERENCES urunler (id)
            )
        """)
        self.db.commit()

    def load_sales(self):
        # Veritabanı bağlantısını yenile
        self.connect_db()
        
        try:
            # Tarih aralığını al
            baslangic = self.baslangic_date.date().toPyDate()
            bitis = self.bitis_date.date().toPyDate() + timedelta(days=1)  # Bitiş gününü de dahil et
            
            # Satışları getir
            self.cursor.execute("""
                SELECT 
                    s.tarih,
                    u.urun_adi,
                    s.adet,
                    s.fiyat,
                    s.toplam_fiyat,
                    s.odeme_turu
                FROM satislar s
                JOIN urunler u ON s.urun_id = u.id
                WHERE s.tarih BETWEEN ? AND ?
                ORDER BY s.tarih DESC
            """, (baslangic, bitis))
            
            sales = self.cursor.fetchall()
            
            # Tabloyu doldur
            self.table.setRowCount(len(sales))
            for row, sale in enumerate(sales):
                # Tarih formatını düzenle
                tarih = datetime.strptime(sale[0], "%Y-%m-%d %H:%M:%S").strftime("%d.%m.%Y %H:%M")
                self.table.setItem(row, 0, QTableWidgetItem(tarih))
                
                # Diğer bilgiler
                self.table.setItem(row, 1, QTableWidgetItem(sale[1]))  # Ürün adı
                self.table.setItem(row, 2, QTableWidgetItem(str(sale[2])))  # Adet
                self.table.setItem(row, 3, QTableWidgetItem(f"{sale[3]:.2f} TL"))  # Fiyat
                self.table.setItem(row, 4, QTableWidgetItem(f"{sale[4]:.2f} TL"))  # Toplam
                self.table.setItem(row, 5, QTableWidgetItem(sale[5]))  # Ödeme türü
            
            # Özet bilgileri hesapla ve güncelle
            self.update_summary(sales, baslangic, bitis)
            
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Hata", f"Veritabanı hatası: {str(e)}")

    def update_summary(self, sales, baslangic, bitis):
        if not sales:
            return
        
        # Toplam satış bilgileri
        total_amount = sum(sale[4] for sale in sales)  # toplam_fiyat
        total_count = len(sales)
        avg_sale = total_amount / total_count
        
        self.total_amount_label.setText(f"Toplam Tutar: {total_amount:.2f} TL")
        self.total_count_label.setText(f"Toplam Satış Adedi: {total_count}")
        self.avg_sale_label.setText(f"Ortalama Satış Tutarı: {avg_sale:.2f} TL")
        
        # Ödeme türü dağılımı
        cash_sales = sum(sale[4] for sale in sales if sale[5] == "Nakit")
        credit_sales = sum(sale[4] for sale in sales if sale[5] == "Kredi Kartı")
        debt_sales = sum(sale[4] for sale in sales if sale[5] == "Borç")
        
        cash_percent = (cash_sales / total_amount) * 100 if total_amount > 0 else 0
        credit_percent = (credit_sales / total_amount) * 100 if total_amount > 0 else 0
        debt_percent = (debt_sales / total_amount) * 100 if total_amount > 0 else 0
        
        self.cash_label.setText(f"Nakit: %{cash_percent:.1f} ({cash_sales:.2f} TL)")
        self.credit_label.setText(f"Kredi Kartı: %{credit_percent:.1f} ({credit_sales:.2f} TL)")
        self.debt_label.setText(f"Borç: %{debt_percent:.1f} ({debt_sales:.2f} TL)")
        
        # Günlük satış bilgileri
        days = (bitis - baslangic).days
        if days < 1:
            days = 1
        
        daily_avg_amount = total_amount / days
        daily_avg_count = total_count / days
        
        self.daily_amount_label.setText(f"Günlük Ortalama Satış: {daily_avg_amount:.2f} TL")
        self.daily_count_label.setText(f"Günlük Ortalama İşlem: {daily_avg_count:.1f}")
        
        # En yüksek satış günü
        daily_totals = {}
        for sale in sales:
            date = datetime.strptime(sale[0], "%Y-%m-%d %H:%M:%S").date()
            daily_totals[date] = daily_totals.get(date, 0) + sale[4]
        
        if daily_totals:
            best_day = max(daily_totals.items(), key=lambda x: x[1])
            self.best_day_label.setText(
                f"En Yüksek Satış Günü: {best_day[0].strftime('%d.%m.%Y')} ({best_day[1]:.2f} TL)")

    def closeEvent(self, event):
        self.db.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SatisRaporu()
    window.show()
    sys.exit(app.exec()) 