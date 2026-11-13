import sys
from pathlib import Path


def resource_path(*parts: str) -> Path:
    """Caminho de arquivos que acompanham o programa (funciona também no .exe do PyInstaller)."""
    base = Path(getattr(sys, "_MEIPASS", Path(__file__).resolve().parent.parent))
    return base.joinpath(*parts)
