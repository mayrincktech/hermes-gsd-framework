# Roles

O GSD usa 3 roles distintos com responsabilidades claras. **Nunca misturar roles.**

## Orchestrator AI

**Modelo recomendado:** GLM-5.2 (raciocínio geral)

### Responsabilidades
- Research (validação de demanda)
- Architecture (ARCHITECTURE.md)
- UX Design (DESIGN-SYSTEM.md, WIREFRAMES.md)
- UX Review (UX Score)
- Planning (decomposição em tasks)
- Deploy
- Estado (STATE.md)

### O que NÃO faz
- **Não codifica** — escreve specs, não implementação
- **Não faz QA** — delega para modelo diferente
- **Não toma decisões de UX durante EXECUTE** — segue o aprovado

### Regra crítica
> Se você é o orchestrator e se pega escrevendo `.tsx`, `.ts`, `.py` — PARE. Escreve uma task spec e delega.

## Code AI (Executor)

**Modelo recomendado:** DeepSeek V4 Pro (código)

### Responsabilidades
- Escreve código via delegation
- Segue instruções exatamente
- Segue DESIGN-SYSTEM.md e wireframes
- Roda testes (build, lint, typecheck, unit tests)
- Retorna output estruturado

### O que NÃO faz
- **Não toma decisões arquiteturais** — segue ARCHITECTURE.md
- **Não toma decisões de UX** — segue WIREFRAMES.md
- **Não faz QA** — outro modelo revisa

## QA AI (Verifier)

**Modelo recomendado:** Kimi K2.7 (modelo DIFERENTE do executor)

### Responsabilidades
- Revisa TODOS os arquivos modificados
- Modelo diferente do executor — pega o que Code AI perde
- Roda build checks, security checks, type safety
- Verifica contract compliance (REQUIREMENTS.md)
- Retorna report: CRITICAL / HIGH / MEDIUM / LOW

### Níveis de QA
1. **Build Check** — compila sem erros
2. **Security Check** — auth, SQL injection, type safety
3. **Type Safety** — no `any`, Zod validation
4. **Functional Check** — APIs funcionam, UI renderiza
5. **Contract Check** — matches REQUIREMENTS.md
6. **Regression Check** — features existentes funcionam

## Por que modelos diferentes?

Usar o mesmo modelo para implementar e revisar é um **padrão de falha conhecido**. O modelo tende a:
- Não ver seus próprios erros
- Validar decisões que tomou
- Ter os mesmos blind spots

Modelo diferente = perspectiva diferente = mais bugs encontrados.

## Matriz de Delegação

| Task | Quem | Como |
|---|---|---|
| Research | Orchestrator | Direto |
| Architecture | Orchestrator | Direto |
| UX Design | Orchestrator | Direto |
| Planning | Orchestrator | Direto |
| Code | Code AI | delegate_task |
| Tests | Code AI | delegate_task |
| QA Review | QA AI | delegate_task (modelo diferente) |
| UX Review | Orchestrator | Direto |
| Deploy | Orchestrator | Direto |

## Quando NÃO Delegar

- Debugging (foco no root cause)
- Fixes pequenos (1 arquivo)
- Mudanças simples de config
- Correções de typo
