# Revisión diaria de la base de Compra

Este repositorio guarda `compra.json`, la base de inmuebles recuperados por bancos que muestra la pestaña **Compra** de Jacaranda. El botón **Actualizar** de la app descarga este archivo.

Este documento es el procedimiento que sigue la revisión automática diaria. Quien lo ejecute debe seguirlo tal cual.

## Reglas

- **Solo fuentes oficiales de los bancos.** Nunca agregues inmuebles de portales o revendedores (Mercado Libre, Lamudi, Inmuebles24, TikTok, "remates" en redes, etc.).
- Si un sitio bloquea la lectura automática (robots), no busques otra forma de entrar. Déjalo fuera.
- No inventes datos. Si un dato no aparece en la fuente, va como `null`.
- Zona: Ciudad de México (`"edo": "CDMX"`) y estos municipios del Estado de México (`"edo": "Edomex"`): Acolman, Atenco, Atizapán de Zaragoza, Chalco, Chicoloapan, Chiconcuac, Chimalhuacán, Coacalco, Coyotepec, Cuautitlán, Cuautitlán Izcalli, Ecatepec, Huehuetoca, Huixquilucan, Ixtapaluca, Jaltenco, La Paz, Melchor Ocampo, Naucalpan, Nextlalpan, Nezahualcóyotl, Nicolás Romero, Tecámac, Teoloyucan, Tepotzotlán, Texcoco, Tezoyuca, Tlalmanalco, Tlalnepantla, Tonanitla, Tultepec, Tultitlán, Valle de Chalco, Zumpango.
- Solo casas, departamentos y terrenos habitacionales. Nada de bodegas, oficinas, locales ni hoteles.

## Formato de cada inmueble

```json
{"id":"bbva-540186","src":"bbva","tipo":"Departamento","colonia":"Héroes de Padierna","alc":"Tlalpan","edo":"CDMX",
 "r":3,"b":2,"e":2,"m2c":102.63,"m2t":26.01,"p":3326900,"lista":4305000,
 "venta":"directa","pos":null,"pago":"Crédito o contado","folio":"540186",
 "url":"https://www.bbvainmuebles.mx/inmuebles/heroes-de-padierna-tlalpan-ciudad-de-mexico/",
 "nota":null,"visto":"2026-10-19"}
```

- `src`: `bbva`, `banorte`, `hsbc` o `bancomext`.
- `r`, `b`, `e`: recámaras, baños, cajones. `m2c`: m² construidos. `m2t`: m² de terreno.
- `p`: precio de venta. `lista`: precio de lista (BBVA) o valor comercial (HSBC). `null` si no se publica.
- `venta`: `directa` (inmueble propio del banco: BBVA, Bancomext y Banorte "Venta de Inmuebles"), `normal` (HSBC "Venta Normal") o `cesion` (HSBC "Cesión de Derechos" y Banorte "Derechos Adjudicatarios").
- `pos`: `true` si la casilla "Posesión física" está marcada, `false` si está vacía, `null` si la fuente no lo dice.
- `visto`: última fecha en que se confirmó en la fuente. Lo usa este procedimiento, la app lo ignora.

## Pasos

1. Copia `compra.json` a `/tmp/anterior.json`.

2. **BBVA** (`https://www.bbvainmuebles.mx`)
   - Su catálogo completo solo responde a un navegador real (ver "Carga completa con navegador"). En la revisión diaria:
   - Para cada inmueble de BBVA que ya está en `compra.json`, abre su `url`. Si sigue publicado, actualiza su precio (`p`) y `visto`. Si la página ya no muestra el inmueble, no actualices `visto`.
   - Recorre `https://www.bbvainmuebles.mx/categoria-g12/` y `https://www.bbvainmuebles.mx/categoria-g2/` (con `/page/2/`, `/page/3/`…). Si aparece un inmueble de la zona que no está en `compra.json`, ábrelo y agrégalo: `id` = `bbva-<folio>`, primer precio = `p`, segundo precio = `lista`. **El m² de esos listados es de terreno (`m2t`)**; los m² construidos, recámaras, baños y cajones salen de la ficha.
   - No agregues fichas encontradas solo por buscadores web: BBVA deja en línea páginas de inmuebles que ya retiró de su catálogo.

3. **HSBC**: lee `https://www.hsbc.com.mx/content/dam/hsbc/mx/documents/hipotecario/bienes-adjudicados/zona_metro1.pdf`.
   - Toma las fichas de la zona. Por cada una: número de inmueble (`folio`, e `id` = `hsbc-<número>`), tipo, colonia, alcaldía o municipio, recámaras, baños, cajones, terreno, construcción, tipo de venta, valor comercial (`lista`), precio de venta (`p`) y la casilla "Posesión física".
   - Si el precio dice "especial", "sujeto a revisión" o "en actualización", ponlo en `nota`.
   - Si dudas de una casilla de posesión, vuelve a preguntar solo por esa ficha antes de decidir.

