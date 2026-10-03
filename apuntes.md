# Proyecto base de datos

### Requisitos

- Cantidad de campos por archivo. Hecho 
- Cantidad de campos sin informacion. Hecho
- Varianza de los campos que contengan informacion numerica. Hecho
- Cantidad de elementos distintos por cada campo con informacion no numerica. Hecho
- cantidad de elementos con baja frecuencia. hecho

#### Campos obligatorios

Los siguientes campos se deben evaluar si o si:

- **RA (Right ascension):** Presente en 269 archivos. Los 18 archivos de categoría SCIENCE lo poseen. Se normalizará para derivar la longitud espacial.
- **DEC (Declination):** Presente en 269 archivos. Los 18 archivos de categoría SCIENCE lo poseen. Se utilizará como latitud espacial.
- **DATE-OBS:** 1.861 valores distintos. Se preserva íntegro para indexar y permitir consultas rápidas por rangos de fechas.
- **OBJECT:** 18 valores distintos. Fundamental preservarlo en la raíz del documento para indexar y ejecutar búsquedas por nombre de objeto.

### Definicion de tecnologias

Se debe justificar por que se eligio la base de datos no relacional, en base a lo visto en clases.

Para este proyecto se utilizará una arquitectura híbrida: una **Base de Datos Documental (MongoDB)** para almacenar e indexar los metadatos y un sistema de almacenamiento secundario (Object Storage o File System) para los archivos binarios pesados (FITS). 

Los archivos FITS no deben incrustarse en la base de datos, ya que esto saturaría el rendimiento y la memoria del motor. En su lugar, el archivo pesado se guarda externamente y el documento en MongoDB conserva una ruta (URI) estable hacia él. De esta forma, el motor de búsqueda puede consultar los metadatos rápidamente sin verse lastrado por el transporte de imágenes pesadas.

**Justificación sobre un modelo puramente relacional (SQL)**
Un modelo puramente relacional requiere un esquema rígido y predefinido, lo cual no es adecuado para este volumen y alta variabilidad de datos. Al analizar la muestra, se observó que los encabezados contienen entre 438 y 552 campos por archivo, con claves que pueden estar ausentes o variar de un instrumento a otro. Si intentáramos modelar esto en SQL puro, tendríamos dos opciones, ambas ineficientes:
1. **Una tabla monolítica gigante:** Obligaría a crear una tabla con más de 550 columnas donde la inmensa mayoría de las celdas serían `NULL` (matriz muy dispersa), desperdiciando espacio y obligando a alterar el esquema (`ALTER TABLE`) cada vez que un nuevo instrumento introduzca un nuevo campo.
2. **Modelo Entidad-Atributo-Valor (EAV):** Requeriría dividir los metadatos en múltiples filas de una tabla atributo-valor, lo que exigiría ejecutar costosos e intensivos `JOIN` sucesivos para realizar consultas y reconstruir un solo archivo. Esto degradaría severamente el rendimiento del motor de búsqueda.

Por estas razones, la elección de una **Base de Datos Documental** (MongoDB) es la idónea. Su diseño permite almacenar documentos heterogéneos nativamente mediante JSON/BSON, admitiendo metadatos variables y campos anidados sin penalizar la estructura ni el rendimiento.


### Diseño del esquema

Como se va indexar y modelar los encabezados

Se creará un documento por cada archivo FITS, donde los metadatos consultados con frecuencia se elevan a campos de primer nivel, mientras que el encabezado original completo se anida en la clave `header`. Ejemplo ilustrativo:

```json
{
	"_id": "XSHOO.2026-09-04T01:43:37.983.fits",
	"fileId": "XSHOO.2026-09-04T01:43:37.983.fits",
	"sourceFile": "XSHOOTER_SLT_AFC_UVB_247_0001.fits",
	"instrument": "XSHOOTER",
	"object": "Target name",
	"observedAt": "2026-09-04T01:43:37.983Z",
	"raDeg": 331.01846,
	"decDeg": -46.42268,
	"location": { "type": "Point", "coordinates": [-28.98154, -46.42268] },
	"exposureSeconds": 5.0,
	"product": { "category": "SCIENCE", "type": "OBJECT" },
	"storageUri": "s3://bucket/path/to/file.fits",
	"header": { "...": "resto de las claves FITS originales sin perder información" }
}
```

Para soportar el motor de búsqueda espacial, MongoDB requiere un formato GeoJSON ordenado como `[longitud, latitud]`. Por lo tanto, el campo `RA` se convertirá de `[0, 360)` a `[-180, 180)` usándolo como longitud, y `DEC` se usará directamente como latitud `[-90, 90]`. Todo el resto del contenido que no requiera búsquedas rápidas quedará intacto dentro del subdocumento `"header"`.

**Estrategia de Indexación:**
- `location`: Índice **2dsphere** para habilitar búsquedas geométricas rápidas por región del cielo.
- `observedAt`: Índice ascendente para filtrar eficientemente por fechas de observación.
- `object`: Índice ascendente para búsquedas por nombres de cuerpos celestes.

**Reglas de negocio (Qué indexar y qué descartar):**
1. **Datos indexables (Buscador Principal):** La categoría `SCIENCE` (Ciencia) entrará al catálogo del motor de búsqueda espacial únicamente si `RA`, `DEC` y `DATE-OBS` existen y son válidos.
2. **Datos a descartar/mover (Almacenamiento Secundario):** Dado que el 98,9% de los archivos observados corresponden a calibraciones (`CALIB`) u otras pruebas, estos serán movidos a un almacenamiento secundario más económico. Se mantendrá solo un registro mínimo de ellos (su `ARCFILE` y `URI`) fuera del índice geoespacial para no saturar las búsquedas de los astrónomos.

### Informe y presentacion
