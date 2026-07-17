# 🌦️ Projeto Clima DF — Pipeline de Dados Meteorológicos (INMET)

Pipeline de engenharia de dados que processa dados históricos meteorológicos do **INMET** (Instituto Nacional de Meteorologia), transformando arquivos CSV brutos em datasets analíticos prontos para consumo, seguindo uma arquitetura inspirada no modelo **Medallion (Raw → Processed → Gold)**.

Projeto desenvolvido como parte da minha transição de carreira de **Analista de Dados** para **Engenharia de Dados**, com foco em aplicar na prática conceitos como pipelines de ETL, organização em camadas de dados, versionamento e boas práticas de estruturação de código.

---

## 🏗️ Arquitetura do pipeline

```
data/raw/  --(catalogo_uf.py)-->  data/raw__{uf}__/*.parquet  -->(transform_data.py)-->  data/gold/{uf}/*.csv
   (CSV bruto do INMET)              (Parquet intermediário)                (CSV tratado, pronto para análise)
```

1. **Raw** (`data/raw`) — arquivos CSV originais baixados do portal de dados históricos do INMET 2025 (um arquivo por estação meteorológica).
2. **Ingestão** (`src/config/catalogo_uf.py`) — lê os CSVs, separa os metadados do cabeçalho (região, UF, coordenadas, altitude etc.) dos dados horários, junta as duas partes e salva o resultado em **Parquet**, particionado por UF.
3. **Transformação / Gold** (`src/config/transform_data.py`) — aplica uma pipeline de limpeza e enriquecimento (normalização de nomes de colunas, correção de tipos, cálculo de amplitude térmica mensal, reordenação de colunas, tratamento de datas) e exporta o resultado final em **CSV** na camada Gold.
4. **Exploração** (`sql/consulta.ipynb`) — notebook usando **PySpark** para validar as transformações de forma independente e calcular métricas como amplitude térmica mensal e anual.

---

## ⚙️ Tecnologias utilizadas

- **Python 3.13**
- **Pandas** + **PyArrow** — pipeline principal (ingestão e transformação)
- **PySpark** — exploração e validação de dados em notebook
- **Argparse** — interface de linha de comando

---

## 📂 Estrutura do projeto

```
projeto_clima-df/
├── main/
│   └── main.py                # Ponto de entrada (CLI)
├── src/
│   └── config/
│       ├── path.py            # Paths centralizados do projeto
│       ├── catalogo_uf.py     # Ingestão: CSV bruto -> Parquet
│       └── transform_data.py  # Transformação: Parquet -> CSV (gold)
├── sql/
│   └── consulta.ipynb         # Notebook exploratório (PySpark)
├── data/
│   ├── raw/                   # CSVs originais do INMET (não versionado)
│   ├── raw__{uf}__/           # Parquet intermediário por UF (não versionado)
│   └── gold/                  # Dados finais tratados (versionado só a estrutura)
└── .gitignore
```

---

## ▶️ Como executar

1. Clone o repositório e crie um ambiente virtual:
   ```bash
   git clone https://github.com/<seu-usuario>/projeto_clima-df.git
   cd projeto_clima-df
   python -m venv .venv
   source .venv/bin/activate  # Windows: .venv\Scripts\activate
   pip install -r requirements.txt
   ```

2. Baixe os dados históricos do [INMET](https://portal.inmet.gov.br/dadoshistoricos) e coloque os arquivos `.CSV` em `data/raw/` (no repositório você irá notar que a pasta `raw/` já contém os arquivos de 2025).

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

---

## 📊 Exemplo de análise: Amplitude Térmica

O pipeline calcula a **amplitude térmica mensal** (diferença entre a maior temperatura máxima e a menor temperatura mínima registradas no mês), uma métrica clássica de climatologia usada para entender a variação de temperatura ao longo do ano.

| Mês | Temp. Mín (°C) | Temp. Máx (°C) | Amplitude (°C) |
|-----|-----------------|-----------------|-----------------|
| Jan | 16.7            | 30.3            | 13.6            |
| Jul | 12.5            | 28.6            | 16.1            |
| Out | 13.4            | 33.2            | 19.8            |

---

## 🚧 Próximos passos
- [ ] Escrever testes unitários (pytest) para as funções de transformação
- [ ] Adicionar checagens de qualidade de dados (ex: Great Expectations)
- [ ] Orquestrar o pipeline com Airflow ou Dagster
- [ ] Containerizar a aplicação com Docker
- [ ] Publicar a camada Gold em um data warehouse (BigQuery/DuckDB/Postgres) para consumo em dashboards

---

## 👤 Autor

**[Bruno Matsuda]**

[LinkedIn](https://www.linkedin.com/in/bruno-matsuda-904747262/) • [GitHub](https://github.com/brunomatsuda)
