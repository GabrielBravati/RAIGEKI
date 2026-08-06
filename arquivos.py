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
        
        # Define o caminho do arquivo de configuração (na pasta raiz do programa)
        self.arquivo_config = os.path.join(self.pasta_base, "config.json")
        self._garantir_config()

    def _garantir_config(self):
        """Cria o config.json com valores padrão caso ele não exista."""
        if not os.path.exists(self.arquivo_config):
            config_padrao = {
                "cnpjs_alvo": [
                    "48.122.295/0025-72", 
                    "48.122.295/0027-34",
                    "48.122.295/0024-91", 
                    "48.122.295/0026-53"
                ],
                "limite_divergencia_peso": 10.0
            }
            try:
                with open(self.arquivo_config, "w", encoding="utf-8") as arquivo:
                    # O indent=4 deixa o arquivo formatado e bonito para humanos lerem
                    json.dump(config_padrao, arquivo, indent=4)
            except Exception as e:
                print(f"Erro ao criar config.json: {e}")

    def carregar_config(self):
        """Lê as configurações. Se houver erro, retorna um padrão seguro."""
        try:
            with open(self.arquivo_config, "r", encoding="utf-8") as arquivo:
                return json.load(arquivo)
        except Exception:
            return {"cnpjs_alvo": [], "limite_divergencia_peso": 10.0}

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