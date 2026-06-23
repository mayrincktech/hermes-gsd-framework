# Provision Script

Automatiza o setup completo de um novo app web em segundos:

1. **Copia o template** Next.js + shadcn/ui
2. **Personaliza** nome do app em todos os arquivos
3. **Cria repo** no GitHub e faz push
4. **Faz deploy** no Vercel (produção)
5. **Cria schema** no Neon Postgres

## Uso

```bash
python3 provision_app.py \
  --name "Meu App" \
  --slug "meu-app" \
  --description "Uma descrição"
```

## Pré-requisitos

- Python 3.11+
- Node.js 22+ (nvm)
- gh CLI autenticado
- Vercel CLI instalado
- Conta Neon com connection string

## Credenciais

```bash
export GITHUB_TOKEN=ghp_...port VERCEL_TOKEN=vcp_...port NEON_CONNECTION_STRING=postgresql://...
```

Veja `docs/provision.md` para troubleshooting e configuração avançada.
