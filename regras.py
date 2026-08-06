import re
from datetime import datetime


class MotorRegras:
    # Regex compiladas uma única vez (evita recompilar a cada HAWB processada)
    CNPJ_REGEX = re.compile(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}')
    PESO_REGEX = re.compile(r'(\d{1,3}(?:\.\d{3})*,\d+|\d+,\d+)')

    def __init__(self, configuracoes):
        # Recebe a lista do JSON e converte para frozenset (mantém a performance O(1))
        lista_cnpjs = configuracoes.get("cnpjs_alvo", [])
        self.cnpjs_alvo = frozenset(lista_cnpjs)
        
        # Puxa o limite de divergência dinamicamente (10.0 é o fallback)
        self.limite_divergencia = configuracoes.get("limite_divergencia_peso", 10.0)
        
    def converter_valor_br(self, valor_str):
        # Limpa e converte o formato de peso brasileiro (ex: 1.500,45) para float (1500.45)
        val = valor_str.strip()
        if not val:
            return 0.0

        # Lida com pontos de milhar e vírgula decimal
        if "," in val and "." in val:
            val = val.replace(".", "").replace(",", ".")
        elif "," in val:
            val = val.replace(",", ".")

        try:
            return float(val)
        except ValueError:
            return 0.0

    def triar_dados(self, dados_brutos, hawbs_finalizados):
        resultado = {
            "valido": True, "erro": "",
            "acao": [], "pendentes": [], "concluidos": [], "fora": [],
            "lista_recepcionados": [], "lista_pendentes": [], "lista_fora_controle": [],
            "lista_concluidos": [],
            "mapa_status": {}
        }

        if not dados_brutos:
            return resultado

        if "HAWB" not in dados_brutos.upper():
            resultado["valido"] = False
            resultado["erro"] = "A palavra-chave 'HAWB' não foi encontrada."
            return resultado

        linhas = [linha.strip() for linha in dados_brutos.split("\n") if linha.strip() != ""]
        
        # 1. Agrupar as linhas em "blocos", onde cada bloco representa uma única HAWB
        blocos = []
        bloco_atual = []
        for linha in linhas:
            if linha.upper() == "HAWB":
                if bloco_atual:
                    blocos.append(bloco_atual)
                bloco_atual = [linha]
            elif bloco_atual:
                bloco_atual.append(linha)
                
        # Adiciona o último bloco que ficou na memória
        if bloco_atual:
            blocos.append(bloco_atual)

        temp_concluidos = []

        # 2. Processar cada bloco de forma independente
        for bloco in blocos:
            if len(bloco) < 2:
                continue

            # A HAWB costuma ser sempre a linha imediatamente após o cabeçalho "HAWB"
            hawb = bloco[1]
            
            cnpj_limpo = "S/CNPJ"
            status = "N/A"

            # 3. Varrer o bloco para achar o CNPJ dinamicamente
            for idx_linha, linha_texto in enumerate(bloco):
                match_cnpj = self.CNPJ_REGEX.search(linha_texto)
                if match_cnpj:
                    cnpj_limpo = match_cnpj.group()
                    
                    # No Siscomex, o Status fica sempre posicionado logo após o CNPJ.
                    # Como ancoramos no CNPJ, não importa quantas linhas "lixo" vieram antes!
                    if idx_linha + 1 < len(bloco):
                        status = bloco[idx_linha + 1]
                    break  # Achou o CNPJ e o Status, pode parar de procurar neste bloco

            filial = cnpj_limpo.split("/")[1] if "/" in cnpj_limpo else "S/CNPJ"
            texto_formatado = f"{hawb} ({filial})"

            # REGRA DE CNPJ: Se não for um dos alvos, vai para Fora de Controle
            if cnpj_limpo not in self.cnpjs_alvo:
                status_final = f"FORA DE CONTROLE ({status})"
                resultado["fora"].append(f"{texto_formatado} - {status_final}")
                if hawb != "N/A":
                    resultado["lista_fora_controle"].append(hawb)
                    resultado["mapa_status"][hawb] = status_final
                continue

            if hawb in hawbs_finalizados:
                hora_conclusao = hawbs_finalizados[hawb]
                status_final = f"CONCLUÍDO ({hora_conclusao})"

                temp_concluidos.append({
                    "hawb": hawb,
                    "texto": f"{texto_formatado} - {status_final}",
                    "hora": hora_conclusao,
                    "status_final": status_final
                })

            elif status.upper() == "RECEPCIONADA":
                identificacao_peso = ""
                
                # Como já temos o bloco inteiro isolado, basta juntar o texto para achar os pesos
                bloco_texto = " ".join(bloco)
                pesos = self.PESO_REGEX.findall(bloco_texto)

                if len(pesos) >= 2:
                    peso_conhecimento = self.converter_valor_br(pesos[0])  # Manifestado
                    peso_estoque = self.converter_valor_br(pesos[1])       # Declarado / Estoque

                    if peso_estoque > 0:
                        divergencia = ((peso_conhecimento - peso_estoque) / peso_estoque) * 100
                        
                        # Usando a variável configurável que criamos no passo anterior
                        if abs(divergencia) > self.limite_divergencia:
                            identificacao_peso = f" [⚠️ DIVERGÊNCIA: {divergencia:.2f}%]"
                        else:
                            identificacao_peso = f" [✅ PESO OK: {divergencia:.2f}%]"

                status_final = f"RECEPCIONADA{identificacao_peso}"
                resultado["acao"].append(f"{texto_formatado} - {status_final}")
                
                if hawb != "N/A":
                    resultado["lista_recepcionados"].append(hawb)
                    resultado["mapa_status"][hawb] = status_final
                    
            else:
                status_final = "AGUARDANDO"
                resultado["pendentes"].append(f"{texto_formatado} - {status_final}")
                if hawb != "N/A":
                    resultado["lista_pendentes"].append(hawb)
                    resultado["mapa_status"][hawb] = status_final

        # Ordenação cronológica inteligente dos concluídos
        def extrair_data(item):
            try:
                return datetime.strptime(item["hora"], "%d/%m/%Y %H:%M:%S")
            except ValueError:
                try:
                    return datetime.strptime(item["hora"], "%H:%M:%S")
                except ValueError:
                    return datetime.min

        temp_concluidos.sort(key=extrair_data)

        for item in temp_concluidos:
            resultado["concluidos"].append(item["texto"])
            if item["hawb"] != "N/A":
                resultado["lista_concluidos"].append(item["hawb"])
                resultado["mapa_status"][item["hawb"]] = item["status_final"]

        return resultado