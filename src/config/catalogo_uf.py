"""
Este script é responsável por consolidar e organizar os dados de Unidades da Federação (UF),
realizando a junção dos metadados com as bases de dados correspondentes.
"""

from src.config.path import RAW_PATH, RAW_DF_PATH, RAW_UF_PATH
from pathlib import Path
import pandas as pd



def create_base(uf:str): # Cria um diretório com a uf passada
    global RAW_UF_PATH

    arquivos = list(Path(RAW_PATH).glob("*.CSV"))
    
    if uf != '*':
        RAW_UF_PATH = RAW_UF_PATH/f"raw{uf}"
    else:
        RAW_UF_PATH = RAW_UF_PATH/"raw_all"

    paste = RAW_UF_PATH
    paste.mkdir(parents=True, exist_ok=True)

    for arquivo in arquivos:
        if uf in arquivo.name.lower() or uf=="_*_":
            try: #try para pegar os metadados
                df_meta_dados = pd.read_csv(
                    arquivo,
                    encoding="ISO-8859-1",
                    sep=";",
                    nrows=8,
                    header=None,
                    usecols=[0,1]
                )

                metadados = {}
                for _, linha in df_meta_dados.iterrows():
                    chave = str(linha[0]).replace(":", "").strip()
                    valor = str(linha[1]).strip()
                    metadados[chave] = valor
                
                # pega o restante dos dados
                df_dados = pd.read_csv(
                    arquivo,
                    encoding="ISO-8859-1",
                    sep=";",
                    skiprows=8,
                    header=0,
                    decimal=","
                )

                #df_dados = df_dados.dropna(how='all', axis=1) # Remove a colunas, caso todos os valoers sejam null

                # Inserindo metadados em df_dados
                for chave, valor in metadados.items():
                    df_dados[chave] = valor
                
                colunas_metadados = list(metadados.keys())
                colunas_dados = [col for col in df_dados.columns if col not in colunas_metadados]
                df_dados = df_dados[colunas_metadados + colunas_dados]
                
                df_dados.to_parquet(RAW_UF_PATH/(arquivo.stem+".parquet"), engine="pyarrow", index=False)
                

            except Exception as e:
                print(f"Erro em {arquivo.name}: {e}")
                
    print(f"Pasta raw{uf} gerada com sucesso!")

if __name__ == "__main__":
    create_base("_*_") #Passar a UF desejada ou "_*_" para passar todas as uf`s