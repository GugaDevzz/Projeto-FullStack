# =============================================================================
# tests/conftest.py — Fixtures globais do Catatau Lanches (Pytest)
# =============================================================================
# A suíte usa APENAS banco em memória (SQLite) por TESTE, garantindo
# isolamento total sem depender do SQL Server de produção.
# =============================================================================

import json
import sys
import types
import pathlib
import importlib.util

import pytest
from sqlalchemy import create_engine
from sqlalchemy.pool import StaticPool
from sqlalchemy.orm import sessionmaker, declarative_base

ROOT = pathlib.Path(__file__).resolve().parent.parent
API_SRC = ROOT / "src" / "API"


# ---------------------------------------------------------------------------
# Garante que API_SRC está no sys.path (uma única vez)
# ---------------------------------------------------------------------------
if str(API_SRC) not in sys.path:
    sys.path.insert(0, str(API_SRC))


# ---------------------------------------------------------------------------
# Carrega database.Tabelas usando um Base externo já criado
# ---------------------------------------------------------------------------
def _load_tabelas(base_obj):
    """
    Carrega database.Tabelas.py substituindo o `Base` pelo base_obj recebido.
    Cada chamada recria os modelos vinculados ao Base correto.
    """
    fake_banco = types.ModuleType("database.Banco")
    fake_banco.Base = base_obj

    pkg = types.ModuleType("database")
    sys.modules["database"] = pkg
    sys.modules["database.Banco"] = fake_banco

    spec = importlib.util.spec_from_file_location(
        "database.Tabelas",
        API_SRC / "database" / "Tabelas.py",
    )
    mod = importlib.util.module_from_spec(spec)
    sys.modules["database.Tabelas"] = mod
    spec.loader.exec_module(mod)
    return mod


# ---------------------------------------------------------------------------
# Fixture por TESTE — engine + sessão totalmente novos a cada test function
# ---------------------------------------------------------------------------
@pytest.fixture()
def db_infra():
    """
    Cria um engine SQLite in-memory, Base e SessionLocal NOVOS para cada teste,
    garantindo isolamento total de dados entre testes.
    Devolve (engine, SessionLocal, Base, tabelas_mod).
    """
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
        echo=False,
    )
    Base = declarative_base()
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    tabelas_mod = _load_tabelas(Base)
    Base.metadata.create_all(bind=engine)

    yield engine, SessionLocal, Base, tabelas_mod

    Base.metadata.drop_all(bind=engine)
    engine.dispose()


@pytest.fixture()
def db_session(db_infra):
    """
    Sessão SQLAlchemy limpa para cada teste.
    Faz rollback se o teste não fez commit, fecha em seguida.
    """
    engine, SessionLocal, Base, _ = db_infra
    session = SessionLocal()
    try:
        yield session
    finally:
        session.close()


# ---------------------------------------------------------------------------
# Fixture do FastAPI TestClient
# ---------------------------------------------------------------------------
@pytest.fixture()
def api_client(db_infra):
    """
    TestClient do FastAPI com banco SQLite in-memory isolado por teste.
    Injeta módulos falsos e sobrescreve a dependência get_db.
    """
    from starlette.testclient import TestClient

    engine, SessionLocal, Base, tabelas_mod = db_infra

    # Injeta módulos falsos para o app poder importar
    fake_banco = types.ModuleType("database.Banco")
    fake_banco.Base = Base
    fake_banco.engine = engine
    fake_banco.SessionLocal = SessionLocal

    def get_db_test():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    fake_banco.get_db = get_db_test
    pkg = types.ModuleType("database")
    sys.modules["database"] = pkg
    sys.modules["database.Banco"] = fake_banco

    import os
    orig_cwd = os.getcwd()
    os.chdir(API_SRC)

    try:
        spec = importlib.util.spec_from_file_location(
            "_api_main_test",
            API_SRC / "main.py",
        )
        api_main = importlib.util.module_from_spec(spec)
        sys.modules["_api_main_test"] = api_main
        spec.loader.exec_module(api_main)

        app = api_main.app

        # Sobrescreve dependência get_db
        from database.Banco import get_db as orig_get_db
        app.dependency_overrides[orig_get_db] = get_db_test

        with TestClient(app, raise_server_exceptions=True) as client:
            yield client

        app.dependency_overrides.clear()
    finally:
        os.chdir(orig_cwd)


