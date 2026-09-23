# Hermes Agent Self Hosted

Stack Docker de um agente pessoal: Hermes (cérebro + API), Open WebUI (chat no browser), Perlite (notas do vault) e Traefik no home server.

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
| Chat (Open WebUI) | http://localhost:3000 |
| Notas (Perlite) | http://localhost:8080 |
| Dashboard Hermes | http://localhost:9119 |
| API do Hermes | http://localhost:8642/v1 |

O primeiro usuário que você cadastrar no Open WebUI vira admin. O chat só responde depois de colar uma chave de LLM no dashboard do Hermes, em **Keys** (ou nas variáveis comentadas do `.env`).

O Open WebUI é só a boca: RAG/documentos dele estão desligados. Título, follow-up, tags e autocomplete também — cada um virava uma sessão extra no Hermes. Memória extra do agente é o **Holographic** (SQLite local, ligado no boot). Extração automática de fatos fica **desligada** — o agente grava fato com a tool quando fizer sentido.

O vault do Obsidian no container é `/vaults/Pessoal`. No boot o Hermes copia `OBSIDIAN_VAULT_PATH` para o `.env` interno; sem isso a skill cai em `~/Documents/Obsidian Vault` e grava fora do Perlite.

A API exige `Authorization: Bearer <API_SERVER_KEY>`. Sem token ela responde `401`.

## No home server (Portainer + Traefik)

Arquivo do stack no Portainer: `docker-compose.homeserver.yml`. Só o link do Git + as envs; o sidecar do grafo usa `python:3.12-alpine` (imagem pública) e os scripts que já vêm no repositório.

No `.env` do servidor, preencha os hosts (`CHAT_HOST`, `NOTES_HOST`, `HERMES_HOST`, `API_HOST`) e o hash do basicAuth (`TRAEFIK_BASIC_AUTH_USERS`). Gere o hash com:

```bash
htpasswd -nbB admin SUA_SENHA
```

Cole o resultado entre aspas simples, com `$` simples (sem `$$`).

| Serviço | Auth |
|---|---|
| Open WebUI | conta própria do Open WebUI |
| Perlite | basicAuth do Traefik |
| Dashboard Hermes | basicAuth do Traefik + login do Hermes |
| API Hermes | só HTTPS + Bearer `API_SERVER_KEY` (sem basicAuth, senão o app do celular quebra) |

O vault em `obsidian/vaults/Pessoal` começa vazio. O sidecar `perlite-graph` monta o `metadata.json` do grafo sozinho quando nascer nota.

## O que não entra no Git

- `.env` (segredos)
- `hermes/data/` (estado, sessões, memória do agente)
- `open-webui/data/` (contas e histórico do chat)
- `obsidian/vaults/Pessoal/metadata.json` (gerado pelo sidecar)
