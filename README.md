# Jacaranda · datos de Compra

Base pública de inmuebles recuperados por bancos en la Ciudad de México y su zona metropolitana. La usa la pestaña **Compra** de la app Jacaranda.

- `compra.json`: los datos. Se revisan cada día contra los catálogos oficiales de BBVA, HSBC y Bancomext.
- `ACTUALIZAR.md`: el procedimiento de la revisión diaria.
- `scripts/validar.py`: valida el archivo y compara con la versión anterior.
- `scripts/incrustar.py`: copia los datos dentro de la página web de la app.

Los precios son los que publica cada banco y pueden cambiar sin aviso. Esta información no es asesoría legal ni financiera.
