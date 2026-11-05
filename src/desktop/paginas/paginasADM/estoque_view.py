import customtkinter as ctk
# Importe a sessão e o modelo do seu banco (ajuste o caminho se necessário)
from DB.Banco import SessionLocal as Session
from DB.models import Ingredientes

class ModalItemEstoque(ctk.CTkToplevel):
    def __init__(self, parent, item_dados=None, callback_salvar=None):
        super().__init__(parent)
        
        self.callback_salvar = callback_salvar
        self.item_dados = item_dados

        # Configurações do Pop-up Modal
        self.title("Editar Item" if item_dados else "Adicionar Novo Item")
        self.geometry("400x260")
        self.configure(fg_color="#F3EBE1")
        self.resizable(False, False)
        
        # Garante que o modal fique sobreposto e em foco
        self.transient(parent)
        self.grab_set()

        # Título do Modal
        titulo_txt = "EDITAR ITEM DO ESTOQUE" if item_dados else "NOVO ITEM NO ESTOQUE"
        ctk.CTkLabel(
            self, text=titulo_txt, 
            font=ctk.CTkFont(size=16, weight="bold"), 
            text_color="#3A1A10"
        ).pack(pady=(15, 10))

        # Campos de Entrada
        self.entry_nome = ctk.CTkEntry(self, placeholder_text="Nome (ex: Pão (uni.))", width=320)
        self.entry_nome.pack(pady=8)

        self.entry_qtd = ctk.CTkEntry(self, placeholder_text="Quantidade (ex: 15)", width=320)
        self.entry_qtd.pack(pady=8)

        # Se for EDIÇÃO, preenche os campos com os dados existentes
        if item_dados:
            self.entry_nome.insert(0, item_dados["nome"])
            self.entry_qtd.insert(0, str(item_dados["qtd"]))

        # Botão Salvar
        ctk.CTkButton(
            self, 
            text="Salvar Alterações" if item_dados else "Cadastrar Item",
            fg_color="#3A1A10",
            hover_color="#52291B",
            width=320,
            height=35,
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.salvar
        ).pack(pady=15)

    def salvar(self):
        nome = self.entry_nome.get()
        qtd = self.entry_qtd.get()

        if not nome or not qtd:
            return  # Evita salvar se estiver vazio

        if self.callback_salvar:
            self.callback_salvar(nome, qtd, self.item_dados)

        self.destroy()


