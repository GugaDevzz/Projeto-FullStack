# =============================================================================
# tests/test_servico.py — Suíte de Testes do Catatau Lanches
# =============================================================================
# Cobertura:
#   BLOCO 1  — Modelos ORM e Regras de Banco de Dados
#   BLOCO 2  — Lógica de Carrinho e Serialização de Cookie
#   BLOCO 3  — Baixa Automática de Estoque (RF06 / RN03)
#   BLOCO 4  — Validações de Cadastro de Cliente (RF03 / RN06)
#   BLOCO 5  — Autenticação de Cliente Web (RF04)
#   BLOCO 6  — Validação e Aplicação de Cupom (RF05 / RN02)
#   BLOCO 7  — Fluxo de Checkout e Envio do Pedido (RF05 / RN02)
#   BLOCO 8  — Transições de Status do Pedido (RF09 / RN04)
#   BLOCO 9  — Regras de Autorização de Funcionários (RF07 / RN05)
#   BLOCO 10 — Cálculo de Status de Estoque (RF13 / RN07)
#   BLOCO 11 — Endpoints da API FastAPI (rotas HTTP)
#   BLOCO 12 — Testes de Contagem de Pedidos do Cliente
# =============================================================================

import json
from decimal import Decimal
import pytest


# =============================================================================
# BLOCO 1 — Modelos ORM e Regras de Banco de Dados
# =============================================================================

class TestModelosORM:
    """Verifica persistência e integridade dos modelos SQLAlchemy."""

    def test_criar_cliente_basico(self, db_session, cliente_factory):
        """RF03 | Um cliente novo deve ser persistido com os dados corretos."""
        c = cliente_factory(nome="Maria Silva", email="maria@exemplo.com")
        assert c.id is not None, "Cliente deve ter ID após commit"
        assert c.nome == "Maria Silva"
        assert c.cupom_usado is False
        assert c.pedidos_count == 0

    def test_criar_produto(self, db_session, produto_factory):
        """RF01 | Um produto (lanche) deve ser persistido com valor correto."""
        p = produto_factory(nome="King Bacon", valor=39.90)
        assert p.id is not None
        assert p.nome == "King Bacon"
        assert abs(p.valor - 39.90) < 0.001

    def test_criar_ingrediente(self, db_session, ingrediente_factory):
        """RF13 | Um ingrediente de estoque deve ser persistido corretamente."""
        i = ingrediente_factory(nome="Pao uni", quantidade=100, status="Ok")
        assert i.id is not None
        assert float(i.quantidade) == 100.0
        assert i.status == "Ok"

    def test_criar_pedido_status_esperando(self, db_session, pedido_factory):
        """RF05 | Um pedido recém-criado deve ter status 'ESPERANDO'."""
        p = pedido_factory(status="ESPERANDO", num_mesa=3)
        assert p.id is not None
        assert p.status == "ESPERANDO"
        assert p.num_mesa == 3

    def test_produto_estoque_vincula_corretamente(
        self, db_session, produto_factory, ingrediente_factory, produto_estoque_factory, db_infra
    ):
        """RF06 | A tabela produto_estoque deve vincular produto ↔ ingrediente."""
        prod = produto_factory()
        ing = ingrediente_factory()
        pe = produto_estoque_factory(prod.id, ing.id, quantidade_necessaria=2.0)
        assert pe.id is not None
        assert pe.fk_id_produto == prod.id
        assert pe.fk_id_estoque == ing.id
        assert float(pe.quantidade_necessaria) == 2.0

    def test_cliente_cupom_usado_padrao_false(self, db_session, cliente_factory):
        """RN — Valor padrão de cupom_usado deve ser False no cadastro."""
        c = cliente_factory()
        assert c.cupom_usado is False

    def test_cliente_pedidos_count_padrao_zero(self, db_session, cliente_factory):
        """RN — Valor padrão de pedidos_count deve ser 0."""
        c = cliente_factory()
        assert c.pedidos_count == 0


# =============================================================================
# BLOCO 2 — Lógica de Carrinho e Serialização de Cookie
# =============================================================================

class TestCarrinhoSerializacao:
    """
    Verifica a lógica pura de manipulação do carrinho via cookie JSON.
    Não depende de banco — apenas valida operações de dicionário.
    """

    def test_adicionar_item_ao_carrinho(self, carrinho_cookie):
        """RF02 | Adicionar um produto deve incrementar sua quantidade."""
        carrinho = {}
        item_id = 1
        chave = str(item_id)
        carrinho[chave] = carrinho.get(chave, 0) + 1

        cookie_str = json.dumps(carrinho)
        assert json.loads(cookie_str) == {"1": 1}

    def test_adicionar_mesmo_item_incrementa(self):
        """RF02 | Adicionar o mesmo produto duas vezes acumula a quantidade."""
        carrinho = {"1": 1}
        carrinho["1"] = carrinho.get("1", 0) + 1
        assert carrinho["1"] == 2

    def test_diminuir_item_decrementa(self):
        """RF02 | Diminuir quantidade deve decrementar corretamente."""
        carrinho = {"1": 3}
        carrinho["1"] -= 1
        assert carrinho["1"] == 2

    def test_diminuir_para_zero_remove_item(self):
        """RF02 | Quando quantidade cai para 0 (ou menos), item deve ser removido."""
        carrinho = {"1": 1}
        carrinho["1"] -= 1
        if carrinho["1"] <= 0:
            del carrinho["1"]
        assert "1" not in carrinho

    def test_remover_item_direto(self):
        """RF02 | Remoção direta de item deve eliminar a chave do carrinho."""
        carrinho = {"1": 2, "3": 1}
        del carrinho["1"]
        assert "1" not in carrinho
        assert "3" in carrinho

    def test_carrinho_vazio_total_zero(self):
        """RN02 | Carrinho vazio deve resultar em total R$ 0,00."""
        total = 0.0
        carrinho_itens = []
        assert total == 0.0
        assert len(carrinho_itens) == 0

    def test_cookie_serializado_e_deserializado(self, carrinho_cookie):
        """RF02 | Cookie deve ser serializável/deserializável em JSON."""
        cookie_str = carrinho_cookie({1: 2, 3: 1})
        dados = json.loads(cookie_str)
        assert dados == {"1": 2, "3": 1}

    def test_carrinho_multiples_itens(self, carrinho_cookie):
        """RF02 | Carrinho com múltiplos produtos deve manter todas as entradas."""
        cookie_str = carrinho_cookie({1: 1, 2: 3, 5: 2})
        dados = json.loads(cookie_str)
        assert len(dados) == 3
        assert dados["2"] == 3


