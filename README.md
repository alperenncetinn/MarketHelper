# Market Otomasyon Sistemi (MarketHelper)

Modern, kullanımı kolay ve **Yapay Zeka (AI)** destekli masaüstü market satış ve yönetim sistemi. Küçük ve orta ölçekli işletmeler için tasarlanmış, "Dark Theme" (Koyu Tema) ve "High Contrast" (Yüksek Kontrast) prensipleriyle geliştirilmiş kullanıcı dostu bir arayüze sahiptir.

![Python](https://img.shields.io/badge/Python-3.13+-3776AB?style=for-the-badge&logo=python&logoColor=white)
![PyQt6](https://img.shields.io/badge/PyQt6-GUI-41CD52?style=for-the-badge&logo=qt&logoColor=white)
![AI](https://img.shields.io/badge/AI-Scikit--Learn-F7931E?style=for-the-badge&logo=scikit-learn&logoColor=white)

## 🚀 Özellikler

### 🛒 Market Satış (POS) Ekranı
*   **Hızlı Satış**: Barkod okuyucu desteği ile seri ürün ekleme.
*   **Ergonomik Tasarım**: Fitts Kanunu'na uygun yerleşim, büyük butonlar ve dokunmatik dostu arayüz.
*   **Görsel Geri Bildirim**: Başarılı okutmada mavi, hatada kırmızı ekran flaşı.
*   **Ödeme Seçenekleri**: Nakit, Kredi Kartı ve Veresiye (Borç) satış imkanı.

### 🤖 Yapay Zeka (AI) Modülleri
Projeyi diğerlerinden ayıran akıllı özellikler:
1.  **Gelecek Satış Tahmini**: Geçmiş verileri analiz ederek (Lineer Regresyon) gelecek 7 günün ciro tahminini yapar ve grafiksel olarak sunar.
2.  **Müşteri Güvenilirlik Analizi**: Veresiye müşterilerinin ödeme alışkanlıklarını analiz eder. Müşterileri "Güvenilir (A+)", "Standart (B)" veya "Riskli (C-)" olarak sınıflandırır.
3.  **Model Doğruluk Skoru**: Yapılan tahminlerin güvenilirliğini (R² Score) kullanıcıya bildirir.

### 📦 Ürün ve Stok Yönetimi
*   Ürün ekleme, silme ve düzenleme.
*   Kritik stok seviyesi takibi.
*   Hızlı ürün arama ve filtreleme.

### 📒 Borç Defteri
*   Müşteri kayıt ve bakiye takibi.
*   Detaylı borç geçmişi görüntüleme.
*   Parçalı veya tam tahsilat işlemleri.
*   **AI Destekli Risk Göstergesi**: Riskli müşteriler için görsel uyarılar.

### 📊 Raporlama ve Etiket
*   Günlük detaylı satış raporları.
*   Ciro ve ödeme yöntemi dağılım grafikleri.
*   Ürünler için barkodlu raf etiketi (PDF) oluşturma.

## 🛠️ Kurulum

Proje Python tabanlıdır. Çalıştırmak için aşağıdaki adımları izleyin:

1.  **Depoyu Klonlayın** (veya indirin):
    ```bash
    git clone https://github.com/alperenncetinn/MarketHelper.git
    cd MarketHelper
    ```

2.  **Gerekli Kütüphaneleri Yükleyin**:
    ```bash
    pip install -r requirements.txt
    ```
    *Gereksinimler: PyQt6, pandas, scikit-learn, matplotlib, python-barcode, reportlab*

3.  **Uygulamayı Başlatın**:
    ```bash
    python3 main.py
    ```

## 💻 Kullanılan Teknolojiler

*   **Programlama Dili**: Python 3
*   **Arayüz (GUI)**: PyQt6
*   **Veritabanı**: SQLite
*   **Veri Analizi & AI**: Scikit-learn, Pandas, NumPy
*   **Görselleştirme**: Matplotlib
*   **Raporlama**: ReportLab

## 🎨 Tasarım Prensipleri

Uygulama, uzun süreli kullanımlarda göz yorgunluğunu azaltmak için **Koyu Gece Mavisi (#0F172A)** arka plan ve canlı **Aksiyon Mavisi (#3B82F6)** renk paleti ile tasarlanmıştır.

---
Geliştirici: **Alperen**
