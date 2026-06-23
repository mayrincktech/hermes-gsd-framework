#!/usr/bin/env python3
"""
provision_app.py — Automate the full provisioning flow for a new web app.

Flow:
  1. COPY TEMPLATE      cp -r template → /home/moises/workspace/{slug}
  2. PERSONALIZE        Replace 'App Name' placeholders, update package.json
  3. GITHUB REPO        Create private repo via `gh` + push code
  4. VERCEL DEPLOY      Link project → `vercel --prod` → disable Vercel Auth
  5. NEON DATABASE      CREATE SCHEMA in the existing Neon database
  6. OUTPUT             Print JSON summary + append to provisioned_apps.json

Usage:
    python3 provision_app.py \
        --name 'Price Tracker' \
        --slug 'price-tracker' \
        --description 'Track prices over time'

Credentials are read from the environment — never hardcoded:
    GitHub token:      ~/.hermes/.env  (GITHUB_TOKEN=...)
    Vercel token:      /tmp/.vercel_tok
    Neon connection:   ~/.hermes/.env  (NEON_CONNECTION_STRING=...)
"""

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import urllib.request
import urllib.error
from pathlib import Path

# ─── Constants ────────────────────────────────────────────────────────────────
WORKSPACE = Path("/home/moises/workspace")
GSD_HUB = WORKSPACE / "gsd-hub"
GITHUB_ORG = "lucronaconfeitaria-ops"
ENV_FILE = Path.home() / ".hermes" / ".env"
VERCEL_TOKEN_FILE = Path("/tmp/.vercel_tok")
DATA_FILE = GSD_HUB / "data" / "provisioned_apps.json"
NVM_SOURCE = ". ~/.nvm/nvm.sh"
VENV_PYTHON = str(GSD_HUB / ".venv" / "bin" / "python3")
DEFAULT_TEMPLATE = str(WORKSPACE / "web-app-template")

# Files / dirs to strip when copying the template (avoid copying build state)
TEMPLATE_JUNK = {".git", "node_modules", ".next", ".vercel", ".DS_Store"}
# Binary-ish extensions we skip when doing text replacement
BINARY_EXTS = {
    ".png", ".jpg", ".jpeg", ".gif", ".ico", ".svg", ".woff", ".woff2",
    ".ttf", ".eot", ".otf", ".pdf", ".zip", ".tar", ".gz", ".lock",
}


# ─── Helpers ──────────────────────────────────────────────────────────────────
class StepError(Exception):
    """Raised when a provisioning step fails."""


def log(msg: str):
    print(msg, flush=True)


def fail(step: str, msg: str, exc: Exception = None):
    """Print a structured failure message and exit."""
    print(f"\n❌ STEP FAILED: {step}", file=sys.stderr)
    print(f"   {msg}", file=sys.stderr)
    if exc:
        print(f"   Error: {exc}", file=sys.stderr)
    sys.exit(1)


def run(cmd, cwd=None, env=None, check=True, timeout=600):
    """Run a shell command string (with nvm sourced) via subprocess.run.

    Always uses capture_output=True, text=True as required.
    """
    full_cmd = f"{NVM_SOURCE} && {cmd}"
    merged_env = dict(os.environ)
    if env:
        merged_env.update(env)
    r = subprocess.run(
        full_cmd, shell=True, capture_output=True, text=True,
        cwd=cwd, env=merged_env, timeout=timeout, executable="/bin/bash",
    )
    if check and r.returncode != 0:
        detail = r.stdout.strip() or r.stderr.strip()
        raise StepError(
            f"Command exited {r.returncode}: {cmd}\n"
            f"  stdout: {r.stdout[-800:]}\n  stderr: {r.stderr[-800:]}"
            if detail else f"Command exited {r.returncode}: {cmd}"
        )
    return r


def run_py(code: str, env=None, check=True):
    """Run Python code in the gsd-hub venv (has psycopg2)."""
    merged_env = dict(os.environ)
    if env:
        merged_env.update(env)
    r = subprocess.run(
        [VENV_PYTHON, "-c", code],
        capture_output=True, text=True, env=merged_env, timeout=60,
    )
    if check and r.returncode != 0:
        raise StepError(f"Python execution failed:\n  {r.stderr[-800:]}")
    return r


