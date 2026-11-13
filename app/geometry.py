"""Cálculos da marcação de 40% (sem Qt, para poder testar isoladamente).

Mesma lógica do projeto web (AnnotationCanvas.tsx).
"""
from __future__ import annotations

from dataclasses import dataclass

MIN_SIZE = 5.0


@dataclass(frozen=True)
class Box:
    x: float
    y: float
    w: float
    h: float

    @property
    def right(self) -> float:
        return self.x + self.w

    @property
    def bottom(self) -> float:
        return self.y + self.h


@dataclass(frozen=True)
class Forty:
    vertical40: float  # 40% da altura
    horizontal40: float  # 40% da largura
    vertical_overlay: Box  # faixa azul (altura)
    horizontal_overlay: Box  # faixa amarela (largura)
    horizontal_line_y: float
    vertical_line_x: float


def normalize(x1: float, y1: float, x2: float, y2: float) -> Box:
    return Box(min(x1, x2), min(y1, y2), abs(x2 - x1), abs(y2 - y1))


def forty(rect: Box, h_side: str, v_side: str) -> Forty:
    v40 = rect.h * 0.4
    h40 = rect.w * 0.4
    overlay_y = rect.y if v_side == "top" else rect.y + rect.h - v40
    line_y = rect.y + v40 if v_side == "top" else rect.y + rect.h - v40
    overlay_x = rect.x if h_side == "left" else rect.x + rect.w - h40
    line_x = rect.x + h40 if h_side == "left" else rect.x + rect.w - h40
    return Forty(
        vertical40=v40,
        horizontal40=h40,
        vertical_overlay=Box(rect.x, overlay_y, rect.w, v40),
        horizontal_overlay=Box(overlay_x, rect.y, h40, rect.h),
        horizontal_line_y=line_y,
        vertical_line_x=line_x,
    )


HANDLES = ("tl", "tc", "tr", "ml", "mr", "bl", "bc", "br")


def handle_points(rect: Box) -> dict[str, tuple[float, float]]:
    cx = rect.x + rect.w / 2
    cy = rect.y + rect.h / 2
    return {
        "tl": (rect.x, rect.y),
        "tc": (cx, rect.y),
        "tr": (rect.right, rect.y),
        "ml": (rect.x, cy),
        "mr": (rect.right, cy),
        "bl": (rect.x, rect.bottom),
        "bc": (cx, rect.bottom),
        "br": (rect.right, rect.bottom),
    }


def resize(start: Box, handle: str, dx: float, dy: float) -> Box:
    """Redimensiona arrastando uma alça, sem deixar menor que MIN_SIZE."""
    left, top, right, bottom = start.x, start.y, start.right, start.bottom
    if handle[0] == "t":
        top = min(top + dy, bottom - MIN_SIZE)
    if handle[0] == "b":
        bottom = max(bottom + dy, top + MIN_SIZE)
    if handle in ("tl", "ml", "bl"):
        left = min(left + dx, right - MIN_SIZE)
    if handle in ("tr", "mr", "br"):
        right = max(right + dx, left + MIN_SIZE)
    return Box(left, top, right - left, bottom - top)
