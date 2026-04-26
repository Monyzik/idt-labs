# todo-app Helm

В этом chart нет секретов в `values.yaml`.

Перед установкой создайте:

- `secret-dev.yaml` по образцу `secret-dev.example.yaml`
- `secret-prod.yaml` по образцу `secret-prod.example.yaml`

Затем примените Secret и только после этого устанавливайте chart.

## Dev

```bash
kubectl apply -f ./k8s/helm/todo-app/secret-dev.yaml -n todo-demo

helm upgrade --install todo-app ./k8s/helm/todo-app \
  --namespace todo-demo --create-namespace \
  -f ./k8s/helm/todo-app/values-dev.yaml
```

## Prod

```bash
kubectl apply -f ./k8s/helm/todo-app/secret-prod.yaml -n todo-prod

helm upgrade --install todo-app ./k8s/helm/todo-app \
  --namespace todo-prod --create-namespace \
  -f ./k8s/helm/todo-app/values-prod.yaml
```