4. **Bancomext**: abre `https://www.bancomext.com/conoce-bancomext/licitaciones/venta-de-bienes-adjudicados/` y lee el PDF del catálogo de inmuebles más reciente. Toma solo las viviendas de la zona. Si no hay precio, `p` va en `null` y la nota dice que Bancomext no publica el precio.

5. **Altas y bajas.** Un inmueble que no se pudo confirmar hoy se conserva si su `visto` tiene 3 días o menos. Si lleva más de 3 días sin confirmarse, se quita. Así una falla pasajera de un sitio no borra media base.
   - **Excepción: Banorte.** La revisión en la nube no puede leer su sitio. **No toques los inmuebles de Banorte** en la revisión diaria (ni los quites ni cambies su `visto`); solo se actualizan con la carga completa con navegador.

6. Pon `"verificado"` con la fecha de hoy y guarda `compra.json` con sangría de 1 espacio y `ensure_ascii=False`.

7. Valida: `python3 scripts/validar.py compra.json /tmp/anterior.json`.
   - Si sale con error o con **ALERTA**, no publiques nada. Termina explicando qué falló.

8. Publica: commit en `main` con el mensaje `Revisión diaria AAAA-MM-DD: N inmuebles (+altas −bajas)` y haz push.

9. **Actualiza la versión web.** Lee la página de la app con la herramienta Artifact (`action: "read"`, la URL que te dio la tarea y `path: "index.html"`). Ejecuta `python3 scripts/incrustar.py compra.json <archivo guardado>` y publica ese archivo con Artifact en la misma URL.

10. Termina con un resumen corto: total de inmuebles, altas, bajas, cambios de precio y cualquier fuente que no se pudo leer.

## Carga completa con navegador

BBVA (catálogo "Mi hogar") y Banorte publican su inventario completo a través de servicios que solo responden a un navegador real. Esta carga se hace desde una sesión con la computadora del dueño conectada y el navegador de la app de Claude, idealmente una vez por semana.

**BBVA.** Abre `https://www.bbvainmuebles.mx/busqueda/minoristas/` y, en la página, consulta:

```
/bbva-components/search?&q=***&fq=(and(and%20content_language:%27es%27)(or%20wp_double_array:54)+(or%20wp_double_array:368))&project=kta59b5o&start=0&size=100
```

(pagina con `start=100`, `200`… hasta que regrese menos de 100). Cada resultado trae `content` (folio), `resourcename` (ruta de la ficha), `title` (colonia, municipio, estado), `wp_text` (municipio), `topic` (estado) y `wp_text_array` = `[tipo, modalidad de pago, precio de lista (0 = no hay), precio, m² construidos, cajones, recámaras]`. Quédate con `topic` `ciudad-de-mexico` y `estado-de-mexico` dentro de la zona. Los inmuebles de BBVA que ya no aparezcan en este catálogo se quitan.

**Banorte.** Abre `https://www.inmueblesbanorte.com.mx/Inmuebles/` y, en la página, haz `POST` con cuerpo JSON a:

```
/Inmuebles-0.0.1/bnt/inmuebles/busquedaInmueble/page/<página desde 0>/100
{"idTipoInmuble":3,"idEstado":<9 CDMX | 15 Edomex>,"listaCiudades":[],"listaColonias":[],"palabraClave":null,"tipoVenta":<1 | 2>}
```

`tipoVenta` 1 = "Venta de Inmuebles" (`venta: "directa"`), 2 = "Derechos Adjudicatarios" (`venta: "cesion"`). Pagina hasta que `respuesta.last` sea verdadero. Cada resultado trae `folio`, `subtipo` (Casa o Departamento), `colonia`, `ciudad`, `estado`, `precio` (1 = sin precio publicado → `p: null`), `terreno` y `construccion`. `id` = `banorte-<folio>`, `url` = `https://www.inmueblesbanorte.com.mx/Inmuebles/#/detalle/<folio>`. La nota de cada uno dice si es cesión de derechos adjudicatarios y si Banorte no publica el precio. No guardes datos de los gerentes o promotores que aparecen en las fichas.

Para pasar los datos del navegador al espacio de trabajo, descárgalos como archivo JSON (con permiso del dueño) y léelos desde su carpeta Descargas. Después valida, publica y actualiza la versión web igual que en los pasos 7 a 9.
