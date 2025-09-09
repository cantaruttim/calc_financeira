import pandas as pd
from datetime import datetime

hoje = datetime.today()
ano_mes_atual = hoje.strftime('%Y-%m')

donos = pd.read_excel("./dados/Controle de Gastos.xlsx", sheet_name="Gastos_2025")
gf = pd.read_excel("./dados/parcelado.xlsx", sheet_name="parcelados")

def retorna_status_parcela(df):
    if (df["PARCELA"] <= df["TOTAL_PARCELA"]).all():
        df["proxima_parcela"] = "Possui"
    else:
        df["proxima_parcela"] = "Não Possui"
    return df

def retorna_maior_anomes(df):
    df["ANOMES"] = df["ANOMES"].astype(int)
    maior_anomes = df["ANOMES"].max()
    return df[ df["ANOMES"] == maior_anomes ]

def tras_dono_cartao(gf, donos):
    df22 = gf.copy()

    if isinstance(df22.columns, pd.MultiIndex):
        df22.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in df22.columns]

    df22.reset_index(inplace=True)

    if 'Cartão' not in df22.columns:
        raise ValueError("A coluna 'Cartão' não foi encontrada em df22!")

    df22 = df22.merge(donos.drop_duplicates(), on='Cartão', how='left')
    df22 = df22[ df22["Dono"].isin(
            [
                "GABRIELLA QUINTEIRO", 
                "MATHEUS CANTARUTTI"
            ]
        )
    ]

    df22 = df22.drop(columns=["index"])
    return df22

df = tras_dono_cartao(gf, donos[["Cartão", "Dono"]])
df = retorna_maior_anomes(df)
df = retorna_status_parcela(df)




print(df)