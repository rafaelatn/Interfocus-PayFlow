# Botpress Studio + PayFlow

## 1. URL do backend

O Botpress Cloud precisa acessar uma URL publica. Se o FastAPI estiver local,
publique com Render/Railway/VPS ou use ngrok:

```powershell
python -m uvicorn app.main:app --host 127.0.0.1 --port 8000
ngrok http 8000
```

No Botpress Studio, crie uma configuracao/variavel:

```text
PAYFLOW_API_URL=https://sua-url-publica
```

Sem barra no final.

## 2. Variaveis de workflow

Crie estas variaveis no Botpress:

```text
workflow.nome_cliente
workflow.valor_inadimplencia
workflow.dias_inadimplencia
workflow.tipo_risco
workflow.bairro
workflow.consulta_ia
workflow.resposta_payflow
workflow.cliente_payflow
workflow.resultados_payflow
```

## 3. Execute Code: cadastrar cliente

Use depois de coletar nome, valor, dias, risco e bairro.

```js
const API_BASE = env.PAYFLOW_API_URL?.replace(/\/$/, '')

if (!API_BASE) {
  throw new Error('Configure PAYFLOW_API_URL nas configuracoes do Botpress.')
}

const cliente = {
  nome_cliente: workflow.nome_cliente,
  valor_inadimplencia: Number(String(workflow.valor_inadimplencia).replace(',', '.')),
  dias_inadimplencia: Number(workflow.dias_inadimplencia),
  tipo_risco: workflow.tipo_risco || 'Médio',
  bairro: workflow.bairro,
  tentativas_cobranca: 0
}

if (!cliente.nome_cliente) throw new Error('Nome do cliente nao informado.')
if (!cliente.bairro) throw new Error('Bairro nao informado.')
if (!Number.isFinite(cliente.valor_inadimplencia)) throw new Error('Valor invalido.')
if (!Number.isFinite(cliente.dias_inadimplencia)) throw new Error('Dias de atraso invalido.')

const { data } = await axios.post(`${API_BASE}/botpress/clientes`, cliente, {
  headers: { 'Content-Type': 'application/json' },
  timeout: 120000
})

workflow.cliente_payflow = data.cliente
workflow.resposta_payflow = data.mensagem
```

Depois coloque um Text Card:

```text
{{workflow.resposta_payflow}}
```

## 4. Execute Code: buscar clientes com IA

Use quando o usuario pedir algo como:

```text
clientes de alto risco no Palmital
dividas altas perto do Centro
clientes com muitos dias de atraso no Alto Cafezal
```

```js
const API_BASE = env.PAYFLOW_API_URL?.replace(/\/$/, '')

if (!API_BASE) {
  throw new Error('Configure PAYFLOW_API_URL nas configuracoes do Botpress.')
}

const consulta = workflow.consulta_ia || event.preview

if (!consulta) {
  throw new Error('Consulta nao informada.')
}

const { data } = await axios.post(`${API_BASE}/botpress/buscar-clientes`, {
  consulta,
  limite: 5
}, {
  headers: { 'Content-Type': 'application/json' },
  timeout: 120000
})

workflow.resultados_payflow = data.resultados
workflow.resposta_payflow = data.mensagem
```

Depois coloque um Text Card:

```text
{{workflow.resposta_payflow}}
```

## 5. Fluxo recomendado

### Cadastro

```text
Usuario: cadastrar cliente
Bot: Qual o nome?
Bot: Qual o valor em atraso?
Bot: Quantos dias de atraso?
Bot: Qual o risco? Baixo, Medio ou Alto?
Bot: Qual o bairro de Marilia?
Execute Code: cadastrar cliente
Bot: {{workflow.resposta_payflow}}
```

### Busca IA

```text
Usuario: buscar clientes de alto risco no Palmital
Execute Code: buscar clientes com IA
Bot: {{workflow.resposta_payflow}}
```