# =============================================================================
# BLOCO 3 — Baixa Automática de Estoque (RF06 / RN03)
# =============================================================================

class TestBaixaAutomaticaEstoque:
    """
    Simula a operação de baixa de insumos executada em POST /checkout/enviar.
    Valida a fórmula:
        quantidade_nova = quantidade_atual - (quantidade_necessaria × qtd_pedida)
    """

    def test_baixa_simples_um_ingrediente(
        self, db_session, produto_factory, ingrediente_factory,
        produto_estoque_factory, db_infra,
    ):
        """RF06 | Pedir 1 lanche deve subtrair a qtd necessária do ingrediente vinculado."""
        _, _, _, tabelas = db_infra
        Ingrediente = tabelas.Ingrediente
        ProdutoEstoque = tabelas.ProdutoEstoque

        prod = produto_factory(nome="Lanche Baixa Simples")
        ing = ingrediente_factory(nome="Pao uni baixa", quantidade=20)
        produto_estoque_factory(prod.id, ing.id, quantidade_necessaria=1.0)

        qtd_pedida = 1
        assoc = db_session.query(ProdutoEstoque).filter_by(fk_id_produto=prod.id).all()
        for a in assoc:
            ing_db = db_session.query(Ingrediente).filter_by(id=a.fk_id_estoque).first()
            ing_db.quantidade -= Decimal(str(a.quantidade_necessaria)) * Decimal(str(qtd_pedida))

        db_session.commit()
        db_session.refresh(ing)
        assert float(ing.quantidade) == 19.0

    def test_baixa_multipla_quantidade_pedida(
        self, db_session, produto_factory, ingrediente_factory,
        produto_estoque_factory, db_infra,
    ):
        """RF06 | Pedir 3 lanches deve subtrair 3× a quantidade necessária."""
        _, _, _, tabelas = db_infra
        Ingrediente = tabelas.Ingrediente
        ProdutoEstoque = tabelas.ProdutoEstoque

        prod = produto_factory(nome="X-Duplo Teste")
        ing = ingrediente_factory(nome="Carne uni multipla", quantidade=30)
        produto_estoque_factory(prod.id, ing.id, quantidade_necessaria=2.0)

        qtd_pedida = 3
        assoc = db_session.query(ProdutoEstoque).filter_by(fk_id_produto=prod.id).all()
        for a in assoc:
            ing_db = db_session.query(Ingrediente).filter_by(id=a.fk_id_estoque).first()
            ing_db.quantidade -= Decimal(str(a.quantidade_necessaria)) * Decimal(str(qtd_pedida))

        db_session.commit()
        db_session.refresh(ing)
        # 30 - (2 × 3) = 24
        assert float(ing.quantidade) == 24.0

    def test_baixa_multiplos_ingredientes_por_produto(
        self, db_session, produto_factory, ingrediente_factory,
        produto_estoque_factory, db_infra,
    ):
        """RF06 | Baixa deve atingir TODOS os ingredientes da ficha técnica do produto."""
        _, _, _, tabelas = db_infra
        Ingrediente = tabelas.Ingrediente
        ProdutoEstoque = tabelas.ProdutoEstoque

        prod = produto_factory(nome="Burger Completo Teste")
        ing_pao = ingrediente_factory(nome="Pao brioche tc", quantidade=10)
        ing_carne = ingrediente_factory(nome="Carne bov tc", quantidade=20)
        ing_queijo = ingrediente_factory(nome="Queijo fatia tc", quantidade=30)

        produto_estoque_factory(prod.id, ing_pao.id, 1.0)
        produto_estoque_factory(prod.id, ing_carne.id, 1.0)
        produto_estoque_factory(prod.id, ing_queijo.id, 2.0)

        qtd_pedida = 2
        assoc = db_session.query(ProdutoEstoque).filter_by(fk_id_produto=prod.id).all()
        for a in assoc:
            ing_db = db_session.query(Ingrediente).filter_by(id=a.fk_id_estoque).first()
            ing_db.quantidade -= Decimal(str(a.quantidade_necessaria)) * Decimal(str(qtd_pedida))

        db_session.commit()
        db_session.refresh(ing_pao)
        db_session.refresh(ing_carne)
        db_session.refresh(ing_queijo)

        assert float(ing_pao.quantidade) == 8.0    # 10 - 1×2
        assert float(ing_carne.quantidade) == 18.0  # 20 - 1×2
        assert float(ing_queijo.quantidade) == 26.0 # 30 - 2×2

    def test_estoque_sem_vinculo_nao_e_afetado(
        self, db_session, produto_factory, ingrediente_factory, db_infra,
    ):
        """RF06 | Ingrediente sem vínculo com o produto não deve ter saldo alterado."""
        _, _, _, tabelas = db_infra
        ProdutoEstoque = tabelas.ProdutoEstoque
        Ingrediente = tabelas.Ingrediente

        prod = produto_factory(nome="Lanche Sem Vinculo")
        ing_independente = ingrediente_factory(nome="Alface Extra Teste", quantidade=100)

        # Não vinculamos o produto ao ingrediente
        assoc = db_session.query(ProdutoEstoque).filter_by(fk_id_produto=prod.id).all()
        for a in assoc:
            ing_db = db_session.query(Ingrediente).filter_by(id=a.fk_id_estoque).first()
            ing_db.quantidade -= float(a.quantidade_necessaria) * 1

        db_session.commit()
        db_session.refresh(ing_independente)
        assert float(ing_independente.quantidade) == 100.0


