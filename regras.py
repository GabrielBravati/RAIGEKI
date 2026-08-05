import re
from datetime import datetime


class MotorRegras:
    # Regex compiladas uma única vez (evita recompilar a cada HAWB processada)
    CNPJ_REGEX = re.compile(r'\d{2}\.\d{3}\.\d{3}/\d{4}-\d{2}')
    PESO_REGEX = re.compile(r'(\d{1,3}(?:\.\d{3})*,\d+|\d+,\d+)')

    def __init__(self):
        # Lista de CNPJs sob controle (set -> checagem "in" em O(1))
        self.cnpjs_alvo = frozenset([
            "48.122.295/0025-72", "48.122.295/0027-34",
            "48.122.295/0024-91", "48.122.295/0026-53"
        ])

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
        total_linhas = len(linhas)
        temp_concluidos = []

        for i in range(total_linhas):
            if linhas[i].upper() != "HAWB":
                continue

            hawb = linhas[i + 1] if i + 1 < total_linhas else "N/A"
            linha_cnpj = linhas[i + 4] if i + 4 < total_linhas else ""
            status = linhas[i + 5] if i + 5 < total_linhas else "N/A"  # Situação Atual

            # Extração robusta do CNPJ ignorando sujeiras no texto
            match_cnpj = self.CNPJ_REGEX.search(linha_cnpj)
            cnpj_limpo = match_cnpj.group() if match_cnpj else "S/CNPJ"

            filial = cnpj_limpo.split("/")[1] if "/" in cnpj_limpo else "S/CNPJ"
            texto_formatado = f"{hawb} ({filial})"

            # REGRA DE CNPJ: Se não for um dos 4, vai para Fora de Controle
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
                bloco_linhas = []

                # Isola as linhas pertencentes apenas a esta HAWB para buscar o peso
                for j in range(i + 1, total_linhas):
                    if linhas[j].upper() == "HAWB":
                        break
                    bloco_linhas.append(linhas[j])

                bloco_texto = " ".join(bloco_linhas)

                # Extrai todos os valores numéricos no formato brasileiro
                pesos = self.PESO_REGEX.findall(bloco_texto)

                # O padrão da tela colada exibe primeiro o peso Manifestado e depois o Declarado
                if len(pesos) >= 2:
                    peso_conhecimento = self.converter_valor_br(pesos[0])  # Manifestado (Aparece 1º)
                    peso_estoque = self.converter_valor_br(pesos[1])       # Declarado / Estoque (Aparece 2º)

                    if peso_estoque > 0:
                        # Cálculo de divergência mantendo o estoque (Declarado) como base divisora
                        divergencia = ((peso_conhecimento - peso_estoque) / peso_estoque) * 100

                        # Classificação baseada no valor absoluto, acionando limite de 10%
                        if abs(divergencia) > 10.0:
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

        # Ordenação cronológica inteligente
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