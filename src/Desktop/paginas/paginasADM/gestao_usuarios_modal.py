import customtkinter as ctk
from tkinter import messagebox
from DB.Banco import SessionLocal
from DB.models import Funcionario

class ModalFormularioUsuario(ctk.CTkToplevel):
    """Modal para adicionar um novo funcionário ou editar nome e cargo de um existente."""
    def __init__(self, parent, funcionario=None, callback_sucesso=None):
        super().__init__(parent)
        self.funcionario = funcionario
        self.callback_sucesso = callback_sucesso
        self.is_edicao = funcionario is not None

        titulo = "Editar Funcionário" if self.is_edicao else "Novo Funcionário"
        self.title(titulo)
        self.geometry("440x420")
        self.configure(fg_color="#F3EBE1")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        # Frame Principal (Card)
        card = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=16)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        # Cabeçalho
        ctk.CTkLabel(
            card,
            text=f"👤 {titulo.upper()}",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#3A1A10"
        ).pack(pady=(20, 5))

        subtitulo = "Altere o nome e o nível de acesso" if self.is_edicao else "Cadastre quem terá acesso ao sistema"
        ctk.CTkLabel(
            card,
            text=subtitulo,
            font=ctk.CTkFont(size=12),
            text_color="#777"
        ).pack(pady=(0, 15))

        # Campo Nome
        ctk.CTkLabel(
            card,
            text="Nome do Usuário (Login):",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#444"
        ).pack(anchor="w", padx=25, pady=(0, 3))

        self.entry_nome = ctk.CTkEntry(
            card,
            placeholder_text="Ex: joao, maria, gerente",
            height=38,
            corner_radius=10,
            fg_color="#F8F8F8",
            border_color="#D1C4B8",
            text_color="#000"
        )
        self.entry_nome.pack(fill="x", padx=25, pady=(0, 12))

        # Campo Senha (apenas na criação)
        if not self.is_edicao:
            ctk.CTkLabel(
                card,
                text="Senha:",
                font=ctk.CTkFont(size=12, weight="bold"),
                text_color="#444"
            ).pack(anchor="w", padx=25, pady=(0, 3))

            self.entry_senha = ctk.CTkEntry(
                card,
                placeholder_text="Digite a senha de acesso",
                show="•",
                height=38,
                corner_radius=10,
                fg_color="#F8F8F8",
                border_color="#D1C4B8",
                text_color="#000"
            )
            self.entry_senha.pack(fill="x", padx=25, pady=(0, 12))

        # Campo Função / Cargo (Controle)
        ctk.CTkLabel(
            card,
            text="Nível de Acesso (Cargo):",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#444"
        ).pack(anchor="w", padx=25, pady=(0, 3))

        self.cargos_map = {
            "👑 Administrador / Gerência (Painel ADM)": 1,
            "🍳 Cozinha (Painel Cozinha)": 2
        }

        valores_cargo = list(self.cargos_map.keys())
        valor_inicial = valores_cargo[0]

        if self.is_edicao:
            self.entry_nome.insert(0, self.funcionario.nome)
            if self.funcionario.controle == 2:
                valor_inicial = valores_cargo[1]

        self.combo_cargo = ctk.CTkOptionMenu(
            card,
            values=valores_cargo,
            height=38,
            corner_radius=10,
            fg_color="#3A1A10",
            button_color="#27120B",
            button_hover_color="#52291B",
            dropdown_fg_color="#FFFFFF",
            dropdown_text_color="#000000",
            dropdown_hover_color="#DFCBB8"
        )
        self.combo_cargo.set(valor_inicial)
        self.combo_cargo.pack(fill="x", padx=25, pady=(0, 15))

        # Label de aviso / erro
        self.lbl_aviso = ctk.CTkLabel(
            card,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#EF4444"
        )
        self.lbl_aviso.pack(pady=(0, 8))

        # Botão Salvar
        btn_salvar = ctk.CTkButton(
            card,
            text="Salvar Alterações" if self.is_edicao else "Cadastrar Funcionário",
            height=40,
            corner_radius=10,
            fg_color="#3A1A10",
            hover_color="#52291B",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.salvar
        )
        btn_salvar.pack(fill="x", padx=25, pady=(0, 10))

    def salvar(self):
        nome = self.entry_nome.get().strip()
        cargo_str = self.combo_cargo.get()
        controle = self.cargos_map.get(cargo_str, 1)

        if not nome:
            self.lbl_aviso.configure(text="Preencha o nome do usuário!")
            return

        session = SessionLocal()
        try:
            query = session.query(Funcionario).filter(Funcionario.nome == nome)
            if self.is_edicao:
                query = query.filter(Funcionario.id != self.funcionario.id)
            
            existente = query.first()
            if existente:
                self.lbl_aviso.configure(text="Já existe um funcionário com esse nome de usuário!")
                return

            if self.is_edicao:
                func_db = session.query(Funcionario).filter(Funcionario.id == self.funcionario.id).first()
                if func_db:
                    func_db.nome = nome
                    func_db.controle = controle
                    session.commit()
            else:
                senha = self.entry_senha.get().strip()
                if not senha:
                    self.lbl_aviso.configure(text="Preencha a senha para o novo funcionário!")
                    return
                
                novo_func = Funcionario(
                    nome=nome,
                    senha=senha,
                    controle=controle,
                    ativo=True
                )
                session.add(novo_func)
                session.commit()

            if self.callback_sucesso:
                self.callback_sucesso()
            self.destroy()

        except Exception as e:
            session.rollback()
            self.lbl_aviso.configure(text=f"Erro ao salvar: {e}")
        finally:
            session.close()


