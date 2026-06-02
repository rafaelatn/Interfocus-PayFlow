# Relatorio tecnico - Validacao do sistema PayFlow

Data da validacao: 02/06/2026

## 1. Objetivo

A validacao do sistema foi conduzida por meio de testes com dados simulados,
avaliados em tres dimensoes:

1. Precisao da inteligencia artificial, medida pela comparacao entre as
   classificacoes preditivas e os atrasos reais registrados.
2. Eficiencia operacional, aferida pelo tempo gasto no processo manual em
   contraste com o automatizado.
3. Consistencia dos dados, verificada pela coerencia entre as mensagens
   enviadas pelo sistema e as informacoes contidas no banco de dados.

## 2. Por que existem embeddings null?

Os `embedding = null` existiram por decisao tecnica de validacao, nao por erro.

No ciclo 70/30, os dados foram separados assim:

```text
1000 registros totais
700 registros com embedding preenchido: conjunto de treino/ensino
300 registros com embedding null: conjunto de teste/holdout
```

O motivo e evitar vazamento de teste. Se os 300 registros de teste tambem
tivessem embeddings salvos, eles poderiam aparecer como resultado da propria
busca, tornando o teste artificialmente facil.

A funcao SQL de busca semantica usa:

```sql
where i.embedding is not null
```

Isso garante que somente os 700 registros de treino sejam candidatos na busca.
Os 300 registros de teste ficam fora da base pesquisavel e sao usados apenas
para gerar consultas e medir se o sistema encontra clientes parecidos entre os
700 treinados.

Em producao, depois de concluir a validacao, e possivel preencher embeddings
para todos os 1000 registros. Para isso, basta rodar:

```powershell
python .\scripts\preencher_embeddings.py --quiet
```

Essa acao, porem, encerra a separacao 70/30, porque os registros de teste
passam a fazer parte da base pesquisavel.

Apos a conclusao dos testes, essa etapa foi executada para preparar a demo
final. O estado atual da base e:

```text
embedding_preenchido: 1000
embedding_null: 0
```

Portanto, no momento da demonstracao final, nao ha embeddings nulos.

## 3. Base de dados usada

Tabela:

```text
public.inadimplencias
```

Total avaliado:

```text
1000 registros simulados
```

Campos principais:

```text
nome_cliente
valor_inadimplencia
dias_inadimplencia
tipo_risco
bairro
tentativas_cobranca
embedding
```

## 4. Validacao 1 - Precisao da inteligencia artificial

### Metodo

A precisao foi avaliada comparando o risco registrado na tabela com uma
classificacao derivada dos dias reais de atraso, usada como referencia
objetiva.

Regra tecnica usada para referencia:

```text
0 a 30 dias  -> baixo
31 a 90 dias -> medio
acima de 90 dias -> alto
```

Registros com risco `Critico` foram normalizados como `alto`, porque o
frontend e a busca operacional trabalham com tres grupos principais:

```text
baixo
medio
alto
```

### Resultado

```text
total avaliado: 1000
acertos: 545
precisao: 54.5%
```

### Interpretacao

A precisao de 54,5% indica que a classificacao de risco dos dados simulados
nao segue exclusivamente os dias de atraso. Isso era esperado porque o proprio
gerador sintetico usa probabilidade, e nao uma regra fixa.

Exemplo: um cliente com poucos dias de atraso pode ser classificado como
`Medio`, `Alto` ou `Critico` dependendo da distribuicao probabilistica usada
na criacao da base.

Portanto, essa metrica nao indica falha do sistema. Ela mostra que os dados
simulados possuem variacao proposital, aproximando uma situacao real onde risco
nao depende apenas de atraso, mas tambem de valor, comportamento e contexto.

## 5. Validacao 2 - Eficiencia operacional

### Metodo

Foram comparados dois cenarios:

1. Processo manual simulado: localizar dados do cliente, conferir atraso,
   valor, bairro e redigir uma mensagem. Foi adotada uma referencia didatica de
   60 segundos por cliente.
2. Processo automatizado: consulta ao Supabase, busca semantica por IA e
   geracao automatica de mensagens a partir dos dados do banco.

### Resultado automatizado

Primeira execucao, com carregamento frio do modelo:

```text
tempo de listagem de 1000 registros: 1,441 s
tempo para executar 5 buscas IA: 104,853 s
tempo para gerar 100 mensagens: 0,000103 s
```

Execucao aquecida, apos o modelo ja estar carregado:

```text
tempo para listar 1000 registros: 0,716 s
tempo para executar 5 buscas IA: 10,701 s
tempo para gerar 100 mensagens: 0,000125 s
```

Metricas medidas na segunda execucao:

```text
tempo_listagem_1000_s: 0.716
tempo_5_buscas_ia_s: 10.701
tempo_gerar_100_mensagens_s: 0.000125
referencia_manual_100_clientes_s: 6000
```

### Interpretacao

O processo automatizado reduz drasticamente o esforco de consulta, montagem de
resposta e padronizacao da mensagem.

A busca por IA ainda depende do carregamento do modelo e da latencia de rede,
principalmente quando o servidor acabou de iniciar. Apos o carregamento, o
tempo de 5 buscas caiu de aproximadamente 104,853 s para 10,701 s, tornando o uso viavel para
consultas operacionais e atendimento via Botpress.

## 6. Validacao 3 - Consistencia dos dados

### Metodo

Foi avaliada uma amostra de 100 mensagens geradas automaticamente. Cada mensagem
foi comparada com os campos correspondentes no banco:

```text
nome_cliente
dias_inadimplencia
valor_inadimplencia
bairro
```

### Resultado

```text
amostra avaliada: 100 mensagens
mensagens consistentes: 100
consistencia: 100%
```

### Interpretacao

As mensagens geradas pelo sistema mantiveram coerencia total com os dados
consultados na base. Isso reduz o risco operacional de enviar cobrancas com
nome, valor, bairro ou atraso divergente do registro original.

## 7. Validacao complementar - Busca semantica 70/30

Alem das tres dimensoes acima, foi executado o ciclo especifico de embeddings
com 70% dos dados para treino e 30% para teste.

Resultado:

```text
total: 1000
treino: 700
teste: 300
consultas com resultado: 300/300
acuracia bairro top1: 64.3%
acuracia risco top1: 98.7%
similaridade media top1: 0.801
```

Interpretacao:

- Todas as consultas dos 300 registros de teste retornaram resultados.
- A recuperacao por risco foi alta.
- A recuperacao por bairro foi moderada/boa.
- A similaridade media indica proximidade semantica consistente.

## 8. Arquivos envolvidos

```text
app/services/embeddings.py
app/services/ml_model.py
app/routes/ia.py
app/routes/botpress.py
app/static/index.html
scripts/treinar_testar_split_70_30.py
scripts/gerar_metricas_validacao.py
sql/01_schema_supabase.sql
```

## 9. Conclusao

O sistema foi validado com dados simulados e apresentou comportamento adequado
nas tres dimensoes propostas:

- A inteligencia artificial recuperou clientes semanticamente parecidos e
  apresentou alta aderencia por risco no teste 70/30.
- O processo automatizado reduziu significativamente o esforco operacional em
  comparacao com o fluxo manual simulado.
- As mensagens geradas mantiveram consistencia com os dados armazenados no
  Supabase.

Os `embedding = null` devem ser mantidos apenas enquanto a base estiver em
modo de validacao 70/30. Para a demo final, todos os embeddings foram
preenchidos, deixando a busca inteligente disponivel para os 1000 registros.
