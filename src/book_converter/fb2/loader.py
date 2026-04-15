"""Load .fb2 or .fb2.zip into an ElementTree root element."""
from __future__ import annotations

import zipfile
from pathlib import Path
from xml.etree import ElementTree as ET

from defusedxml.ElementTree import parse as _safe_parse


def load_fb2(path: Path) -> ET.Element:
    path = Path(path)
    if not path.exists():
        raise FileNotFoundError(path)

    if path.suffix.lower() == ".zip" or str(path).lower().endswith(".fb2.zip"):
        with zipfile.ZipFile(path) as z:
            try:
                fb2_name = next(n for n in z.namelist() if n.lower().endswith(".fb2"))
            except StopIteration as e:
                raise ValueError(f"no .fb2 entry in {path}") from e
            with z.open(fb2_name) as f:
                return _safe_parse(f).getroot()

    return _safe_parse(path).getroot()
