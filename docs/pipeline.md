# Pipeline GSD

O pipeline GSD é uma sequência de gates de qualidade. Cada gate é um checkpoint — nada passa sem aprovação.

## Visão Geral

```
RESEARCH GATE
    ↓ (BUILD?)
BUSINESS VALIDATION
    ↓ (viable?)
[CONTENT STRATEGY] (opcional)
    ↓
ARCHITECTURE GATE
    ↓ (locked)
UX DESIGN GATE
    ↓ (wireframes aprovados)
PLAN
    ↓
EXECUTE
    ↓
UX REVIEW (apenas tasks com UI)
    ↓ (UX Score ≥ 42/60?)
TEST
    ↓ (all pass?)
VERIFY (QA — modelo diferente)
    ↓ (0 critical/high?)
FIX (se necessário)
    ↓
DEPLOY
    ↓
DONE
```

## Estágios Detalhados

### 0. RESEARCH GATE
**Objetivo:** Validar demanda antes de investir em engenharia.
**Quem:** Orchestrator + Research Agent
**Output:** BUILD / VALIDATE FIRST / AVOID
**Exceção:** Tasks técnicas internas (refactor, bug fix, infra) não precisam.

### 0.5. BUSINESS VALIDATION
**Objetivo:** Validar viabilidade comercial.
**Quem:** Orchestrator
**Output:** BUSINESS-VALIDATION.md
**Exceção:** Ferramentas internas, infra, refactor não precisam.

### 0.6. CONTENT STRATEGY (opcional)
**Objetivo:** Para projetos onde conteúdo é o produto.
**Output:** CONTENT-STRATEGY.md

### 1. ARCHITECTURE GATE
**Objetivo:** Travar stack antes de codar.
**Quem:** Orchestrator
**Output:** ARCHITECTURE.md
**Regra:** Depois de locked, ninguém muda sem aprovação.

### 2. UX DESIGN GATE
**Objetivo:** Travar visuais antes de código UI.
**Quem:** Orchestrator (como UX Designer)
**Outputs:** DESIGN-SYSTEM.md + WIREFRAMES.md
**Regra:** NUNCA começar código React/Next.js sem wireframe aprovado.
**Exceção:** Tasks puramente backend não precisam.

### 3. INIT
**Objetivo:** Criar estrutura de planning.
**Outputs:** PROJECT.md, REQUIREMENTS.md, ARCHITECTURE.md, DESIGN-SYSTEM.md, WIREFRAMES.md, ROADMAP.md, STATE.md

### 4. DISCUSS
**Objetivo:** Remover ambiguidade antes da execução.
**Defaults:** REST over GraphQL, Serverless-first, Minimal UI

### 5. PLAN
**Objetivo:** Decompor em tasks atômicas.
**Quem:** Orchestrator
**Regras:** Máx 2-3 tasks por plan, agrupadas por dependency waves

### 6. EXECUTE
**Objetivo:** Codificar.
**Quem:** Code AI via delegation
**Modelo:** Wave 1 (independentes, paralelo) → Wave 2 (dependentes, sequencial)
**Regras:** Orchestrator nunca codifica. Todo código UI começa por mobile.

### 7. UX REVIEW
**Objetivo:** Score objetivo de qualidade UI.
**Quem:** Orchestrator (como UX Reviewer)
**Mínimo:** 42/60 para aprovar
**Exceção:** Tasks puramente backend não precisam.

### 8. TEST
**Objetivo:** Validar build, lint, tipos, testes.
**Quem:** Code AI via delegation
**Checklist:** `npm run build` → `npm run lint` → `npx tsc --noEmit` → `npm test`

### 9. VERIFY (QA)
**Objetivo:** Code review com modelo diferente.
**Quem:** QA AI (modelo DIFERENTE do executor)
**Níveis:** Build → Security → Type Safety → Functional → Contract → Regression
**Severidade:** CRITICAL (bloqueia) / HIGH (corrige) / MEDIUM (backlog) / LOW (optional)

### 10. DEPLOY
**Objetivo:** Produção.
**Quem:** Orchestrator
**Como:** Vercel auto-deploy ou CLI

### 11. DONE
**Objetivo:** Checklist final.
**Definition of Done:** Todos os items do checklist passam.

## Decision Matrix

| Situação | Ação |
|---|---|
| Build/Lint/Typecheck falha | Dev corrige antes de QA |
| Tests falham | Dev corrige antes de QA |
| UX Score < 42/60 | Volta para EXECUTE com feedback |
| QA: CRITICAL | Bloqueia deploy, dev corrige |
| QA: HIGH | Dev corrige antes do deploy |
| QA: MEDIUM | Backlog, próxima wave |
| QA: LOW | Nice to have, opcional |
