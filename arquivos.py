import json
import os
import sys

class GerenciadorArquivos:
    def __init__(self):
        # Garante que salva na pasta certa, mesmo depois de virar .exe
        if getattr(sys, "frozen", False):
            self.pasta_base = os.path.dirname(sys.executable)
        else:
            self.pasta_base = os.path.dirname(os.path.abspath(__file__))
            
        # Cria a subpasta "dados" se ela não existir
        self.pasta_dados = os.path.join(self.pasta_base, "dados")
        os.makedirs(self.pasta_dados, exist_ok=True)

    def salvar(self, caminho, dados):
        try:
            with open(caminho, "w", encoding="utf-8") as arquivo:
                json.dump(dados, arquivo)
            return True, f"Análise salva em:\n{os.path.basename(caminho)}"
        except Exception as e:
            return False, str(e)

    def carregar(self, caminho):
        try:
            with open(caminho, "r", encoding="utf-8") as arquivo:
                return True, json.load(arquivo)
        except Exception as e:
            return False, str(e)