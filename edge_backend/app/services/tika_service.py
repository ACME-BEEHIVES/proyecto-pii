"""
tika_service.py — Mantiene compatibilidad de nombre, delega todo a ocr_service (PaddleOCR).

Este archivo existe para que no haya que cambiar los imports en el resto del codebase.
"""

from app.services.ocr_service import extract_text, check_health

__all__ = ["extract_text", "check_health"]
