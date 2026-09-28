import matplotlib.pyplot as plt
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

def save_csv(resume: dict[str, int], nombre: str ="sumatoria_campos.csv") -> None:
    with open(nombre, mode="w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["archivo", "sumatoria_campos"])

        for archivo, sumatoria in resume.items():
            writer.writerow([archivo, sumatoria])
            print("archivo guardado")

