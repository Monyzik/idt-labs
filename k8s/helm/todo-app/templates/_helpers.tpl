{{/*
Expand the name of the chart.
*/}}
{{- define "todo-app.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
We truncate at 63 chars because some Kubernetes name fields are limited to this (by the DNS naming spec).
If release name contains chart name it will be used as a full name.
*/}}
{{- define "todo-app.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := include "todo-app.name" . -}}
{{- if contains $name .Release.Name -}}
{{- .Release.Name | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- printf "%s-%s" .Release.Name $name | trunc 63 | trimSuffix "-" -}}
{{- end -}}
{{- end -}}
{{- end -}}

{{/*
Create chart name and version as used by the chart label.
*/}}
{{- define "todo-app.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Common labels
*/}}
{{- define "todo-app.labels" -}}
helm.sh/chart: {{ include "todo-app.chart" . }}
{{ include "todo-app.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Selector labels
*/}}
{{- define "todo-app.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-app.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{/*
Shared resource names
*/}}
{{- define "todo-app.configMapName" -}}
{{- .Values.config.name | default "todo-app-config" -}}
{{- end -}}

{{- define "todo-app.dbDeploymentName" -}}
{{- .Values.database.deploymentName | default "todo-app-db" -}}
{{- end -}}

{{- define "todo-app.dbServiceName" -}}
{{- .Values.database.serviceName | default "todo-app-db" -}}
{{- end -}}

{{- define "todo-app.dbSecretName" -}}
{{- if .Values.database.auth.existingSecret -}}
{{- .Values.database.auth.existingSecret -}}
{{- else -}}
{{- .Values.database.secretName | default "todo-app-db-secret" -}}
{{- end -}}
{{- end -}}

{{- define "todo-app.dbPvcName" -}}
{{- .Values.database.persistence.pvcName | default "todo-app-db-pvc" -}}
{{- end -}}

{{- define "todo-app.todoDeploymentName" -}}
{{- .Values.todo.deploymentName | default "todo-app" -}}
{{- end -}}

{{- define "todo-app.todoServiceName" -}}
{{- .Values.todo.serviceName | default "todo-app-service" -}}
{{- end -}}

{{- define "todo-app.ingressName" -}}
{{- .Values.ingress.name | default "todo-app-ingress" -}}
{{- end -}}

{{- define "todo-app.todoDatabaseUrl" -}}
{{- if .Values.todo.databaseUrl -}}
{{- .Values.todo.databaseUrl -}}
{{- else -}}
{{- printf "postgresql://%s:%s@%s:%v/%s" .Values.database.auth.username .Values.database.auth.password (include "todo-app.dbServiceName" .) .Values.database.port .Values.config.postgresDb -}}
{{- end -}}
{{- end -}}
