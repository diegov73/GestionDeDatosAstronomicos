from utils import *
main_folder = "./muestras"
target_file = "./muestras/XSHOO.2026-09-04/XSHOO.2026-09-04T01_43_37.983.fits"

df = to_pandas(main_folder)

save_dataframe(df, "./csv/dataSet.csv")