import os
import argparse

IGNORADOS = ["build", "__pycache__", ".git", ".venv", "venv", ".vscode", ".idea"]  # Adicione outros conforme necessário
IGNORAR_EXTENSOES = [".pyc", ".log"]

def mapear_diretorio(diretorio, saida, prefixo=""):
    with open(saida, "w", encoding="utf-8") as f:
        for root, dirs, files in os.walk(diretorio):
            dirs[:] = [d for d in dirs if d not in IGNORADOS]
            nivel = root.replace(diretorio, "").count(os.sep)
            indentacao = '│   ' * nivel + '├── '
            subdiretorio = os.path.basename(root)
            f.write(f"{prefixo}{indentacao}{subdiretorio}/\n")
            sub_indentacao = '│   ' * (nivel + 1) + '└── '
            for file in files:
                if not any(file.endswith(ext) for ext in IGNORAR_EXTENSOES):
                    f.write(f"{prefixo}{sub_indentacao}{file}\n")

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("diretorio", help="Diretório a ser mapeado")
    parser.add_argument("saida", help="Arquivo de saída")
    args = parser.parse_args()
    mapear_diretorio(args.diretorio, args.saida)

if __name__ == "__main__":
    main()

#run python map_project_structure.py D:\projects\marco\sound-to-text estrutura_projeto.txt