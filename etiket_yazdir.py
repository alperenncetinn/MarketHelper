import sys
import barcode
from barcode.writer import ImageWriter
from reportlab.pdfgen import canvas
from reportlab.lib.units import mm
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                            QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                            QMessageBox, QFileDialog)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
import sqlite3
import os
import tempfile

from styles import Styles

class EtiketYazdir(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Etiket Yazdır")
        self.setGeometry(100, 100, 400, 350) 
        
        # Veritabanı bağlantısı
        self.connect_db()
        
        # Ana widget ve layout
        main_widget = QWidget()
        self.setCentralWidget(main_widget)
        layout = QVBoxLayout(main_widget)
        
        # Logo ekle
        Styles.add_logo(layout, 100)
        
        # Barkod girişi
        barkod_layout = QHBoxLayout()
        barkod_label = QLabel("Barkod:")
        barkod_label.setFont(QFont("Arial", 12))
        self.barkod_input = QLineEdit()
        self.barkod_input.setFont(QFont("Arial", 12))
        self.barkod_input.setFixedHeight(40)
        self.barkod_input.returnPressed.connect(self.print_label)
        barkod_layout.addWidget(barkod_label)
        barkod_layout.addWidget(self.barkod_input)
        
        # Butonlar
        button_layout = QHBoxLayout()
        
        # Yazdır butonu
        # Yazdır butonu
        self.yazdir_button = QPushButton("Yazdır")
        self.yazdir_button.setObjectName("SuccessButton")
        self.yazdir_button.clicked.connect(self.print_label)
        
        # PDF Kaydet butonu
        self.pdf_button = QPushButton("PDF Kaydet")
        self.pdf_button.setObjectName("NeutralButton")
        self.pdf_button.clicked.connect(self.save_as_pdf)
        
        button_layout.addWidget(self.yazdir_button)
        button_layout.addWidget(self.pdf_button)
        
        # Layout'a ekle
        layout.addLayout(barkod_layout)
        layout.addLayout(button_layout)
        
        # Stil - Global stylesheet kullanılıyor
        pass

    def connect_db(self):
        """Veritabanı bağlantısını oluşturur"""
        self.db = sqlite3.connect('market_urunler.db')
        self.cursor = self.db.cursor()

    def get_product_info(self, barkod):
        """Barkoda göre ürün bilgilerini getirir"""
        try:
            self.cursor.execute("""
                SELECT urun_adi, fiyat
                FROM urunler
                WHERE barkod = ?
            """, (barkod,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            QMessageBox.critical(self, "Hata", f"Veritabanı hatası: {str(e)}")
            return None

    def create_barcode_image(self, barkod):
        """Barkod görüntüsü oluşturur"""
        try:
            # Geçici dosya oluştur
            temp_dir = tempfile.gettempdir()
            barcode_path = os.path.join(temp_dir, f"barcode_{barkod}")
            
            # Barkod oluştur
            EAN = barcode.get_barcode_class('ean13')
            ean = EAN(barkod, writer=ImageWriter())
            
            # Barkodu kaydet
            ean.save(barcode_path)
            
            return f"{barcode_path}.png"
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"Barkod oluşturma hatası: {str(e)}")
            return None

    def create_label_pdf(self, barkod, urun_adi, fiyat, barcode_image):
        """Etiket PDF'i oluşturur"""
        try:
            # Geçici dosya oluştur
            temp_dir = tempfile.gettempdir()
            pdf_path = os.path.join(temp_dir, f"etiket_{barkod}.pdf")
            
            # PDF oluştur
            c = canvas.Canvas(pdf_path, pagesize=(80*mm, 40*mm))
            
            # Ürün adı
            c.setFont("Helvetica", 10)
            c.drawString(5*mm, 30*mm, urun_adi)
            
            # Fiyat (büyük boyutta)
            c.setFont("Helvetica-Bold", 20)
            c.drawString(5*mm, 15*mm, f"{fiyat:.2f} TL")
            
            # Barkod
            c.drawImage(barcode_image, 5*mm, 2*mm, width=70*mm, height=10*mm)
            
            c.save()
            return pdf_path
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"PDF oluşturma hatası: {str(e)}")
            return None

    def save_as_pdf(self):
        """Etiketi PDF olarak kaydeder"""
        barkod = self.barkod_input.text().strip()
        if not barkod:
            QMessageBox.warning(self, "Uyarı", "Lütfen barkod girin!")
            return
        
        # Ürün bilgilerini al
        product_info = self.get_product_info(barkod)
        if not product_info:
            QMessageBox.warning(self, "Uyarı", "Ürün bulunamadı!")
            return
        
        urun_adi, fiyat = product_info
        
        # Barkod görüntüsü oluştur
        barcode_image = self.create_barcode_image(barkod)
        if not barcode_image:
            return
        
        try:
            # Kayıt yolu seç
            file_name = f"etiket_{barkod}_{urun_adi.replace(' ', '_')}.pdf"
            save_path, _ = QFileDialog.getSaveFileName(
                self,
                "PDF Kaydet",
                file_name,
                "PDF Dosyası (*.pdf)"
            )
            
            if save_path:
                # PDF oluştur
                c = canvas.Canvas(save_path, pagesize=(80*mm, 40*mm))
                
                # Ürün adı
                c.setFont("Helvetica", 10)
                c.drawString(5*mm, 30*mm, urun_adi)
                
                # Fiyat (büyük boyutta)
                c.setFont("Helvetica-Bold", 20)
                c.drawString(5*mm, 15*mm, f"{fiyat:.2f} TL")
                
                # Barkod
                c.drawImage(barcode_image, 5*mm, 2*mm, width=70*mm, height=10*mm)
                
                c.save()
                
                QMessageBox.information(self, "Başarılı", "PDF başarıyla kaydedildi!")
                
                # Input'u temizle
                self.barkod_input.clear()
            
            # Geçici barkod dosyasını temizle
            os.remove(barcode_image)
            
        except Exception as e:
            QMessageBox.critical(self, "Hata", f"PDF kaydetme hatası: {str(e)}")

    def print_label(self):
        """Etiketi yazdırır"""
        barkod = self.barkod_input.text().strip()
        if not barkod:
            QMessageBox.warning(self, "Uyarı", "Lütfen barkod girin!")
            return
        
        # Ürün bilgilerini al
        product_info = self.get_product_info(barkod)
        if not product_info:
            QMessageBox.warning(self, "Uyarı", "Ürün bulunamadı!")
            return
        
        urun_adi, fiyat = product_info
        
        # Barkod görüntüsü oluştur
        barcode_image = self.create_barcode_image(barkod)
        if not barcode_image:
            return
        
        # PDF oluştur
        pdf_path = self.create_label_pdf(barkod, urun_adi, fiyat, barcode_image)
        if not pdf_path:
            return
        
        try:
            # PDF'i varsayılan yazıcıda yazdır
            if sys.platform == 'darwin':  # macOS
                result = os.system(f'lpr "{pdf_path}"')
                if result != 0:  # Yazdırma başarısız olduysa
                    raise Exception("Yazıcı bulunamadı")
            elif sys.platform == 'win32':  # Windows
                result = os.system(f'print "{pdf_path}"')
                if result != 0:  # Yazdırma başarısız olduysa
                    raise Exception("Yazıcı bulunamadı")
            else:  # Linux
                result = os.system(f'lpr "{pdf_path}"')
                if result != 0:  # Yazdırma başarısız olduysa
                    raise Exception("Yazıcı bulunamadı")
            
            QMessageBox.information(self, "Başarılı", "Etiket yazdırma işlemi başarılı!")
            
            # Input'u temizle
            self.barkod_input.clear()
            
        except Exception as e:
            # Yazdırma başarısız olduysa PDF kaydetme seçeneği sun
            reply = QMessageBox.question(
                self,
                "Yazdırma Hatası",
                "Yazıcıya erişilemedi. PDF olarak kaydetmek ister misiniz?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
            )
            
            if reply == QMessageBox.StandardButton.Yes:
                self.save_as_pdf()
        
        finally:
            # Geçici dosyaları temizle
            try:
                os.remove(barcode_image)
                os.remove(pdf_path)
            except:
                pass

    def closeEvent(self, event):
        self.db.close()
        event.accept()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EtiketYazdir()
    window.show()
    sys.exit(app.exec()) 