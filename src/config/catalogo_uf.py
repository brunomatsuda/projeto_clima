from src.config.path import RAW_PATH, RAW_DF_PATH
from pathlib import Path
import pandas as pd

#Rodar no CMD: python3 -m src.config.catalogo_uf.py

arquivos = list(Path(RAW_PATH).glob("*.CSV"))

for arquivo in arquivos:
    if '_df_' in arquivo.name.lower():
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

            df_dados = df_dados.dropna(how='all', axis=1)

            # Inserindo metadados em df_dados
            for chave, valor in metadados.items():
                df_dados[chave] = valor
            
            colunas_metadados = list(metadados.keys())
            colunas_dados = [col for col in df_dados.columns if col not in colunas_metadados]
            df_dados = df_dados[colunas_metadados + colunas_dados]

            df_dados.to_parquet(RAW_DF_PATH/(arquivo.stem+".parquet"), engine="pyarrow", index=False)

        except Exception as e:
            print(f"Erro em {arquivo.name}: {e}")