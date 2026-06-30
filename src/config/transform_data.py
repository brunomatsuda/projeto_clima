from src.config.path import RAW_DF_PATH
import pandas as pd

def remove_dots(df:pd.DataFrame) -> pd.DataFrame:
    df = df.rename(columns=lambda c: c.replace(".", ""))
    print(df.head())
    return df









def data_pipeline(df):
    return(df
        .pipe(remove_dots)
    )




if __name__ == "__main__":
    for arquivo in RAW_DF_PATH.glob("*parquet"):
        df = pd.read_parquet(arquivo)
        data_pipeline(df)

