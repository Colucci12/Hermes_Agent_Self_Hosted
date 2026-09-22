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

A API exige `Authorization: Bearer <API_SERVER_KEY>`. Sem token ela responde `401`.

## No home server (Portainer + Traefik)

Arquivo completo, sem portas no host:

```bash
docker compose -f docker-compose.homeserver.yml up -d
```

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

## O que não entra no Git

- `.env` (segredos)
- `hermes/data/` (estado, sessões, memória do agente)
- `open-webui/data/` (contas e histórico do chat)
