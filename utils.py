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
    plt.colorbar(label="Intensida")
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
            print("archivo guardado")
            
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
    
def to_pandas()        