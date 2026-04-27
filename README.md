## Todo приложение

Короткая инструкция для запуска основного приложения

### Подготовка секретов

Создание секретов из примеров

```bash
cp todo-infra/k8s/helm/postgres-infra/secret-dev.example.yaml todo-infra/k8s/helm/postgres-infra/secret-dev.yaml
cp k8s/helm/todo-app/secret-dev.example.yaml k8s/helm/todo-app/secret-dev.yaml
kubectl apply -f todo-infra/k8s/helm/postgres-infra/secret-dev.yaml
kubectl apply -f k8s/helm/todo-app/secret-dev.yaml
```

### Запуск PostgreSQL

```bash
helm upgrade --install todo-db ./todo-infra/k8s/helm/postgres-infra \
  -n default \
  -f ./todo-infra/k8s/helm/postgres-infra/values.yaml \
  -f ./todo-infra/k8s/helm/postgres-infra/values-dev.yaml
```

### Запуск приложения

```bash
helm upgrade --install todo-app-v1 ./k8s/helm/todo-app \
  -n default \
  -f ./k8s/helm/todo-app/values.yaml \
  -f ./k8s/helm/todo-app/values-dev.yaml
```

### Проверка

```bash
kubectl get pods,svc,ingress -n default
kubectl rollout status deployment/todo-app -n default
kubectl rollout status statefulset/postgres -n default
```

Проверка API:

```bash
curl -H "Host: todo.local" http://127.0.0.1/api/health/
```
