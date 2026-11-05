# Projeto Integrador: Catatau Lanches 🍔

> **Language / Idioma:** [🇧🇷 Português](#-português) | [🇺🇸 English](#-english)

---

## 🇧🇷 Português

### Sistema Integrado Full-Stack de Autoatendimento, Gestão de Linha de Produção (KDS) e Retaguarda Administrativa para Hamburguerias

---

### 📌 Visão Geral do Sistema

O projeto **Catatau Lanches** é uma solução completa desenvolvida para automatizar e integrar o fluxo operacional de uma lanchonete em três pontas estratégicas:

1. **Autoatendimento Web (Salão / Mesas):**
   * Desenvolvido em **FastAPI** + **Jinja2** + **HTML5/CSS3**.
   * Cardápio interativo e responsivo (adaptado para smartphones dos clientes na mesa).
   * Carrinho de compras dinâmico persistido via cookies seguros.
   * Cadastro e autenticação de clientes com histórico de compras.
   * Envio direto da comanda para a cozinha com número da mesa e observações de preparo.
   * **Baixa automática de insumos:** ao confirmar o pedido, o sistema abate os ingredientes correspondentes na tabela de estoque.

2. **Terminal de Cozinha - KDS (Kitchen Display System):**
   * Interface Desktop em **CustomTkinter**.
   * Exibição visual de pedidos em cards organizados por ordem cronológica.
   * Transição ágil de status da comanda: `ESPERANDO` ➔ `PREPARANDO` ➔ `FINALIZADO`.
   * Destaque para observações do cliente (ex: sem cebola, carne bem passada).
   * Histórico de pedidos finalizados com contadores de produtividade do dia.

3. **Painel de Retaguarda Administrativa (Gerência):**
   * Interface Desktop em **CustomTkinter** com segregação de permissões (`funcionario.controle`).
   * Dashboard executivo com vendas brutas do dia, ranking de produtos mais vendidos e alertas visuais de estoque crítico.
   * Gestão e auditoria global de comandas com visualização detalhada de itens e valores.
   * CRUD completo de insumos de estoque (Nome, Quantidade e Status: Ok, Atenção, Crítico).
   * Gestão de carteira de clientes cadastrados.
   * Cadastro e controle de cupons promocionais.
   * Módulo de relatórios gerenciais e fechamento de caixa.

4. **Banco de Dados Centralizado:**
   * **Microsoft SQL Server** (`(localdb)\MSSQLLocalDB` / `DBCATATAU`).
   * Camada de persistência relacional com **SQLAlchemy 2.0** e **PyODBC**.

---

### 🏗️ Estrutura do Repositório

```
Projeto-FullStack/
│
├── src/
│   ├── API/                    ← Aplicação Web (FastAPI + Jinja2)
│   │   ├── main.py             ← Endpoints, lógica de carrinho, checkout e baixa de estoque
│   │   ├── database/
│   │   │   ├── Banco.py        ← Engine SQLAlchemy → SQL Server
│   │   │   └── Tabelas.py      ← Modelos ORM da API (Cliente, Produto, Pedido…)
│   │   ├── templates/          ← Templates Jinja2 (HTML)
│   │   ├── static/             ← CSS e imagens
│   │   └── requirements.txt    ← Dependências específicas da API (mantido)
│   │
│   └── Desktop/                ← Aplicação Desktop (CustomTkinter)
│       ├── main.py             ← Ponto de entrada do app desktop
│       ├── paginas/
│       │   ├── pagina_login.py ← Autenticação com controle de acesso por nível
│       │   ├── paginaCozinha/  ← KDS: pedidos.py (cards, status, histórico)
│       │   └── paginasADM/     ← Painel ADM: dashboard, estoque, clientes, cupons, relatórios
│       ├── DB/
│       │   ├── Banco.py        ← Engine SQLAlchemy → SQL Server (desktop)
│       │   └── models.py       ← Modelos ORM do Desktop (Funcionario, Pedido, Ingredientes…)
│       └── requirements.txt    ← Dependências específicas do Desktop (mantido)
│
├── tests/
│   ├── __init__.py
│   ├── conftest.py             ← Fixtures globais Pytest (banco SQLite in-memory)
│   └── test_servico.py         ← 60+ testes cobrindo regras de negócio e endpoints
│
├── requirements.txt            ← ⭐ Requirements GLOBAL UNIFICADO (API + Desktop + Pytest)
├── pytest.ini                  ← Configuração do Pytest (pythonpath = src, cobertura)
├── DOCUMENTACAO_REQUISITOS.md  ← ERS completa (IEEE 830 / ISO/IEC/IEEE 29148)
└── README.md                   ← Este arquivo
```

---

### 📖 Documentação Completa de Requisitos

A especificação completa de Engenharia de Software (norma IEEE 830 / ISO/IEC/IEEE 29148 adaptada para Projeto Integrador acadêmico) está disponível em:

👉 **[DOCUMENTACAO_REQUISITOS.md](DOCUMENTACAO_REQUISITOS.md)**

Nela constam:
* Matriz de Requisitos Funcionais (RF01 ao RF16 com classificação MoSCoW);
* Regras de Negócio (RN01 ao RN07);
* Requisitos Não Funcionais (RNF01 ao RNF09);
* Diagrama Entidade-Relacionamento (DER em Mermaid);
* Diagramas de Máquina de Estados e Sequência da Baixa de Estoque;
* Matriz de Rastreabilidade (Requisitos x Linhas de Código);
* Recomendações e Melhorias para Banca Examinadora.

---

### 🛠️ Tecnologias Utilizadas

| Camada | Tecnologia |
|:---|:---|
| Linguagem | Python 3.10+ |
| Backend Web | FastAPI 0.141, Uvicorn, Starlette, Jinja2 |
| Desktop GUI | CustomTkinter 6.0, Pillow, Matplotlib |
| Banco de Dados & ORM | MS SQL Server LocalDB, SQLAlchemy 2.0, PyODBC |
| Frontend Web | HTML5 Semântico, CSS3 Flexbox/Grid |
| Testes | Pytest 8+, pytest-cov, httpx, SQLite in-memory |

---

### 🚀 Como Executar

#### 1. Pré-requisitos
* Python 3.10+ instalado.
* SQL Server Express ou LocalDB configurado com a base `DBCATATAU`.
* ODBC Driver 17 for SQL Server instalado.

#### 2. Instalar as Dependências (Requirements Global Unificado)

> ⭐ **Recomendado:** usar o `requirements.txt` da **raiz** do repositório para instalar tudo de uma vez (API + Desktop + Pytest).

```bash
# Na raiz do repositório
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate    # Linux/macOS

pip install -r requirements.txt
```

#### 3. Executar a Aplicação Web (FastAPI)

```bash
cd src/API
uvicorn main:app --reload --port 8000
```

Acesse no navegador: `http://localhost:8000/catatau`

Rotas principais:
| Rota | Descrição |
|:---|:---|
| `GET /catatau` | Página principal (cardápio logado) |
| `GET /cardapio` | Cardápio público |
| `GET /login` | Tela de login de clientes |
| `GET /cadastro` | Tela de cadastro |
| `GET /checkout` | Revisão do carrinho e cupom |
| `POST /checkout/enviar` | Finaliza pedido e faz baixa de estoque |
| `POST /carrinho/adicionar` | Adiciona item ao carrinho (cookie) |
| `GET /logout` | Encerra sessão do cliente |

#### 4. Executar o Módulo Desktop (Cozinha & Gerência)

```bash
cd src/Desktop
python main.py
```

* **Login de Gerência:** Usuário cadastrado com `controle = 1` → abre `PaginaADM`.
* **Login de Cozinha:** Usuário cadastrado com `controle = 2` → abre `CozinhaApp` (KDS).

---

### 🧪 Executar os Testes Automatizados (Pytest)

A suíte de testes **não requer SQL Server** — usa banco SQLite em memória via `conftest.py`.

```bash
# Na raiz do repositório (onde está o pytest.ini)
pytest
```

**Com relatório de cobertura de código:**

```bash
pytest --cov=src --cov-report=term-missing
```

**Executar apenas um bloco de testes específico:**

```bash
# Ex: apenas testes de estoque
pytest tests/test_servico.py::TestBaixaAutomaticaEstoque -v

# Ex: apenas testes de endpoints HTTP
pytest tests/test_servico.py::TestEndpointsAPI -v
```

**Executar por marcador:**

```bash
# Testes marcados como lentos (integração)
pytest -m lento
pytest -m integracao
```

#### 📊 Cobertura da Suíte de Testes

| Bloco de Testes | Regras Cobertas | Nº de Testes |
|:---|:---|:---:|
| Modelos ORM e Banco | Persistência SQLAlchemy | 7 |
| Carrinho via Cookie | RF02 — Serialização JSON | 8 |
| Baixa Automática de Estoque | RF06 / RN03 — Fórmula de baixa | 4 |
| Cadastro de Cliente | RF03 / RN06 — Unicidade | 6 |
| Autenticação Web | RF04 — Login por nome/e-mail | 4 |
| Cupom de Desconto | RF15 / RN — 30% BEMVINDO30 | 10 |
| Fluxo de Checkout | RF05 / RN02 — Envio e marcação | 10 |
| Transições de Status | RF09 / RN04 — Máquina de estados | 7 |
| Autorização de Funcionários | RF07 / RN05 — Segregação de acesso | 7 |
| Cálculo de Status de Estoque | RF13 / RN07 — Thresholds por unidade | 15 |
| Endpoints HTTP (FastAPI) | RF02-05 — Integração de rotas | 9 |
| Contagem de Pedidos | RF05 — pedidos_count | 4 |
| **TOTAL** | | **~91 asserções** |

---

### 🔐 Controle de Acesso no Desktop

| `funcionario.controle` | Papel | Destino ao Login |
|:---:|:---|:---|
| `1` | Gerente / Administrador | `PaginaADM` (Dashboard, Estoque, Clientes, Cupons, Relatórios) |
| `2` | Operador de Cozinha | `CozinhaApp` (KDS — fila de pedidos, status, histórico) |

---

### ⚙️ Configuração do Pytest (`pytest.ini`)

```ini
[pytest]
pythonpath = src
testpaths = tests
addopts = -v -s --cov=src --cov-report=term-missing
markers =
    lento: marca testes demorados
    integracao: marca testes de subsistemas
```

---

---

## 🇺🇸 English

# Capstone Project: Catatau Burgers 🍔

### Integrated Full-Stack Self-Service, Kitchen Display System (KDS), and Back-Office Management for Burger Joints and Diners

---

### 📌 System Overview

The **Catatau Burgers** project is a comprehensive solution engineered to automate and streamline a restaurant's operational workflow across three strategic touchpoints:

1. **Web Self-Service (Dining Room / Tables):**
   * Built with **FastAPI** + **Jinja2** + **HTML5/CSS3**.
   * Interactive and fully responsive menu (tailored for customer mobile devices at dining tables).
   * Dynamic shopping cart persisted via secure HTTP cookies.
   * Customer account registration, login, and profile view.
   * Direct order dispatch to the kitchen with table numbers and custom preparation notes (e.g., *"no onions"*, *"well-done beef"*).
   * **Automatic Ingredient Stock Deduction:** upon order confirmation, the system looks up each burger's recipe and automatically deducts the required ingredient quantities from the stock table.

2. **Kitchen Display System - KDS (Production Line Terminal):**
   * Touch-friendly Desktop interface built with **CustomTkinter**.
   * Visual order cards arranged chronologically in a grid layout.
   * Fast order lifecycle status transitions: `ESPERANDO` (Waiting) ➔ `PREPARANDO` (In Preparation) ➔ `FINALIZADO` (Completed).
   * High-visibility banner highlighting custom customer notes.
   * Production history view with daily completed orders metrics and counters.

3. **Back-Office Management Dashboard (Administration):**
   * Desktop interface in **CustomTkinter** featuring role-based access control (`funcionario.controle`: `1` for Admin/Manager, `2` for Kitchen).
   * Executive dashboard featuring gross daily sales, top-selling items ranking, and visual critical inventory alerts.
   * Global order monitoring and auditing with itemized price inspection and status conclusion (`Entregue` / Delivered).
   * Full CRUD management for inventory ingredients (Name, Quantity, and Alert Status: Ok, Attention, Critical).
   * Registered customer directory with order metrics.
   * Promotional coupon creation and lifecycle management.
   * Management reporting suite and end-of-day register closing.

4. **Centralized Database:**
   * **Microsoft SQL Server** (`(localdb)\MSSQLLocalDB` / `DBCATATAU`).
   * Relational persistence and schema mapping powered by **SQLAlchemy 2.0** and **PyODBC**.

---

### 📖 Software Requirements Specification (SRS)

The full Software Engineering specification document (following IEEE 830 / ISO/IEC/IEEE 29148 standards tailored for academic Capstone evaluation) is available at:

👉 **[DOCUMENTACAO_REQUISITOS.md](DOCUMENTACAO_REQUISITOS.md)**

---

### 🛠️ Tech Stack

* **Programming Language:** Python 3.10+
* **Web Backend:** FastAPI, Uvicorn, Starlette, Jinja2
* **Desktop GUI:** CustomTkinter, Pillow (PIL), Matplotlib
* **Database & ORM:** SQL Server LocalDB, SQLAlchemy 2.0, PyODBC
* **Web Frontend:** Semantic HTML5, CSS3 Flexbox/Grid, Material Icons
* **Testing:** Pytest 8+, pytest-cov, httpx, SQLite in-memory

---

### 🚀 Getting Started

#### 1. Prerequisites
* Python 3.10+ installed.
* SQL Server Express or LocalDB configured with the database `DBCATATAU`.
* ODBC Driver 17 for SQL Server installed.

#### 2. Install All Dependencies (Unified Global Requirements)

```bash
# At the repository root
python -m venv venv
.\venv\Scripts\activate        # Windows
# source venv/bin/activate    # Linux/macOS

pip install -r requirements.txt
```

#### 3. Running the Web Application

```bash
cd src/API
uvicorn main:app --reload --port 8000
```

Open your browser and navigate to: `http://localhost:8000/catatau`

#### 4. Running the Desktop Application (Kitchen & Management)

```bash
cd src/Desktop
python main.py
```

* **Manager Login:** User with `controle = 1`.
* **Kitchen Staff Login:** User with `controle = 2`.

#### 5. Running the Automated Test Suite

```bash
# At the repository root (requires no SQL Server — uses SQLite in-memory)
pytest

# With coverage report
pytest --cov=src --cov-report=term-missing
```
