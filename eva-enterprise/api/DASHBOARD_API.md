# 📊 Dashboard API - EVA-back

## Endpoints Disponíveis

Todas as rotas estão sob `/api/v1/dashboard/`

### 1. Health Triage Metrics
**GET** `/api/v1/dashboard/health-triage`

Retorna métricas de triagem de saúde (Thinking Mode).

**Response**:
```json
{
  "total_analises": 150,
  "hoje": 12,
  "semana": 45,
  "mes": 150,
  "criticos": 5,
  "altos": 15,
  "medios": 50,
  "baixos": 80,
  "notificados": 20,
  "tempo_medio_notificacao_seg": 45.5
}
```

---

### 2. A/B Testing Results
**GET** `/api/v1/dashboard/ab-testing`

Compara performance entre Thinking Mode e Normal Mode.

**Response**:
```json
[
  {
    "metric": "response_time_ms",
    "group_a": "thinking_mode",
    "mean_a": 1250.5,
    "samples_a": 100,
    "group_b": "normal_mode",
    "mean_b": 850.2,
    "samples_b": 98,
    "difference_percent": -32.0,
    "winner": "Grupo B Melhor"
  }
]
```

---

### 3. Medical Images Statistics
**GET** `/api/v1/dashboard/medical-images`

Estatísticas de análise de imagens médicas.

**Response**:
```json
[
  {
    "image_type": "prescription",
    "total": 50,
    "requer_atencao": 5,
    "notificados": 5,
    "ultimas_24h": 10
  },
  {
    "image_type": "malaria_smear",
    "total": 25,
    "requer_atencao": 8,
    "notificados": 8,
    "ultimas_24h": 3
  }
]
```

---

### 4. Epidemiological Data (Heatmap)
**GET** `/api/v1/dashboard/epidemiological`

Dados para mapa epidemiológico (últimos 30 dias).

**Response**:
```json
[
  {
    "tipo_caso": "malaria_smear",
    "total_casos": 15,
    "casos_graves": 3,
    "coordenadas": "(-23.5505,-46.6333)",
    "data": "2026-01-15T00:00:00"
  }
]
```

---

### 5. Malaria Cases
**GET** `/api/v1/dashboard/malaria-cases`

Casos de malária detectados (últimos 50).

**Response**:
```json
[
  {
    "id": 123,
    "paciente_nome": "João Silva",
    "parasitemia": "2.5%",
    "especie": "P. falciparum",
    "gravidade": "MÉDIO",
    "coordenadas": "POINT(-23.5505 -46.6333)",
    "data_diagnostico": "2026-01-15T10:30:00"
  }
]
```

---

### 6. TB Screening
**GET** `/api/v1/dashboard/tb-screening`

Triagens de tuberculose via raio-X.

**Response**:
```json
[
  {
    "id": 456,
    "paciente_nome": "Maria Santos",
    "probabilidade_tb": "0.85",
    "achados": "Infiltrado apical direito",
    "requer_confirmacao": true,
    "coordenadas": "POINT(-23.5505 -46.6333)",
    "created_at": "2026-01-15T11:00:00"
  }
]
```

---

### 7. Rapid Tests
**GET** `/api/v1/dashboard/rapid-tests`

Resultados de testes rápidos (COVID, HIV, Dengue).

**Response**:
```json
[
  {
    "id": 789,
    "paciente_nome": "Pedro Costa",
    "tipo_teste": "COVID-19",
    "fabricante": "Abbott",
    "resultado": "POSITIVE",
    "confianca": "0.98",
    "coordenadas": "POINT(-23.5505 -46.6333)",
    "created_at": "2026-01-15T09:00:00"
  }
]
```

---

### 8. Skin Lesions
**GET** `/api/v1/dashboard/skin-lesions`

Lesões cutâneas analisadas (Mpox, melanoma).

**Response**:
```json
[
  {
    "id": 321,
    "paciente_nome": "Ana Lima",
    "tipo_lesao": "Vesícula",
    "prob_mpox": "0.75",
    "risco_melanoma": "BAIXO",
    "gravidade": "MÉDIO",
    "requer_atencao": true,
    "created_at": "2026-01-15T08:30:00"
  }
]
```

---

### 9. System Health
**GET** `/api/v1/dashboard/system-health`

Métricas de saúde do sistema.

**Response**:
```json
{
  "status": "healthy",
  "active_users_24h": 45,
  "total_analyses_today": 120,
  "database_connected": true
}
```

---

## Implementação no EVA-Front

### Exemplo de uso com SWR:

```typescript
// hooks/useDashboard.ts
import useSWR from 'swr'

const fetcher = (url: string) => fetch(url).then(r => r.json())

export function useHealthTriageMetrics() {
  return useSWR('/api/v1/dashboard/health-triage', fetcher, {
    refreshInterval: 30000 // Auto-refresh a cada 30s
  })
}

export function useABTestingResults() {
  return useSWR('/api/v1/dashboard/ab-testing', fetcher)
}

export function useMedicalImageStats() {
  return useSWR('/api/v1/dashboard/medical-images', fetcher)
}

export function useEpidemiologicalData() {
  return useSWR('/api/v1/dashboard/epidemiological', fetcher)
}
```

### Exemplo de componente:

```typescript
// pages/dashboard/index.tsx
import { useHealthTriageMetrics } from '@/hooks/useDashboard'

export default function DashboardPage() {
  const { data, error, isLoading } = useHealthTriageMetrics()
  
  if (isLoading) return <div>Carregando...</div>
  if (error) return <div>Erro ao carregar dados</div>
  
  return (
    <div className="grid grid-cols-3 gap-4">
      <MetricCard 
        title="Total de Análises" 
        value={data.total_analises} 
      />
      <MetricCard 
        title="Hoje" 
        value={data.hoje} 
      />
      <MetricCard 
        title="Críticos" 
        value={data.criticos}
        variant="danger"
      />
    </div>
  )
}
```

---

## Autenticação

Todas as rotas do dashboard devem ser protegidas. Adicione middleware de autenticação conforme necessário.

---

## Testes

```bash
# Testar endpoint
curl http://localhost:8000/api/v1/dashboard/health-triage

# Com autenticação
curl -H "Authorization: Bearer TOKEN" \
     http://localhost:8000/api/v1/dashboard/health-triage
```
