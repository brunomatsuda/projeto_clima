# dags/clima_df_pipeline.py
from airflow.decorators import dag, task
from src.config.catalogo_uf import create_base
from datetime import datetime
import os
import sys
# Agora o seu import vai funcionar


from src.config.catalogo_uf import create_base
from src.config.transform_data import processar_uf

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__))))



@dag(
    dag_id="clima_df_pipeline",
    schedule="@monthly",          # ou None se quiser só rodar manualmente
    start_date=datetime(2025, 1, 1),
    catchup=False,
    tags=["clima", "inmet"],
)
def clima_df_pipeline():

    @task
    def gerar_base_raw(uf: str):
        create_base(uf)

    @task
    def transformar_para_gold(uf: str):
        processar_uf(uf)

    uf = "df"  # depois dá pra parametrizar isso
    gerar_base_raw(uf) >> transformar_para_gold(uf)

clima_df_pipeline()