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

Arquivo do stack no Portainer: `docker-compose.homeserver.yml`. Ao implantar pelo repositório, configure as variáveis no formulário da stack; não é necessário ter um arquivo `.env` no repositório. O sidecar do grafo usa `python:3.12-alpine` (imagem pública) e os scripts que já vêm no repositório.

Nas variáveis da stack, preencha `NOTES_HOST`, `HERMES_HOST`, `TRAEFIK_BASIC_AUTH_USERS`, `HERMES_DASHBOARD_BASIC_AUTH_USERNAME`, `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD` e `HERMES_DASHBOARD_BASIC_AUTH_SECRET`. O Traefik protege apenas o Perlite. O dashboard Hermes usa seu próprio login com usuário e senha; não há middleware de autenticação Traefik nessa rota. Gere o hash bcrypt do Perlite com:

```bash
htpasswd -nbB admin SUA_SENHA
```

No formulário de variáveis da stack do Portainer, escape cada `$` como `$$` no hash `TRAEFIK_BASIC_AUTH_USERS`. O Portainer/Compose reduz `$$` a `$` ao criar o container; colar o hash com `$` simples pode remover trechos dele. A senha do Hermes é texto simples na variável `HERMES_DASHBOARD_BASIC_AUTH_PASSWORD`. Em um `.env` usado diretamente pelo Docker Compose, use `$` simples no hash.

O compose do home server não monta arquivos do checkout do Git no host: a configuração do Nginx e o código do grafo ficam no próprio compose, e o vault e o estado do Hermes ficam em volumes Docker nomeados. Isso permite implantar pelo Git no Portainer CE sem depender do recurso Business Edition para copiar bind mounts relativos. Um serviço de inicialização transfere a propriedade do volume do vault para o UID 10000 usado pelo Hermes antes de subir os serviços; sem isso, um volume novo pode ser legível, mas não gravável pelo Hermes.

O sidecar do grafo verifica mudanças a cada 10 segundos. Ele só relê o conteúdo das notas quando o nome, tamanho ou data de modificação muda; os backlinks são montados em uma passagem pelos links. O processamento roda em CPU e não precisa de GPU. O grafo visual usa `vis.js` no navegador ([documentação do Perlite](https://github.com/secure-77/Perlite/wiki/Graph)).

O Perlite publica e permite consultar as notas em uma interface web; ele não é o aplicativo completo do Obsidian. O próprio Obsidian informa que seu aplicativo oficial não está disponível como aplicação web ([Obsidian Help](https://obsidian.md/help/teams/deploy)).

| Serviço | Auth |
|---|---|
| Perlite | basicAuth do Traefik |
| Dashboard Hermes | login próprio do Hermes |

No compose local, o vault fica em `obsidian/vaults/Pessoal`. No home server, o volume Docker `obsidian_vault` é compartilhado entre Hermes e Perlite e começa vazio. O sidecar `perlite-graph` gera o `metadata.json` do grafo quando surgem notas.

## O que não entra no Git

- `.env` (segredos)
- `hermes/data/` (estado, sessões, memória do agente)
- `obsidian/vaults/Pessoal/metadata.json` (gerado pelo sidecar)
