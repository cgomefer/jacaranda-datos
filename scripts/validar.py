#!/usr/bin/env python3
"""Valida compra.json y compara con la versión anterior.

Uso:
  python3 scripts/validar.py compra.json [compra_anterior.json]

Sale con código 1 si hay errores. Las mismas reglas aplica la app al
descargar los datos, así que un archivo que pasa aquí se verá completo.
"""
import json, re, sys

SRC = {"bbva", "hsbc", "bancomext"}
TIPO = {"Casa", "Departamento", "Terreno"}
EDO = {"CDMX", "Edomex"}
VENTA = {"directa", "normal", "cesion"}
NUM = ["r", "b", "e", "m2c", "m2t", "p", "lista"]
URL = re.compile(r"^https://(www\.)?bbvainmuebles\.mx/inmuebles/[a-z0-9-]+/?$")


def errores(d):
    err = []
    if not re.match(r"^\d{4}-\d{2}-\d{2}$", str(d.get("verificado", ""))):
        err.append("'verificado' debe ser una fecha AAAA-MM-DD")
    items = d.get("items")
    if not isinstance(items, list) or not items:
        return err + ["'items' debe ser una lista no vacía"]
    vistos = set()
    for i, x in enumerate(items):
        tag = f"items[{i}] ({x.get('id', '?')})"
        if not isinstance(x.get("id"), str) or not x["id"] or len(x["id"]) > 64:
            err.append(f"{tag}: id inválido")
        elif x["id"] in vistos:
            err.append(f"{tag}: id repetido")
        vistos.add(x.get("id"))
        for k, ok in (("src", SRC), ("tipo", TIPO), ("edo", EDO), ("venta", VENTA)):
            if x.get(k) not in ok:
                err.append(f"{tag}: {k}={x.get(k)!r} no es uno de {sorted(ok)}")
        for k in ("colonia", "alc"):
            if not isinstance(x.get(k), str) or not x[k].strip():
                err.append(f"{tag}: falta {k}")
        for k in NUM:
            v = x.get(k)
            if v is not None and not (isinstance(v, (int, float)) and not isinstance(v, bool) and v >= 0):
                err.append(f"{tag}: {k} debe ser número >= 0 o null")
        if x.get("src") == "bbva" and x.get("url") and not URL.match(x["url"]):
            err.append(f"{tag}: url de BBVA con formato inesperado")
        if x.get("src") == "hsbc" and not x.get("folio"):
            err.append(f"{tag}: HSBC requiere folio")
        if x.get("p") and x.get("lista") and x["p"] > x["lista"]:
            err.append(f"{tag}: precio mayor que el de lista")
        if x.get("pos") not in (True, False, None):
            err.append(f"{tag}: pos debe ser true, false o null")
    return err


def resumen(nuevo, viejo):
    a = {x["id"]: x for x in viejo.get("items", [])}
    b = {x["id"]: x for x in nuevo.get("items", [])}
    altas = sorted(set(b) - set(a))
    bajas = sorted(set(a) - set(b))
    cambios = [k for k in set(a) & set(b) if a[k].get("p") != b[k].get("p") or a[k].get("venta") != b[k].get("venta")]
    print(f"Altas: {len(altas)}  Bajas: {len(bajas)}  Cambios de precio o tipo de venta: {len(cambios)}")
    for k in altas:
        print("  +", k, b[k].get("colonia"), b[k].get("p"))
    for k in bajas:
        print("  -", k, a[k].get("colonia"), a[k].get("p"))
    for k in sorted(cambios):
        print("  ~", k, a[k].get("p"), "->", b[k].get("p"), a[k].get("venta"), "->", b[k].get("venta"))
    if a and len(bajas) > 0.5 * len(a):
        print("ALERTA: desaparece más de la mitad de los inmuebles. Revisa antes de publicar.")
        return False
    return True


if __name__ == "__main__":
    d = json.load(open(sys.argv[1], encoding="utf-8"))
    e = errores(d)
    for m in e:
        print("ERROR:", m)
    items = d.get("items", [])
    print(f"{len(items)} inmuebles · {sum(x.get('edo') == 'CDMX' for x in items)} en CDMX · verificado {d.get('verificado')}")
    ok = not e
    if len(sys.argv) > 2:
        ok = resumen(d, json.load(open(sys.argv[2], encoding="utf-8"))) and ok
    sys.exit(0 if ok else 1)
