"""pytest-qt için ortak fixture'lar."""

import os

# Headless CI/sandbox ortamlarında ekran olmayabilir — offscreen platform kullan
os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