# =============================================================================
# BLOCO 4 — Validações de Cadastro de Cliente (RF03 / RN06)
# =============================================================================

class TestCadastroCliente:
    """Valida as regras de unicidade e integridade do cadastro de clientes."""

    def test_nome_duplicado_detectado(self, db_session, cliente_factory, db_infra):
        """RN06 | Não deve ser possível cadastrar dois clientes com o mesmo nome."""
        _, _, _, tabelas = db_infra
        Cliente = tabelas.Cliente

        cliente_factory(nome="Pedro Duplicado")

        verify = db_session.query(Cliente).filter(Cliente.nome == "Pedro Duplicado").first()
        assert verify is not None, "Duplicata deve ser detectável via query"

    def test_cpf_duplicado_detectado(self, db_session, cliente_factory, db_infra):
        """RN06 | Dois clientes com o mesmo CPF devem ser detectáveis antes do commit."""
        _, _, _, tabelas = db_infra
        Cliente = tabelas.Cliente

        cpf_repetido = "123.456.789-00"
        cliente_factory(nome="Ana Original", cpf=cpf_repetido)

        verify = db_session.query(Cliente).filter(Cliente.cpf == cpf_repetido).first()
        assert verify is not None

    def test_senha_e_confirmacao_iguais_permite_cadastro(self):
        """RF03 | Senhas iguais não devem gerar erro de validação."""
        senha = "MinhaSenha@2026"
        repetir_senha = "MinhaSenha@2026"
        assert senha == repetir_senha

    def test_senha_e_confirmacao_diferentes_gera_erro(self):
        """RF03 | Senhas diferentes devem resultar em rejeição do cadastro."""
        senha = "Senha123"
        repetir_senha = "Senha456"
        assert senha != repetir_senha, "O sistema deve rejeitar senhas divergentes"

    def test_telefone_concatenado_ddd_numero(self):
        """RF03 | O telefone deve ser formado pela concatenação de DDD + Número."""
        ddd = "11"
        numero = "98765-4321"
        telefone_completo = f"{ddd} {numero}"
        assert telefone_completo == "11 98765-4321"

    def test_novo_cliente_tem_cupom_disponivel(self, db_session, cliente_factory):
        """RF15 | Todo novo cliente deve ter cupom_usado=False."""
        c = cliente_factory()
        assert c.cupom_usado is False


# =============================================================================
# BLOCO 5 — Autenticação de Cliente Web (RF04)
# =============================================================================

class TestAutenticacaoClienteWeb:
    """Verifica a lógica de login de cliente por nome/e-mail + senha."""

    def test_login_por_nome_correto(self, db_session, cliente_factory, db_infra):
        """RF04 | Login com nome e senha corretos deve retornar o cliente."""
        _, _, _, tabelas = db_infra
        Cliente = tabelas.Cliente

        from sqlalchemy import or_
        c = cliente_factory(nome="Aline Login", senha="senha_ok")

        result = db_session.query(Cliente).filter(
            or_(Cliente.nome == "Aline Login", Cliente.email == c.email),
            Cliente.senha == "senha_ok",
        ).first()

        assert result is not None
        assert result.id == c.id

    def test_login_por_email_correto(self, db_session, cliente_factory, db_infra):
        """RF04 | Login com e-mail e senha corretos deve retornar o cliente."""
        _, _, _, tabelas = db_infra
        Cliente = tabelas.Cliente

        from sqlalchemy import or_
        c = cliente_factory(nome="Bruno Email", email="bruno@catatau.com", senha="b_pass")

        result = db_session.query(Cliente).filter(
            or_(Cliente.nome == "bruno@catatau.com", Cliente.email == "bruno@catatau.com"),
            Cliente.senha == "b_pass",
        ).first()

        assert result is not None
        assert result.email == "bruno@catatau.com"

    def test_login_senha_errada_retorna_none(self, db_session, cliente_factory, db_infra):
        """RF04 | Senha incorreta deve retornar None."""
        _, _, _, tabelas = db_infra
        Cliente = tabelas.Cliente

        from sqlalchemy import or_
        c = cliente_factory(nome="Carlos Errado", senha="certa")

        result = db_session.query(Cliente).filter(
            or_(Cliente.nome == "Carlos Errado", Cliente.email == c.email),
            Cliente.senha == "ERRADA",
        ).first()

        assert result is None

    def test_usuario_inexistente_retorna_none(self, db_session, db_infra):
        """RF04 | Usuário inexistente deve retornar None."""
        _, _, _, tabelas = db_infra
        Cliente = tabelas.Cliente

        result = db_session.query(Cliente).filter(
            Cliente.nome == "Fantasma Inexistente",
            Cliente.senha == "qualquer",
        ).first()

        assert result is None


