#!/usr/bin/env python3
"""Copia los datos de compra.json dentro de la página web de Jacaranda.

Uso:
  python3 scripts/incrustar.py compra.json pagina.html

Reemplaza las líneas `let BUY_VER=...;` y `const BUY_RAW=[...];` de la página
para que la versión web muestre los datos nuevos aunque no pueda descargarlos.
"""
import json, re, sys

datos = json.load(open(sys.argv[1], encoding="utf-8"))
ruta = sys.argv[2]
html = open(ruta, encoding="utf-8").read()

raw = json.dumps(datos["items"], ensure_ascii=False, separators=(",", ":"))
html, n1 = re.subn(r'let BUY_VER="\d{4}-\d{2}-\d{2}";', f'let BUY_VER="{datos["verificado"]}";', html, count=1)
html, n2 = re.subn(r"const BUY_RAW=\[.*?\];\n", lambda m: f"const BUY_RAW={raw};\n", html, count=1, flags=re.S)
if n1 != 1 or n2 != 1:
    sys.exit("No encontré BUY_VER o BUY_RAW en la página; no se cambió nada.")
open(ruta, "w", encoding="utf-8").write(html)
print(f"Página actualizada con {len(datos['items'])} inmuebles del {datos['verificado']}.")
