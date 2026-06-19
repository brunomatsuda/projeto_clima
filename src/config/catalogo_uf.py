from src.config.path import RAW_PATH, RAW_DF_PATH
from pathlib import Path
import pandas as pd

#Rodar no CMD: python3 -m src.config.catalogo_uf.py

arquivos = list(Path(RAW_PATH).glob("*.CSV"))

for arquivo in arquivos:
    if '_df_' in arquivo.name.lower():
        try:
            df = pd.read_csv(
                arquivo,
                encoding="ISO-8859-1",
                sep=";",
                on_bad_lines="skip"
            )
            parquet_path = Path(RAW_DF_PATH) / (arquivo.stem + ".parquet")
            df.to_parquet(parquet_path, engine="pyarrow", index=False)

        except Exception as e:
            print(f"ERRO em {arquivo.name}: {e}")
