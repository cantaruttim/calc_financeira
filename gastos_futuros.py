import pandas as pd


gf = pd.read_excel(
    "./dados/parcelado.xlsx", 
    sheet_name="parcelados"
)

print(gf)