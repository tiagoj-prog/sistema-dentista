# Arquitetura do Sistema Dentista

Documento vivo. Descreve a estrutura **atual** do código. Sempre confira os arquivos antes de assumir que algo permanece igual.

## 1. Objetivo

Sistema web local para apoio à gestão de um consultório odontológico, executado em uma única máquina com Flask + SQLite.

Premissas do projeto:

- Uso local, sem autenticação e sem acesso pela rede (`127.0.0.1`).
- Preservação total dos dados existentes.
- Sem ORM, sem Docker, sem banco externo.
- Compatibilidade com imports e pontos de entrada antigos.

## 2. Visão em camadas

```text
Navegador
  -> sistema_dentista/web.py        (rotas, formulários, templates)
    -> services/                    (regras que atravessam domínios)
    -> repositories/                (SQL e persistência por domínio)
      -> database/connection.py     (conexão, criação e migração da estrutura)
        -> dentista.db (SQLite, WAL)
```

Regras da direção de dependência:

- `web.py` pode importar `services` e `repositories`.
- `repositories` pode importar `database`.
- `services` pode importar `repositories` e `database`.
- `database` não importa camadas superiores.

## 3. Estrutura de diretórios

```text
Sistema dentista/
├── app.py / main.py / run.py      # pontos de entrada equivalentes
├── banco.py, backup.py            # shims de compatibilidade
├── pacientes.py, consultas.py, odontograma.py,
│   tratamentos.py, agenda_visual.py, financeiro.py   # shims
├── VERIFICAR_BANCO.py             # diagnóstico do banco
├── dentista.db                    # banco (não versionado)
├── backups/                       # backups mensais (não versionados)
├── docs/architecture.md
├── tests/test_smoke.py
└── sistema_dentista/
    ├── __init__.py                # create_flask_app, initialize_database, create_app
    ├── config.py                  # caminhos absolutos, HOST, PORT, DEBUG, SECRET_KEY
    ├── web.py                     # factory Flask + 39 rotas
    ├── database/
    │   ├── __init__.py
    │   └── connection.py          # conectar, criar_banco, adicionar_coluna_se_nao_existir
    ├── repositories/
    │   ├── patients_repository.py
    │   ├── appointments_repository.py
    │   ├── agenda_repository.py
    │   ├── odontogram_repository.py
    │   ├── treatments_repository.py
    │   └── financial_repository.py
    ├── services/
    │   ├── backup_service.py
    │   └── finance_summary_service.py
    ├── templates/                 # 8 arquivos HTML
    └── static/                    # visual_modern.css, app.js, mostrar_mais.js, icons/
```

## 4. Camadas

### `config.py`

Centraliza caminhos absolutos (`PROJECT_ROOT`, `DATABASE_PATH`, `BACKUP_DIR`, `TEMPLATES_DIR`, `STATIC_DIR`) e parâmetros de execução (`HOST`, `PORT`, `DEBUG`).

A chave secreta do Flask segue esta ordem:

1. variável de ambiente `SECRET_KEY`, se existir;
2. conteúdo de `.secret_key`, se o arquivo existir;
3. geração aleatória, persistida em `.secret_key`.

`.secret_key` está no `.gitignore` e pode ser recriado sem perda de dados.

### `__init__.py`

Expõe três funções com responsabilidades separadas:

- `create_flask_app()`: cria e configura o Flask, **sem tocar no banco** (usada pelos testes).
- `initialize_database()`: executa a criação/migração da estrutura.
- `create_app(init_database=True)`: combina as duas.

### `web.py`

Contém a factory `create_flask_app()`, as 39 rotas, validação de formulários, montagem de dados para templates e o hook `before_request` `executar_backup_mensal`.

### `repositories/`

Todo o SQL fica aqui, separado por domínio. `repositories/__init__.py` reexporta as funções públicas; os shims da raiz reexportam esse pacote.

### `services/`

- `backup_service.py`: geração do backup mensal, validação de arquivos (tamanho, `integrity_check`, `foreign_key_check`, tabelas essenciais) e quarentena de backups inválidos.
- `finance_summary_service.py`: agregações de resumo financeiro usadas pela rota do painel.

### `database/connection.py`

Conecta com `sqlite3.Row`, foreign keys ativas, timeout e WAL. Expõe `adicionar_coluna_se_nao_existir()`, usado pelas rotinas de migração incremental.

## 5. Inicialização do banco

A ordem é obrigatória, porque `criar_tabelas_contas_individuais()` depende de estruturas criadas antes e executa migração de dados:

1. `criar_banco()`
2. `criar_tabelas_conta_paciente()`
3. `criar_tabela_odontograma()`
4. `criar_tabelas_contas_individuais()`
5. `criar_tabela_agenda_visual()`
6. `criar_tabela_tratamentos()`

Essas funções são idempotentes (`CREATE TABLE IF NOT EXISTS` e verificação de coluna). Não há ferramenta de migração externa.

## 6. Modelo de dados

Banco: `dentista.db` (SQLite, WAL). Arquivos auxiliares `-wal` e `-shm` fazem parte do estado operacional e não devem ser apagados com a aplicação em execução.

