
import sqlite3
import pandas as pd
import numpy as np
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import PolynomialFeatures
from datetime import datetime, timedelta

class MarketAI:
    def __init__(self, db_path='market_urunler.db'):
        self.db_path = db_path
        self.model = None
        self.poly = PolynomialFeatures(degree=2) # 2. derece polinom daha iyi trend yakalar

    def get_sales_data(self):
        """Veritabanından satış verilerini çeker ve günlük olarak gruplar."""
        try:
            conn = sqlite3.connect(self.db_path)
            # Tarih formatı timestamp olduğu için (YYYY-MM-DD HH:MM:SS), gün bazında grupluyoruz
            query = """
                SELECT 
                    date(tarih) as gun, 
                    SUM(toplam_fiyat) as ciro 
                FROM satislar 
                GROUP BY gun 
                ORDER BY gun ASC
            """
            df = pd.read_sql_query(query, conn)
            conn.close()
            
            if df.empty:
                return pd.DataFrame()
                
            df['gun'] = pd.to_datetime(df['gun'])
            # Tarihi sayısal değere çevir (Ordinal)
            df['gun_ordinal'] = df['gun'].apply(lambda x: x.toordinal())
            return df
        except Exception as e:
            print(f"Veri çekme hatası: {e}")
            return pd.DataFrame()

    def train_model(self):
        """Mevcut veri ile modeli eğitir."""
        df = self.get_sales_data()
        if df.empty or len(df) < 5: # En az 5 günlük veri olsun ki mantıklı olsun
            return False, "Yetersiz veri (En az 5 gün gerekli)"

        X = df[['gun_ordinal']]
        y = df['ciro']
        
        X_poly = self.poly.fit_transform(X)
        
        self.model = LinearRegression()
        self.model.fit(X_poly, y)
        
        # Doğruluk skoru (R^2)
        score = self.model.score(X_poly, y)
        
        return True, f"Model eğitildi. Doğruluk (R²): {score:.4f}", score

    def predict_next_days(self, days=7):
        """Gelecek n günün tahminini yapar."""
        score = 0.0
        if not self.model:
            status, msg, score = self.train_model()
            if not status:
                return None, 0.0
        else:
             # Model zaten varsa skoru tekrar hesapla veya sakla. Şimdilik yeniden eğitim yapalım garanti olsun
             status, msg, score = self.train_model()
            
        last_date = datetime.now()
        predictions = []
        
        for i in range(1, days + 1):
            next_date = last_date + timedelta(days=i)
            next_date_ordinal = next_date.toordinal()
            
            # Tahmin yap
            X_pred = np.array([[next_date_ordinal]])
            X_pred_poly = self.poly.transform(X_pred)
            predicted_sales = self.model.predict(X_pred_poly)[0]
            
            # Negatif tahminleri 0'a çek
            predicted_sales = max(0, predicted_sales)
            
            predictions.append({
                'tarih': next_date.strftime("%d.%m.%Y"),
                'tahmin': round(predicted_sales, 2),
                'gun': next_date.strftime("%A") # Hangi gün olduğu (İngilizce dönebilir, TR için map gerekebilir)
            })
            
        return predictions, score

    def get_trend_analysis(self):
        """Trend analizi: Artıyor mu azalıyor mu?"""
        if not self.model:
            return "Veri yok"
            
        # Son gün ve bir sonraki gün tahminine bak
        today_ordinal = datetime.now().toordinal()
        tomorrow_ordinal = today_ordinal + 1
        
        X_today = self.poly.transform([[today_ordinal]])
        X_tomorrow = self.poly.transform([[tomorrow_ordinal]])
        
        pred_today = self.model.predict(X_today)[0]
        pred_tomorrow = self.model.predict(X_tomorrow)[0]
        
        if pred_tomorrow > pred_today:
            return "ARTIŞ (#2ecc71)" # Yeşil
        elif pred_tomorrow < pred_today:
            return "AZALIŞ (#e74c3c)" # Kırmızı
        else:
            return "STABİL (#3498db)" # Mavi

    def generate_dummy_data_if_empty(self):
        """Demo amaçlı sahte veri oluşturur (Eğer hiç veri yoksa)"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Kontrol et
        cursor.execute("SELECT count(*) FROM satislar")
        count = cursor.fetchone()[0]
        
        if count < 10:
            print("AI: Yetersiz veri tespit edildi, demo verileri oluşturuluyor...")
            import random
            
            # Rastgele ürün ID'leri bul
            cursor.execute("SELECT id, fiyat FROM urunler")
            products = cursor.fetchall()
            if not products:
                # Ürün bile yoksa yapacak bir şey yok
                conn.close()
                return
            
            # Son 30 gün için veri üret
            for i in range(30):
                date = datetime.now() - timedelta(days=30-i)
                date_str = date.strftime("%Y-%m-%d %H:%M:%S")
                
                # Günde 5-20 satış olsun
                daily_sales_count = random.randint(5, 20)
                
                for _ in range(daily_sales_count):
                    prod = random.choice(products)
                    p_id = prod[0]
                    p_price = prod[1]
                    adet = random.randint(1, 5)
                    total = p_price * adet
                    
                    cursor.execute("""
                        INSERT INTO satislar (urun_id, adet, fiyat, toplam_fiyat, odeme_turu, tarih)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (p_id, adet, p_price, total, "Nakit", date_str))
            
            conn.commit()
            print("AI: Demo verileri eklendi.")
            
        conn.close()

    def analyze_customer_reliability(self, customer_id):
        """Müşterinin borç ödeme alışkanlığına göre güvenilirlik analizi yapar."""
        try:
            conn = sqlite3.connect(self.db_path)
            cursor = conn.cursor()
            
            # Toplam borç ve ödenen miktar
            cursor.execute("""
                SELECT 
                    SUM(alis_fiyati) as toplam_borc,
                    SUM(CASE WHEN odendi = 1 THEN alis_fiyati ELSE 0 END) as odenen
                FROM borclar 
                WHERE musteri_id = ?
            """, (customer_id,))
            
            result = cursor.fetchone()
            conn.close()
            
            if not result or result[0] is None:
                return "Veri Yok", "#95a5a6" # Gri
                
            total_debt = result[0]
            paid_debt = result[1]
            
            if total_debt == 0:
                return "Borçsuz Müşteri", "#2ecc71" # Yeşil
                
            payment_ratio = paid_debt / total_debt
            
            if payment_ratio >= 0.8:
                return "Güvenilir Müşteri (A+)", "#2ecc71" # Yeşil
            elif payment_ratio >= 0.5:
                return "Standart Müşteri (B)", "#f1c40f" # Sarı
            else:
                return "Riskli Müşteri (C-)", "#e74c3c" # Kırmızı
                
        except Exception as e:
            print(f"Analiz Hatası: {e}")
            return "Hata", "#95a5a6"
