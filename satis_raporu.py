import sys
import sqlite3
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QTableWidget, QTableWidgetItem, QHeaderView, QDateEdit,
                            QTabWidget, QFrame, QGroupBox, QMessageBox)
from PyQt6.QtCore import Qt, QDate
from PyQt6.QtGui import QFont, QColor
from datetime import datetime, timedelta

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt

from styles import Styles
from market_ai import MarketAI

class SatisRaporu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Satış Raporu ve AI Analizi")
        self.setGeometry(100, 100, 1200, 800)
        
        # AI Motorunu Başlat
        self.ai = MarketAI()
        self.ai.generate_dummy_data_if_empty() # Demo için veri yoksa oluştur
        
        # Veritabanı bağlantısı
        self.connect_db()
        
        # Ana widget ve layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        main_layout = QVBoxLayout(main_widget)
        
        # Logo ekle
        Styles.add_logo(main_layout, 80)
        
        # TAB WIDGET (Raporlar ve AI Tahminleri)
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane { border: 1px solid #334155; }
            QTabBar::tab { background: #1e293b; color: #94a3b8; padding: 10px 20px; }
            QTabBar::tab:selected { background: #3b82f6; color: white; font-weight: bold; }
        """)
        
        # --- TAB 1: KLASİK RAPORLAR ---
        self.tab_report = QWidget()
        self.setup_report_tab()
        self.tabs.addTab(self.tab_report, "Günlük Satışlar")
        
        # --- TAB 2: AI TAHMİN ---
        self.tab_ai = QWidget()
        self.setup_ai_tab()
        self.tabs.addTab(self.tab_ai, "✨ Yapay Zeka Tahmini")
        
        main_layout.addWidget(self.tabs)
        
        # İlk listeleme
        self.load_sales()

    def setup_report_tab(self):
        layout = QVBoxLayout(self.tab_report)
        
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
        
        layout.addLayout(date_layout)
        
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
        summary_layout.addWidget(total_group)
        
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
        summary_layout.addWidget(payment_group)

        layout.addLayout(summary_layout)
        
        # Satış tablosu
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels(["Tarih", "Ürün", "Adet", "Fiyat", "Toplam", "Ödeme Türü"])
        self.table.horizontalHeader().setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch)
        self.table.setFont(QFont("Arial", 12))
        layout.addWidget(self.table)

    def setup_ai_tab(self):
        layout = QVBoxLayout(self.tab_ai)
        
        # Üst Bilgi
        info_label = QLabel("Bu bölüm, geçmiş verileri analiz ederek gelecek günlerin satış tahminlerini yapar.")
        info_label.setStyleSheet("color: #94a3b8; font-style: italic;")
        layout.addWidget(info_label)
        
        # Tahmin Butonu
        btn_predict = QPushButton("ANALİZ ET VE TAHMİN OLUŞTUR")
        btn_predict.setObjectName("PrimaryButton")
        btn_predict.clicked.connect(self.run_ai_prediction)
        layout.addWidget(btn_predict)
        
        # Sonuçlar Alanı
        results_layout = QHBoxLayout()
        
        # Sol: Liste
        self.ai_table = QTableWidget()
        self.ai_table.setColumnCount(2)
        self.ai_table.setHorizontalHeaderLabels(["Tarih", "Tahmini Ciro (TL)"])
        self.ai_table.horizontalHeader().setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        results_layout.addWidget(self.ai_table, 1)
        
        # Sağ: Grafik
        self.figure = Figure(figsize=(5, 4), dpi=100, facecolor=Styles.COLOR_SURFACE)
        self.canvas = FigureCanvas(self.figure)
        results_layout.addWidget(self.canvas, 2)
        
        layout.addLayout(results_layout)
        
        # Trend Göstergesi
        self.trend_label = QLabel("Trend: Analiz bekleniyor...")
        self.trend_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.trend_label.setStyleSheet("font-size: 24px; font-weight: bold; margin-top: 10px;")
        layout.addWidget(self.trend_label)
        
        # Doğruluk Skoru
        self.score_label = QLabel("Model Doğruluğu: -")
        self.score_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.score_label.setStyleSheet("color: #94a3b8; font-size: 14px; margin-top: 5px;")
        layout.addWidget(self.score_label)

    def run_ai_prediction(self):
        predictions, score = self.ai.predict_next_days(7)
        
        if not predictions:
            self.ai_table.setRowCount(0)
            self.trend_label.setText("Yetersiz Veri - Tahmin Yapılamadı")
            self.score_label.setText("Model Doğruluğu: Hesaplanamadı")
            return
            
        # Tabloyu Doldur
        self.ai_table.setRowCount(len(predictions))
        dates = []
        values = []
        
        for i, pred in enumerate(predictions):
            self.ai_table.setItem(i, 0, QTableWidgetItem(f"{pred['tarih']} ({pred['gun']})"))
            self.ai_table.setItem(i, 1, QTableWidgetItem(f"{pred['tahmin']:.2f} TL"))
            dates.append(pred['tarih'][:5]) # Sadece gün.ay
            values.append(pred['tahmin'])
            
        # Trendi Göster
        trend_status = self.ai.get_trend_analysis()
        color = trend_status.split("(")[1].strip(")")
        text = trend_status.split("(")[0]
        self.trend_label.setText(f"TREND: {text}")
        self.trend_label.setStyleSheet(f"font-size: 24px; font-weight: bold; margin-top: 10px; color: {color};")
        
        # Skoru Göster
        self.score_label.setText(f"Model Doğruluğu (R²): {score:.4f} (1.00 üzerinden)")
        if score > 0.7:
             self.score_label.setStyleSheet("color: #2ecc71; font-size: 14px; margin-top: 5px; font-weight: bold;")
        elif score > 0.4:
             self.score_label.setStyleSheet("color: #f1c40f; font-size: 14px; margin-top: 5px;")
        else:
             self.score_label.setStyleSheet("color: #e74c3c; font-size: 14px; margin-top: 5px;")
            
        # Grafiği Çiz
        self.figure.clear()
        ax = self.figure.add_subplot(111)
        ax.set_facecolor(Styles.COLOR_SURFACE) # Grafik zemini koyu
        
        # Çizgi
        ax.plot(dates, values, marker='o', linestyle='-', color='#3b82f6', linewidth=3, label='Tahmin')
        
        # Alanı doldur
        ax.fill_between(dates, values, alpha=0.3, color='#3b82f6')
        
        ax.set_title("Gelecek 7 Günün Satış Tahmini", color='white', fontsize=14)
        ax.set_ylabel("Ciro (TL)", color='white')
        
        # Eksen renkleri
        ax.tick_params(axis='x', colors='#94a3b8')
        ax.tick_params(axis='y', colors='#94a3b8')
        ax.spines['bottom'].set_color('#334155')
        ax.spines['top'].set_color('none') 
        ax.spines['right'].set_color('none')
        ax.spines['left'].set_color('#334155')
        
        # Değerleri noktaların üzerine yaz
        for i, v in enumerate(values):
            ax.text(i, v + (max(values)*0.05), f"{int(v)}", color='white', ha='center')
        
        self.canvas.draw()

    def connect_db(self):
        self.db = sqlite3.connect('market_urunler.db')
        self.cursor = self.db.cursor()

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

    def closeEvent(self, event):
        self.db.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = SatisRaporu()
    window.show()
    sys.exit(app.exec())