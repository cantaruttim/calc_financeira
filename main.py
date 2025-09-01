import pandas as pd
from datetime import datetime

file_path = "./dados/Controle de Gastos.xlsx"
sheet = "Gastos_2025"

descontos = {
    '10-2025': 870,
    '12-2025': 1100,
    '02-2026': 350,
    '05-2026': 1695
}

def ler_arquivo_excel(file_path, sheet):
    try:
        df = pd.read_excel(
            file_path, 
            sheet_name=sheet, 
            engine="openpyxl"
        )
    except FileNotFoundError:
        print(f"Arquivo não encontrado: {file_path}")
    except ValueError as e:
        print(f"Erro ao ler a planilha: {e}")
    except Exception as e:
        print(f"Ocorreu um erro: {e}")
    return df
df = ler_arquivo_excel(file_path, sheet)

def tratar_arquivo(df):
    if df is not None:
        df['Vigência'] = pd.to_datetime(df['Vigência'], errors='coerce').dt.strftime('%m-%Y')

        grouped = df.groupby(['Cartão', 'Vigência']).sum(numeric_only=True).reset_index()
        
        tabela_pivot = grouped.pivot(index='Cartão', columns='Vigência')
        tabela_pivot = tabela_pivot.fillna(0)
        return df, tabela_pivot

df, tabela = tratar_arquivo(df)
descontos_dt = {datetime.strptime(k, '%m-%Y'): v for k, v in descontos.items()}

def proximo_desconto(mes_atual, descontos_dict):
    """Retorna o valor do menor desconto cuja data seja >= mes_atual"""
    candidatos = [d for d in descontos_dict if d >= mes_atual]
    if not candidatos:
        return 0  
    desconto_data = min(candidatos)
    return descontos_dict[desconto_data]


def gastos_cartao(df):
    meses = list(df.columns.get_level_values(1).unique())

    for i in range(len(meses)):
        nome_mes = meses[i]
        dt_mes = datetime.strptime(nome_mes, '%m-%Y')

        valor_mes = df.xs(nome_mes, level=1, axis=1).sum().sum()
        desconto = proximo_desconto(dt_mes, descontos_dt)
        valor_com_desconto = valor_mes - desconto

        if i == 0:
            print(
                f'''
                Os gastos do mês {nome_mes} no cartão
                    foi de R$ {round(valor_com_desconto, 2)}
                '''
            )
        else:
            nome_mes_anterior = meses[i - 1]
            dt_anterior = datetime.strptime(nome_mes_anterior, '%m-%Y')
            valor_anterior = df.xs(nome_mes_anterior, level=1, axis=1).sum().sum()
            desconto_anterior = proximo_desconto(dt_anterior, descontos_dt)
            valor_anterior_com_desconto = valor_anterior - desconto_anterior

            perc_gastos = ((valor_com_desconto - valor_anterior_com_desconto) / valor_anterior_com_desconto * 100) if valor_anterior_com_desconto != 0 else 0

            print(
                f'''
                Os gastos do mês {nome_mes} no cartão
                    foi de R$ {round(valor_com_desconto, 2)} com um percentual de
                    {round(perc_gastos, 2)}% em relação ao mês anterior.
                '''
            )
          

def tras_dono_cartao(tabela):
    df2 = tabela.copy()

    if 'Vigência' in df2.columns:
        df2 = df2.drop(columns='Vigência')

    if isinstance(df2.columns, pd.MultiIndex):
        df2.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in df2.columns]

    df2.reset_index(inplace=True)
    donos = df[['Cartão', 'Dono']].drop_duplicates()
    df2 = df2.merge(donos, on='Cartão', how='left')
    return df2



def reordena_colunas(df):
    cols = df.columns.tolist()
    new_order = [col for col in ['Dono', 'Cartão'] if col in cols] + [col for col in cols if col not in ['Dono', 'Cartão']]
    df = df[new_order]
    return df

df = reordena_colunas(tras_dono_cartao(tabela))
print(df)
gastos_cartao(tabela)
