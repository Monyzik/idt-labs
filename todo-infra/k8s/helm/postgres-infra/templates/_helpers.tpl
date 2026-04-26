{{/*
Expand the name of the chart.
*/}}
{{- define "todo-infra.name" -}}
{{- default .Chart.Name .Values.nameOverride | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Create a default fully qualified app name.
*/}}
{{- define "todo-infra.fullname" -}}
{{- if .Values.fullnameOverride -}}
{{- .Values.fullnameOverride | trunc 63 | trimSuffix "-" -}}
{{- else -}}
{{- $name := include "todo-infra.name" . -}}
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
{{- define "todo-infra.chart" -}}
{{- printf "%s-%s" .Chart.Name .Chart.Version | replace "+" "_" | trunc 63 | trimSuffix "-" -}}
{{- end -}}

{{/*
Common labels
*/}}
{{- define "todo-infra.labels" -}}
helm.sh/chart: {{ include "todo-infra.chart" . }}
{{ include "todo-infra.selectorLabels" . }}
{{- if .Chart.AppVersion }}
app.kubernetes.io/version: {{ .Chart.AppVersion | quote }}
{{- end }}
app.kubernetes.io/managed-by: {{ .Release.Service }}
{{- end -}}

{{/*
Selector labels
*/}}
{{- define "todo-infra.selectorLabels" -}}
app.kubernetes.io/name: {{ include "todo-infra.name" . }}
app.kubernetes.io/instance: {{ .Release.Name }}
{{- end -}}

{{- define "todo-infra.dbDeploymentName" -}}
{{- .Values.database.deploymentName | default "postgres" -}}
{{- end -}}

{{- define "todo-infra.dbServiceName" -}}
{{- .Values.database.serviceName | default "postgres" -}}
{{- end -}}

{{- define "todo-infra.dbSecretName" -}}
{{- .Values.database.secretName | default "postgres-secret" -}}
{{- end -}}

{{- define "todo-infra.dbPvcName" -}}
{{- .Values.database.persistence.pvcName | default "postgres-pvc" -}}
{{- end -}}
