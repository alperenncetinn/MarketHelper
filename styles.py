
class Styles:
    @staticmethod
    def add_logo(layout, size=100):
        """Adds the application logo to the given layout."""
        import os
        from PyQt6.QtWidgets import QLabel
        from PyQt6.QtGui import QPixmap
        from PyQt6.QtCore import Qt

        logo_label = QLabel()
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Resim yolunu dinamik olarak bul
        current_dir = os.path.dirname(os.path.abspath(__file__))
        logo_path = os.path.join(current_dir, "..", "images", "400*400-logo-blue-theme.png")
        
        if os.path.exists(logo_path):
            pixmap = QPixmap(logo_path)
            # Logoyu makul bir boyuta ölçekle
            scaled_pixmap = pixmap.scaled(size, size, Qt.AspectRatioMode.KeepAspectRatio, Qt.TransformationMode.SmoothTransformation)
            logo_label.setPixmap(scaled_pixmap)
            layout.addWidget(logo_label)
            return True
        return False

    # Renk Paleti
    COLOR_BACKGROUND = "#0F172A"  # Koyu Gece Mavisi / Slate 900
    COLOR_SURFACE = "#1E293B"     # Slate 800
    COLOR_PRIMARY = "#3B82F6"     # Canlı Mavi
    COLOR_SECONDARY = "#334155"   # Slate 700
    COLOR_TEXT = "#F8FAFC"        # Slate 50
    COLOR_TEXT_MUTED = "#94A3B8"  # Slate 400
    COLOR_WARNING = "#F59E0B"     # Amber 500
    COLOR_ERROR = "#EF4444"       # Red 500
    COLOR_SUCCESS = "#10B981"     # Emerald 500
    COLOR_HIGHLIGHT = "rgba(59, 130, 246, 0.3)" # Saydam Mavi

    POS_THEME = f"""
    /* General App Styling */
    QApplication {{
        font-family: 'Roboto', 'Segoe UI', sans-serif;
    }}

    QMainWindow, QDialog, QWidget {{
        background-color: {COLOR_BACKGROUND};
        color: {COLOR_TEXT};
    }}

    /* Labels */
    QLabel {{
        color: {COLOR_TEXT};
        font-size: 16px;
    }}
    
    QLabel#Header {{
        font-size: 28px;
        font-weight: bold;
        color: {COLOR_PRIMARY};
        margin-bottom: 20px;
    }}
    
    QLabel#TotalDisplay {{
        background-color: {COLOR_SURFACE};
        color: {COLOR_SUCCESS};
        border: 2px solid {COLOR_PRIMARY};
        border-radius: 4px;
        padding: 20px;
        font-family: 'Roboto Mono', monospace;
    }}

    /* Inputs */
    QLineEdit {{
        background-color: {COLOR_SURFACE};
        border: 2px solid {COLOR_SECONDARY};
        border-radius: 4px;
        color: {COLOR_TEXT};
        padding: 10px;
        font-size: 18px;
        font-family: 'Roboto Mono', monospace;
    }}
    
    QLineEdit:focus {{
        border: 2px solid {COLOR_PRIMARY};
    }}

    /* Buttons - Flat & Matte */
    QPushButton {{
        background-color: {COLOR_SURFACE};
        color: {COLOR_TEXT};
        border: 1px solid {COLOR_SECONDARY};
        border-radius: 4px;
        padding: 15px;
        font-weight: bold;
        font-size: 16px;
        text-transform: uppercase;
    }}
    
    QPushButton:hover {{
        background-color: {COLOR_SECONDARY};
        border-color: {COLOR_TEXT_MUTED};
    }}
    
    QPushButton:pressed {{
        background-color: {COLOR_PRIMARY};
        color: white;
    }}

    /* Primary Action Buttons (Payment, Enter) */
    QPushButton[objectName="PrimaryButton"] {{
        background-color: {COLOR_PRIMARY};
        color: white;
        border: none;
        font-size: 24px;
        font-weight: 900;
    }}
    
    QPushButton[objectName="PrimaryButton"]:hover {{
        background-color: #2563EB; /* Slightly Darker Blue */
    }}

    /* Danger Actions */
    QPushButton[objectName="DeleteButton"], QPushButton[objectName="CancelButton"] {{
        background-color: {COLOR_SURFACE};
        color: {COLOR_ERROR};
        border: 1px solid {COLOR_ERROR};
    }}
    
    QPushButton[objectName="DeleteButton"]:hover, QPushButton[objectName="CancelButton"]:hover {{
        background-color: {COLOR_ERROR};
        color: white;
    }}

    /* Tables */
    QTableWidget {{
        background-color: {COLOR_SURFACE};
        gridline-color: {COLOR_SECONDARY};
        border: none;
        color: {COLOR_TEXT};
        font-family: 'Roboto Mono', monospace;
        font-size: 16px;
    }}
    
    QTableWidget::item {{
        padding: 10px;
        border-bottom: 1px solid {COLOR_SECONDARY};
    }}
    
    QTableWidget::item:selected {{
        background-color: {COLOR_HIGHLIGHT};
        color: {COLOR_TEXT};
    }}
    
    QHeaderView::section {{
        background-color: {COLOR_BACKGROUND};
        color: {COLOR_TEXT_MUTED};
        padding: 5px;
        border: none;
        border-bottom: 2px solid {COLOR_PRIMARY};
        font-weight: bold;
        text-transform: uppercase;
    }}

    /* Scrollbars */
    QScrollBar:vertical {{
        background: {COLOR_BACKGROUND};
        width: 14px;
        margin: 0px;
    }}
    QScrollBar::handle:vertical {{
        background: {COLOR_SECONDARY};
        min-height: 20px;
    }}
    QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
        height: 0px;
    }}
    """