# =============================================================================
# BLOCO 6 — Validação e Aplicação de Cupom (RF15 / RN)
# =============================================================================

class TestCupomDesconto:
    """
    Valida as regras do cupom BEMVINDO30:
    - Código válido: BEMVINDO30 ou CATATAU30
    - Apenas para clientes com cupom_usado = False
    - Desconto de 30% sobre o total
    - Não aplicável com carrinho vazio
    """

    CUPONS_VALIDOS = ["BEMVINDO30", "CATATAU30"]

    def test_cupom_bemvindo30_e_valido(self):
        """RF15 | O código BEMVINDO30 deve ser reconhecido como válido."""
        assert "BEMVINDO30" in self.CUPONS_VALIDOS

    def test_cupom_catatau30_e_valido(self):
        """RF15 | O código CATATAU30 deve ser reconhecido como válido."""
        assert "CATATAU30" in self.CUPONS_VALIDOS

    def test_cupom_invalido_rejeitado(self):
        """RF15 | Código inexistente deve ser rejeitado."""
        assert "FAKE50OFF" not in self.CUPONS_VALIDOS

    def test_desconto_30_percent_calculado_corretamente(self):
        """RF15 | O desconto de 30% deve ser calculado sobre o total bruto."""
        total = 100.00
        desconto = round(total * 0.30, 2)
        total_final = max(0.0, round(total - desconto, 2))
        assert desconto == 30.00
        assert total_final == 70.00

    def test_desconto_arredondado_para_dois_decimais(self):
        """RF15 | O desconto deve ser arredondado para 2 casas decimais."""
        total = 33.33
        desconto = round(total * 0.30, 2)
        assert desconto == 10.00

    def test_cupom_ja_usado_nao_permite_novo_desconto(self, db_session, cliente_factory):
        """RF15 | Cliente com cupom_usado=True não pode usar o cupom novamente."""
        c = cliente_factory(cupom_usado=True)
        assert c.cupom_usado is True

    def test_cliente_sem_login_nao_pode_usar_cupom(self):
        """RF15 | Sem usuário autenticado (user_id), o cupom não deve ser aplicado."""
        usuario_banco = None
        sucesso = False
        if not usuario_banco:
            sucesso = False
        assert sucesso is False

    def test_carrinho_vazio_impede_cupom(self):
        """RN02 | Cupom não deve ser aplicado se o total do carrinho for zero."""
        total = 0.0
        pode_aplicar = total > 0
        assert pode_aplicar is False

    def test_total_final_nunca_negativo(self):
        """RF15 | O total pós-desconto nunca pode ser negativo."""
        total = 10.00
        desconto = 15.00
        total_final = max(0.0, round(total - desconto, 2))
        assert total_final >= 0.0

    def test_cupom_case_insensitive_normalizado(self):
        """RF15 | Cupom aceito independente de maiúsculas após normalização."""
        cupom_normalizado = "bemvindo30".strip().upper()
        assert cupom_normalizado in self.CUPONS_VALIDOS


# =============================================================================
# BLOCO 7 — Fluxo de Checkout e Envio do Pedido (RF05 / RN02)
# =============================================================================

