import pandas as pd
import os
from dotenv import load_dotenv
load_dotenv()

caminho = "./dados"
path_file = f"{caminho}/Controle de Gastos.xlsx"
sheet = "Investimentos"
taxa_selic = f"{caminho}/taxa_selic_apurada.csv"

def ler_investimentos(path_file, sheet):

    df = pd.read_excel(
        path_file, 
        sheet_name=sheet, 
        engine="openpyxl"
    )
    return df

def ler_taxa_selic(path_file):
    selic = pd.read_csv(
        taxa_selic, 
        sep=";"
    )
    return selic    

## Dados de investimentos
df = ler_investimentos(path_file, sheet)
df["acumulado_investido"] = df["Valor"].sum()
# print(df.info())

print()

## Dados da Selic - Bacen
selic = ler_taxa_selic(taxa_selic)

def trata_data(df, col):
    df[col] = pd.to_datetime(df[col], format= "%Y-%m-%d", errors='coerce')
    df["ano"] = df[col].dt.year
    df["mes"] = df[col].dt.month
    df["ANOMES"] = df["ano"].astype(str) + df["mes"].astype(str).str.zfill(2)
    df = df.drop(columns=["ano", "mes"])

    return df

def trata_valores(df, column_list: list):
    df.columns = df.columns.str.strip()

    # Verificar colunas ausentes
    for col in column_list:
        if col not in df.columns:
            raise KeyError(f"Coluna '{col}' não encontrada no DataFrame.")

    df[column_list] = df[column_list].apply(
        lambda col: col.astype(str).str.replace(",", ".", regex=False).astype(float)
    )

    return df

selic = trata_data(selic, "Data")
df = trata_data(df, "Data")

selic = trata_valores(
          selic,
          column_list=[
            "Taxa_aa", 
            "Taxa_media", 
            "Taxa_mediana", 
            "Taxa_modal", 
            "Desvio_Padrao", 
            "Curtose"]
        )

selic2 = selic[["Taxa_media", "ANOMES"]]

def add_taxa(df, selic):
    df = (
        pd.merge(
            df, selic, 
            on='ANOMES', 
            how='left'
        )
    )
    df = df.fillna(df["Taxa_media"].mean())
    return df


def calcula_juros(df):
    ## Taxa media mensal
    df = add_taxa(df, selic[["ANOMES", "Taxa_media"]])
    df["Taxa_media_mensal"] = (
        (((1 + (df["Taxa"] +  df["fixo"])) ** (1/12)) - 1)
    )

    df['vl_invest_acum'] = df['Valor'].cumsum()


    df2 = df[['Data']]
    df2 = df2.sort_values('Data').reset_index(drop=True)

    df2['Dias_para_proximo'] = (
        df2['Data'].shift(-1) - df2['Data']
    )
    df2['Dias_para_proximo'] = df2['Dias_para_proximo'].dt.days 
    data_final = df2['Data'].max()

    df2 = (
        pd.merge(
            df2, df[
                ['Data', 
                 'Taxa_media_mensal',
                 'Valor',
                 'vl_invest_acum'
                ]
            ], 
            on='Data', 
            how='left'
        )
    )

    return df2

df2 = calcula_juros(df)

## confirmar corretamente o calculo
df2["taxa_total_periodo"] = df2["Taxa_media_mensal"] * df2["Dias_para_proximo"]
df2["juros"] = df2["vl_invest_acum"] * (df2["taxa_total_periodo"])
print(df2)

