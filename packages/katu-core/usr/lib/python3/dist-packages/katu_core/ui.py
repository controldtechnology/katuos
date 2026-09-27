"""Katu UI Kit — shared visual identity for all Katu applications.

Colors from branding/tokens/katu-tokens.json
"""

# ── Color Palette ─────────────────────────────────────────────────────────────
BG       = "#0d1117"
SURFACE  = "#161b22"
CARD     = "#1c2128"
BORDER   = "#30363d"
BORDER_H = "#484f58"
ACCENT   = "#00c853"
ACCENT_H = "#00e676"
ACCENT_A = "#00a040"
AMBER    = "#ffab00"
TEXT     = "#e6edf3"
TEXT_SEC = "#b1bac4"
MUTED    = "#8b949e"
TEXT_INV = "#0d1117"
ERROR    = "#f85149"
INFO     = "#58a6ff"
SUCCESS  = "#3fb950"

# ── Stylesheet ────────────────────────────────────────────────────────────────
STYLESHEET = f"""
* {{
    font-family: 'Noto Sans', 'Liberation Sans', sans-serif;
    font-size: 13px;
    color: {TEXT};
}}
QMainWindow, QDialog {{
    background: {BG};
}}
QWidget {{
    background: transparent;
    color: {TEXT};
}}
QWidget#root, QWidget#sidebar, QWidget#content {{
    background: {BG};
}}
QWidget#card {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 10px;
}}
QWidget#card:hover {{
    border-color: {BORDER_H};
}}

/* Labels */
QLabel#title {{
    font-size: 22px;
    font-weight: bold;
    color: {TEXT};
}}
QLabel#subtitle {{
    font-size: 15px;
    color: {TEXT_SEC};
}}
QLabel#caption {{
    font-size: 12px;
    color: {MUTED};
}}
QLabel#accent {{
    color: {ACCENT};
    font-weight: bold;
}}
QLabel#error {{
    color: {ERROR};
}}
QLabel#warning {{
    color: {AMBER};
}}
QLabel#success {{
    color: {SUCCESS};
}}

/* Buttons */
QPushButton {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 9px 20px;
    color: {TEXT};
    font-size: 13px;
}}
QPushButton:hover {{
    border-color: {BORDER_H};
    background: {SURFACE};
}}
QPushButton:pressed {{
    background: {BG};
}}
QPushButton:disabled {{
    color: {MUTED};
    border-color: {BORDER};
}}
QPushButton#primary {{
    background: {ACCENT};
    color: {TEXT_INV};
    border: none;
    font-weight: bold;
}}
QPushButton#primary:hover {{
    background: {ACCENT_H};
}}
QPushButton#primary:pressed {{
    background: {ACCENT_A};
}}
QPushButton#primary:disabled {{
    background: {BORDER};
    color: {MUTED};
}}
QPushButton#danger {{
    background: {ERROR};
    color: white;
    border: none;
    font-weight: bold;
}}
QPushButton#danger:hover {{
    background: #ff6b6b;
}}

/* Inputs */
QLineEdit, QTextEdit, QPlainTextEdit {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 9px 12px;
    color: {TEXT};
    selection-background-color: {ACCENT};
    selection-color: {TEXT_INV};
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus {{
    border-color: {ACCENT};
}}

/* Combo / Spin */
QComboBox {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 8px 12px;
    color: {TEXT};
}}
QComboBox::drop-down {{ border: none; padding-right: 8px; }}
QComboBox QAbstractItemView {{
    background: {CARD};
    border: 1px solid {BORDER};
    color: {TEXT};
    selection-background-color: {ACCENT};
    selection-color: {TEXT_INV};
}}

/* Lists / Trees */
QListWidget, QTreeWidget, QTableWidget {{
    background: {CARD};
    border: 1px solid {BORDER};
    border-radius: 8px;
    padding: 4px;
    alternate-background-color: {SURFACE};
}}
QListWidget::item, QTreeWidget::item {{
    padding: 8px 10px;
    border-radius: 6px;
    color: {TEXT_SEC};
}}
QListWidget::item:selected, QTreeWidget::item:selected {{
    background: {SURFACE};
    color: {TEXT};
    border-left: 3px solid {ACCENT};
}}
QListWidget::item:hover, QTreeWidget::item:hover {{
    background: {SURFACE};
    color: {TEXT};
}}

/* Scrollbars */
QScrollBar:vertical {{
    background: {BG};
    width: 6px;
    border-radius: 3px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {BORDER};
    border-radius: 3px;
    min-height: 30px;
}}
QScrollBar::handle:vertical:hover {{ background: {MUTED}; }}
QScrollBar::add-line, QScrollBar::sub-line {{ height: 0; }}
QScrollBar:horizontal {{
    background: {BG};
    height: 6px;
    border-radius: 3px;
}}
QScrollBar::handle:horizontal {{
    background: {BORDER};
    border-radius: 3px;
    min-width: 30px;
}}

/* Progress */
QProgressBar {{
    background: {SURFACE};
    border: 1px solid {BORDER};
    border-radius: 6px;
    height: 8px;
    text-align: center;
    color: transparent;
}}
QProgressBar::chunk {{
    background: {ACCENT};
    border-radius: 6px;
}}

/* Check / Radio */
QCheckBox, QRadioButton {{ color: {TEXT}; spacing: 6px; }}
QCheckBox::indicator, QRadioButton::indicator {{
    width: 16px; height: 16px;
    border: 2px solid {BORDER};
    border-radius: 3px;
    background: {SURFACE};
}}
QCheckBox::indicator:checked {{
    background: {ACCENT};
    border-color: {ACCENT};
}}

/* Tabs */
QTabWidget::pane {{
    border: 1px solid {BORDER};
    border-radius: 8px;
    background: {SURFACE};
}}
QTabBar::tab {{
    background: {BG};
    color: {MUTED};
    padding: 9px 20px;
    border-bottom: 2px solid transparent;
    font-size: 13px;
}}
QTabBar::tab:selected {{
    color: {ACCENT};
    border-bottom: 2px solid {ACCENT};
    font-weight: bold;
}}
QTabBar::tab:hover {{ color: {TEXT}; }}

/* Splitter */
QSplitter::handle {{ background: {BORDER}; }}

/* Tooltip */
QToolTip {{
    background: {CARD};
    border: 1px solid {BORDER};
    color: {TEXT};
    padding: 6px 10px;
    border-radius: 6px;
}}

/* Message Box */
QMessageBox {{ background: {BG}; }}
QMessageBox QLabel {{ color: {TEXT}; }}

/* Frame separators */
QFrame[frameShape="4"], QFrame[frameShape="5"] {{
    color: {BORDER};
}}
"""


# ── Status helpers ────────────────────────────────────────────────────────────
STATUS_OK      = f'<span style="color:{SUCCESS}">✓</span>'
STATUS_WARN    = f'<span style="color:{AMBER}">⚠</span>'
STATUS_ERROR   = f'<span style="color:{ERROR}">✗</span>'
STATUS_LOADING = f'<span style="color:{MUTED}">⟳</span>'
STATUS_NA      = f'<span style="color:{MUTED}">—</span>'


def status_icon(ok: bool, unknown: bool = False) -> str:
    if unknown:
        return STATUS_NA
    return STATUS_OK if ok else STATUS_ERROR
