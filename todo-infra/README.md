# todo-infra

Отдельный каталог инфраструктуры PostgreSQL для приложения `todo-app`.

## Контракт для приложения

- DNS-имя headless service: `postgres`
- DNS-имя pod в dev: `postgres-0.postgres`
- FQDN для доступа из другого namespace: `postgres-0.postgres.<namespace>.svc.cluster.local`
- Порт: `5432`
- База данных: `todo_db`
- Пользователь и пароль задаются через отдельный `secret.yaml` инфраструктуры

Пример строки подключения:

```text
postgresql://user:password@postgres-0.postgres:5432/todo_db
```

Пример меж-namespace подключения:

```text
postgresql://user:password@postgres-0.postgres.todo-data.svc.cluster.local:5432/todo_db
```

## Порядок деплоя

Сначала инфраструктура, затем приложение.

### Helm

Сначала создайте файл `secret-dev.yaml` по образцу `secret-dev.example.yaml`, затем примените Secret:

```bash
kubectl apply -f ./k8s/helm/postgres-infra/secret-dev.yaml -n todo-demo
```

```bash
helm upgrade --install todo-infra ./k8s/helm/postgres-infra \
  --namespace todo-demo --create-namespace \
  -f ./k8s/helm/postgres-infra/values-dev.yaml
```

### Kustomize

```bash
kubectl apply -k k8s/kustomization/overlays/dev
```