| Grupo | Tabelas |
| --- | --- |
| Núcleo clínico | `pacientes`, `consultas`, `agenda_eventos`, `odontograma`, `odontograma_faces`, `odontograma_procedimentos`, `tratamentos` |
| Financeiro | `orcamentos`, `contas_orcamento`, `itens_conta_orcamento`, `pagamentos_conta_orcamento`, `contas_receber`, `contas_pagar`, `movimentacoes`, `despesas_recorrentes` |
| Legado preservado | `contas_paciente`, `pagamentos_paciente`, `quitacoes_paciente`, `orcamentos_transferidos`, `boletos`, `notas_fiscais` |
| Controle | `migracoes_sistema` (chave + data de execução) |

Observações:

- `migracoes_sistema` registra migrações já aplicadas (ex.: `contas_orcamento_v2`).
- Não existem índices explícitos criados pelo sistema; apenas os automáticos de chave primária e `UNIQUE`.
- Tabelas legadas permanecem para não perder histórico. A remoção exige autorização, análise e backup.

## 7. Templates e assets

- `templates/`: 8 arquivos (`index`, `pacientes`, `perfil_paciente`, `agenda`, `odontograma`, `tratamento`, `financeiro`, `_dente_faces`).
- Não há `base.html`; cabeçalho e navegação estão repetidos em cada página.
- `odontograma.html` concentra JavaScript inline extenso.
- `static/`: `visual_modern.css` (folha única carregada por todas as páginas, referenciada com `?v=` para evitar cache), `app.js`, `mostrar_mais.js` e `icons/*.svg` (ícones próprios que substituíram os emojis).
- `_dente_faces.html` não possui referência direta conhecida; verificar antes de remover.

## 8. Backups

- Diretório: `backups/`, calculado a partir de `DATABASE_PATH`.
- Nome: `dentista_YYYY-MM.db`, um por mês.
- A geração usa a API de backup do SQLite em arquivo temporário, valida o resultado e só então promove para o nome final.
- Backups inválidos são movidos para quarentena em vez de sobrescrever o arquivo existente.
- O backup é disparado no `before_request` da aplicação.

## 9. Fluxos legados preservados

Continuam existindo, com funções e tabelas antigas:

- `contas_paciente`, `pagamentos_paciente`, `quitacoes_paciente`, `orcamentos_transferidos`;
- boletos e notas fiscais;
- passagem de orçamento para conta de paciente.

Esses fluxos não devem ser removidos durante manutenções comuns. Limpeza exige autorização separada, backup e testes.

## 10. Segurança e recuperação

- Bind em `127.0.0.1`, sem exposição na rede local.
- `DEBUG` desligado por padrão; ativável por `FLASK_DEBUG`.
- Chave secreta persistente e fora do versionamento.
- Antes de qualquer etapa que mova arquivos ou altere estrutura:

1. Criar backup externo e consistente do banco.
2. Validar `PRAGMA integrity_check`.
3. Registrar contagem de tabelas e registros.
4. Verificar `dentista.db`, `dentista.db-wal` e `dentista.db-shm`.
5. Registrar local do backup e resultado da verificação.
6. Parar a aplicação antes de copiar ou mover o banco.

Se houver falha, não continuar e restaurar a partir do backup externo.

## 11. Decisões de projeto

| Decisão | Motivo |
| --- | --- |
| SQLite em arquivo único | Instalação simples, uso monousuário, backup por cópia. |
| Sem ORM | O SQL existente é extenso e testado; um ORM exigiria reescrever regras. |
| Sem login | Aplicação local em máquina única; autenticação adicionaria complexidade sem ganho. |
| Camadas `repositories`/`services` | Separar SQL de regra de negócio e permitir testes sem Flask. |
| Shims na raiz | Preservar imports antigos durante a migração, sem quebrar scripts e atalhos. |
| CSS único com `?v=` | Evitar cache do navegador sem introduzir pipeline de build. |

## 12. Pendências conhecidas

Itens identificados e ainda não executados:

- `web.py` com ~1.500 linhas; separação em `routes/` está planejada.
- `financial_repository.py` com ~2.480 linhas; candidato a divisão por fluxo.
- Templates sem `base.html` (sem herança Jinja).
- Cobertura de testes restrita a smoke tests.
- Ausência de linter/formatter e de versões fixadas em `requirements.txt`.
- Sem índices explícitos para colunas usadas em filtros frequentes.
- Projeto ainda sem versionamento Git nesta máquina.

Nenhuma dessas pendências altera o comportamento atual; são melhorias de manutenção.

## 13. Histórico da reorganização

1. Templates e `static` movidos para dentro do pacote `sistema_dentista/`.
2. SQL extraído para `repositories/`, mantendo shims na raiz.
3. Serviços de backup e resumo financeiro extraídos para `services/`.
4. Factory do Flask separada da inicialização do banco, permitindo testes sem migração.
5. Exclusão permanente de paciente endurecida (verificação prévia de tabelas, transação e rollback).
6. Backup mensal passou a validar integridade e colocar arquivos inválidos em quarentena.
7. Interface modernizada (tema azul, ícones SVG próprios) sem alterar rotas ou regras.
