import customtkinter as ctk
import tkinter as tk
from tkinter import filedialog, messagebox
import os
import re
from datetime import datetime
from arquivos import GerenciadorArquivos
from regras import MotorRegras

# ESTILO GLOBAL
FONTE = "Segoe UI"

CORES = {
    "bg_light": "#F4F5F7",
    "text_dark": "#111827",
    "text_muted": "#6B7280",
    "text_soft": "#9CA3AF",
    "border": "#E5E7EB",

    "success": "#16A34A",
    "success_soft": "#DCFCE7",
    "success_hover": "#15803D",

    "primary": "#2563EB",
    "primary_soft": "#DBEAFE",
    "primary_hover": "#1D4ED8",

    "warning": "#D97706",
    "warning_soft": "#FEF3C7",
    "warning_hover": "#B45309",

    "danger": "#DC2626",
    "danger_soft": "#FEE2E2",
    "danger_hover": "#B91C1C",

    "purple": "#7C3AED",
    "purple_soft": "#EDE9FE",

    "white": "#FFFFFF",
}

ESTILO_INPUT = {"font": (FONTE, 14), "justify": "center", "fg_color": CORES["white"], "border_color": CORES["border"], "corner_radius": 8}
ESTILO_TXTBOX = {"font": ("Consolas", 12), "fg_color": CORES["white"], "border_width": 1, "border_color": CORES["border"], "corner_radius": 10}
ESTILO_INPUT_CALC = {"font": (FONTE, 13), "fg_color": "#F9FAFB", "border_color": CORES["border"], "corner_radius": 8}

ESTILO_BTN_SUCESSO = {"fg_color": CORES["success"], "hover_color": CORES["success_hover"], "text_color": "white", "font": (FONTE, 11, "bold"), "height": 34, "corner_radius": 10}
ESTILO_BTN_PRIMARIO = {"fg_color": CORES["primary"], "hover_color": CORES["primary_hover"], "text_color": "white", "font": (FONTE, 11, "bold"), "height": 34, "corner_radius": 10}
ESTILO_BTN_NEUTRO = {"fg_color": "#475569", "hover_color": "#334155", "text_color": "white", "font": (FONTE, 11, "bold"), "height": 34, "corner_radius": 10}

