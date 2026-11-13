"""Make openpyxl write XML with the standard library, whether or not lxml is installed.

openpyxl reads OPENPYXL_LXML once, when it is first imported, and writes
differently spaced XML through lxml. Import this module before openpyxl so that
tools/build_template.py writes the same bytes on every machine.
"""

from __future__ import annotations

import os

os.environ["OPENPYXL_LXML"] = "False"
