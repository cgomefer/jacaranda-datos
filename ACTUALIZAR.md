# Revisión diaria de la base de Compra

Este repositorio guarda `compra.json`, la base de inmuebles recuperados por bancos que muestra la pestaña **Compra** de Jacaranda. El botón **Actualizar** de la app descarga este archivo.

Este documento es el procedimiento que sigue la revisión automática diaria. Quien lo ejecute debe seguirlo tal cual.

## Reglas

- **Solo fuentes oficiales de los bancos.** Nunca agregues inmuebles de portales o revendedores (Mercado Libre, Lamudi, Inmuebles24, TikTok, "remates" en redes, etc.).
- Si un sitio bloquea la lectura automática (robots), no busques otra forma de entrar. Déjalo fuera.
- No inventes datos. Si un dato no aparece en la fuente, va como `null`.
- Zona: Ciudad de México (`"edo": "CDMX"`) y estos municipios del Estado de México (`"edo": "Edomex"`): Atizapán de Zaragoza, Chalco, Chimalhuacán, Coacalco, Cuautitlán, Cuautitlán Izcalli, Ecatepec, Huixquilucan, Ixtapaluca, La Paz, Naucalpan, Nezahualcóyotl, Nicolás Romero, Tecámac, Tlalnepantla, Tultitlán, Valle de Chalco.
- Solo casas, departamentos y terrenos habitacionales. Nada de bodegas, oficinas, locales ni hoteles.

## Formato de cada inmueble

```json
{"id":"bbva-540186","src":"bbva","tipo":"Departamento","colonia":"Héroes de Padierna","alc":"Tlalpan","edo":"CDMX",
 "r":3,"b":2,"e":2,"m2c":102.63,"m2t":26.01,"p":3326900,"lista":4305000,
 "venta":"directa","pos":null,"pago":"Crédito o contado","folio":"540186",
 "url":"https://www.bbvainmuebles.mx/inmuebles/heroes-de-padierna-tlalpan-ciudad-de-mexico/",
 "nota":null,"visto":"2026-10-19"}
```

- `src`: `bbva`, `hsbc` o `bancomext`.
- `r`, `b`, `e`: recámaras, baños, cajones. `m2c`: m² construidos. `m2t`: m² de terreno.
- `p`: precio de venta. `lista`: precio de lista (BBVA) o valor comercial (HSBC). `null` si no se publica.
- `venta`: `directa` (inmueble propio del banco, BBVA y Bancomext), `normal` (HSBC "Venta Normal") o `cesion` (HSBC "Cesión de Derechos").
- `pos`: `true` si la casilla "Posesión física" está marcada, `false` si está vacía, `null` si la fuente no lo dice.
- `visto`: última fecha en que se confirmó en la fuente. Lo usa este procedimiento, la app lo ignora.

## Pasos

1. Copia `compra.json` a `/tmp/anterior.json`.

2. **BBVA** (`https://www.bbvainmuebles.mx`)
   - Recorre `https://www.bbvainmuebles.mx/categoria-g12/` y `https://www.bbvainmuebles.mx/categoria-g2/`, con sus páginas `/page/2/`, `/page/3/`… hasta que no haya más. Quédate con los de la zona.
   - En estos listados el primer precio es `p` y el segundo es `lista`. **El m² del listado es de terreno (`m2t`), no de construcción.**
   - Para cada inmueble de BBVA que ya está en `compra.json` y no apareció en esas categorías, abre su `url`. Si sigue publicado, actualiza su precio (`p`), deja `lista` en `null` y actualiza `visto`.
   - Busca fichas nuevas con búsquedas web como `site:bbvainmuebles.mx/inmuebles ciudad-de-mexico` y `site:bbvainmuebles.mx/inmuebles "estado de mexico"` más el nombre de las alcaldías o municipios. Abre cada ficha nueva y toma precio, folio, m² construidos, m² de terreno, recámaras, baños, cajones y forma de pago.
   - El `id` es `bbva-<folio>`. Si la ficha no muestra recámaras ni baños (salen en 0), pon la nota "La ficha del banco no indica recámaras ni baños; pide los detalles".

3. **HSBC**: lee `https://www.hsbc.com.mx/content/dam/hsbc/mx/documents/hipotecario/bienes-adjudicados/zona_metro1.pdf`.
   - Toma las fichas de la zona. Por cada una: número de inmueble (`folio`, e `id` = `hsbc-<número>`), tipo, colonia, alcaldía o municipio, recámaras, baños, cajones, terreno, construcción, tipo de venta, valor comercial (`lista`), precio de venta (`p`) y la casilla "Posesión física".
   - Si el precio dice "especial", "sujeto a revisión" o "en actualización", ponlo en `nota`.
   - Si dudas de una casilla de posesión, vuelve a preguntar solo por esa ficha antes de decidir.

4. **Bancomext**: abre `https://www.bancomext.com/conoce-bancomext/licitaciones/venta-de-bienes-adjudicados/` y lee el PDF del catálogo de inmuebles más reciente. Toma solo las viviendas de la zona. Si no hay precio, `p` va en `null` y la nota dice que Bancomext no publica el precio.

5. **Altas y bajas.** Un inmueble que no se pudo confirmar hoy se conserva si su `visto` tiene 3 días o menos. Si lleva más de 3 días sin confirmarse, se quita. Así una falla pasajera de un sitio no borra media base.

6. Pon `"verificado"` con la fecha de hoy y guarda `compra.json` con sangría de 1 espacio y `ensure_ascii=False`.

7. Valida: `python3 scripts/validar.py compra.json /tmp/anterior.json`.
   - Si sale con error o con **ALERTA**, no publiques nada. Termina explicando qué falló.

8. Publica: commit en `main` con el mensaje `Revisión diaria AAAA-MM-DD: N inmuebles (+altas −bajas)` y haz push.

9. **Actualiza la versión web.** Lee la página de la app con la herramienta Artifact (`action: "read"`, la URL que te dio la tarea y `path: "index.html"`). Ejecuta `python3 scripts/incrustar.py compra.json <archivo guardado>` y publica ese archivo con Artifact en la misma URL.

10. Termina con un resumen corto: total de inmuebles, altas, bajas, cambios de precio y cualquier fuente que no se pudo leer.
