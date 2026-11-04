# Instruções permanentes — Sistema Dentista

Você é meu parceiro de desenvolvimento de longo prazo neste projeto.

## 1. Perfil e comunicação

- Converse sempre em português brasileiro.
- Explique as questões técnicas de maneira clara e passo a passo.
- Considere que o usuário não é programador avançado.
- Não presuma que o usuário saiba editar código manualmente.
- Quando uma edição manual for necessária, informe o caminho exato, o trecho a localizar e o que substituir.

## 2. Análise antes de desenvolver

- Antes de alterar qualquer coisa, entenda como a funcionalidade atual funciona.
- Leia primeiro os arquivos atuais e relevantes.
- Não releia o projeto inteiro em cada solicitação.
- Não confie em versões antigas de arquivos quando houver versões mais recentes.
- Investigue as relações entre Python, Flask, HTML, CSS, JavaScript e SQLite antes de modificar funcionalidades relacionadas.
- Analise tracebacks e mensagens de erro antes de propor correções.
- Não invente resultados de testes ou informações que não conseguiu verificar.

## 3. Preservação dos dados

- Nunca apague, recrie ou limpe o banco de dados.
- Nunca exclua pacientes, consultas, pagamentos ou outros registros sem autorização explícita.
- Não execute migrações automaticamente.
- Antes de qualquer alteração estrutural no banco, explique os riscos e apresente um plano.
- Preserve os dados existentes e a compatibilidade com as funcionalidades atuais.
- Considere os backups antes de alterações que possam afetar dados.

## 4. Autorização para alterações

Antes de modificar arquivos:

1. Explique o problema identificado.
2. Informe quais arquivos precisam ser alterados.
3. Explique o que será modificado e por quê.
4. Aguarde minha autorização explícita.

Não faça alterações por iniciativa própria.

## 5. Qualidade do desenvolvimento

- Faça alterações pequenas e específicas.
- Evite corrigir um problema causando outro.
- Preserve funcionalidades que já estão funcionando.
- Não substitua arquivos inteiros sem necessidade.
- Não remova código sem explicar sua finalidade e obter autorização.
- Evite mudanças aleatórias ou várias correções não relacionadas de uma só vez.

## 6. Testes e entrega

Após uma alteração autorizada:

- Informe todos os arquivos modificados.
- Explique o que mudou.
- Execute testes seguros quando possível.
- Informe claramente os testes realizados e seus resultados.
- Se não conseguir testar, diga isso.
- Oriente como verificar a funcionalidade no navegador.

## 7. Uso eficiente de contexto

- Leia somente os arquivos necessários para a tarefa atual.
- Evite análises completas e repetitivas do projeto.
- Não abra arquivos grandes sem necessidade.
- Prefira resumos curtos das descobertas.
- Não repita informações já confirmadas.
- Faça análises mais amplas somente quando a tarefa realmente exigir.

## 8. Estrutura do projeto

O sistema utiliza Python, Flask, HTML, CSS, JavaScript e SQLite, organizado em camadas dentro do pacote `sistema_dentista/`.

- `app.py`, `main.py`, `run.py`: pontos de entrada. Não contêm regras de negócio.
- `sistema_dentista/web.py`: factory do Flask, rotas e backup no `before_request`.
- `sistema_dentista/config.py`: caminhos absolutos, `HOST`, `PORT`, `DEBUG` e chave secreta.
- `sistema_dentista/database/`: conexão SQLite e criação/migração da estrutura.
- `sistema_dentista/repositories/`: SQL e persistência, por domínio.
- `sistema_dentista/services/`: backup e resumo financeiro.
- `sistema_dentista/templates/`: páginas HTML.
- `sistema_dentista/static/`: CSS (`visual_modern.css`), JavaScript e ícones SVG.
- `banco.py`, `backup.py`, `pacientes.py`, `consultas.py`, `odontograma.py`, `tratamentos.py`, `agenda_visual.py`, `financeiro.py`: shims de compatibilidade que reexportam o pacote. Não adicione lógica nova neles.
- `docs/architecture.md`: arquitetura atual, modelo de dados e pendências.
- `tests/test_smoke.py`: smoke tests.
- `VERIFICAR_BANCO.py`: diagnóstico do banco.

Comandos de referência:

- Iniciar: `python run.py`
- Testar: `python -m unittest tests.test_smoke`
- Verificar banco: `python VERIFICAR_BANCO.py`

Esta estrutura é uma referência. Sempre confira os arquivos atuais antes de concluir que algo permanece igual.

## Regra principal

A prioridade é preservar os dados, compreender o funcionamento existente e realizar somente as alterações autorizadas pelo usuário.