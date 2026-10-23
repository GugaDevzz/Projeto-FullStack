
from pathlib import Path

class Configuracao:

    # ==========================================
    # IDENTIDADE DO SISTEMA
    # ==========================================

    NOME_SISTEMA = "Lanchao"
    NOME_EMPRESA = "Catatau"

    # ==========================================
    # CORES
    # ==========================================

    COR_PRIMARIA = "#8B5CF6"
    COR_SECUNDARIA = "#6D28D9"

    COR_SIDEBAR = "#171717"
    COR_SIDEBAR_HOVER = "#262626"

    COR_BACKGROUND = "#101010"
    COR_CARD = "#1C1C1C"

    COR_TEXTO = "#FFFFFF"
    COR_TEXTO_SECUNDARIO = "#A3A3A3"

    # ==========================================
    # TAMANHOS
    # ==========================================

    SIDEBAR_LARGURA = 230

    JANELA_LARGURA = 1400
    JANELA_ALTURA = 800

    # ==========================================
    # LOGO E ICONE
    # ==========================================

    BASE_DIR = Path(__file__).resolve().parent.parent #pegar img

    LOGO = BASE_DIR / "img" / "logo.png"

    ICONE = BASE_DIR / "img" / "icon.ico"