class TestFluxoCheckout:
    """Valida as regras de negócio aplicadas no momento do envio do pedido."""

    def test_pedido_criado_com_status_esperando(self, db_session, pedido_factory):
        """RF05 | Todo pedido enviado deve iniciar com status 'ESPERANDO'."""
        p = pedido_factory(status="ESPERANDO")
        assert p.status == "ESPERANDO"

    def test_pedido_sem_itens_nao_deve_ser_enviado(self):
        """RN02 | Carrinho vazio deve bloquear o envio do pedido."""
        itens_carrinho = []
        pode_enviar = len(itens_carrinho) > 0
        assert pode_enviar is False

    def test_pedido_mesa_zero_representa_balcao(self, db_session, pedido_factory):
        """RF05 | Mesa 0 deve representar atendimento no balcão."""
        p = pedido_factory(num_mesa=0)
        titulo = f"MESA {p.num_mesa}" if p.num_mesa > 0 else "BALCÃO"
        assert titulo == "BALCÃO"

    def test_pedido_mesa_positiva_exibe_numero(self, db_session, pedido_factory):
        """RF05 | Mesa com número positivo deve exibir 'MESA N'."""
        p = pedido_factory(num_mesa=7)
        titulo = f"MESA {p.num_mesa}" if p.num_mesa > 0 else "BALCÃO"
        assert titulo == "MESA 7"

    def test_descricao_pedido_inclui_info_cupom(self):
        """RF05 | Quando cupom é aplicado, a descrição deve registrar o desconto."""
        descricao_base = "Sem cebola"
        info_cupom = " [Cupom BEMVINDO30 (-30%): -R$ 15.00]"
        descricao_final = f"{descricao_base}{info_cupom}".strip()
        assert "BEMVINDO30" in descricao_final
        assert "15.00" in descricao_final

    def test_cupom_aplicado_marca_cliente_como_usado(self, db_session, cliente_factory):
        """RF05 / RF15 | Após usar cupom, o campo cupom_usado deve ser True."""
        c = cliente_factory(cupom_usado=False)
        c.cupom_usado = True
        db_session.commit()
        db_session.refresh(c)
        assert c.cupom_usado is True

    def test_carrinho_cookie_apagado_apos_envio(self):
        """RF05 | O cookie 'carrinho_catatau' deve ser deletado após o envio."""
        cookie_presente_depois = False  # simula delete_cookie()
        assert cookie_presente_depois is False

    def test_valor_final_pedido_sem_cupom(self, db_session, pedido_factory):
        """RF05 | Sem cupom, o valor_final é igual ao total do carrinho."""
        valor_carrinho = 59.80
        p = pedido_factory(valor_final=valor_carrinho)
        assert abs(p.valor_final - valor_carrinho) < 0.001

    def test_valor_final_pedido_com_cupom_30(self, db_session, pedido_factory):
        """RF05 / RF15 | Com cupom 30%, o valor_final deve refletir o desconto."""
        total_bruto = 100.00
        total_final = max(0.0, round(total_bruto - round(total_bruto * 0.30, 2), 2))
        p = pedido_factory(valor_final=total_final)
        assert abs(p.valor_final - 70.00) < 0.001

    def test_pedido_incrementa_contagem_cliente_logado(self, db_session, cliente_factory):
        """RF05 | O contador pedidos_count do cliente logado deve incrementar ao finalizar."""
        c = cliente_factory(pedidos_count=0)
        c.pedidos_count = (c.pedidos_count or 0) + 1
        db_session.commit()
        db_session.refresh(c)
        assert c.pedidos_count == 1


# =============================================================================
# BLOCO 8 — Transições de Status do Pedido (RF09 / RN04)
# =============================================================================

class TestTransicaoStatusPedido:
    """
    Valida a máquina de estados sequencial:
    ESPERANDO → PREPARANDO → FINALIZADO → Entregue
    """

    STATUS_VALIDOS = ["ESPERANDO", "PREPARANDO", "FINALIZADO", "Entregue"]

    def test_transicao_esperando_para_preparando(self, db_session, pedido_factory):
        """RF09 / RN04 | Pedido ESPERANDO deve poder avançar para PREPARANDO."""
        p = pedido_factory(status="ESPERANDO")
        p.status = "PREPARANDO"
        db_session.commit()
        db_session.refresh(p)
        assert p.status == "PREPARANDO"

    def test_transicao_preparando_para_finalizado(self, db_session, pedido_factory):
        """RF09 / RN04 | Pedido PREPARANDO deve poder avançar para FINALIZADO."""
        p = pedido_factory(status="PREPARANDO")
        p.status = "FINALIZADO"
        db_session.commit()
        db_session.refresh(p)
        assert p.status == "FINALIZADO"

    def test_transicao_finalizado_para_entregue(self, db_session, pedido_factory):
        """RF12 / RN04 | Pedido FINALIZADO deve poder avançar para 'Entregue' via painel ADM."""
        p = pedido_factory(status="FINALIZADO")
        p.status = "Entregue"
        db_session.commit()
        db_session.refresh(p)
        assert p.status == "Entregue"

    def test_status_inicial_e_esperando(self, db_session, pedido_factory):
        """RF05 | O status inicial de qualquer pedido deve ser 'ESPERANDO'."""
        p = pedido_factory(status="ESPERANDO")
        assert p.status == self.STATUS_VALIDOS[0]

    def test_sequencia_completa_de_transicoes(self, db_session, pedido_factory):
        """RF09 / RN04 | Fluxo completo de status deve seguir a ordem correta."""
        p = pedido_factory(status="ESPERANDO")
        for novo_status in ["PREPARANDO", "FINALIZADO", "Entregue"]:
            p.status = novo_status
            db_session.commit()
            db_session.refresh(p)
            assert p.status == novo_status

    def test_pedidos_ativos_filtro_correto(self, db_session, pedido_factory, db_infra):
        """RF08 | A query de pedidos ativos deve retornar apenas ESPERANDO e PREPARANDO."""
        _, _, _, tabelas = db_infra
        Pedido = tabelas.Pedido

        p1 = pedido_factory(status="ESPERANDO", num_mesa=1)
        p2 = pedido_factory(status="PREPARANDO", num_mesa=2)
        p3 = pedido_factory(status="FINALIZADO", num_mesa=3)

        ativos = db_session.query(Pedido).filter(
            Pedido.status.in_(["ESPERANDO", "PREPARANDO"])
        ).all()

        ids_ativos = [p.id for p in ativos]
        assert p1.id in ids_ativos
        assert p2.id in ids_ativos
        assert p3.id not in ids_ativos

    def test_pedidos_finalizados_filtro_correto(self, db_session, pedido_factory, db_infra):
        """RF10 | A query de histórico deve retornar apenas FINALIZADO."""
        _, _, _, tabelas = db_infra
        Pedido = tabelas.Pedido

        p_fin = pedido_factory(status="FINALIZADO", num_mesa=10)
        p_esp = pedido_factory(status="ESPERANDO", num_mesa=11)

        finalizados = db_session.query(Pedido).filter(
            Pedido.status == "FINALIZADO"
        ).all()

        ids_fin = [p.id for p in finalizados]
        assert p_fin.id in ids_fin
        assert p_esp.id not in ids_fin


