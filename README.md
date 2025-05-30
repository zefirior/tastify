# Tastify

## Structure
 * /front - UI over react
 * /back - backend over Python
 * /scripts - common scripts (deploy/tests...)

## Links
 * [notion](https://www.notion.so/GameThingsDone-1a58e2cd4ea9807483b1d2e46b4e3361)

## Run app locally in docker
```bash
docker compose --file ./docker/local.docker-compose.yaml up -d --build && sleep 1
open http://localhost:5173
```

## Deploying the App
Update the remote server manually with:
```bash
bash ./scripts/update_remote.sh
```
Deployment is also triggered automatically by GitHub Actions when pushing to
`main` or updating a pull request. The workflow connects to the server over SSH
and runs the same update commands.

## Test
1. Install requirements
```bash
bash ./scripts/local-install.sh
```
2. Run tests
```bash
pytest back
```
