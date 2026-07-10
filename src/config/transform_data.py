from src.config.path import RAW_DF_PATH, GOLD_PATH, RAW_UF_PATH
import pandas as pd

pd.set_option('display.max_columns', None)
pd.set_option('display.width', None)
pd.set_option('display.max_colwidth', None)


def normalize_column(df:pd.DataFrame) -> pd.DataFrame:
    df.columns = df.columns.str.lower()
    df.columns = df.columns.str.replace(".", "", regex=False)\
                .str.replace(",","_", regex=False)\
                .str.replace(" ","_", regex=False)
    
    return df


def normalize_values(df:pd.DataFrame) -> pd.DataFrame:
    df["latitude"] = df["latitude"].str.replace(",", ".")
    df["longitude"] = df["longitude"].str.replace(",", ".")
    df["altitude"] = df["altitude"].str.replace(",", ".")

    df["data"] = pd.to_datetime(df["data"], format="%Y/%m/%d")
    df["data_br"] = df["data"].dt.strftime("%d/%m/%Y")
    df["mes"] = df["data"].dt.month

    df["hora_utc"] = df["hora_utc"].str[0:4]

    df["timestamp_utc"] = pd.to_datetime(df["data_br"] + " " + df["hora_utc"], format="%d/%m/%Y %H%M")
    return df


def rename_columns(df:pd.DataFrame) -> pd.DataFrame:
    renames = {
    "precipitação_total__horário_(mm)": "precipitacao_total_mm",
    "pressao_atmosferica_ao_nivel_da_estacao__horaria_(mb)": "pressao_estacao_mb",
    "pressão_atmosferica_maxna_hora_ant_(aut)_(mb)": "pressao_max_mb",
    "pressão_atmosferica_min_na_hora_ant_(aut)_(mb)": "pressao_min_mb",
    "radiacao_global_(kj/m²)": "radiacao_global_kj_m2",
    "temperatura_do_ar_-_bulbo_seco__horaria_(°c)": "temperatura_seco_c",
    "temperatura_do_ponto_de_orvalho_(°c)": "temperatura_orvalho_c",
    "temperatura_máxima_na_hora_ant_(aut)_(°c)": "temperatura_max_c",
    "temperatura_mínima_na_hora_ant_(aut)_(°c)": "temperatura_min_c",
    "temperatura_orvalho_max_na_hora_ant_(aut)_(°c)": "temperatura_orvalho_max_c",
    "temperatura_orvalho_min_na_hora_ant_(aut)_(°c)": "temperatura_orvalho_min_c",
    "umidade_rel_max_na_hora_ant_(aut)_(%)": "umidade_max_porcento",
    "umidade_rel_min_na_hora_ant_(aut)_(%)": "umidade_min_porcento",
    "umidade_relativa_do_ar__horaria_(%)": "umidade_porcento",
    "vento__direção_horaria_(gr)_(°_(gr))": "vento_direcao_graus",
    "vento__rajada_maxima_(m/s)": "vento_rajada_ms",
    "vento__velocidade_horaria_(m/s)": "vento_velocidade_ms"
    }

    df = df.rename(columns=renames)
    return df


def alter_schema_columns(df:pd.DataFrame) -> pd.DataFrame:
    schema_dict = {
        "latitude": "float",
        "longitude": "float",
        "altitude": "float"
    }

    df = df.astype(schema_dict)
    return df


def drop_columns(df:pd.DataFrame) -> pd.DataFrame:
    df = df.drop(columns=["codigo_(wmo)", "data_de_fundacao", "data"])
    return df


def termal_amplitude_column(df:pd.DataFrame) -> pd.DataFrame:
    df["month_max_t"] = (
        df.groupby("mes")["temperatura_max_c"].transform("max")
    )

    df["month_min_t"] = (
        df.groupby("mes")["temperatura_min_c"].transform("min")
    )

    df["month_amplitude_t"] = (
        df.groupby("mes")["temperatura_max_c"].transform("max") - df.groupby("mes")["temperatura_min_c"].transform("min")
    )

    return df


def order_columns(df:pd.DataFrame) -> pd.DataFrame:
    colunas_ordenadas = [
    # Identificação
    "regiao", "uf","estacao",
    
    # Localização
    "latitude", "longitude", "altitude",

    # Tempo
    "timestamp_utc", "data_br", "hora_utc", "mes",

    # Temperatura
    "temperatura_seco_c", "temperatura_max_c", "temperatura_min_c", "month_max_t", "month_min_t", "month_amplitude_t",

    # Ponto de orvalho
    "temperatura_orvalho_c", "temperatura_orvalho_max_c", "temperatura_orvalho_min_c",

    # Umidade
    "umidade_porcento", "umidade_max_porcento", "umidade_min_porcento",

    # Pressão
    "pressao_estacao_mb", "pressao_max_mb", "pressao_min_mb",

    # Precipitação e radiação
    "precipitacao_total_mm", "radiacao_global_kj_m2",

    # Vento
    "vento_direcao_graus", "vento_velocidade_ms", "vento_rajada_ms",
    ]

    df = df[colunas_ordenadas]
    return df


def export_df(df:pd.DataFrame, archive_name:str, uf:str) -> None:
    uf = uf.replace(uf[0:3],"gold") #trocando 'raw' por 'gold'
    gold_uf = GOLD_PATH/uf
    gold_uf.mkdir(parents=True, exist_ok=True)

    df.to_csv(
        gold_uf /f"{archive_name}.csv",
        index=False
    )


def data_pipeline(df: pd.DataFrame, archive_name: str, uf:str) -> pd.DataFrame:
    return(df
        .pipe(normalize_column)
        .pipe(normalize_values)
        .pipe(rename_columns)
        .pipe(alter_schema_columns)
        .pipe(drop_columns)
        .pipe(termal_amplitude_column)
        .pipe(order_columns)
        .pipe(export_df, archive_name, uf)
    )



if __name__ == "__main__":
    uf = 'raw_df_'
    RAW_UF_PATH = RAW_UF_PATH/uf
    for arquivo in RAW_UF_PATH.glob("*parquet"):
        df = pd.read_parquet(arquivo)
        data_pipeline(df, archive_name=arquivo.stem, uf=uf)