class EstoqueView(ctk.CTkFrame):
    def __init__(self, parent):
        super().__init__(parent, fg_color="#FFFFFF", corner_radius=15)

        # Lista que vai guardar os dados vindos do banco
        self.itens_estoque = []

        # Topo
        header_frame = ctk.CTkFrame(self, fg_color="transparent")
        header_frame.pack(fill="x", padx=20, pady=15)

        ctk.CTkLabel(
            header_frame, 
            text="CONTROLE DE ESTOQUE 📦", 
            font=ctk.CTkFont(size=18, weight="bold"), 
            text_color="#3A1A10"
        ).pack(side="left")

        ctk.CTkButton(
            header_frame, 
            text="+ Adicionar Item", 
            fg_color="#3A1A10", 
            hover_color="#52291B",
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self.abrir_modal_adicionar
        ).pack(side="right")

        # ÁREA ROLÁVEL DOS ITENS
        self.scroll = ctk.CTkScrollableFrame(self, fg_color="transparent")
        self.scroll.pack(fill="both", expand=True, padx=15, pady=(0, 15))

        # Carrega do banco e renderiza os itens na tela
        self.atualizar_lista()

    def calcular_status_automatico(self, nome, qtd):
        """Calcula o status com base na unidade extraída do nome e nas regras de quantidade."""
        try:
            qtd_float = float(qtd)
        except ValueError:
            return "Ok"

        nome_lower = nome.lower()

        # Unidades (uni.) -> < 15: Crítico | 15 a 50: Atenção | > 50: Ok
        if "uni" in nome_lower:
            if qtd_float < 15:
                return "Crítico"
            elif qtd_float <= 50:
                return "Atenção"
            else:
                return "Ok"
        
        # Fatias (fatia/fatias) -> < 20: Crítico | 20 a 60: Atenção | > 60: Ok
        elif "fatia" in nome_lower:
            if qtd_float < 20:
                return "Crítico"
            elif qtd_float <= 60:
                return "Atenção"
            else:
                return "Ok"
        
        # Quilogramas (kg) -> < 1.0: Crítico | 1.0 a 3.0: Atenção | > 3.0: Ok
        elif "kg" in nome_lower:
            if qtd_float < 0.5:
                return "Crítico"
            elif qtd_float <= 1.2:
                return "Atenção"
            else:
                return "Ok"
        
        # Gramas (g) -> < 200: Crítico | 200 a 600: Atenção | > 600: Ok
        elif "g" in nome_lower:
            if qtd_float < 200:
                return "Crítico"
            elif qtd_float <= 600:
                return "Atenção"
            else:
                return "Ok"
        
        return "Ok"

    def get_cor_status(self, status):
        coreshash = {
            "Crítico": "#D97706",
            "Atenção": "#F59E0B",
            "Ok": "#10B981"
        }
        return coreshash.get(status, "#000000")

    def carregar_do_banco(self):
        """Busca os itens diretamente na tabela 'ingredientes' do banco de dados"""
        session = Session()
        try:
            resultados = session.query(Ingredientes).all()
            self.itens_estoque = []
            for item in resultados:
                qtd_val = round(float(item.quantidade), 2)
                status_calculado = self.calcular_status_automatico(item.nome, qtd_val)
                
                self.itens_estoque.append({
                    "id": item.id,
                    "nome": item.nome, 
                    "qtd": qtd_val,
                    "status": status_calculado
                })
        except Exception as e:
            print(f"Erro ao carregar estoque do banco: {e}")
            self.itens_estoque = []
        finally:
            session.close()

    def atualizar_lista(self):
        self.carregar_do_banco()

        for widget in self.scroll.winfo_children():
            widget.destroy()

        for item in self.itens_estoque:
            row = ctk.CTkFrame(self.scroll, fg_color="#F9F9F9", height=40)
            row.pack(fill="x", pady=4, padx=5)

            ctk.CTkLabel(
                row, text=item["nome"], 
                font=ctk.CTkFont(size=13, weight="bold"), 
                text_color="#000", width=200, anchor="w"
            ).pack(side="left", padx=15)

            ctk.CTkLabel(
                row, text=str(item["qtd"]), 
                font=ctk.CTkFont(size=12), 
                text_color="#000", width=100
            ).pack(side="left", padx=15)

            ctk.CTkLabel(
                row, text=item["status"], 
                font=ctk.CTkFont(size=12, weight="bold"), 
                text_color=self.get_cor_status(item["status"]), width=100
            ).pack(side="left", padx=15)

            ctk.CTkButton(
                row, 
                text="Editar", 
                width=60, 
                height=24, 
                fg_color="#C09267",
                hover_color="#A37851",
                font=ctk.CTkFont(size=11, weight="bold"),
                command=lambda item_alvo=item: self.abrir_modal_editar(item_alvo)
            ).pack(side="right", padx=10)

    def abrir_modal_adicionar(self):
        ModalItemEstoque(self, item_dados=None, callback_salvar=self.salvar_item)

    def abrir_modal_editar(self, item):
        ModalItemEstoque(self, item_dados=item, callback_salvar=self.salvar_item)

    def salvar_item(self, nome, qtd, item_original=None):
        session = Session()
        try:
            qtd_formatada = round(float(qtd), 2)
            status_calculado = self.calcular_status_automatico(nome, qtd_formatada)

            if item_original:
                item_db = session.query(Ingredientes).filter_by(id=item_original["id"]).first()
                if item_db:
                    item_db.nome = nome
                    item_db.quantidade = qtd_formatada
                    item_db.status = status_calculado
                    session.commit()
            else:
                novo_item = Ingredientes(
                    nome=nome,
                    quantidade=qtd_formatada,
                    status=status_calculado
                )
                session.add(novo_item)
                session.commit()
        except Exception as e:
            session.rollback()
            print(f"Erro ao salvar item no banco: {e}")
        finally:
            session.close()

        self.atualizar_lista()