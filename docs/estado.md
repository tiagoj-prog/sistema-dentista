# Sistema Dentista — estado do trabalho

Atualizado: 2026-11-09

> Fonte de verdade do andamento, versionada junto do código.

## Objetivo

Sistema web para gestão de consultório odontológico (Flask + SQLite). Portfólio público em https://github.com/tiagoj-prog/sistema-dentista.

## Stack e comandos

- Stack: Python 3.13, Flask 3.1.3, SQLite, HTML/CSS/JS.
- Rodar: `python run.py` (porta 5000)
- Testar: `python -m unittest tests.test_smoke`
- Demo: `python scripts/seed_demo.py` + `python scripts/run_demo.py` (porta 5001)
- Publicar: `git add -A && git commit && git push origin main` (somente com autorização explícita do usuário)

## Estado atual

- Repositório público, branch `main`, sincronizado.
- CI verde (GitHub Actions).
- Licença: PolyForm Noncommercial 1.0.0.
- Demo online: https://sistema-dentista-x5tu.onrender.com/
- Banco real intacto (1 paciente, 8 movimentações, integridade ok).
- Melhorias 1-10 implementadas (logging, índices, base.html, error pages, CSV, validação, paginação, inadimplência, anexos, lembrete WhatsApp).
- Corrigido bug de clique na agenda (botão WhatsApp restaurado).

## Fluxo de trabalho (regra permanente)

1. O usuário pede uma mudança.
2. Eu implemento localmente e rodo testes.
3. Eu mostro o diff e o resultado dos testes.
4. **Eu NÃO faço commit nem push por iniciativa própria.**
5. Somente quando o usuário disser explicitamente "pode publicar/commitar/push" eu executo `git add`, `git commit` e `git push`.
6. Commits devem ser pequenos e com mensagens claras.
7. Manter mudanças locais até o usuário validar.

## Decisões

- PolyForm Noncommercial: permite estudo/portfólio, proíbe uso comercial.
- AGENTS.md removido do repositório público (mantido localmente).
- Demo usa dados fictícios, nunca o banco real.
- Sem login/auth, Docker, banco externo ou ORM (por enquanto).

## Arquivos importantes

- `sistema_dentista/web.py`: factory Flask, 45 rotas, backup no before_request.
- `sistema_dentista/database/connection.py`: conexão SQLite + criar_banco + criar_indices + criar_tabela_anexos.
- `sistema_dentista/repositories/patients_repository.py`: SQL de pacientes (com validação e paginação).
- `sistema_dentista/repositories/financial_repository.py`: SQL financeiro + contas vencidas.
- `sistema_dentista/repositories/attachments_repository.py`: anexos de pacientes.
- `sistema_dentista/validators.py`: validação de CPF e telefone.
- `sistema_dentista/templates/base.html`: template base com herança Jinja.
- `sistema_dentista/templates/inadimplencia.html`: relatório de inadimplência.
- `scripts/seed_demo.py` / `scripts/run_demo.py`: demo com dados fictícios.
- `docs/deploy_render.md`: guia de hospedagem no Render.
- `tests/test_smoke.py`: 4 smoke tests.

## Próximo passo

Aguardar instrução do usuário.

## Pendências

- [ ] Remover paciente de teste "Teste Val2" do banco real (se autorizado).
- [ ] Remover anexo de teste do banco real (se autorizado).
- [ ] Validar demo com dentistas reais.

## Histórico

- 2026-11-04: repositório publicado, autor corrigido, screenshots, demo criada.
- 2026-11-07: CI, licença PolyForm, AGENTS.md removido do repo.
- 2026-11-09: melhorias 1-7 (logging, índices, base.html, error pages, CSV, validação, paginação).
- 2026-11-11: melhorias 8-10 (inadimplência, anexos, lembrete WhatsApp) + correção de clique na agenda.
