"""Arquivo de snippets de cada pessoa (fica na pasta AppData do usuário)."""
from __future__ import annotations

import shutil
import time
from pathlib import Path

from PySide6.QtCore import QObject, QStandardPaths, QTimer, Signal

from .snippets import Snippet, find_matches, load_snippets_file, save_snippets_file
from .resources import resource_path


def user_data_dir() -> Path:
    base = QStandardPaths.writableLocation(QStandardPaths.StandardLocation.AppDataLocation)
    path = Path(base)
    path.mkdir(parents=True, exist_ok=True)
    return path


class SnippetStore(QObject):
    """Mantém a lista de snippets em memória e grava no arquivo do usuário."""

    changed = Signal()

    def __init__(self, path: Path | None = None, parent: QObject | None = None):
        super().__init__(parent)
        self.path = path or (user_data_dir() / "snippets.json")
        self.snippets: list[Snippet] = []
        self.load_warning: str | None = None

        self._save_timer = QTimer(self)
        self._save_timer.setSingleShot(True)
        self._save_timer.setInterval(400)
        self._save_timer.timeout.connect(self.save_now)

        self._load()

    # ------------------------------------------------------------------
    def _load(self) -> None:
        default = resource_path("app", "snippets_padrao.json")
        if not self.path.exists():
            if default.exists():
                shutil.copyfile(default, self.path)
            else:
                save_snippets_file(self.path, [])
        try:
            self.snippets = load_snippets_file(self.path)
        except Exception as exc:  # arquivo corrompido: guarda uma cópia e recomeça do padrão
            backup = self.path.with_name(f"snippets.corrompido-{time.strftime('%Y%m%d-%H%M%S')}.json")
            shutil.copyfile(self.path, backup)
            self.load_warning = (
                f"Não foi possível ler o arquivo de snippets ({exc}).\n\n"
                f"Uma cópia foi guardada em:\n{backup}\n\nOs snippets padrão foram carregados."
            )
            self.snippets = load_snippets_file(default) if default.exists() else []
            save_snippets_file(self.path, self.snippets)

    # ------------------------------------------------------------------
    def matches(self, word: str):
        return find_matches(self.snippets, word)

    def schedule_save(self) -> None:
        self._save_timer.start()
        self.changed.emit()

    def save_now(self) -> None:
        self._save_timer.stop()
        save_snippets_file(self.path, self.snippets)

    def replace_all(self, snippets: list[Snippet]) -> None:
        self.snippets = list(snippets)
        self.save_now()
        self.changed.emit()

    def add(self, snippet: Snippet) -> None:
        self.snippets.append(snippet)
        self.schedule_save()

    def remove(self, snippet: Snippet) -> None:
        if snippet in self.snippets:
            self.snippets.remove(snippet)
        self.schedule_save()
