# 🌦️ Projeto Clima — Pipeline de Dados Meteorológicos (INMET)

Pipeline de engenharia de dados que processa dados históricos meteorológicos do **INMET** (Instituto Nacional de Meteorologia), transformando arquivos CSV brutos em datasets analíticos prontos para consumo, seguindo uma arquitetura inspirada no modelo **Medallion (Raw → Processed → Gold)** e orquestrado com **Apache Airflow**.

Projeto desenvolvido como parte da minha transição de carreira de **Analista de Dados** para **Engenharia de Dados**, com foco em aplicar na prática conceitos como pipelines de ETL, organização em camadas de dados, versionamento e boas práticas de estruturação de código.

---

## 🏗️ Arquitetura do pipeline

```
data/raw/  --(catalogo_uf.py)-->  data/raw__{uf}__/*.parquet  -->(transform_data.py)-->  data/gold/{uf}/*.csv
   (CSV bruto do INMET)              (Parquet intermediário)                (CSV tratado, pronto para análise)

                                                               ⬆
                                          orquestrado pela DAG `clima_df_pipeline` (Airflow)
```

1. **Raw** (`data/raw`) — arquivos CSV originais baixados do portal de dados históricos do INMET 2025 (um arquivo por estação meteorológica).
2. **Ingestão** (`src/config/catalogo_uf.py`) — lê os CSVs, separa os metadados do cabeçalho (região, UF, coordenadas, altitude etc.) dos dados horários, junta as duas partes e salva o resultado em **Parquet**, particionado por UF.
3. **Transformação / Gold** (`src/config/transform_data.py`) — aplica uma pipeline de limpeza e enriquecimento (normalização de nomes de colunas, correção de tipos, cálculo de amplitude térmica mensal, reordenação de colunas, tratamento de datas) e exporta o resultado final em **CSV** na camada Gold.
4. **Exploração** (`sql/consulta.ipynb`) — notebook usando **PySpark** para validar as transformações de forma independente e calcular métricas como amplitude térmica mensal e anual.

---

## 🔄 Orquestração com Airflow
 
O pipeline é orquestrado pela DAG **`clima_df_pipeline`**, que automatiza as duas etapas principais do processo (ingestão e transformação), eliminando a necessidade de rodar os scripts manualmente.
 
| Configuração | Valor |
|---|---|
| **DAG ID** | `clima_df_pipeline` |
| **Schedule** | `@monthly` |
| **Catchup** | `False` |
| **Tags** | `clima`, `inmet` |
 
**Fluxo de tasks:**
 
```
gerar_base_raw(uf) >> transformar_para_gold(uf)
```
 
- `gerar_base_raw` — chama `create_base()`, responsável por gerar o Parquet intermediário a partir dos CSVs brutos.
- `transformar_para_gold` — chama `processar_uf()`, responsável por aplicar as transformações e exportar o CSV final para a camada Gold.
A DAG usa a API de **TaskFlow** (`@dag` / `@task`) do Airflow, reaproveitando diretamente as funções já existentes em `src/config/`, sem duplicar lógica entre o pipeline "manual" (`main/main.py`) e o orquestrado.

### Subindo o ambiente do Airflow localmente
 
O projeto usa o `docker-compose.yaml` oficial do Airflow (CeleryExecutor + Redis + Postgres):
 
```bash
cd airflow
echo -e "AIRFLOW_UID=$(id -u)" > .env
docker compose up airflow-init
docker compose up
```
 
Depois de subir, a UI fica disponível em [http://localhost:8080](http://localhost:8080) (usuário/senha padrão: `airflow` / `airflow`).
 
---

## ⚙️ Tecnologias utilizadas

- **Python 3.13**
- **Pandas** + **PyArrow** — pipeline principal (ingestão e transformação)
- **PySpark** — exploração e validação de dados em notebook
- **Argparse** — interface de linha de comando

---

## 📂 Estrutura do projeto

```
projeto_clima/
├── airflow/
│   ├── dags/
│   │   └── clima_df_pipeline.py   # DAG de orquestração do pipeline
│   ├── config/                    # airflow.cfg
│   ├── logs/                      # logs de execução (não versionado)
│   └── docker-compose.yaml        # ambiente Airflow (Celery + Redis + Postgres)
├── main/
│   └── main.py                    # Ponto de entrada (CLI)
├── src/
│   └── config/
│       ├── path.py                # Paths centralizados do projeto
│       ├── catalogo_uf.py         # Ingestão: CSV bruto -> Parquet
│       └── transform_data.py      # Transformação: Parquet -> CSV (gold)
├── sql/
│   └── consulta.ipynb             # Notebook exploratório (PySpark)
├── data/
│   ├── raw/                       # CSVs originais do INMET (não versionado)
│   ├── raw__{uf}__/               # Parquet intermediário por UF (não versionado)
│   └── gold/                      # Dados finais tratados (versionado só a estrutura)
└── .gitignore
```

---

## ▶️ Como executar
### Opção 1 — Rodando o pipeline manualmente (sem Airflow)
1. Clone o repositório e crie um ambiente virtual:
   ```bash
   git clone https://github.com/brunomatsuda/projeto_clima.git
   cd projeto_clima
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Baixe os dados históricos do [INMET](https://portal.inmet.gov.br/dadoshistoricos) e coloque os arquivos `.CSV` em `data/raw/` (no repositório você irá notar que a pasta `raw/` já contém os arquivos de 2026(janeira - junho)).

3. Rode o pipeline para uma UF específica:
   ```bash
   python -m main.main --uf df
   ```
   OU
   ```bash
   echo isso irá rodar todos os arquivos presentes na pasta raw/
   python -m main.main --uf all
   ```
   O resultado final estará disponível em `data/gold/`.

### Opção 2 — Rodando via Airflow (orquestrado)
1. Suba o ambiente do Airflow (veja seção [Orquestração com Airflow](#-orquestração-com-airflow) acima).
2. Acesse a UI em `http://localhost:8080` e ative a DAG `clima_df_pipeline`.
3. Dispare a DAG manualmente (▶️) ou aguarde o agendamento mensal (`@monthly`).
4. Acompanhe a execução das tasks `gerar_base_raw` e `transformar_para_gold` pela Grid/Graph View.
---


## 📊 Exemplo de análise: Amplitude Térmica

O pipeline calcula a **amplitude térmica mensal** (diferença entre a maior temperatura máxima e a menor temperatura mínima registradas no mês), uma métrica clássica de climatologia usada para entender a variação de temperatura ao longo do ano.

| Mês | Temp. Mín (°C) | Temp. Máx (°C) | Amplitude (°C) |
|-----|-----------------|-----------------|-----------------|
| Jan | 16.7            | 30.3            | 13.6            |
| Jul | 12.5            | 28.6            | 16.1            |
| Out | 13.4            | 33.2            | 19.8            |

---
## 🇰 Kaggle

Caso queira um arquivo com todas as 27 uf`s compiladas, basta acessar o site do [kaggle](https://www.kaggle.com/datasets/brunommm/dados-climticos-inmet-2026-tratados)


## 👤 Autor

**[Bruno Matsuda]**

[LinkedIn](https://www.linkedin.com/in/bruno-matsuda-904747262/) • [GitHub](https://github.com/brunomatsuda)

