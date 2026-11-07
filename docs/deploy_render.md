# Hospedando a demo no Render (gratuito)

Este guia coloca a demonstração do sistema na internet com um link
público, sem precisar instalar nada no computador do dentista.

## O que será publicado

Apenas a demo (`demo/dentista_demo.db`), com dados fictícios.
O banco real (`dentista.db`) não é enviado nem usado.

## Passo a passo

### 1. Criar conta no Render

1. Acesse https://render.com
2. Clique em **Get Started** e crie conta com GitHub (recomendado)
   ou e-mail.
3. Confirme o e-mail.

### 2. Conectar o repositório

1. No painel do Render, clique em **New +** → **Web Service**.
2. Escolha **Connect a repository**.
3. Selecione `tiagoj-prog/sistema-dentista`.
4. Se pedir permissão ao GitHub, autorize o Render.

### 3. Configurar o serviço

Preencha os campos assim:

| Campo | Valor |
| --- | --- |
| Name | `sistema-dentista-demo` |
| Region | `Oregon (US West)` ou o mais próximo |
| Branch | `main` |
| Runtime | `Python 3` |
| Build Command | `pip install -r requirements.txt && python scripts/seed_demo.py --force` |
| Start Command | `gunicorn scripts.run_demo:app --bind 0.0.0.0:$PORT --timeout 120` |
| Plan | `Free` |

O arquivo `render.yaml` já contém essas configurações. Se o Render
detectá-lo, preenche automaticamente.

### 4. Criar o serviço

1. Clique em **Create Web Service**.
2. O Render começa o build. Acompanhe os logs.
3. O primeiro build leva 2 a 4 minutos.
4. Quando aparecer **"Your service is live"**, o link está pronto.

### 5. Acessar a demo

O endereço será algo como:

```
https://sistema-dentista-demo.onrender.com
```

Abra no navegador e teste. A primeira visita pode demorar ~30 segundos
porque o serviço gratuito "dorme" após inatividade.

### 6. Compartilhar

Copie o link e envie para dentistas por WhatsApp, e-mail ou posts em
grupos. Não é necessário login.

## Limitações do plano gratuito

- O serviço dorme após 15 minutos sem acesso. A primeira visita
  demora até 30 segundos para "acordar".
- 750 horas por mês (suficiente para uma demo).
- O banco demo é recriado a cada novo deploy (dados fictícios, sem
  problema).
- Não use para dados reais de pacientes.

## Atualizando a demo

Sempre que você fizer `git push origin main`, o Render faz rebuild
automaticamente. O banco demo é recriado com os dados fictícios.

## Removendo a demo

No painel do Render: **Settings** → **Delete Web Service**.
Não afeta o repositório nem o banco real.
