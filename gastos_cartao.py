import pandas as pd
from datetime import datetime
from dotenv import load_dotenv
from dados.despesas.despesas_fixas import DespesasFixas
import os

load_dotenv()

caminho = "./dados"
gastos = f"{caminho}/Controle de Gastos.xlsx"
sheet = "Gastos_2025"

descontos = {
    '10-2025': 870,
    '12-2025': 1250,
    '02-2026': 350,
    '05-2026': 1695,
}

## Instanciando a classe ja preenchida em dados para o valor das despesas fixas
despFixas = DespesasFixas()
print(f"""
    O valor das despesas fixas é de: R$ {despFixas.total_despesas()}
""")


receita_bolha = os.getenv("RECEITA_BOLHA")
gastos_bolha = os.getenv("GASTOS_BOLHA")
IR_math = os.getenv("IR_MATH")
IR_gabi = os.getenv("IR_GABI")
salario_math = os.getenv("SALARIO_MATH")
salario_gabis = os.getenv("SALARIO_GABIS")

def parse_salario(valor_str):
    """Converte uma string de salário no formato '1.234,56' para float."""
    if valor_str is None:
        return 0.0
    valor_str = valor_str.replace('.', '').replace(',', '.')
    return float(valor_str)

def soma_outras_receitas(s1,s2,s3,s4):
    receita_bolha = parse_salario(s1)
    gastos_bolha = parse_salario(s2)
    IR_math = parse_salario(s3)
    IR_gabi = parse_salario(s4)
    outras_receitas = sum([receita_bolha, IR_math, IR_gabi]) - gastos_bolha
    return outras_receitas

receitas_extras = (
    soma_outras_receitas(
        receita_bolha,
        gastos_bolha,
        IR_math,
        IR_gabi
    )
)

receitas_extras = {
    'Vigência': ['2025-09'],
    'outras_receitas': [receitas_extras] 
}

receitas_extras = pd.DataFrame(receitas_extras)

def soma_salarios(s1, s2):
    salario_gabis = parse_salario(s2)
    salario_math = parse_salario(s1)
    
    salario_total = salario_math + salario_gabis
    return salario_total
salario_total = soma_salarios(salario_math, salario_gabis)


def dizimo(salario_total):
    dizimo = salario_total * 0.1
    salario_total = salario_total - dizimo
    return salario_total, dizimo
salario_total, dizimo = dizimo(salario_total)
print(f"""salario após dízimo: R$ {salario_total:.2f}, 
            sendo o dízimo de R$ {dizimo:.2f}
""")

def reserva(salario_total):
    reserva = salario_total * 0.1
    salario_total = salario_total - reserva
    return salario_total, reserva
salario_total, reserva = reserva(salario_total)
print(f"""salario após reserva: R$ {salario_total:.2f}, 
            sendo a reserva de R$ {reserva:.2f}
""")


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
df = ler_arquivo_excel(gastos, sheet)

def gastos_totais(df):
    df['Vigência'] = pd.to_datetime(df['Vigência'], errors='coerce').dt.strftime('%Y-%m')
    df = df.groupby('Vigência')['Valor'].sum().reset_index()
    return df
df = gastos_totais(df)

def comparativo_gastos(df):
    df3 = df.copy()
    df3 = df3.sort_values('Vigência').reset_index(drop=True)

    df3['Diferença'] = df3['Valor'].diff()
    df3['Percentual'] = df3['Valor'].pct_change() * 100

    for i, row in df3.iterrows():
        mes = row['Vigência']
        valor = row['Valor']
        if i == 0:
            print(f"No mês {mes}, o gasto foi de R$ {valor:.2f}.")
        else:
            diff = row['Diferença']
            perc = row['Percentual']
            status = "aumento" if diff > 0 else "queda" if diff < 0 else "estável"
            print(
                f"""No mês {mes}, 
                    o gasto foi de R$ {valor:.2f} 
                    ({status} de R$ {diff:.2f}, {perc:.2f}% 
                    em relação ao mês anterior).
                """
            )
    return df3
df3 = comparativo_gastos(df)

def aplicar_descontos(df3, descontos):
    descontos_fmt = {k if '-' in k and len(k) == 7 else datetime.strptime(k, '%m-%Y').strftime('%Y-%m'): v for k, v in descontos.items()}

    descontos_acumulados = []
    for mes in df3['Vigência']:
        desconto_total = sum(
            v for k, v in descontos_fmt.items() if k <= mes
        )
        descontos_acumulados.append(desconto_total)
    df3['Descontos acumulados'] = descontos_acumulados
    df3['Valor com desconto'] = df3['Valor'] - df3['Descontos acumulados']
    return df3

df3 = aplicar_descontos(df3, descontos)
    

def preencher_valores_faltantes(df3):
    df3 = df3.fillna(0)
    return df3


def tratar_arquivo(df):
    if df is not None:
        ## converte a coluna vigência para date_time
        df['Vigência'] = pd.to_datetime(df['Vigência'], errors='coerce').dt.strftime('%m-%Y')

        ## fazemos o agrupamento e depois somamos os valores
        grouped = df.groupby(['Cartão', 'Vigência']).sum(numeric_only=True).reset_index()
        
        ## pivotamos a tabela agrupada pelo cartão e criamos as colunas de vigência
        tabela_pivot = grouped.pivot(index='Cartão', columns='Vigência')
        tabela_pivot = tabela_pivot.fillna(0)
        return df, tabela_pivot

df  = ler_arquivo_excel(gastos, sheet)
df2, tabela = tratar_arquivo(df)

def tras_dono_cartao(tabela):
    # Copia os dados
    df22 = tabela.copy()

    # Remove a coluna 'Vigência' se existir
    if 'Vigência' in df22.columns:
        df22 = df22.drop(columns='Vigência')
    # Se df22 tem MultiIndex nas colunas, achatamos:
    if isinstance(df22.columns, pd.MultiIndex):
        df22.columns = ['_'.join(col).strip() if isinstance(col, tuple) else col for col in df22.columns]

    # Resetamos o índice, por segurança
    df22.reset_index(inplace=True)

    # Garante que df2 tenha 'Cartão' e 'Dono'
    donos = df2[['Cartão', 'Dono']].drop_duplicates()
    df22 = df22.merge(donos, on='Cartão', how='left')
    return df22



def reordena_colunas(df2):
    cols = df2.columns.tolist()
    # Garante que 'Dono' e 'Cartão' estejam no início
    new_order = [col for col in ['Dono', 'Cartão'] if col in cols] + [col for col in cols if col not in ['Dono', 'Cartão']]
    df2 = df2[new_order]

    return df2

df3 = preencher_valores_faltantes(df3)

def perc_gastos(salario_total):
    ## Perc_Gastos é a variação percentual em relação ao salário total
    df3["Perc_Gastos"] = round((df3["Valor com desconto"] - salario_total) / salario_total, 4) * 100
    df3.sort_values("Vigência", ascending=True)
    return df3


df3 = perc_gastos(salario_total)

def outras_receitas(df3, receitas_extras):
    df3 = df3.merge(receitas_extras, on='Vigência', how='left')
    df3.fillna(0.0)
    return df3

df3 = outras_receitas(df3, receitas_extras)

def calcular_sobra(df3, salario_total):
    if (df3["Perc_Gastos"] < 0.0).any():
        df3["sobra"] = (salario_total - df3["Valor com desconto"]) + df3["outras_receitas"]
    else:
        df3["sobra"] = 0.0
    return df3

df3 = calcular_sobra(df3, salario_total)
# print(df3)
