import pandas as pd
from utils import *
main_folder = "./muestras"
target_file = "./muestras/XSHOO.2026-09-04/XSHOO.2026-09-04T01_43_37.983.fits"
data_frame = pd.read_csv("./csv/dataSet.csv")


cardinalidad_no_numerica(data_frame, "./csv/cardinalidaNoNumerica.csv")