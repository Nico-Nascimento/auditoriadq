"""Garante que só exista uma janela do programa aberta por usuário.

Se o programa for aberto de novo, a segunda cópia avisa a primeira (que vem para a frente)
e se encerra. Assim, duas janelas nunca gravam ao mesmo tempo nos mesmos arquivos.
"""
from __future__ import annotations

import getpass
import re
import sys

from PySide6.QtCore import QObject, Signal
from PySide6.QtNetwork import QLocalServer, QLocalSocket


def default_name() -> str:
    try:
        user = getpass.getuser()
    except Exception:
        user = "usuario"
    return "AuditoriaDQ-" + re.sub(r"[^A-Za-z0-9_.-]", "_", user)


class SingleInstance(QObject):
    activated = Signal()  # outra cópia pediu para mostrar a janela

    def __init__(self, name: str | None = None, parent: QObject | None = None):
        super().__init__(parent)
        self.name = name or default_name()
        self.server: QLocalServer | None = None

    def already_running(self) -> bool:
        """True se já existe uma cópia aberta (e a avisa); senão, passa a ser a cópia principal."""
        sock = QLocalSocket()
        sock.connectToServer(self.name)
        if sock.waitForConnected(500):
            if sys.platform.startswith("win"):
                try:  # permite que a janela já aberta venha para a frente
                    import ctypes

                    ctypes.windll.user32.AllowSetForegroundWindow(-1)
                except Exception:
                    pass
            sock.write(b"show")
            sock.flush()
            sock.waitForBytesWritten(500)
            sock.disconnectFromServer()
            return True

        QLocalServer.removeServer(self.name)  # limpa resto de uma execução que travou
        self.server = QLocalServer(self)
        self.server.listen(self.name)
        self.server.newConnection.connect(self._on_connection)
        return False

    def _on_connection(self) -> None:
        while self.server is not None and self.server.hasPendingConnections():
            conn = self.server.nextPendingConnection()
            conn.disconnected.connect(conn.deleteLater)
            self.activated.emit()
