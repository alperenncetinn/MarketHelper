import sys
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, 
                            QVBoxLayout, QPushButton)
from PyQt6.QtGui import QFont
from market_satis import MarketSatis
from urun_yonetimi import UrunYonetimi
from satis_raporu import SatisRaporu
from borc_defteri import BorcDefteri
from etiket_yazdir import EtiketYazdir

class MainMenu(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Market Otomasyonu")
        self.setGeometry(100, 100, 400, 500)
        
        # Ana widget ve layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Satış sayfası butonu
        self.satis_button = QPushButton("Satış Sayfası")
        self.satis_button.setFont(QFont("Arial", 14))
        self.satis_button.clicked.connect(self.open_satis)
        
        # Ürün yönetimi butonu
        self.urun_button = QPushButton("Ürün Yönetimi")
        self.urun_button.setFont(QFont("Arial", 14))
        self.urun_button.clicked.connect(self.open_urun)
        
        # Satış raporu butonu
        self.rapor_button = QPushButton("Satış Raporu")
        self.rapor_button.setFont(QFont("Arial", 14))
        self.rapor_button.clicked.connect(self.open_rapor)
        
        # Borç defteri butonu
        self.borc_button = QPushButton("Borç Defteri")
        self.borc_button.setFont(QFont("Arial", 14))
        self.borc_button.clicked.connect(self.open_borc)
        
        # Etiket yazdırma butonu
        self.etiket_button = QPushButton("Etiket Yazdır")
        self.etiket_button.setFont(QFont("Arial", 14))
        self.etiket_button.clicked.connect(self.open_etiket)
        
        # Butonları layout'a ekle
        layout.addWidget(self.satis_button)
        layout.addWidget(self.urun_button)
        layout.addWidget(self.rapor_button)
        layout.addWidget(self.borc_button)
        layout.addWidget(self.etiket_button)
        
        # Stil
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f0f0f0;
            }
            QPushButton {
                padding: 20px;
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 10px;
                margin: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        
        # Pencere örnekleri
        self.satis_window = None
        self.urun_window = None
        self.rapor_window = None
        self.borc_window = None
        self.etiket_window = None
    
    def open_satis(self):
        if not self.satis_window:
            self.satis_window = MarketSatis()
        self.satis_window.show()
    
    def open_urun(self):
        if not self.urun_window:
            self.urun_window = UrunYonetimi()
        self.urun_window.show()
    
    def open_rapor(self):
        if not self.rapor_window:
            self.rapor_window = SatisRaporu()
        self.rapor_window.show()
    
    def open_borc(self):
        if not self.borc_window:
            self.borc_window = BorcDefteri()
        self.borc_window.show()
    
    def open_etiket(self):
        if not self.etiket_window:
            self.etiket_window = EtiketYazdir()
        self.etiket_window.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = MainMenu()
    window.show()
    sys.exit(app.exec()) 