class ModalAlterarSenha(ctk.CTkToplevel):
    """Modal específico para alterar a senha de um funcionário."""
    def __init__(self, parent, funcionario, callback_sucesso=None):
        super().__init__(parent)
        self.funcionario = funcionario
        self.callback_sucesso = callback_sucesso

        self.title("Alterar Senha")
        self.geometry("400x350")
        self.configure(fg_color="#F3EBE1")
        self.resizable(False, False)

        self.transient(parent)
        self.grab_set()

        card = ctk.CTkFrame(self, fg_color="#FFFFFF", corner_radius=16)
        card.pack(fill="both", expand=True, padx=20, pady=20)

        ctk.CTkLabel(
            card,
            text="🔑 ALTERAR SENHA",
            font=ctk.CTkFont(size=18, weight="bold"),
            text_color="#3A1A10"
        ).pack(pady=(15, 4))

        ctk.CTkLabel(
            card,
            text=f"Usuário: {self.funcionario.nome}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#555"
        ).pack(pady=(0, 15))

        # Nova Senha
        ctk.CTkLabel(
            card,
            text="Nova Senha:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#444"
        ).pack(anchor="w", padx=25, pady=(0, 3))

        self.entry_nova_senha = ctk.CTkEntry(
            card,
            placeholder_text="Digite a nova senha",
            show="•",
            height=38,
            corner_radius=10,
            fg_color="#F8F8F8",
            border_color="#D1C4B8",
            text_color="#000"
        )
        self.entry_nova_senha.pack(fill="x", padx=25, pady=(0, 10))

        # Confirmação
        ctk.CTkLabel(
            card,
            text="Confirmar Senha:",
            font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#444"
        ).pack(anchor="w", padx=25, pady=(0, 3))

        self.entry_confirma_senha = ctk.CTkEntry(
            card,
            placeholder_text="Repita a nova senha",
            show="•",
            height=38,
            corner_radius=10,
            fg_color="#F8F8F8",
            border_color="#D1C4B8",
            text_color="#000"
        )
        self.entry_confirma_senha.pack(fill="x", padx=25, pady=(0, 10))

        self.lbl_aviso = ctk.CTkLabel(
            card,
            text="",
            font=ctk.CTkFont(size=11),
            text_color="#EF4444"
        )
        self.lbl_aviso.pack(pady=(0, 6))

        btn_salvar = ctk.CTkButton(
            card,
            text="Salvar Nova Senha",
            height=40,
            corner_radius=10,
            fg_color="#3A1A10",
            hover_color="#52291B",
            font=ctk.CTkFont(size=13, weight="bold"),
            command=self.salvar_senha
        )
        btn_salvar.pack(fill="x", padx=25, pady=(0, 10))

    def salvar_senha(self):
        nova_senha = self.entry_nova_senha.get().strip()
        confirma = self.entry_confirma_senha.get().strip()

        if not nova_senha:
            self.lbl_aviso.configure(text="Digite a nova senha!")
            return

        if nova_senha != confirma:
            self.lbl_aviso.configure(text="As senhas não coincidem!")
            return

        session = SessionLocal()
        try:
            func_db = session.query(Funcionario).filter(Funcionario.id == self.funcionario.id).first()
            if func_db:
                func_db.senha = nova_senha
                session.commit()

            if self.callback_sucesso:
                self.callback_sucesso()
            self.destroy()

        except Exception as e:
            session.rollback()
            self.lbl_aviso.configure(text=f"Erro ao salvar senha: {e}")
        finally:
            session.close()


