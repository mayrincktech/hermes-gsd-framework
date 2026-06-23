# Provisioning

O script `provision/provision_app.py` automatiza o setup completo de um novo app: template → GitHub → Vercel → Neon.

## Pré-requisitos

| Ferramenta | Versão | Como instalar |
|---|---|---|
| Python | 3.11+ | `apt install python3` |
| Node.js | 22+ | nvm |
| gh CLI | 2.95+ | [cli.github.com](https://cli.github.com/) |
| Vercel CLI | 54+ | `npm i -g vercel` |
| Neon | Free tier | [neon.tech](https://neon.tech) |

## Credenciais Necessárias

```bash
# Variáveis de ambiente
GITHUB_TOKEN=ghp_...          # GitHub PAT com repo scope
VERCEL_TOKEN=vcp_...          # Vercel token (vercel.com > Settings > Tokens)
NEON_CONNECTION_STRING=postgresql://...  # Neon connection string
```

Ou armazene em `~/.hermes/.env` (Hermes Agent) ou `.env` na raiz do projeto.

## Uso

```bash
python3 provision/provision_app.py \
  --name "Task Manager" \
  --slug "task-manager" \
  --description "Sistema de gerenciamento de tarefas"
```

### Parâmetros

| Parâmetro | Obrigatório | Descrição |
|---|---|---|
| `--name` | Sim | Nome de exibição (ex: "Task Manager") |
| `--slug` | Sim | Slug URL-safe (ex: "task-manager") |
| `--description` | Sim | Descrição de uma linha |
| `--template-dir` | Não | Path do template (default: `../template`) |

## Fluxo Executado

### Step 1: Copy Template
Copia o template para `/home/moises/workspace/{slug}` (ou diretório configurado).

### Step 2: Personalize
Substitui "App Name" pelo nome real em todos os arquivos. Atualiza `package.json`.

### Step 3: GitHub Repo
Cria repo privado via `gh repo create` e faz push inicial.
- Verifica se repo já existe (idempotente)
- Adiciona remote origin
- Push automático

### Step 4: Vercel Deploy
- Linka o projeto ao Vercel
- Deploy para produção (`vercel deploy --prod`)
- Desativa Vercel Authentication (acesso público)
- Captura URL de produção

### Step 5: Neon Database
Cria um schema isolado no Neon:
```sql
CREATE SCHEMA IF NOT EXISTS {slug_underscored};
```
- Cada app tem seu próprio schema
- Compartilha a mesma instância Neon (free tier)

### Step 6: Output
Retorna JSON com todas as URLs e credenciais:
```json
{
  "app_name": "Task Manager",
  "slug": "task-manager",
  "github_url": "https://github.com/org/task-manager",
  "vercel_url": "https://task-manager-xxx.vercel.app",
  "database_schema": "task_manager",
  "database_url": "postgresql://...?schema=task_manager",
  "status": "provisioned"
}
```

Também appenda em `data/provisioned_apps.json` para registro.

## Configuração do GitHub Org

O script usa o usuário `mayrincktech` por padrão. Para mudar:

```python
# No topo do script
GITHUB_ORG = "sua-org"
```

## Configuração do Vercel Team

O script detecta automaticamente o team/org do Vercel. Para override:

```python
# No topo do script
VERCEL_TEAM = "sua-team"
```

## Troubleshooting

### `source: not found`
O script usa `. ~/.nvm/nvm.sh` (compatível com sh e bash). Se ainda falhar:
```bash
export NVM_DIR="$HOME/.nvm"
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh"
```

### `gh auth failed`
```bash
echo "$GITHUB_TOKEN" | gh auth login --with-token
gh auth setup-git
```

### Vercel deploy timeout
O timeout é 600s. Se Vercel demorar mais:
- Verifique conexão de internet
- Tente `vercel deploy --prod` manualmente no diretório do app

### Neon schema creation failed
- Verifique `NEON_CONNECTION_STRING`
- Teste conexão: `psql "$NEON_CONNECTION_STRING" -c "SELECT 1"`