# ---------------------------------------------------------------------------
# Factories reutilizáveis
# ---------------------------------------------------------------------------
@pytest.fixture()
def cliente_factory(db_session, db_infra):
    _, _, _, tabelas = db_infra
    Cliente = tabelas.Cliente

    _counter = [0]

    def _criar(
        nome=None,
        email=None,
        cpf=None,
        telefone=None,
        senha="senha123",
        cupom_usado=False,
        pedidos_count=0,
    ):
        _counter[0] += 1
        n = _counter[0]
        c = Cliente(
            nome=nome or f"Cliente Teste {n}",
            email=email or f"cliente{n}@catatau.com",
            cpf=cpf or f"000.000.{n:03d}-00",
            telefone=telefone or f"11 9{n:04d}-{n:04d}",
            senha=senha,
            cupom_usado=cupom_usado,
            pedidos_count=pedidos_count,
        )
        db_session.add(c)
        db_session.commit()
        db_session.refresh(c)
        return c

    return _criar


@pytest.fixture()
def produto_factory(db_session, db_infra):
    _, _, _, tabelas = db_infra
    Produto = tabelas.Produto

    _counter = [0]

    def _criar(nome=None, descricao="Descrição do teste", valor=25.90):
        _counter[0] += 1
        p = Produto(
            nome=nome or f"Produto Teste {_counter[0]}",
            descricao=descricao,
            valor=valor,
        )
        db_session.add(p)
        db_session.commit()
        db_session.refresh(p)
        return p

    return _criar


@pytest.fixture()
def ingrediente_factory(db_session, db_infra):
    _, _, _, tabelas = db_infra
    Ingrediente = tabelas.Ingrediente

    _counter = [0]

    def _criar(nome=None, unidade_medida="uni", quantidade=50, status="Ok"):
        _counter[0] += 1
        i = Ingrediente(
            nome=nome or f"Ingrediente Teste {_counter[0]}",
            unidade_medida=unidade_medida,
            quantidade=quantidade,
            status=status,
        )
        db_session.add(i)
        db_session.commit()
        db_session.refresh(i)
        return i

    return _criar


@pytest.fixture()
def produto_estoque_factory(db_session, db_infra):
    _, _, _, tabelas = db_infra
    ProdutoEstoque = tabelas.ProdutoEstoque

    def _criar(produto_id: int, ingrediente_id: int, quantidade_necessaria: float = 1.0):
        pe = ProdutoEstoque(
            fk_id_produto=produto_id,
            fk_id_estoque=ingrediente_id,
            quantidade_necessaria=quantidade_necessaria,
        )
        db_session.add(pe)
        db_session.commit()
        db_session.refresh(pe)
        return pe

    return _criar


@pytest.fixture()
def pedido_factory(db_session, db_infra):
    _, _, _, tabelas = db_infra
    Pedido = tabelas.Pedido

    def _criar(
        nome_cliente="Cliente Teste",
        num_mesa=5,
        status="ESPERANDO",
        valor_final=25.90,
        descricao=None,
    ):
        p = Pedido(
            nome_cliente=nome_cliente,
            num_mesa=num_mesa,
            status=status,
            valor_final=valor_final,
            descricao=descricao,
        )
        db_session.add(p)
        db_session.commit()
        db_session.refresh(p)
        return p

    return _criar


@pytest.fixture()
def carrinho_cookie():
    def _build(itens: dict) -> str:
        return json.dumps({str(k): v for k, v in itens.items()})
    return _build
