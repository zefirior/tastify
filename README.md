# Tastify

## Structure
 * /front - UI over react
 * /back - backend over Python
 * /scripts - common scripts (deploy/tests...)

## Links
 * [notion](https://www.notion.so/Tastify-1778e2cd4ea98093a2e5d30b602115f6)

## Run app locally in docker
```bash
docker compose --file ./docker/local.docker-compose.yaml up
```

## Deploying the App
Update remote through ssh
```bash
ssh tastify "bash -s" < ./scripts/update_remote.sh
```
