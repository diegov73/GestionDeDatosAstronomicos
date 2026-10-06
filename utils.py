import matplotlib.pyplot as plt
import pandas as pd
import csv
from astropy.visualization import ImageNormalize, ZScaleInterval
from astropy.io import fits
from pathlib import Path

def metadata(target: str) -> dict:
    with fits.open(target) as obs:
        hdr = dict(obs[0].header)
    return hdr

def show_metadata(target: str) -> None:
    datos = metadata(target)

    for k, v in datos.items():
        print(f"{k}: {v}")

def photo(target: str) -> None:
    with fits.open(target) as hdul:
        data = hdul[0].data

    plt.figure(figsize=(8, 8))
    norm = ImageNormalize(data, interval=ZScaleInterval())
    plt.imshow(data, cmap="gray", origin= "lower", norm=norm)
    plt.colorbar(label="Intensidad")
    plt.title(f"FITS viewer - {target}")
    plt.show()

def cantidad_de_campos_por_archivo(ruta_folder: str) -> dict[str, int]:
    folder = Path(ruta_folder)
    resume = {}

    for archivo in folder.rglob("*.fits"):
        if archivo.name.startswith("._"):
            continue

        header_dict = metadata(str(archivo))
        num_claves = len(header_dict)
        resume[str(archivo)] = num_claves

    return resume

def atributos_vacios_por_archivo(ruta_folder: str) -> dict[str, dict[str, int]]:
    folder = Path(ruta_folder)
    resume = {}

    for archivo in folder.rglob("*.fits"):
        if archivo.name.startswith("._"):
            continue

        with fits.open(archivo) as hdul:
            hdr = dict(hdul[0].header)

            total_campos = len(hdr)
            sin_info = sum(1 for v in hdr.values() if v is None or str(v).strip() == "")
            
            resume[str(archivo)] = {
                "total_campos": total_campos,
                "campos_sin_informacion": sin_info
            }

    return resume    

def save_csv_1(resume: dict, nombre: str) -> None:
    with open(nombre, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["archivo", "sumatoria_campos"])

    for archivo, sumatoria in resume.items():                                                                                                        
        writer.writerow([archivo, sumatoria])                                                                                                        
    print(f"archivo guardado en: {nombre}")  
            
def save_csv_2(resume: dict, nombre: str) -> None:
    with open(nombre, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["archivo", "sumatoria_campo", "campos_sin_informacion"])

        for archivo, datos in resume.items():
            writer.writerow([                                                                                                                            
                archivo,                                                                                                                                 
                datos["total_campos"],                                                                                                                   
                datos["campos_sin_informacion"]                                                                                                          
            ])                                                                                                                                           
    print(f"archivo guardado en: {nombre}")
    
def to_pandas(ruta_folder: str) -> pd.DataFrame:
    filas = []

    archivos_fits = list(Path(ruta_folder).rglob("*.fits"))

    for archivo in archivos_fits:
        if archivo.name.startswith("._"):
            continue

        try:
            with fits.open(archivo, memmap=True) as hdul:
                
                hdr_dict = {}
                
                for k, v in hdul[0].header.items():
                    if not k or k in ("COMMENT", "HISTORY", ""):
                        continue

                    hdr_dict[k] = v

                hdr_dict["__archivo__"] = str(archivo.resolve())
                filas.append(hdr_dict)

        except Exception as e:
            print(f"error en {archivo}: {e}")

    df = pd.DataFrame(filas)
    print("Datos trasladados a dataFrame de pandas")
    return df

def save_dataframe(df: pd.DataFrame, ruta_destino: str) -> None:

    Path(ruta_destino).parent.mkdir(parents=True, exist_ok=True)

    df.to_csv(ruta_destino, index=False, encoding="utf-8")
    print(f"archivo guardado exitosamente en: {ruta_destino}")

def obtener_varianza(df: pd.DataFrame, guardar_en: str) -> None:
    columna_datos = [c for c in df.columns if c != "__archivo__"]
    df_num = df[columna_datos].apply(pd.to_numeric, errors='coerce')
    columnas_numericas = df_num.dropna(how="all", axis=1)
    varianza = columnas_numericas.var(ddof=1)
    varianza = varianza.dropna().sort_values(ascending=False)
    print("varianza calculada")

    df_varianza = varianza.reset_index()
    df_varianza.columns = ["campo", "varianza"]

    df_varianza.to_csv(guardar_en, index=False, encoding="utf-8")
    print(f"archivo guardado en: {guardar_en}")

def cardinalidad_no_numerica(df: pd.DataFrame, guardar_en: str) -> None:
    columna_datos = [c for c in df.columns if c != "__archivo__"]
    df_num = df[columna_datos].apply(pd.to_numeric, errors='coerce')
    columnas_numericas = df_num.dropna(how='all', axis=1).columns

    columnas_no_numericas = [c for c in columna_datos if c not in columnas_numericas]

    cardinalidad = df[columnas_no_numericas].nunique(dropna=True)
    cardinalidad = cardinalidad.sort_values(ascending=False)
    print("cardinalidad calculada")

    df_cardinalidad = cardinalidad.reset_index()
    df_cardinalidad.columns = ["campo", "elementos_distintos"]

    df_cardinalidad.to_csv(guardar_en, index=False, encoding="utf-8")
    print(f"archivo guardado en: {guardar_en}")

def Elementos_con_baja_frecuencia(df: pd.DataFrame, guardar_en: str) -> None:
    columna_datos = [c for c in df.columns if c != "__archivo__"]
    df_num = df[columna_datos].apply(pd.to_numeric, errors='coerce')
    columnas_numericas = df_num.dropna(how='all', axis=1).columns

    columnas_no_numericas = [c for c in columna_datos if c not in columnas_numericas]

    resultados = []

    for col in columnas_no_numericas:
        conteo = df[col].dropna().value_counts()
        conteo = df[col].dropna().value_counts()
        for valor, frec in conteo.items():
            resultados.append({
                "campo": col,
                "valor": valor,
                "frecuencia": frec
            })
    
    df_frecuencias = pd.DataFrame(resultados)

    if not df_frecuencias.empty:
        df_frecuencias = df_frecuencias.sort_values(by=["frecuencia", "campo"], ascending=[True, True])

    print("frecuencias de elementos calculadas")

    df_frecuencias.to_csv(guardar_en, index=False, encoding="utf-8")
    print(f"archivo guardado en: {guardar_en}")

    