CATEGORIAS_ESTILO = {
    "MUDANÇAS RECENTES": {"icone": "🔄", "cor": CORES["purple"], "fundo": CORES["purple_soft"]},
    "RECEPCIONADOS": {"icone": "📥", "cor": CORES["success"], "fundo": CORES["success_soft"]},
    "AGUARDANDO SISCOMEX": {"icone": "⏳", "cor": CORES["warning"], "fundo": CORES["warning_soft"]},
    "CONCLUÍDOS": {"icone": "✅", "cor": CORES["primary"], "fundo": CORES["primary_soft"]},
    "FORA DE CONTROLE": {"icone": "🚫", "cor": CORES["danger"], "fundo": CORES["danger_soft"]},
}
# JANELA PERSONALIZADA PARA INSERIR A DATA
class DialogoData(ctk.CTkToplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.title("Nova Análise")
        self.geometry("320x230")
        self.resizable(False, False)
        self.data_escolhida = None

        self.transient(parent)
        self.grab_set()

        ctk.set_appearance_mode("Light")
        self.configure(fg_color=CORES["bg_light"])
        ctk.CTkLabel(self, text="🗓️  Data da Análise", font=(FONTE, 16, "bold"), text_color=CORES["text_dark"]).pack(pady=(22, 5))
        ctk.CTkLabel(self, text="Insira dia, mês e ano:", font=(FONTE, 12), text_color=CORES["text_muted"]).pack(pady=(0, 15))
        frame_data = ctk.CTkFrame(self, fg_color="transparent")
        frame_data.pack()
        vcmd_dia_mes = (self.register(self.validar_tamanho), '%P', 2)
        vcmd_ano = (self.register(self.validar_tamanho), '%P', 4)
        hoje = datetime.now()

        self.dia = ctk.CTkEntry(frame_data, width=45, validate="key", validatecommand=vcmd_dia_mes, **ESTILO_INPUT)
        self.dia.insert(0, hoje.strftime("%d"))
        self.dia.pack(side=tk.LEFT, padx=3)

        ctk.CTkLabel(frame_data, text="/", font=(FONTE, 16, "bold"), text_color=CORES["text_soft"]).pack(side=tk.LEFT)

        self.mes = ctk.CTkEntry(frame_data, width=45, validate="key", validatecommand=vcmd_dia_mes, **ESTILO_INPUT)
        self.mes.insert(0, hoje.strftime("%m"))
        self.mes.pack(side=tk.LEFT, padx=3)

        ctk.CTkLabel(frame_data, text="/", font=(FONTE, 16, "bold"), text_color=CORES["text_soft"]).pack(side=tk.LEFT)

        self.ano = ctk.CTkEntry(frame_data, width=65, validate="key", validatecommand=vcmd_ano, **ESTILO_INPUT)
        self.ano.insert(0, hoje.strftime("%Y"))
        self.ano.pack(side=tk.LEFT, padx=3)
        self.btn_confirmar = ctk.CTkButton(self, text="Confirmar (Enter)", command=self.confirmar,
                                            fg_color=CORES["success"], hover_color=CORES["success_hover"],
                                            font=(FONTE, 12, "bold"), height=36, corner_radius=10)
        self.btn_confirmar.pack(pady=22)

        for widget in (self.dia, self.mes, self.ano):
            widget.bind("<FocusIn>", lambda e, w=widget: self.selecionar_tudo(w))
        self.dia.bind("<KeyRelease>", lambda e: self.auto_avancar(e, self.dia, self.mes, 2))
        self.mes.bind("<KeyRelease>", lambda e: self.auto_avancar(e, self.mes, self.ano, 2))
        self.ano.bind("<KeyRelease>", lambda e: self.auto_avancar(e, self.ano, self.btn_confirmar, 4))
        self.dia.focus()
        self.bind("<Return>", lambda e: self.confirmar())
        self.wait_window()

    def validar_tamanho(self, novo_texto, max_len):
        if not novo_texto:
            return True
        return novo_texto.isdigit() and len(novo_texto) <= int(max_len)

    def auto_avancar(self, event, widget_atual, proximo_widget, max_len):
        if event.keysym in ('BackSpace', 'Tab', 'Left', 'Right', 'Shift_L', 'Shift_R'):
            return
        if len(widget_atual.get()) == max_len:
            proximo_widget.focus()

    def selecionar_tudo(self, widget):
        self.after(1, lambda: widget.select_range(0, tk.END))

    def confirmar(self):
        d, m, a = self.dia.get().zfill(2), self.mes.get().zfill(2), self.ano.get()
        try:
            data_obj = datetime.strptime(f"{d}/{m}/{a}", "%d/%m/%Y")
            self.data_escolhida = data_obj.strftime("%d-%m-%Y")
            self.destroy()
        except ValueError:
            messagebox.showerror("Data Inválida", "A data informada não existe.", parent=self)
# INTERFACE PRINCIPAL
class InterfaceGrafica:
    def __init__(self, root):
        self.root = root
        ctk.set_appearance_mode("Light")

        self.arquivos = GerenciadorArquivos()
        self.motor = MotorRegras()
        self.arquivo_atual = ""
        self.hawbs_finalizados = {}
        self.listas_copia = {"recepcionados": [], "pendentes": [], "concluidos": [], "fora": []}
        self.ultimo_texto_processado = ""
        self._ultimo_resultado = None
        self.mudancas_recentes = []
        self.texto_exportacao = ""
        self.root.protocol("WM_DELETE_WINDOW", self.fechar_programa)
        self.abrir_tela_boas_vindas()

    def voltar_inicio(self):
        if self.arquivo_atual:
            resposta = messagebox.askyesnocancel("Sair do Arquivo", "Deseja salvar as alterações antes de voltar ao início?")
            if resposta is None:
                return
            if resposta is True:
                self.salvar_dados(mostrar_aviso=False)
        self.root.config(menu="")
        self.abrir_tela_boas_vindas()

    def fechar_programa(self):
        if self.arquivo_atual:
            resposta = messagebox.askyesnocancel("Sair", "Deseja salvar as alterações antes de sair do sistema?")
            if resposta is None:
                return
            if resposta is True:
                self.salvar_dados(mostrar_aviso=False)
        self.root.destroy()

    def salvar_dados(self, mostrar_aviso=True):
        if not self.arquivo_atual:
            return

        if mostrar_aviso and os.path.exists(self.arquivo_atual):
            resposta = messagebox.askyesnocancel("Salvar Dados", "Este arquivo já existe. O que deseja fazer?\n\n[SIM] Reescrever\n[NÃO] Criar um Novo")
            if resposta is None:
                return
            if resposta is False:
                base, ext = os.path.splitext(self.arquivo_atual)
                self.arquivo_atual = f"{base}_v_{datetime.now().strftime('%H%M%S')}{ext}"

        dados = {"finalizados": self.hawbs_finalizados, "texto_colado": self.caixa_entrada.get("1.0", tk.END).strip()}
        sucesso, msg = self.arquivos.salvar(self.arquivo_atual, dados)

        if mostrar_aviso:
            if sucesso:
                messagebox.showinfo("Sucesso", msg)
                self.root.title(f"Guardião - {os.path.basename(self.arquivo_atual)}")
                if hasattr(self, 'lbl_arquivo_nome'):
                    self.lbl_arquivo_nome.configure(text=f"📂  {os.path.basename(self.arquivo_atual)}")
            else:
                messagebox.showerror("Erro", f"Erro ao salvar: {msg}")

    def exportar_txt(self):
        if not self.arquivo_atual or not self.texto_exportacao.strip():
            messagebox.showwarning("Aviso", "Não há dados no painel para exportar.")
            return

        nome_sugerido = os.path.basename(self.arquivo_atual).replace(".json", ".txt")
        caminho_txt = filedialog.asksaveasfilename(defaultextension=".txt", initialfile=nome_sugerido,
                                                   title="Exportar Relatório",
                                                   filetypes=(("Arquivo de Texto", "*.txt"), ("Todos", "*.*")))
        if caminho_txt:
            try:
                with open(caminho_txt, "w", encoding="utf-8") as f:
                    f.write(self.texto_exportacao)
                messagebox.showinfo("Sucesso", "Relatório exportado com sucesso!")
            except Exception as e:
                messagebox.showerror("Erro", f"Falha ao exportar TXT:\n{e}")

    def _on_scroll_painel(self, event):
        self.painel_scroll._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def _on_scroll_sidebar(self, event):
        self.sidebar._parent_canvas.yview_scroll(int(-1 * (event.delta / 120)), "units")

    def bind_to_scroll(self, widget, handler=None):
        handler = handler or self._on_scroll_painel
        if not getattr(widget, "_scroll_bound", False):
            if isinstance(widget, ctk.CTkTextbox):
                widget._textbox.bind("<MouseWheel>", handler)
            widget.bind("<MouseWheel>", handler)
            widget._scroll_bound = True

        for child in widget.winfo_children():
            self.bind_to_scroll(child, handler)

    def _criar_frames_sombra(self, parent):
        sombra = ctk.CTkFrame(parent, fg_color=CORES["border"], corner_radius=15)
        card = ctk.CTkFrame(sombra, fg_color=CORES["white"], corner_radius=15, border_width=1, border_color="#E5E7EB")
        card.pack(fill=tk.BOTH, expand=True, padx=(0, 3), pady=(0, 3))
        return sombra, card

    def _criar_stat_card(self, parent, icone, label_texto, cor, cor_fundo):
        card = ctk.CTkFrame(parent, fg_color=cor_fundo, corner_radius=12)
        ctk.CTkLabel(card, text=icone, font=(FONTE, 16)).pack(pady=(10, 0))
        lbl_valor = ctk.CTkLabel(card, text="0", font=(FONTE, 20, "bold"), text_color=cor)
        lbl_valor.pack()
        ctk.CTkLabel(card, text=label_texto, font=(FONTE, 10, "bold"), text_color=cor).pack(pady=(0, 10))
        return card, lbl_valor

    def _criar_secao_sidebar(self, parent, numero, titulo, cor):
        bloco = ctk.CTkFrame(parent, fg_color=CORES["bg_light"], corner_radius=12)
        bloco.pack(fill=tk.X, padx=15, pady=(0, 12))
        header = ctk.CTkFrame(bloco, fg_color="transparent")
        header.pack(fill=tk.X, padx=12, pady=(10, 6))
        ctk.CTkLabel(header, text=str(numero), font=(FONTE, 10, "bold"), text_color="white",
                     fg_color=cor, corner_radius=9, width=18, height=18).pack(side=tk.LEFT, padx=(0, 8))
        ctk.CTkLabel(header, text=titulo, font=(FONTE, 11, "bold"), text_color=CORES["text_dark"]).pack(side=tk.LEFT)
        return bloco

    def processar_interface(self):
        dados_brutos = self.caixa_entrada.get("1.0", tk.END).strip()
        resultado = self.motor.triar_dados(dados_brutos, self.hawbs_finalizados)
        if not resultado["valido"]:
            messagebox.showwarning("Formato Inválido", resultado["erro"])
            self.mostrar_erro_painel("Aguardando dados válidos do SISCOMEX...")
            return

        self.listas_copia.update({
            "recepcionados": resultado["lista_recepcionados"],
            "pendentes": resultado["lista_pendentes"],
            "concluidos": resultado["lista_concluidos"],
            "fora": resultado["lista_fora_controle"]
        })

        if not self.ultimo_texto_processado:
            self.mudancas_recentes = []
        elif dados_brutos != self.ultimo_texto_processado:
            mapa_antigo = (self._ultimo_resultado or {}).get("mapa_status", {})
            novo_mapa = resultado.get("mapa_status", {})
            self.mudancas_recentes = [
                f"{hawb} : de {mapa_antigo[hawb]} -> {status_atual}"
                for hawb, status_atual in novo_mapa.items()
                if hawb in mapa_antigo and mapa_antigo[hawb] != status_atual
            ]

        self.ultimo_texto_processado = dados_brutos
        self._ultimo_resultado = resultado

        self.atualizar_metricas(len(resultado["acao"]), len(resultado["pendentes"]), len(resultado["concluidos"]), len(resultado["fora"]))
        self.escrever_painel(resultado["acao"], resultado["pendentes"], resultado["concluidos"], resultado["fora"], self.mudancas_recentes)

    def concluir_hawb(self):
        texto = self.caixa_concluir.get("1.0", tk.END).strip()
        if not texto:
            return

        dados_brutos = self.caixa_entrada.get("1.0", tk.END).strip()
        if self._ultimo_resultado is not None and dados_brutos == self.ultimo_texto_processado:
            mapa_status = self._ultimo_resultado.get("mapa_status", {})
        else:
            mapa_status = self.motor.triar_dados(dados_brutos, self.hawbs_finalizados).get("mapa_status", {})

        hawbs = [h.strip() for h in re.split(r'[,\s\n]+', texto) if h.strip()]
        hora_atual = datetime.now().strftime("%d/%m/%Y %H:%M:%S")

        hawbs_nao_encontrados, hawbs_ja_concluidos = [], []

        for h in hawbs:
            if h in self.hawbs_finalizados:
                hawbs_ja_concluidos.append(h)
            elif h in mapa_status:
                self.hawbs_finalizados[h] = hora_atual
            else:
                hawbs_nao_encontrados.append(h)

        self.caixa_concluir.delete("1.0", tk.END)

        msg_alerta = ""
        if hawbs_ja_concluidos:
            msg_alerta += "⚠️ JÁ ESTAVAM CONCLUÍDOS (Ignorados):\n" + "\n".join(hawbs_ja_concluidos) + "\n\n"
        if hawbs_nao_encontrados:
            msg_alerta += "❌ NÃO ENCONTRADOS (Verifique):\n" + "\n".join(hawbs_nao_encontrados)

        if msg_alerta:
            messagebox.showwarning("Atenção aos Status", msg_alerta.strip())

        if self.caixa_entrada.get("1.0", tk.END).strip():
            self.processar_interface()

    def buscar_hawb(self):
        texto_busca = self.caixa_busca.get("1.0", tk.END).strip()
        if not texto_busca:
            return

        dados_brutos = self.caixa_entrada.get("1.0", tk.END).strip()
        if self._ultimo_resultado is not None and dados_brutos == self.ultimo_texto_processado:
            mapa_status = self._ultimo_resultado.get("mapa_status", {})
        else:
            mapa_status = self.motor.triar_dados(dados_brutos, self.hawbs_finalizados).get("mapa_status", {})

        hawbs_buscados = [h.strip() for h in re.split(r'[,\s\n]+', texto_busca) if h.strip()]

        janela_busca = ctk.CTkToplevel(self.root)
        janela_busca.title("Busca")
        janela_busca.geometry("400x300")
        janela_busca.configure(fg_color=CORES["bg_light"])

        ctk.CTkLabel(janela_busca, text="🔎  RESULTADO DA BUSCA", font=(FONTE, 14, "bold"), text_color=CORES["text_dark"]).pack(pady=15)

        texto_res = ctk.CTkTextbox(janela_busca, font=("Consolas", 12), fg_color=CORES["white"], corner_radius=10, border_width=1, border_color=CORES["border"])
        texto_res.pack(fill=tk.BOTH, expand=True, padx=15, pady=(0, 15))

        linhas = [f"{h}\n -> {mapa_status.get(h, 'NÃO ENCONTRADO')}\n\n" for h in hawbs_buscados]
        texto_res.insert(tk.END, "".join(linhas))

        texto_res._textbox.configure(state="disabled")
        self.caixa_busca.delete("1.0", tk.END)

    def copiar_lista(self, categoria):
        lista = self.listas_copia.get(categoria, [])
        if not lista:
            messagebox.showwarning("Aviso", "Lista vazia!")
            return

        self.root.clipboard_clear()
        self.root.clipboard_append("\n".join(lista))
        self.root.update()
        messagebox.showinfo("Copiado!", f"{len(lista)} HAWB(s) copiados!")

    def abrir_tela_boas_vindas(self):
        self.arquivo_atual = ""
        self.hawbs_finalizados.clear()

        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.geometry("400x260")
        self.root.resizable(False, False)
        self.root.configure(fg_color=CORES["bg_light"])

        frame_menu = ctk.CTkFrame(self.root, fg_color="transparent")
        frame_menu.place(relx=0.5, rely=0.5, anchor="center")

        ctk.CTkLabel(frame_menu, text="🛡️  GUARDIÃO DA PLANILHA", font=(FONTE, 18, "bold"), text_color=CORES["text_dark"]).pack(pady=(0, 25))
        ctk.CTkButton(frame_menu, text="NOVA ANÁLISE", command=self.opcao_1_novo, width=220, **ESTILO_BTN_SUCESSO).pack(pady=8)
        ctk.CTkButton(frame_menu, text="CARREGAR ARQUIVO", command=self.opcao_2_carregar, width=220, **ESTILO_BTN_PRIMARIO).pack(pady=8)

    def converter_valor_br(self, valor_str):
        val = valor_str.strip()
        if not val:
            return 0.0
        if "," in val and "." in val:
            val = val.replace(".", "").replace(",", ".")
        elif "," in val:
            val = val.replace(",", ".")
        return float(val)

    def formatar_valor_br(self, valor):
        return f"{valor:,.2f}".replace(",", "X").replace(".", ",").replace("X", ".")

    def criar_bloco_calculadora(self, parent, titulo, tipo_calculo):
        sombra, card = self._criar_frames_sombra(parent)

        cor_titulo = CORES["primary"] if tipo_calculo == "maior" else CORES["warning"]
        ctk.CTkLabel(card, text=titulo, font=(FONTE, 18, "bold"), text_color=cor_titulo).pack(pady=(20, 10))

        f_entradas = ctk.CTkFrame(card, fg_color="transparent")
        f_entradas.pack(pady=10, padx=20, fill=tk.X)

        ctk.CTkLabel(f_entradas, text="Peso Declarado:", font=(FONTE, 12, "bold"), text_color="#4B5563").grid(row=0, column=0, padx=(0, 10), pady=10, sticky="e")
        ent_declarado = ctk.CTkEntry(f_entradas, width=130, **ESTILO_INPUT_CALC)
        ent_declarado.grid(row=0, column=1, pady=10)

        ctk.CTkLabel(f_entradas, text="Peso Manifestado:", font=(FONTE, 12, "bold"), text_color="#4B5563").grid(row=1, column=0, padx=(0, 10), pady=10, sticky="e")
        ent_manifestado = ctk.CTkEntry(f_entradas, width=130, **ESTILO_INPUT_CALC)
        ent_manifestado.grid(row=1, column=1, pady=10)

        btn_calc = ctk.CTkButton(card, text="CALCULAR", **ESTILO_BTN_SUCESSO)
        btn_calc.pack(pady=(5, 15), padx=20, fill=tk.X)

        f_resultados = ctk.CTkFrame(card, fg_color="#F3F4F6", corner_radius=10)
        f_resultados.pack(pady=(0, 20), padx=20, fill=tk.BOTH, expand=True)
        lbl_dif = ctk.CTkLabel(f_resultados, text="Diferença:\n--", font=(FONTE, 13, "bold"), text_color=CORES["text_muted"])
        lbl_dif.pack(pady=(15, 5))
        lbl_perc = ctk.CTkLabel(f_resultados, text="Percentual:\n--", font=(FONTE, 16, "bold"), text_color=CORES["text_muted"])
        lbl_perc.pack(pady=(5, 15))

        def realizar_calculo(event=None):
            try:
                decl = self.converter_valor_br(ent_declarado.get())
                manif = self.converter_valor_br(ent_manifestado.get())
                dif = (manif - decl) if tipo_calculo == "maior" else (decl - manif)
                perc = (dif / decl) * 100 if decl != 0 else 0
                alta_divergencia = abs(perc) > 10.1
                cor = CORES["danger"] if alta_divergencia else CORES["success_hover"]
                fundo = CORES["danger_soft"] if alta_divergencia else CORES["success_soft"]
                texto_alerta = "⚠️ ALTA DIVERGÊNCIA" if alta_divergencia else "✅ DENTRO DO LIMITE"
                f_resultados.configure(fg_color=fundo)
                lbl_dif.configure(text=f"Diferença:\n{self.formatar_valor_br(dif)} kg", text_color=CORES["text_dark"])
                lbl_perc.configure(text=f"Percentual: {perc:.2f}%\n{texto_alerta}", text_color=cor)
            except ValueError:
                f_resultados.configure(fg_color="#F3F4F6")
                lbl_dif.configure(text="Diferença:\nERRO", text_color=CORES["danger"])
                lbl_perc.configure(text="Verifique\nos números!", text_color=CORES["danger"])

        btn_calc.configure(command=realizar_calculo)
        ent_declarado.bind("<Return>", realizar_calculo)
        ent_manifestado.bind("<Return>", realizar_calculo)
        return sombra

    def abrir_calculadora(self):
        janela_calc = ctk.CTkToplevel(self.root)
        janela_calc.title("Calculadora de Divergência de Peso")
        janela_calc.geometry("740x460")
        janela_calc.resizable(False, False)
        janela_calc.configure(fg_color=CORES["bg_light"])
        janela_calc.transient(self.root)

        ctk.CTkLabel(janela_calc, text="⚖️  Análise de Peso", font=(FONTE, 22, "bold"), text_color=CORES["text_dark"]).pack(pady=(20, 0))
        container_calc = ctk.CTkFrame(janela_calc, fg_color="transparent")
        container_calc.pack(fill=tk.BOTH, expand=True, padx=25, pady=20)

        configs = (("Peso Maior (+)", "maior", (0, 10)), ("Peso Menor (-)", "menor", (10, 0)))
        for titulo, tipo, padx in configs:
            self.criar_bloco_calculadora(container_calc, titulo, tipo).pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=padx)
            

    def mostrar_erro_painel(self, msg):
        for widget in self.painel_scroll.winfo_children():
            widget.destroy()
        self.texto_exportacao = ""
        sombra, card = self._criar_frames_sombra(self.painel_scroll)
        sombra.pack(fill=tk.X, padx=10, pady=8)
        ctk.CTkLabel(card, text=f"⚠️  {msg}", font=(FONTE, 12, "bold"), text_color=CORES["danger"]).pack(pady=20)

    def escrever_painel(self, acao, pendentes, concluidos, fora, mudancas=None):
        for widget in self.painel_scroll.winfo_children():
            widget.destroy()

        linhas_exportacao = []

        def criar_card_categoria(titulo, itens):
            if not itens and titulo in ["MUDANÇAS RECENTES", "FORA DE CONTROLE"]:
                return

            estilo = CATEGORIAS_ESTILO[titulo]

            linhas_exportacao.append(f"{titulo} ({len(itens)})\n━━━━━━━━━━━━━━")
            linhas_exportacao.extend([f"  » {i}" for i in itens])
            linhas_exportacao.append("")

            sombra, card = self._criar_frames_sombra(self.painel_scroll)
            sombra.pack(fill=tk.X, padx=10, pady=8)

            linha_topo = ctk.CTkFrame(card, fg_color="transparent")
            linha_topo.pack(fill=tk.BOTH, expand=True)

            ctk.CTkFrame(linha_topo, width=4, fg_color=estilo["cor"], corner_radius=0).pack(side=tk.LEFT, fill=tk.Y)

            corpo = ctk.CTkFrame(linha_topo, fg_color="transparent")
            corpo.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

            header = ctk.CTkFrame(corpo, fg_color="transparent")
            header.pack(fill=tk.X, padx=15, pady=(12, 8))
            ctk.CTkLabel(header, text=f"{estilo['icone']}  {titulo}", font=(FONTE, 14, "bold"), text_color=estilo["cor"]).pack(side=tk.LEFT)
            ctk.CTkLabel(header, text=str(len(itens)), font=(FONTE, 11, "bold"), text_color=estilo["cor"],
                         fg_color=estilo["fundo"], corner_radius=10, width=30, height=22).pack(side=tk.RIGHT)

            ctk.CTkFrame(corpo, height=1, fg_color="#F3F4F6").pack(fill=tk.X, padx=15)

            texto_itens = "\n".join([f"  » {i}" for i in itens]) if itens else "  Nenhum item nesta categoria."
            altura_base = (len(itens) * 24) + 25 if itens else 40

            txt_itens = ctk.CTkTextbox(corpo, font=("Consolas", 13), fg_color="transparent",
                                        text_color="#374151" if itens else CORES["text_soft"],
                                        height=altura_base, border_width=0)
            txt_itens.insert("1.0", texto_itens)

            for linha_idx, item in enumerate(itens, start=1):
                linha_completa = f"  » {item}"
                if "[⚠️ DIVERGÊNCIA" in linha_completa:
                    start_col = linha_completa.find("[⚠️")
                    txt_itens.tag_add("alerta_peso", f"{linha_idx}.{start_col}", f"{linha_idx}.end")
                elif "[✅ PESO OK" in linha_completa:
                    start_col = linha_completa.find("[✅")
                    txt_itens.tag_add("ok_peso", f"{linha_idx}.{start_col}", f"{linha_idx}.end")

            txt_itens.tag_config("alerta_peso", foreground=CORES["danger"])
            txt_itens.tag_config("ok_peso", foreground="#2E7D32")
            txt_itens.configure(state="disabled")
            txt_itens.pack(fill=tk.X, padx=10, pady=(10, 15))

            self.bind_to_scroll(card)

        criar_card_categoria("MUDANÇAS RECENTES", mudancas)
        criar_card_categoria("RECEPCIONADOS", acao)
        criar_card_categoria("AGUARDANDO SISCOMEX", pendentes)
        criar_card_categoria("CONCLUÍDOS", concluidos)
        criar_card_categoria("FORA DE CONTROLE", fora)
        self.texto_exportacao = "\n".join(linhas_exportacao)

    def iniciar_tela_principal(self, texto_recuperado=""):
        for widget in self.root.winfo_children():
            widget.destroy()

        self.root.geometry("820x620")
        self.root.minsize(760, 520)
        self.root.title("Guardião da Planilha")
        self.root.configure(fg_color=CORES["bg_light"])

        menu_bar = tk.Menu(self.root)

        menu_arquivo = tk.Menu(menu_bar, tearoff=0)
        menu_arquivo.add_command(label="Abrir / Carregar Novo...", command=self.opcao_2_carregar)
        menu_arquivo.add_command(label="Salvar Dados", command=self.salvar_dados)
        menu_bar.add_cascade(label="Arquivo", menu=menu_arquivo)

        menu_dados = tk.Menu(menu_bar, tearoff=0)
        menu_dados.add_command(label="Copiar Recepcionados", command=lambda: self.copiar_lista("recepcionados"))
        menu_dados.add_command(label="Copiar Aguardando", command=lambda: self.copiar_lista("pendentes"))
        menu_dados.add_command(label="Copiar Concluídos", command=lambda: self.copiar_lista("concluidos"))
        menu_dados.add_separator()
        menu_dados.add_command(label="Exportar para TXT...", command=self.exportar_txt)
        menu_bar.add_cascade(label="Dados", menu=menu_dados)
        menu_bar.add_command(label="Calculadora", command=self.abrir_calculadora)
        menu_opcoes = tk.Menu(menu_bar, tearoff=0)
        menu_opcoes.add_command(label="Voltar ao Início", command=self.voltar_inicio)
        menu_opcoes.add_separator()
        menu_opcoes.add_command(label="Sair do Programa", command=self.fechar_programa)
        menu_bar.add_cascade(label="Opções", menu=menu_opcoes)

        self.root.config(menu=menu_bar)

        container = ctk.CTkFrame(self.root, fg_color="transparent")
        container.pack(fill=tk.BOTH, expand=True)

        self.sidebar = ctk.CTkScrollableFrame(container, width=250, corner_radius=0, fg_color=CORES["white"],
                                               border_width=1, border_color="#E5E7EB", scrollbar_button_color=CORES["border"])
        self.sidebar.pack(side=tk.LEFT, fill=tk.Y)
        sidebar = self.sidebar

        self.lbl_arquivo_nome = ctk.CTkLabel(sidebar, text=f"📂  {os.path.basename(self.arquivo_atual)}",
                                              font=(FONTE, 11, "bold"), text_color=CORES["primary"],
                                              fg_color=CORES["primary_soft"], corner_radius=8, height=32)
        self.lbl_arquivo_nome.pack(fill=tk.X, padx=5, pady=(5, 14))

        bloco1 = self._criar_secao_sidebar(sidebar, 1, "DADOS SISCOMEX", CORES["success"])
        self.caixa_entrada = ctk.CTkTextbox(bloco1, height=90, **ESTILO_TXTBOX)
        self.caixa_entrada._textbox.configure(undo=True)
        self.caixa_entrada.bind("<Control-y>", lambda e: self.caixa_entrada._textbox.edit_redo())
        self.caixa_entrada.pack(fill=tk.X, padx=12, pady=(0, 8))
        if texto_recuperado:
            self.caixa_entrada.insert("1.0", texto_recuperado)
        ctk.CTkButton(bloco1, text="PROCESSAR", command=self.processar_interface, **ESTILO_BTN_SUCESSO).pack(fill=tk.X, padx=12, pady=(0, 12))

        bloco2 = self._criar_secao_sidebar(sidebar, 2, "CONCLUIR HAWBs", CORES["primary"])
        self.caixa_concluir = ctk.CTkTextbox(bloco2, height=70, **ESTILO_TXTBOX)
        self.caixa_concluir._textbox.configure(undo=True)
        self.caixa_concluir.bind("<Control-y>", lambda e: self.caixa_concluir._textbox.edit_redo())
        self.caixa_concluir.pack(fill=tk.X, padx=12, pady=(0, 8))
        ctk.CTkButton(bloco2, text="CONCLUIR", command=self.concluir_hawb, **ESTILO_BTN_PRIMARIO).pack(fill=tk.X, padx=12, pady=(0, 12))

        bloco3 = self._criar_secao_sidebar(sidebar, 3, "BUSCAR STATUS", CORES["text_muted"])
        self.caixa_busca = ctk.CTkTextbox(bloco3, height=70, **ESTILO_TXTBOX)
        self.caixa_busca._textbox.configure(undo=True)
        self.caixa_busca.bind("<Control-y>", lambda e: self.caixa_busca._textbox.edit_redo())
        self.caixa_busca.pack(fill=tk.X, padx=12, pady=(0, 8))
        ctk.CTkButton(bloco3, text="BUSCAR", command=self.buscar_hawb, **ESTILO_BTN_NEUTRO).pack(fill=tk.X, padx=12, pady=(0, 12))

        self.bind_to_scroll(sidebar, self._on_scroll_sidebar)

        main_area = ctk.CTkFrame(container, fg_color="transparent")
        main_area.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=12, pady=15)

        f_metricas = ctk.CTkFrame(main_area, fg_color="transparent")
        f_metricas.pack(fill=tk.X, pady=(0, 12))

        card, self.lbl_total = self._criar_stat_card(f_metricas, "📊", "TOTAL", CORES["text_dark"], "#F3F4F6")
        card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(0, 6))

        card, self.lbl_recepcionados = self._criar_stat_card(f_metricas, "📥", "RECEP.", CORES["success"], CORES["success_soft"])
        card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6)

        card, self.lbl_pendentes = self._criar_stat_card(f_metricas, "⏳", "AGUARD.", CORES["warning"], CORES["warning_soft"])
        card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6)

        card, self.lbl_concluidos = self._criar_stat_card(f_metricas, "✅", "CONCL.", CORES["primary"], CORES["primary_soft"])
        card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=6)

        card, self.lbl_fora = self._criar_stat_card(f_metricas, "🚫", "FORA", CORES["danger"], CORES["danger_soft"])
        card.pack(side=tk.LEFT, expand=True, fill=tk.BOTH, padx=(6, 0))

        self.painel_scroll = ctk.CTkScrollableFrame(main_area, fg_color="transparent")
        self.painel_scroll.pack(fill=tk.BOTH, expand=True, pady=(2, 0))

        if texto_recuperado:
            self.processar_interface()

    def atualizar_metricas(self, q_acao, q_pend, q_conc, q_fora):
        self.lbl_total.configure(text=str(q_acao + q_pend + q_conc + q_fora))
        self.lbl_recepcionados.configure(text=str(q_acao))
        self.lbl_pendentes.configure(text=str(q_pend))
        self.lbl_concluidos.configure(text=str(q_conc))
        self.lbl_fora.configure(text=str(q_fora))

    def opcao_1_novo(self):
        dialogo = DialogoData(self.root)
        if dialogo.data_escolhida:
            self.arquivo_atual = os.path.join(self.arquivos.pasta_dados, f"analise_{dialogo.data_escolhida}.json")
            self.hawbs_finalizados.clear()
            self.ultimo_texto_processado = ""
            self._ultimo_resultado = None
            self.mudancas_recentes.clear()
            self.iniciar_tela_principal()

    def opcao_2_carregar(self):
        arq = filedialog.askopenfilename(initialdir=self.arquivos.pasta_dados, title="Selecione", filetypes=(("JSON", "*.json"), ("Todos", "*.*")))
        if arq:
            self.arquivo_atual = arq
            sucesso, dados = self.arquivos.carregar(arq)
            if sucesso:
                fins = dados.get("finalizados", {})
                self.hawbs_finalizados = {h: "--:--" for h in fins} if isinstance(fins, list) else fins
                self.ultimo_texto_processado = ""
                self._ultimo_resultado = None
                self.mudancas_recentes.clear()
                self.iniciar_tela_principal(dados.get("texto_colado", ""))
            else:
                messagebox.showerror("Erro", f"Falha ao ler arquivo.\n{dados}")