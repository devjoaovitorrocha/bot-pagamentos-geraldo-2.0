import customtkinter as ctk
from core.app_controller import AppController
from utils.municipios import MUNICIPIOS
import threading


def run_app():
    app = App()
    app.mainloop()


class App(ctk.CTk):
    def __init__(self):
        super().__init__()
        self.title("Bot Pagamento de Resoluções")
        self.geometry("600x700")
        self.controller = AppController()

        ctk.CTkLabel(self, text="Ano de Pagamento").pack(pady=5)
        self.ano = ctk.CTkOptionMenu(self, values=[str(a) for a in range(2019, 2026)])
        self.ano.set("2025")
        self.ano.pack(pady=5)

        # Tipo de Consulta
        ctk.CTkLabel(self, text="Tipo de Consulta").pack(pady=(10, 2))
        self.tipo_var = ctk.StringVar(value="ambos")
        ctk.CTkRadioButton(self, text="Ambos", variable=self.tipo_var, value="ambos").pack()
        ctk.CTkRadioButton(self, text="Restos a Pagar", variable=self.tipo_var, value="restos").pack()
        ctk.CTkRadioButton(self, text="Orçamentários", variable=self.tipo_var, value="orcamentario").pack()

        # Campo de Busca
        ctk.CTkLabel(self, text="Buscar Município").pack(pady=(10, 2))
        self.search_var = ctk.StringVar()
        self.search_var.trace("w", self.atualizar_municipios)
        self.search_entry = ctk.CTkEntry(self, textvariable=self.search_var)
        self.search_entry.pack(pady=2, padx=10, fill="x")

        # Lista de municípios
        ctk.CTkLabel(self, text="Municípios").pack(pady=5)
        self.municipios_frame = ctk.CTkScrollableFrame(self, height=250)
        self.municipios_frame.pack(padx=10, fill="both", expand=True)

        self.estado_municipios = {m: False for m in MUNICIPIOS}  # <- aqui fica o controle de seleção
        self.todos_municipios = MUNICIPIOS.copy()
        self.checkbox_widgets = {}  # Dicionário de checkboxes por município

        self.criar_checkboxes(self.todos_municipios)

        self.select_all = ctk.CTkCheckBox(self, text="Selecionar Todos", command=self.toggle_all)
        self.select_all.pack(pady=5)

        self.run_button = ctk.CTkButton(self, text="Executar", command=self.run_bot)
        self.run_button.pack(pady=20)

        self.status_label = ctk.CTkLabel(self, text="", text_color="green")
        self.status_label.pack(pady=10)

    def criar_checkboxes(self, lista):
        for widget in self.municipios_frame.winfo_children():
            widget.destroy()
        self.checkbox_widgets.clear()

        for m in lista:
            var = ctk.BooleanVar(value=self.estado_municipios.get(m, False))

            def on_toggle(municipio=m, var=var):
                self.estado_municipios[municipio] = var.get()

            checkbox = ctk.CTkCheckBox(self.municipios_frame, text=m, variable=var, command=on_toggle)
            checkbox.pack(anchor="w")
            self.checkbox_widgets[m] = var

    def atualizar_municipios(self, *args):
        if hasattr(self, "debounce_timer") and self.debounce_timer:
            self.debounce_timer.cancel()

        self.debounce_timer = threading.Timer(0.3, self._filtrar_municipios)
        self.debounce_timer.start()

    def _filtrar_municipios(self):
        termo = self.search_var.get().lower()
        filtrados = [m for m in MUNICIPIOS if termo in m.lower()]
        self.after(0, lambda: self.criar_checkboxes(filtrados))


    def toggle_all(self):
        select = self.select_all.get()
        for m, var in self.checkbox_widgets.items():
            var.set(select)
            self.estado_municipios[m] = select

    def run_bot(self):
        ano = self.ano.get()
        tipo = self.tipo_var.get()
        selected_municipios = [m for m, selecionado in self.estado_municipios.items() if selecionado]

        if not selected_municipios:
            self.status_label.configure(text="Nenhum município selecionado.", text_color="red")
            return

        self.run_button.configure(state="disabled")
        self.status_label.configure(text="Executando...", text_color="orange")

        try:
            self.controller.executar_fluxo(ano, selected_municipios, tipo)
            self.status_label.configure(text="Finalizado com sucesso.", text_color="green")
        except Exception as e:
            print(e)
            self.status_label.configure(text=f"Erro: {str(e)}", text_color="red")
        finally:
            self.run_button.configure(state="normal")