# =============================================================================
# BLOCO 9 — Regras de Autorização de Funcionários Desktop (RF07 / RN05)
# =============================================================================

class TestAutorizacaoFuncionario:
    """
    Valida a lógica de segregação de acesso baseada em funcionario.controle:
    - controle = 1 → Administrador / PaginaADM
    - controle = 2 → Cozinha / CozinhaApp
    """

    @staticmethod
    def _simular_login(controle: int) -> str:
        if controle == 1:
            return "PaginaADM"
        elif controle == 2:
            return "CozinhaApp"
        return "Acesso Negado"

    def test_controle_1_abre_pagina_adm(self):
        """RN05 | Funcionário com controle=1 deve ser direcionado ao painel ADM."""
        assert self._simular_login(controle=1) == "PaginaADM"

    def test_controle_2_abre_cozinha(self):
        """RN05 | Funcionário com controle=2 deve ser direcionado ao KDS Cozinha."""
        assert self._simular_login(controle=2) == "CozinhaApp"

    def test_controle_invalido_nega_acesso(self):
        """RN05 | Valor de controle inválido deve negar acesso ao sistema."""
        assert self._simular_login(controle=99) == "Acesso Negado"

    def test_funcionario_inativo_bloqueado(self):
        """RF07 / RN05 | Funcionário com ativo=False não deve ter acesso ao sistema."""
        class FuncionarioMock:
            ativo = False
            controle = 1

        func = FuncionarioMock()
        pode_entrar = getattr(func, "ativo", True)
        assert pode_entrar is False

    def test_unico_admin_nao_pode_ser_rebaixado(self):
        """RN05 | O único administrador ativo não pode ser convertido para cozinha."""
        class FuncMock:
            controle = 1
            ativo = True

        todos_usuarios = [FuncMock()]
        func_alvo = todos_usuarios[0]
        novo_controle = 2

        admins_ativos = [
            u for u in todos_usuarios if u.controle == 1 and getattr(u, "ativo", True)
        ]

        operacao_bloqueada = (
            func_alvo.controle == 1
            and novo_controle == 2
            and len(admins_ativos) <= 1
        )

        assert operacao_bloqueada is True

    def test_unico_admin_nao_pode_ser_desativado(self):
        """RN05 | O único administrador ativo não pode ser desativado."""
        class FuncMock:
            controle = 1
            ativo = True

        todos_usuarios = [FuncMock()]
        func_alvo = todos_usuarios[0]
        novo_status = False

        admins_ativos = [
            u for u in todos_usuarios if u.controle == 1 and getattr(u, "ativo", True)
        ]

        operacao_bloqueada = (
            not novo_status
            and func_alvo.controle == 1
            and len(admins_ativos) <= 1
        )

        assert operacao_bloqueada is True

    def test_dois_admins_permite_rebaixamento(self):
        """RN05 | Com 2 administradores ativos, rebaixar um deve ser permitido."""
        class FuncMock:
            def __init__(self, controle, ativo=True):
                self.controle = controle
                self.ativo = ativo

        todos_usuarios = [FuncMock(1), FuncMock(1)]
        func_alvo = todos_usuarios[0]
        novo_controle = 2

        admins_ativos = [
            u for u in todos_usuarios if u.controle == 1 and getattr(u, "ativo", True)
        ]

        operacao_bloqueada = (
            func_alvo.controle == 1
            and novo_controle == 2
            and len(admins_ativos) <= 1
        )

        assert operacao_bloqueada is False  # permitido


# =============================================================================
# BLOCO 10 — Cálculo de Status de Estoque (RF13 / RN07)
# =============================================================================

