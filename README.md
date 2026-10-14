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

* **Linguagem:** Python 3.14
* **Backend Web:** FastAPI, Uvicorn, Starlette, Jinja2
* **Desktop GUI:** CustomTkinter, Pillow (PIL)
* **Banco de Dados & ORM:** SQL Server LocalDB, SQLAlchemy 2.0, PyODBC
* **Frontend Web:** HTML5 Semântico, CSS3 Flexbox/Grid, Material Icons

---

### 🚀 Como Executar

#### 1. Pré-requisitos
* Python 3.10+ instalado.
* SQL Server Express ou LocalDB configurado com a base `DBCATATAU`.
* ODBC Driver 17 for SQL Server.

#### 2. Executar a Aplicação Web
```bash
cd DB-Jinja2-Python
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Acesse no navegador: `http://localhost:8000/catatau`

#### 3. Executar o Módulo Desktop (Cozinha & Gerência)
```bash
cd "Desktop Tkinter Gestão"
python main.py
```
* **Login de Gerência:** Usuário cadastrado com `controle = 1`.
* **Login de Cozinha:** Usuário cadastrado com `controle = 2`.

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

Key document contents:
* Functional Requirements Matrix (RF01 to RF16 with MoSCoW prioritization);
* Business Rules (RN01 to RN07);
* Non-Functional Requirements (RNF01 to RNF09);
* Entity-Relationship Diagram (ERD in Mermaid);
* State Machine and Sequence Diagrams for Order Lifecycle and Stock Deduction;
* Requirements Traceability Matrix (Requirements mapped to Code files and lines);
* Recommendations and Future Work for the Academic Examining Board.

---

### 🛠️ Tech Stack

* **Programming Language:** Python 3.14
* **Web Backend:** FastAPI, Uvicorn, Starlette, Jinja2
* **Desktop GUI:** CustomTkinter, Pillow (PIL)
* **Database & ORM:** SQL Server LocalDB, SQLAlchemy 2.0, PyODBC
* **Web Frontend:** Semantic HTML5, CSS3 Flexbox/Grid, Material Icons

---

### 🚀 Getting Started

#### 1. Prerequisites
* Python 3.10+ installed.
* SQL Server Express or LocalDB configured with the database `DBCATATAU`.
* ODBC Driver 17 for SQL Server.

#### 2. Running the Web Application
```bash
cd DB-Jinja2-Python
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt
uvicorn main:app --reload --port 8000
```
Open your browser and navigate to: `http://localhost:8000/catatau`

#### 3. Running the Desktop Application (Kitchen & Management)
```bash
cd "Desktop Tkinter Gestão"
python main.py
```
* **Manager Login:** User with `controle = 1`.
* **Kitchen Staff Login:** User with `controle = 2`.