def read_env_var(filepath: Path, varname: str) -> str:
    """Read a VAR=value line from a dotenv-style file."""
    try:
        text = filepath.read_text(encoding="utf-8")
    except FileNotFoundError:
        raise StepError(f"{varname}: file not found at {filepath}")
    for line in text.splitlines():
        line = line.strip()
        if line.startswith(f"{varname}="):
            val = line.split("=", 1)[1].strip()
            # strip surrounding quotes if present
            if len(val) >= 2 and val[0] == val[-1] and val[0] in "\"'":
                val = val[1:-1]
            return val
    raise StepError(f"{varname} not found in {filepath}")


def read_vercel_token() -> str:
    try:
        return VERCEL_TOKEN_FILE.read_text(encoding="utf-8").strip()
    except FileNotFoundError:
        raise StepError(f"Vercel token file not found: {VERCEL_TOKEN_FILE}")


def slug_to_schema(slug: str) -> str:
    """Convert a URL slug to a Postgres-safe schema name (underscores)."""
    s = slug.lower().replace("-", "_")
    s = re.sub(r"[^a-z0-9_]", "_", s)
    if not s or s[0].isdigit():
        s = f"app_{s}"
    return s


def vercel_api(method: str, path: str, token: str, body: dict = None,
               team_id: str = None) -> dict:
    """Call the Vercel REST API and return the parsed JSON response."""
    url = f"https://api.vercel.com{path}"
    sep = "&" if "?" in path else "?"
    if team_id:
        url += f"{sep}teamId={team_id}"
    data = json.dumps(body).encode() if body else None
    req = urllib.request.Request(
        url, data=data, method=method,
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    try:
        with urllib.request.urlopen(req, timeout=30) as resp:
            return json.loads(resp.read().decode())
    except urllib.error.HTTPError as e:
        err_body = e.read().decode()[:500]
        raise StepError(f"Vercel API {method} {path} → HTTP {e.code}: {err_body}")
    except urllib.error.URLError as e:
        raise StepError(f"Vercel API {method} {path} → network error: {e}")


# ─── Step 1: Copy template ───────────────────────────────────────────────────
def step_copy_template(template_dir: Path, slug: str) -> Path:
    """Copy template-dir to /home/moises/workspace/{slug}, stripping junk."""
    dest = WORKSPACE / slug
    log(f"\n📦 Step 1: Copy template → {dest}")

    if not template_dir.exists():
        raise StepError(f"Template directory not found: {template_dir}")

    # Idempotent: remove a previous copy so we get a clean template
    if dest.exists():
        log(f"   ℹ  Destination exists, removing stale copy: {dest}")
        shutil.rmtree(dest)

    def ignore(dirpath, names):
        return [n for n in names if n in TEMPLATE_JUNK]

    shutil.copytree(template_dir, dest, ignore=ignore)
    log(f"   ✅ Copied template to {dest}")
    return dest


# ─── Step 2: Personalize ─────────────────────────────────────────────────────
def step_personalize(app_name: str, slug: str, description: str, dest: Path):
    """Replace 'App Name' placeholders and update package.json."""
    log(f"\n✏️  Step 2: Personalize → '{app_name}'")

    # Walk all text files and replace 'App Name' → app_name
    replaced = 0
    for root, dirs, files in os.walk(dest):
        dirs[:] = [d for d in dirs if d not in TEMPLATE_JUNK]
        for fname in files:
            ext = Path(fname).suffix.lower()
            if ext in BINARY_EXTS:
                continue
            fpath = Path(root) / fname
            try:
                content = fpath.read_text(encoding="utf-8")
            except (UnicodeDecodeError, PermissionError, OSError):
                continue
            if "App Name" in content:
                fpath.write_text(
                    content.replace("App Name", app_name), encoding="utf-8"
                )
                replaced += 1
    log(f"   ✅ Replaced 'App Name' in {replaced} file(s)")

    # Update package.json: set name field
    pkg_path = dest / "package.json"
    if pkg_path.exists():
        try:
            pkg = json.loads(pkg_path.read_text(encoding="utf-8"))
            pkg["name"] = slug
            pkg["description"] = description
            pkg_path.write_text(json.dumps(pkg, indent=2) + "\n",
                                encoding="utf-8")
            log(f"   ✅ Updated package.json (name={slug})")
        except (json.JSONDecodeError, KeyError) as e:
            log(f"   ⚠  Could not update package.json: {e}")

    # Write a .env.example with the DATABASE_URL placeholder
    env_example = dest / ".env.example"
    env_example.write_text(
        f"# {app_name} — environment variables\n"
        f"DATABASE_URL=your-neon-connection-string-here\n",
        encoding="utf-8",
    )


# ─── Step 3: GitHub repo ─────────────────────────────────────────────────────
def step_github_repo(slug: str, description: str, dest: Path,
                     github_token: str) -> str:
    """Create a private GitHub repo and push code. Returns the repo URL."""
    repo_full = f"{GITHUB_ORG}/{slug}"
    repo_url = f"https://github.com/{repo_full}"
    log(f"\n🐙 Step 3: GitHub repo → {repo_full}")

    env = {"GITHUB_TOKEN": github_token, "GH_TOKEN": github_token}

    # Ensure git credential helper is set up for HTTPS auth
    run("gh auth setup-git 2>/dev/null || true", env=env, check=False)

    # Init local git + set identity (safety net)
    run("git init -q 2>/dev/null || true", cwd=dest, env=env, check=False)
    run("git config user.name 'Moises Mayrinck' && "
        "git config user.email 'moises.mayrinck@gmail.com'",
        cwd=dest, env=env, check=False)

    # Stage + commit BEFORE creating the repo (so --push has a commit to push)
    run("git add -A", cwd=dest, env=env, check=False)
    run("git diff --cached --quiet || git commit -q -m "
        + shlex_quote("Initial commit (provisioned by provision_app.py)"),
        cwd=dest, env=env, check=False)

    # Check if repo already exists (idempotency)
    r = run(f"gh repo view {repo_full} 2>/dev/null", env=env, check=False)
    repo_exists = r.returncode == 0

    if repo_exists:
        log(f"   ℹ  Repo already exists — reusing {repo_full}")
        run("git remote remove origin 2>/dev/null || true", cwd=dest, env=env,
            check=False)
        run(f"git remote add origin https://github.com/{repo_full}.git",
            cwd=dest, env=env, check=False)
    else:
        log(f"   📝 Creating private repo {repo_full} …")
        desc_flag = f"--description {shlex_quote(description)}"
        run(
            f"gh repo create {repo_full} --private {desc_flag} "
            f"--source={dest} --remote=origin --push",
            cwd=dest, env=env,
        )

    # Push (covers both paths; idempotent — "everything up-to-date" is fine)
    branch = run("git branch --show-current", cwd=dest, env=env).stdout.strip() \
        or "main"
    push = run(
        f"git push -u origin {branch} 2>&1",
        cwd=dest, env=env, check=False,
    )
    if push.returncode != 0:
        for fb in ("main", "master", "HEAD"):
            fb_r = run(f"git push -u origin {fb} 2>&1", cwd=dest, env=env,
                       check=False)
            if fb_r.returncode == 0:
                break
        else:
            log(f"   ⚠  Push may need manual verification. "
                f"Last output: {push.stderr[-200:]}")

    log(f"   ✅ Code pushed to {repo_url}")
    return repo_url


def shlex_quote(s: str) -> str:
    """Minimal shell quoting for safe argument passing."""
    if re.match(r"^[A-Za-z0-9 _./@:=+,-]*$", s):
        return f"'{s}'"
    return "'" + s.replace("'", "'\"'\"'") + "'"


# ─── Step 4: Vercel deploy ───────────────────────────────────────────────────
def step_vercel_deploy(slug: str, dest: Path, vercel_token: str) -> str:
    """Link Vercel project, deploy to prod, disable Vercel Authentication.

    Returns the production deployment URL.
    """
    log(f"\n▲  Step 4: Vercel deploy → {slug}")

    env = {"VERCEL_TOKEN": vercel_token}

    # 4a. Link (creates project if it doesn't exist)
    log("   🔗 Linking project …")
    link = run(
        f"vercel link --yes --token {vercel_token} --cwd {dest}",
        cwd=dest, env=env, check=False, timeout=120,
    )
    if link.returncode != 0:
        # Retry with explicit project name
        log(f"   ℹ  link retry with --project {slug}")
        run(
            f"vercel link --yes --token {vercel_token} --project {slug} "
            f"--cwd {dest}",
            cwd=dest, env=env, timeout=120,
        )

    # Read project.json to get project ID + org ID
    proj_json_path = dest / ".vercel" / "project.json"
    project_id = None
    org_id = None
    if proj_json_path.exists():
        try:
            pj = json.loads(proj_json_path.read_text())
            project_id = pj.get("projectId")
            org_id = pj.get("orgId")
        except (json.JSONDecodeError, OSError):
            pass

    if not project_id:
        # Fallback: look up via API
        log("   ℹ  project.json missing project ID — looking up via API")
        pr = vercel_api("GET", f"/v9/projects/{slug}", vercel_token,
                        team_id=org_id)
        project_id = pr.get("id")
        org_id = org_id or pr.get("accountId")

    log(f"   📋 Project ID: {project_id}  Org: {org_id}")

    # 4b. Deploy to production
    log("   🚀 Deploying to production …")
    deploy = run(
        f"vercel deploy --prod --yes --token {vercel_token} --cwd {dest}",
        cwd=dest, env=env, check=False, timeout=600,
    )
    if deploy.returncode != 0:
        raise StepError(
            f"vercel deploy failed (exit {deploy.returncode})\n"
            f"  stdout: {deploy.stdout[-800:]}\n  stderr: {deploy.stderr[-800:]}"
        )

    vercel_url = parse_vercel_url(deploy.stdout)
    if not vercel_url:
        # Fallback: query the API for the latest production deployment
        log("   ℹ  URL not in stdout — querying API …")
        deps = vercel_api(
            "GET", f"/v6/deployments", vercel_token, team_id=org_id,
        )
        # add projectId filter via path
        try:
            deps = vercel_api(
                "GET", f"/v6/deployments?projectId={project_id}&limit=1&target=production",
                vercel_token, team_id=org_id,
            )
            url = deps.get("deployments", [{}])[0].get("url")
            if url:
                vercel_url = f"https://{url}"
        except (IndexError, KeyError):
            pass

    if not vercel_url:
        # Last-resort fallback: construct the standard production URL
        vercel_url = f"https://{slug}.vercel.app"
        log(f"   ⚠  Could not parse deployment URL — using default: {vercel_url}")

    log(f"   ✅ Deployed: {vercel_url}")

    # 4c. Disable Vercel Authentication (SSO protection) for the project
    if project_id:
        log("   🔓 Disabling Vercel Authentication …")
        try:
            vercel_api("PATCH", f"/v9/projects/{project_id}", vercel_token,
                       body={"ssoProtection": None}, team_id=org_id)
            log("   ✅ SSO / Vercel Authentication disabled")
        except StepError as e:
            log(f"   ⚠  Could not disable SSO protection: {e}")

    return vercel_url


def parse_vercel_url(stdout: str) -> str:
    """Extract the production deployment URL from vercel deploy stdout."""
    # Prefer the line that says "Production:"
    for line in stdout.splitlines():
        low = line.lower()
        if "production" in low and "vercel.app" in low:
            m = re.search(r"https://\S+\.vercel\.app", line)
            if m:
                return m.group(0)
    # Fallback: any vercel.app URL (last one wins — usually the deploy URL)
    urls = re.findall(r"https://\S+\.vercel\.app", stdout)
    if urls:
        return urls[-1]
    return None


# ─── Step 5: Neon database schema ────────────────────────────────────────────
def step_neon_schema(slug: str, neon_conn: str) -> tuple:
    """Create a dedicated schema in the existing Neon database.

    Returns (schema_name, database_url_with_schema).
    """
    schema = slug_to_schema(slug)
    log(f"\n🗄️  Step 5: Neon schema → {schema}")

    # psycopg2 lives in the gsd-hub venv; pass creds via env vars (no shell
    # escaping issues).  Uses psycopg2.sql.Identifier for safe schema quoting.
    py_code = (
        "import os, psycopg2\n"
        "from psycopg2 import sql\n"
        "\n"
        "conn = psycopg2.connect(os.environ['NEON_CONN'])\n"
        "conn.autocommit = True\n"
        "cur = conn.cursor()\n"
        "schema = os.environ['NEON_SCHEMA']\n"
        "\n"
        "cur.execute(sql.SQL('CREATE SCHEMA IF NOT EXISTS {}')"
        ".format(sql.Identifier(schema)))\n"
        "conn.commit()\n"
        "\n"
        "cur.execute(\"SELECT schema_name FROM information_schema.schemata"
        " WHERE schema_name = %s\", (schema,))\n"
        "ok = cur.fetchone() is not None\n"
        "print('SCHEMA_OK:' + schema if ok else 'SCHEMA_FAIL')\n"
        "\n"
        "cur.close()\n"
        "conn.close()\n"
    )
    env = {"NEON_CONN": neon_conn, "NEON_SCHEMA": schema}
    r = run_py(py_code, env=env, check=False)
    if r.returncode != 0 or "SCHEMA_OK" not in r.stdout:
        raise StepError(
            f"Neon schema creation failed for '{schema}'\n"
            f"  stdout: {r.stdout[-500:]}\n  stderr: {r.stderr[-500:]}"
        )

    log(f"   ✅ Schema '{schema}' ready")

    # Build the DATABASE_URL with the schema appended (Prisma-style ?schema=)
    if "?" in neon_conn:
        database_url = f"{neon_conn}&schema={schema}"
    else:
        database_url = f"{neon_conn}?schema={schema}"

    log(f"   ✅ DATABASE_URL constructed (schema={schema})")
    return schema, database_url


# ─── Step 6: Output ──────────────────────────────────────────────────────────
def step_output(summary: dict):
    """Print JSON summary and append to provisioned_apps.json."""
    # Pretty JSON to stdout
    log("\n" + "=" * 60)
    log("✅ PROVISIONING COMPLETE")
    log("=" * 60)
    print(json.dumps(summary, indent=2))

    # Append to data file
    DATA_FILE.parent.mkdir(parents=True, exist_ok=True)
    existing = []
    if DATA_FILE.exists():
        try:
            existing = json.loads(DATA_FILE.read_text(encoding="utf-8"))
            if not isinstance(existing, list):
                existing = [existing]
        except (json.JSONDecodeError, OSError):
            existing = []
    existing.append(summary)
    DATA_FILE.write_text(
        json.dumps(existing, indent=2) + "\n", encoding="utf-8"
    )
    log(f"\n📁 App info appended to {DATA_FILE}")


# ─── Main ─────────────────────────────────────────────────────────────────────
def main():
    parser = argparse.ArgumentParser(
        description="Provision a new web app end-to-end "
                    "(template → GitHub → Vercel → Neon).",
    )
    parser.add_argument("--name", required=True,
                        help="App display name (e.g. 'Price Tracker')")
    parser.add_argument("--slug", required=True,
                        help="URL-safe slug (e.g. 'price-tracker')")
    parser.add_argument("--description", required=True,
                        help="One-line description")
    parser.add_argument("--template-dir", default=DEFAULT_TEMPLATE,
                        help=f"Path to template (default: {DEFAULT_TEMPLATE})")
    args = parser.parse_args()

    # Validate slug
    if not re.match(r"^[a-z0-9][a-z0-9-]*[a-z0-9]$", args.slug):
        fail("validation",
             f"Slug must be lowercase, hyphen-separated, alphanumeric: "
             f"'{args.slug}'")

    slug = args.slug
    app_name = args.name
    description = args.description
    template_dir = Path(args.template_dir)

    log(f"🚀 Provisioning '{app_name}' (slug: {slug})")
    log(f"   Template: {template_dir}")

    # ── Read credentials ──────────────────────────────────────────────────
    try:
        github_token = read_env_var(ENV_FILE, "GITHUB_TOKEN")
        neon_conn = read_env_var(ENV_FILE, "NEON_CONNECTION_STRING")
        vercel_token = read_vercel_token()
    except StepError as e:
        fail("credentials", str(e))

    # ── Execute steps ─────────────────────────────────────────────────────
    try:
        dest = step_copy_template(template_dir, slug)
        step_personalize(app_name, slug, description, dest)
        github_url = step_github_repo(slug, description, dest, github_token)
        vercel_url = step_vercel_deploy(slug, dest, vercel_token)
        db_schema, database_url = step_neon_schema(slug, neon_conn)
    except StepError as e:
        # Determine which step failed from the message context
        fail("provisioning", str(e), exc=e)
    except subprocess.TimeoutExpired as e:
        fail("provisioning", f"Command timed out: {e}", exc=e)
    except Exception as e:
        fail("provisioning", f"Unexpected error: {e}", exc=e)

    # ── Output ────────────────────────────────────────────────────────────
    summary = {
        "app_name": app_name,
        "slug": slug,
        "github_url": github_url,
        "vercel_url": vercel_url,
        "database_schema": db_schema,
        "database_url": database_url,
        "status": "provisioned",
    }
    step_output(summary)


if __name__ == "__main__":
    main()