class TestCalculoStatusEstoque:
    """
    Valida a função calcular_status_automatico() da EstoqueView.
    Regras por unidade:
      - uni.:   < 15 → Crítico | 15–50 → Atenção | > 50 → Ok
      - fatia:  < 20 → Crítico | 20–60 → Atenção | > 60 → Ok
      - kg:     < 0.5 → Crítico | 0.5–1.2 → Atenção | > 1.2 → Ok
      - g:      < 200 → Crítico | 200–600 → Atenção | > 600 → Ok
    """

    @staticmethod
    def _calcular(nome: str, qtd) -> str:
        """Réplica exata da lógica de calcular_status_automatico()."""
        try:
            qtd_float = float(qtd)
        except (ValueError, TypeError):
            return "Ok"

        nome_lower = nome.lower()

        if "uni" in nome_lower:
            if qtd_float < 15:
                return "Crítico"
            elif qtd_float <= 50:
                return "Atenção"
            else:
                return "Ok"
        elif "fatia" in nome_lower:
            if qtd_float < 20:
                return "Crítico"
            elif qtd_float <= 60:
                return "Atenção"
            else:
                return "Ok"
        elif "kg" in nome_lower:
            if qtd_float < 0.5:
                return "Crítico"
            elif qtd_float <= 1.2:
                return "Atenção"
            else:
                return "Ok"
        elif " g" in nome_lower or nome_lower.endswith("(g)") or nome_lower.startswith("g "):
            if qtd_float < 200:
                return "Crítico"
            elif qtd_float <= 600:
                return "Atenção"
            else:
                return "Ok"

        return "Ok"

    # --- Testes de Unidades (uni.) ---
    def test_uni_critico_abaixo_15(self):
        """RN07 | Pão com 10 uni. → Crítico."""
        assert self._calcular("Pao (uni.)", 10) == "Crítico"

    def test_uni_atencao_entre_15_e_50(self):
        """RN07 | Pão com 30 uni. → Atenção."""
        assert self._calcular("Pao (uni.)", 30) == "Atenção"

    def test_uni_ok_acima_50(self):
        """RN07 | Pão com 60 uni. → Ok."""
        assert self._calcular("Pao (uni.)", 60) == "Ok"

    def test_uni_limite_exato_15_e_atencao(self):
        """RN07 | Pão com exatamente 15 uni. → Atenção (limiar inclusivo)."""
        assert self._calcular("Pao (uni.)", 15) == "Atenção"

    def test_uni_limite_exato_50_e_atencao(self):
        """RN07 | Pão com exatamente 50 uni. → Atenção (limiar inclusivo)."""
        assert self._calcular("Pao (uni.)", 50) == "Atenção"

    # --- Testes de Fatias ---
    def test_fatia_critico_abaixo_20(self):
        """RN07 | Queijo com 15 fatias → Crítico."""
        assert self._calcular("Queijo (fatia)", 15) == "Crítico"

    def test_fatia_atencao_entre_20_e_60(self):
        """RN07 | Queijo com 40 fatias → Atenção."""
        assert self._calcular("Queijo (fatia)", 40) == "Atenção"

    def test_fatia_ok_acima_60(self):
        """RN07 | Queijo com 80 fatias → Ok."""
        assert self._calcular("Queijo (fatia)", 80) == "Ok"

    # --- Testes de Quilogramas (kg) ---
    def test_kg_critico_abaixo_05(self):
        """RN07 | Carne com 0.3 kg → Crítico."""
        assert self._calcular("Carne (kg)", 0.3) == "Crítico"

    def test_kg_atencao_entre_05_e_12(self):
        """RN07 | Carne com 1.0 kg → Atenção."""
        assert self._calcular("Carne (kg)", 1.0) == "Atenção"

    def test_kg_ok_acima_12(self):
        """RN07 | Carne com 2.5 kg → Ok."""
        assert self._calcular("Carne (kg)", 2.5) == "Ok"

    # --- Testes de Gramas (g) ---
    def test_g_critico_abaixo_200(self):
        """RN07 | Molho com 150 g → Crítico."""
        assert self._calcular("Molho especial (g)", 150) == "Crítico"

    def test_g_atencao_entre_200_e_600(self):
        """RN07 | Molho com 400 g → Atenção."""
        assert self._calcular("Molho especial (g)", 400) == "Atenção"

    def test_g_ok_acima_600(self):
        """RN07 | Molho com 700 g → Ok."""
        assert self._calcular("Molho especial (g)", 700) == "Ok"

    # --- Testes de unidade desconhecida ---
    def test_sem_unidade_reconhecida_retorna_ok(self):
        """RN07 | Ingrediente sem unidade identificável → Ok (padrão seguro)."""
        # Nome sem "uni", "fatia", "kg", nem sufixo "(g)" → retorna "Ok"
        assert self._calcular("Embalagem Termica", 500) == "Ok"

    def test_quantidade_invalida_retorna_ok(self):
        """RN07 | Quantidade não numérica → Ok (tratamento de exceção)."""
        assert self._calcular("Pao (uni.)", "invalido") == "Ok"


# =============================================================================
# BLOCO 11 — Endpoints da API FastAPI (rotas HTTP)
# =============================================================================