class GestaoUsuariosModal(ctk.CTkToplevel):
    """
    Tela principal de Gestão de Usuários (Gerência e Funcionários).
    Permite listar, criar, editar (nome/cargo), trocar senha e remover funcionários.
    """
    def __init__(self, parent, usuario_logado=None):
        super().__init__(parent)
        self.parent = parent
        self.usuario_logado = usuario_logado

        self.title("Gestão de Usuários - Catatau Lanches")
        self.geometry("860x600")
        self.minsize(780, 520)
        self.configure(fg_color="#F3EBE1")

        self.transient(parent)
        self.grab_set()

        self.criar_layout()
        self.carregar_usuarios()

    def criar_layout(self):
        # Container principal com padding
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(fill="both", expand=True, padx=25, pady=20)

        # Cabeçalho Superior
        header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        header_frame.pack(fill="x", pady=(0, 12))

        titulo_box = ctk.CTkFrame(header_frame, fg_color="transparent")
        titulo_box.pack(side="left")

        ctk.CTkLabel(
            titulo_box,
            text="4. Gestão de Usuários (Gerência e Funcionários) 👥",
            font=ctk.CTkFont(family="Arial", size=20, weight="bold"),
            text_color="#3A1A10"
        ).pack(anchor="w")

        ctk.CTkLabel(
            titulo_box,
            text="Gerencie quem tem acesso ao painel administrativo e à cozinha",
            font=ctk.CTkFont(size=12),
            text_color="#666"
        ).pack(anchor="w", pady=(2, 0))

        # Barra de Ações Rápidas (Superior)
        acoes_bar = ctk.CTkFrame(self.main_container, fg_color="#FFFFFF", corner_radius=12, height=52)
        acoes_bar.pack(fill="x", pady=(0, 12))

        # Botão Adicionar Novo Funcionário
        self.btn_novo = ctk.CTkButton(
            acoes_bar,
            text="➕ Adicionar Novo Funcionário",
            fg_color="#3A1A10",
            hover_color="#52291B",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=34,
            corner_radius=8,
            command=self.abrir_modal_novo
        )
        self.btn_novo.pack(side="left", padx=12, pady=9)

        # Botão Alterar Senha do Usuário Atual
        self.btn_minha_senha = ctk.CTkButton(
            acoes_bar,
            text="🔑 Alterar Senha do Usuário Atual",
            fg_color="#EADDCF",
            text_color="#3A1A10",
            hover_color="#DFCBB8",
            font=ctk.CTkFont(size=12, weight="bold"),
            height=34,
            corner_radius=8,
            command=self.alterar_senha_usuario_atual
        )
        self.btn_minha_senha.pack(side="left", padx=5, pady=9)

        # Botão Recarregar
        btn_refresh = ctk.CTkButton(
            acoes_bar,
            text="🔄",
            width=36,
            height=34,
            fg_color="#F3EBE1",
            text_color="#3A1A10",
            hover_color="#DFCBB8",
            font=ctk.CTkFont(size=14),
            corner_radius=8,
            command=self.carregar_usuarios
        )
        btn_refresh.pack(side="right", padx=12, pady=9)

        # Campo de Busca
        self.entry_busca = ctk.CTkEntry(
            acoes_bar,
            placeholder_text="🔍 Buscar usuário...",
            width=200,
            height=34,
            corner_radius=8,
            fg_color="#F8F8F8",
            border_color="#D1C4B8",
            text_color="#000"
        )
        self.entry_busca.pack(side="right", padx=(0, 6), pady=9)
        self.entry_busca.bind("<KeyRelease>", lambda event: self.filtrar_usuarios())

        # Cabeçalho da Tabela
        tabela_header = ctk.CTkFrame(self.main_container, fg_color="#EADDCF", height=34, corner_radius=8)
        tabela_header.pack(fill="x", pady=(0, 6))

        ctk.CTkLabel(
            tabela_header, text="USUÁRIO", font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#3A1A10", width=180, anchor="w"
        ).pack(side="left", padx=(20, 10))

        ctk.CTkLabel(
            tabela_header, text="ACESSO / CARGO", font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#3A1A10", width=180, anchor="w"
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            tabela_header, text="STATUS", font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#3A1A10", width=90, anchor="center"
        ).pack(side="left", padx=10)

        ctk.CTkLabel(
            tabela_header, text="AÇÕES", font=ctk.CTkFont(size=12, weight="bold"),
            text_color="#3A1A10", width=220, anchor="e"
        ).pack(side="right", padx=20)

        # Scroll de Usuários
        self.scroll_usuarios = ctk.CTkScrollableFrame(self.main_container, fg_color="transparent")
        self.scroll_usuarios.pack(fill="both", expand=True)

    def carregar_usuarios(self):
        """Carrega todos os funcionários do banco de dados e os exibe."""
        session = SessionLocal()
        try:
            self.todos_usuarios = session.query(Funcionario).order_by(Funcionario.id.asc()).all()
            self.renderizar_lista(self.todos_usuarios)
        except Exception as e:
            print(f"Erro ao carregar usuários: {e}")
            self.todos_usuarios = []
            self.renderizar_lista([])
        finally:
            session.close()

    def filtrar_usuarios(self):
        """Filtra a lista em memória conforme o termo de busca."""
        termo = self.entry_busca.get().strip().lower()
        if not termo:
            self.renderizar_lista(self.todos_usuarios)
            return

        filtrados = [
            u for u in self.todos_usuarios 
            if termo in u.nome.lower() or 
               (u.controle == 1 and termo in "administrador gerencia gerente adm") or
               (u.controle == 2 and termo in "cozinha")
        ]
        self.renderizar_lista(filtrados)

    def renderizar_lista(self, lista):
        for child in self.scroll_usuarios.winfo_children():
            child.destroy()

        if not lista:
            vazio_frame = ctk.CTkFrame(self.scroll_usuarios, fg_color="#FFFFFF", corner_radius=12)
            vazio_frame.pack(fill="x", pady=20, padx=5)
            ctk.CTkLabel(
                vazio_frame,
                text="Nenhum usuário encontrado.",
                font=ctk.CTkFont(size=13),
                text_color="#888"
            ).pack(pady=25)
            return

        for func in lista:
            self.criar_linha_usuario(func)

    def criar_linha_usuario(self, func):
        row = ctk.CTkFrame(self.scroll_usuarios, fg_color="#FFFFFF", corner_radius=10, height=52)
        row.pack(fill="x", pady=3, padx=2)
        row.pack_propagate(False)

        # 1. Informações do Usuário (Nome + Badge se for atual)
        nome_box = ctk.CTkFrame(row, fg_color="transparent", width=180)
        nome_box.pack(side="left", padx=(15, 10))

        icone_usuario = "👑" if func.controle == 1 else "🍳"
        ctk.CTkLabel(
            nome_box,
            text=f"{icone_usuario} {func.nome}",
            font=ctk.CTkFont(size=13, weight="bold"),
            text_color="#000",
            anchor="w"
        ).pack(side="left")

        if self.usuario_logado and func.nome.lower() == str(self.usuario_logado).lower():
            badge_voce = ctk.CTkLabel(
                nome_box,
                text="(Você)",
                font=ctk.CTkFont(size=11, weight="bold"),
                text_color="#FF7338"
            )
            badge_voce.pack(side="left", padx=6)

        # 2. Cargo / Nível de Acesso (com botão para trocar de função rapidamente)
        cargo_box = ctk.CTkFrame(row, fg_color="transparent", width=180)
        cargo_box.pack(side="left", padx=10)

        is_adm = (func.controle == 1)
        cargo_texto = "Administrador" if is_adm else "Cozinha"
        cargo_cor_bg = "#F5EBE1" if is_adm else "#E8F0FE"
        cargo_cor_txt = "#3A1A10" if is_adm else "#1967D2"

        # Badge com opção de trocar cargo direto
        btn_trocar_cargo = ctk.CTkButton(
            cargo_box,
            text=cargo_texto,
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color=cargo_cor_bg,
            text_color=cargo_cor_txt,
            hover_color="#DFCBB8",
            corner_radius=6,
            height=26,
            width=115,
            command=lambda f=func: self.alternar_cargo(f)
        )
        btn_trocar_cargo.pack(side="left")

        # 3. Status (Ativo / Inativo)
        status_box = ctk.CTkFrame(row, fg_color="transparent", width=90)
        status_box.pack(side="left", padx=10)

        is_ativo = bool(getattr(func, 'ativo', True))
        status_texto = "Ativo" if is_ativo else "Inativo"
        status_cor = "#109811" if is_ativo else "#EF4444"

        btn_status = ctk.CTkButton(
            status_box,
            text=status_texto,
            font=ctk.CTkFont(size=11, weight="bold"),
            text_color=status_cor,
            fg_color="transparent",
            hover_color="#F0F0F0",
            width=65,
            height=26,
            command=lambda f=func: self.alternar_status(f)
        )
        btn_status.pack(side="left")

        # 4. Botões de Ações (Editar, Alterar Senha, Remover)
        acoes_frame = ctk.CTkFrame(row, fg_color="transparent")
        acoes_frame.pack(side="right", padx=15)

        # Botão Editar (Nome e Cargo)
        btn_editar = ctk.CTkButton(
            acoes_frame,
            text="✏️ Editar",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#F3EBE1",
            text_color="#3A1A10",
            hover_color="#DFCBB8",
            width=70,
            height=28,
            corner_radius=6,
            command=lambda f=func: self.abrir_modal_editar(f)
        )
        btn_editar.pack(side="left", padx=3)

        # Botão Alterar Senha
        btn_senha = ctk.CTkButton(
            acoes_frame,
            text="🔑 Senha",
            font=ctk.CTkFont(size=11, weight="bold"),
            fg_color="#F3EBE1",
            text_color="#3A1A10",
            hover_color="#DFCBB8",
            width=70,
            height=28,
            corner_radius=6,
            command=lambda f=func: self.abrir_modal_senha(f)
        )
        btn_senha.pack(side="left", padx=3)

        # Botão Remover
        btn_remover = ctk.CTkButton(
            acoes_frame,
            text="🗑️",
            font=ctk.CTkFont(size=13),
            fg_color="#FDE8E8",
            text_color="#EF4444",
            hover_color="#FBD5D5",
            width=32,
            height=28,
            corner_radius=6,
            command=lambda f=func: self.confirmar_remover(f)
        )
        btn_remover.pack(side="left", padx=3)

    def alternar_cargo(self, func):
        """Troca o cargo do funcionário entre Administrador (1) e Cozinha (2)."""
        novo_controle = 2 if func.controle == 1 else 1

        # Se for o único Administrador e estiver tentando virar Cozinha, previne
        if func.controle == 1 and novo_controle == 2:
            admins = [u for u in self.todos_usuarios if u.controle == 1 and getattr(u, 'ativo', True)]
            if len(admins) <= 1:
                messagebox.showwarning(
                    "Operação Bloqueada",
                    "Não é permitido rebaixar o único Administrador ativo do sistema."
                )
                return

        session = SessionLocal()
        try:
            func_db = session.query(Funcionario).filter(Funcionario.id == func.id).first()
            if func_db:
                func_db.controle = novo_controle
                session.commit()
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao alternar cargo: {e}")
        finally:
            session.close()

        self.carregar_usuarios()

    def alternar_status(self, func):
        """Ativa ou inativa o funcionário."""
        novo_status = not getattr(func, 'ativo', True)

        # Se for o único admin ativo e estiver sendo inativado
        if not novo_status and func.controle == 1:
            admins = [u for u in self.todos_usuarios if u.controle == 1 and getattr(u, 'ativo', True)]
            if len(admins) <= 1:
                messagebox.showwarning(
                    "Operação Bloqueada",
                    "Não é possível desativar o único Administrador ativo do sistema."
                )
                return

        session = SessionLocal()
        try:
            func_db = session.query(Funcionario).filter(Funcionario.id == func.id).first()
            if func_db:
                func_db.ativo = novo_status
                session.commit()
        except Exception as e:
            session.rollback()
            messagebox.showerror("Erro", f"Erro ao alterar status: {e}")
        finally:
            session.close()

        self.carregar_usuarios()

    def confirmar_remover(self, func):
        """Exibe confirmação antes de remover o funcionário do banco."""
        # Se for o único Administrador, impede a exclusão
        if func.controle == 1:
            admins = [u for u in self.todos_usuarios if u.controle == 1]
            if len(admins) <= 1:
                messagebox.showwarning(
                    "Operação Bloqueada",
                    "Não é possível remover o único Administrador do sistema."
                )
                return

        resposta = messagebox.askyesno(
            "Confirmar Remoção",
            f"Deseja realmente remover o funcionário '{func.nome}'?\nEssa ação não poderá ser desfeita."
        )
        if resposta:
            session = SessionLocal()
            try:
                func_db = session.query(Funcionario).filter(Funcionario.id == func.id).first()
                if func_db:
                    session.delete(func_db)
                    session.commit()
            except Exception as e:
                session.rollback()
                messagebox.showerror("Erro", f"Erro ao excluir funcionário: {e}")
            finally:
                session.close()

            self.carregar_usuarios()

    def abrir_modal_novo(self):
        ModalFormularioUsuario(self, funcionario=None, callback_sucesso=self.carregar_usuarios)

    def abrir_modal_editar(self, func):
        ModalFormularioUsuario(self, funcionario=func, callback_sucesso=self.carregar_usuarios)

    def abrir_modal_senha(self, func):
        ModalAlterarSenha(self, funcionario=func, callback_sucesso=self.carregar_usuarios)

    def alterar_senha_usuario_atual(self):
        """Abre modal de alteração de senha para o usuário logado no momento."""
        alvo = None
        if self.usuario_logado:
            alvo = next((u for u in self.todos_usuarios if u.nome.lower() == str(self.usuario_logado).lower()), None)
        
        if not alvo and self.todos_usuarios:
            alvo = self.todos_usuarios[0]

        if alvo:
            self.abrir_modal_senha(alvo)
        else:
            messagebox.showinfo("Aviso", "Nenhum usuário cadastrado para alterar senha.")
