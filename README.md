# GSD Framework

**Metodologia + ferramentas para desenvolvimento de apps com IA — do conceito ao deploy em minutos.**

O GSD (Get Shit Done) é um framework que combina:
- **Metodologia estruturada** — pipeline de 11 estágios com gates de qualidade
- **Template reutilizável** — Next.js + shadcn/ui pronto pra clonar
- **Provisionamento automático** — GitHub + Vercel + Neon com um comando

## O que está incluído

| Componente | Descrição |
|---|---|
| `METHODOLOGY.md` | Pipeline GSD v7 completo com todos os gates |
| `docs/` | Guias detalhados de pipeline, design system, roles e provisionamento |
| `template/` | Next.js 16 + TypeScript + Tailwind v4 + shadcn/ui (mobile-first) |
| `provision/` | Script Python que automatiza setup de GitHub + Vercel + Neon |

## Pré-requisitos

- **Python 3.11+**
- **Node.js 22+** (recomendado via [nvm](https://github.com/nvm-sh/nvm))
- **[gh CLI](https://cli.github.com/)** autenticado
- **[Vercel CLI](https://vercel.com/docs/cli)** instalado (`npm i -g vercel`)
- **Conta [Neon](https://neon.tech)** (free tier)

## Quickstart

```bash
# 1. Clone o framework
git clone https://github.com/mayrincktech/gsd-framework.git
cd gsd-framework

# 2. Configure credenciais
export GITHUB_TOKEN=seu_token_aqui
export VERCEL_TOKEN=seu_token_aqui
export NEON_CONNECTION_STRING=postgresql://...

# 3. Crie um novo app
python3 provision/provision_app.py \
  --name "Meu App" \
  --slug "meu-app" \
  --description "Descrição do app"
```

O script retorna:
```json
{
  "app_name": "Meu App",
  "slug": "meu-app",
  "github_url": "https://github.com/mayrincktech/meu-app",
  "vercel_url": "https://meu-app.vercel.app",
  "database_schema": "meu_app",
  "database_url": "postgresql://...?schema=meu_app",
  "status": "provisioned"
}
```

## Pipeline GSD

```
RESEARCH GATE
    ↓
BUSINESS VALIDATION
    ↓
ARCHITECTURE GATE
    ↓
UX DESIGN GATE
    ↓
PLAN → EXECUTE → UX REVIEW → TEST → VERIFY → DEPLOY → DONE
```

Cada gate é um checkpoint de qualidade. Nada passa sem aprovação.

## Template Features

- **Next.js 16** com App Router
- **TypeScript** strict mode
- **Tailwind CSS v4** com tema dark/light
- **shadcn/ui** (Base UI) — 10+ componentes prontos
- **Mobile-first** — sidebar desktop + bottom nav mobile
- **Lucide icons**
- Sem auth, sem DB, sem ORM — adicione só quando precisar

## Licença

MIT — use freely, commercially ou não.