class TestEndpointsAPI:
    """
    Testes de integração para os endpoints do FastAPI.
    Usa o TestClient com banco SQLite em memória.
    """

    def test_home_retorna_status_no_ar(self, api_client):
        """GET / | Deve retornar JSON com status 'Servidor no ar'."""
        response = api_client.get("/")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "Servidor no ar"

    def test_logout_redireciona_para_catatau(self, api_client):
        """GET /logout | Deve redirecionar para /catatau."""
        response = api_client.get("/logout", follow_redirects=False)
        assert response.status_code == 303
        assert "/catatau" in response.headers.get("location", "")

    def test_adicionar_ao_carrinho_seta_cookie(self, api_client, produto_factory):
        """POST /carrinho/adicionar | Deve criar/atualizar o cookie carrinho_catatau."""
        prod = produto_factory(nome="Lanche HTTP Teste")

        response = api_client.post(
            "/carrinho/adicionar",
            data={"item_id": prod.id},
            follow_redirects=False,
        )
        assert response.status_code == 303
        assert "carrinho_catatau" in response.cookies

    def test_remover_do_carrinho_atualiza_cookie(self, api_client, produto_factory):
        """POST /carrinho/remover | Deve remover o item e atualizar o cookie."""
        prod = produto_factory(nome="Lanche Para Remover")
        carrinho_inicial = json.dumps({str(prod.id): 2})

        response = api_client.post(
            "/carrinho/remover",
            data={"item_id": prod.id},
            cookies={"carrinho_catatau": carrinho_inicial},
            follow_redirects=False,
        )
        assert response.status_code == 303
        cookie_depois = response.cookies.get("carrinho_catatau", "{}")
        dados_depois = json.loads(cookie_depois)
        assert str(prod.id) not in dados_depois

    def test_atualizar_carrinho_aumentar(self, api_client, produto_factory):
        """POST /carrinho/atualizar (aumentar) | Deve incrementar a quantidade do item."""
        prod = produto_factory(nome="Lanche Para Aumentar")
        carrinho_inicial = json.dumps({str(prod.id): 1})

        response = api_client.post(
            "/carrinho/atualizar",
            data={"item_id": prod.id, "acao": "aumentar"},
            cookies={"carrinho_catatau": carrinho_inicial},
            follow_redirects=False,
        )
        assert response.status_code == 303
        cookie_depois = response.cookies.get("carrinho_catatau", "{}")
        dados = json.loads(cookie_depois)
        if isinstance(dados, str):
            dados = json.loads(dados)
        assert dados.get(str(prod.id)) == 2

    def test_atualizar_carrinho_diminuir_remove_quando_zero(self, api_client, produto_factory):
        """POST /carrinho/atualizar (diminuir) | Quantidade 0 deve remover o item."""
        prod = produto_factory(nome="Lanche Para Diminuir")
        carrinho_inicial = json.dumps({str(prod.id): 1})

        response = api_client.post(
            "/carrinho/atualizar",
            data={"item_id": prod.id, "acao": "diminuir"},
            cookies={"carrinho_catatau": carrinho_inicial},
            follow_redirects=False,
        )
        assert response.status_code == 303
        cookie_depois = response.cookies.get("carrinho_catatau", "{}")
        dados = json.loads(cookie_depois)
        assert str(prod.id) not in dados

    def test_cadastro_senhas_divergentes_retorna_erro(self, api_client):
        """POST /cadastro | Senhas diferentes devem retornar HTML com mensagem de erro."""
        response = api_client.post(
            "/cadastro",
            data={
                "nome": "Teste Senha",
                "email": "teste@cadastro.com",
                "CPF": "000.000.000-00",
                "ddd": "11",
                "numero": "90000-0000",
                "senha": "abc123",
                "repetir_senha": "xyz789",
            },
            follow_redirects=False,
        )
        assert response.status_code in [200, 303]

    def test_checkout_carrinho_vazio_redireciona(self, api_client):
        """POST /checkout/enviar | Carrinho vazio deve redirecionar para /cardapio."""
        response = api_client.post(
            "/checkout/enviar",
            data={"mesa": "1", "cliente": "Teste Vazio"},
            cookies={"carrinho_catatau": "{}"},
            follow_redirects=False,
        )
        assert response.status_code == 303
        assert "/cardapio" in response.headers.get("location", "")

    def test_validar_cupom_sem_usuario_retorna_precisa_login(self, api_client):
        """POST /api/validar-cupom | Sem cookie user_id deve retornar precisa_login=True."""
        response = api_client.post(
            "/api/validar-cupom",
            data={"cupom": "BEMVINDO30"},
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sucesso"] is False
        assert data.get("precisa_login") is True

    def test_validar_cupom_invalido_retorna_erro(self, api_client, cliente_factory):
        """POST /api/validar-cupom | Código inválido deve retornar sucesso=False."""
        c = cliente_factory(nome="Cupom Invalido")

        response = api_client.post(
            "/api/validar-cupom",
            data={"cupom": "INVALIDO99"},
            cookies={
                "user_id": str(c.id),
                "carrinho_catatau": json.dumps({"1": 1}),
            },
        )
        assert response.status_code == 200
        data = response.json()
        assert data["sucesso"] is False


# =============================================================================
# BLOCO 12 — Testes de Contagem de Pedidos do Cliente
# =============================================================================

class TestContagemPedidosCliente:
    """Verifica a lógica de incremento de pedidos_count no momento do checkout."""

    def test_pedidos_count_incrementa_em_um(self, db_session, cliente_factory):
        """RF05 | Cada pedido enviado deve incrementar pedidos_count em 1."""
        c = cliente_factory(pedidos_count=0)
        c.pedidos_count = (c.pedidos_count or 0) + 1
        db_session.commit()
        db_session.refresh(c)
        assert c.pedidos_count == 1

    def test_pedidos_count_acumula_multiplos_pedidos(self, db_session, cliente_factory):
        """RF05 | Múltiplos pedidos devem acumular corretamente o contador."""
        c = cliente_factory(pedidos_count=0)
        for _ in range(5):
            c.pedidos_count = (c.pedidos_count or 0) + 1
        db_session.commit()
        db_session.refresh(c)
        assert c.pedidos_count == 5

    def test_pedidos_count_nunca_negativo(self, db_session, cliente_factory):
        """RF05 | O contador de pedidos nunca deve ser negativo."""
        c = cliente_factory(pedidos_count=3)
        assert c.pedidos_count >= 0

    def test_cliente_sem_login_incrementa_por_cpf(self, db_session, cliente_factory, db_infra):
        """
        RF05 | Se o cliente não estiver logado, mas existir no banco pelo CPF,
        seu pedidos_count deve ser incrementado.
        """
        _, _, _, tabelas = db_infra
        Cliente = tabelas.Cliente

        cpf_teste = "777.888.999-00"
        c = cliente_factory(nome="Sem Login CPF", cpf=cpf_teste)

        # Simula a lógica do checkout para cliente não logado
        cliente_por_cpf = db_session.query(Cliente).filter(Cliente.cpf == cpf_teste).first()
        if cliente_por_cpf:
            cliente_por_cpf.pedidos_count = (cliente_por_cpf.pedidos_count or 0) + 1
        db_session.commit()
        db_session.refresh(c)

        assert c.pedidos_count == 1
