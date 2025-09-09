import pandas as pd
from datetime import datetime

hoje = datetime.today()
ano_mes_atual = hoje.strftime('%Y-%m')

donos = pd.read_excel("./dados/Controle de Gastos.xlsx", sheet_name="Gastos_2025")
gf = pd.read_excel("./dados/parcelado.xlsx", sheet_name="parcelados")

def tras_dono_cartao(gf, donos):
    # Copia os dados
    df22 = gf.copy()

    # Remove a coluna 'Vigência' se existir
    # if 'Vigência' in df22.columns:
    #     df22 = df22.drop(columns='Vigência')

    # Se df22 tem MultiIndex nas colunas, achatamos:
    if isinstance(df22.columns, pd.MultiIndex):
        df22.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in df22.columns]

    # Resetamos o índice, por segurança
    df22.reset_index(inplace=True)

    # Verificação: Cartão existe?
    if 'Cartão' not in df22.columns:
        raise ValueError("A coluna 'Cartão' não foi encontrada em df22!")

    # Faz o merge com os donos passados como argumento
    df22 = df22.merge(donos.drop_duplicates(), on='Cartão', how='left')
    df22 = df22[ df22["Dono"].isin(
        ["GABRIELLA QUINTEIRO", "MATHEUS CANTARUTTI"]
        )
    ]
    df22 = df22.drop(columns=["index"])
    return df22

df = tras_dono_cartao(gf, donos[["Cartão", "Dono"]])

print(df)