from src.config.catalogo_uf import create_base
from src.config.transform_data import processar_uf
import argparse


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--uf", required=True)

    args = parser.parse_args()

    create_base(args.uf)
    processar_uf(args.uf)





if __name__ == "__main__":
    main() #Passar a UF desejada ou "_*_" para passar todas as uf`s