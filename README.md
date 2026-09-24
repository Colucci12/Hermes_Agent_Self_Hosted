# Hermes Agent Self Hosted

Stack Docker de um agente pessoal: Hermes (agente + API), Perlite (notas do vault) e Traefik no home server.

## No PC

1. Copie o template de ambiente e troque as senhas:

```powershell
copy .env.example .env
```

2. Suba a stack:

```powershell
docker compose up -d
```

| Serviço | Endereço |
|---|---|
| Notas (Perlite) | http://localhost:8080 |
| Dashboard Hermes | http://localhost:9119 |

O agente só responde depois de configurar uma chave de LLM no dashboard do Hermes, em **Keys** (ou nas variáveis comentadas do `.env`). Memória extra do agente é o **Holographic** (SQLite local, ligado no boot). Extração automática de fatos fica **desligada** — o agente grava fato com a tool quando fizer sentido.

O vault no container do Hermes é `/obsidian` (`OBSIDIAN_VAULT_PATH`). A imagem Docker só deixa o `write_file` gravar em `/opt/data`; por isso `HERMES_WRITE_SAFE_ROOT=/opt/data:/obsidian`. O Perlite lê a mesma pasta no host: `obsidian/vaults/Pessoal`.

## No home server (Portainer + Traefik)

Arquivo do stack no Portainer: `docker-compose.homeserver.yml`. Só o link do Git + as envs; o sidecar do grafo usa `python:3.12-alpine` (imagem pública) e os scripts que já vêm no repositório.

No `.env` do servidor, preencha os hosts (`NOTES_HOST`, `HERMES_HOST`) e o hash do basicAuth (`TRAEFIK_BASIC_AUTH_USERS`). Gere o hash com:

```bash
htpasswd -nbB admin SUA_SENHA
```

Cole o resultado entre aspas simples, com `$` simples (sem `$$`).

| Serviço | Auth |
|---|---|
| Perlite | basicAuth do Traefik |
| Dashboard Hermes | basicAuth do Traefik + login do Hermes |

O vault em `obsidian/vaults/Pessoal` começa vazio. O sidecar `perlite-graph` monta o `metadata.json` do grafo sozinho quando nascer nota.

## O que não entra no Git

- `.env` (segredos)
- `hermes/data/` (estado, sessões, memória do agente)
- `obsidian/vaults/Pessoal/metadata.json` (gerado pelo sidecar)
