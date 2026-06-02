# Relatorio tecnico - Ciclo de Machine Learning 70/30

Data da execucao: 02/06/2026

## 1. Objetivo

Validar o ciclo de machine learning do PayFlow usando a tabela `inadimplencias`
do Supabase com 1000 registros.

O objetivo foi separar os dados em:

- 70% para ensino/treino: registros usados para gerar e salvar embeddings.
- 30% para teste: registros reservados sem embedding salvo, usados para medir
  a capacidade da busca semantica de encontrar clientes parecidos.

## 2. Observacao sobre o termo "treino"

Neste projeto, o modelo `sentence-transformers/all-MiniLM-L6-v2` ja vem
pre-treinado. Portanto, o sistema nao treina uma rede neural do zero.

O "ensino" feito aqui consiste em transformar os dados da tabela em embeddings
e salvar esses vetores no Supabase/pgvector. Depois disso, as consultas tambem
viram embeddings e sao comparadas contra os vetores salvos.

## 3. Dados usados

Tabela:

```text
public.inadimplencias
```

Campos usados para montar o texto de cada cliente:

```text
nome_cliente
dias_inadimplencia
tipo_risco
valor_inadimplencia
bairro
```

Texto base usado no embedding:

```text
Cliente {nome_cliente} com {dias_inadimplencia} dias de inadimplencia,
risco {tipo_risco}, valor R$ {valor_inadimplencia}, bairro {bairro}
em Marilia/SP.
```

## 4. Separacao treino/teste

Script usado:

```text
scripts/treinar_testar_split_70_30.py
```

Comando executado:

```powershell
python .\scripts\treinar_testar_split_70_30.py --limite 1000 --quiet
```

Resultado da separacao:

```text
Total: 1000 registros
Treino: 700 registros
Teste: 300 registros
Seed: 42
```

Estado confirmado no Supabase durante a validacao 70/30:

```text
embedding_preenchido: 700
embedding_null: 300
```

## 4.1. Promocao para demo final

Apos a validacao 70/30, a base foi promovida para modo demo final. Os 300
registros que estavam reservados para teste tambem tiveram seus embeddings
preenchidos.

Estado atual da base para demonstracao:

```text
total: 1000
embedding_preenchido: 1000
embedding_null: 0
```

Com isso, todos os clientes podem aparecer na busca inteligente do frontend e
do Botpress.

## 5. Como o teste foi feito

Os 300 registros de teste ficaram com `embedding = null`. Isso impede que eles
entrem diretamente nos resultados da funcao SQL `match_inadimplencias`, porque
a funcao filtra:

```sql
where i.embedding is not null
```

Para cada registro de teste, o script gerou uma consulta textual baseada nos
dados desse proprio registro, por exemplo:

```text
clientes com risco Alto em Jardim Esmeralda com 120 dias de atraso
e valor 2500.00
```

Essa consulta foi convertida em embedding em tempo real e comparada contra os
700 registros do conjunto de treino.

## 6. Metricas finais

Resultado da execucao final:

```text
consultas com resultado: 300/300
acuracia bairro top1: 64.3%
acuracia risco top1: 98.7%
similaridade media top1: 0.801
```

Interpretacao:

- `consultas com resultado`: todas as 300 consultas de teste retornaram ao
  menos um cliente parecido dentro dos 700 registros treinados.
- `acuracia bairro top1`: em 64,3% das consultas, o primeiro resultado retornado
  tinha o mesmo bairro do registro de teste.
- `acuracia risco top1`: em 98,7% das consultas, o primeiro resultado tinha o
  mesmo tipo de risco do registro de teste.
- `similaridade media top1`: a similaridade media do primeiro resultado foi
  0,801, indicando boa proximidade semantica para esse conjunto sintetico.

## 7. Exemplos da execucao

```text
teste id=518 -> Gustavo Martins | Jardim Esmeralda | risco Critico | sim 0.796
teste id=690 -> Lais Rezende | Jardim America | risco Medio | sim 0.804
teste id=134 -> Daniel Camara | Jardim Esmeralda | risco Medio | sim 0.776
teste id=411 -> Sra. Luana Lopes | Jardim Maria Izabel | risco Medio | sim 0.822
teste id=347 -> Sr. Breno da Cunha | Jardim Esmeralda | risco Alto | sim 0.759
```

## 8. Arquivos envolvidos

```text
app/services/embeddings.py
scripts/treinar_testar_split_70_30.py
sql/01_schema_supabase.sql
app/routes/ia.py
app/routes/botpress.py
app/static/index.html
```

## 9. Impacto no frontend

O frontend foi ajustado para buscar 1000 registros:

```js
fetch('/inadimplencia?limite=1000')
```

Com isso, a lista, dashboard, mapa e relatorio gerencial trabalham com todos os
registros disponiveis carregados pela API.

## 10. Limitacoes tecnicas

1. O modelo nao foi re-treinado com pesos proprios. Foi usado um modelo
   pre-treinado de embeddings.
2. A avaliacao mede busca semantica/retrieval, nao classificacao supervisionada.
3. Como os dados sao sinteticos, as metricas podem ficar diferentes quando
   dados reais de clientes forem usados.
4. A acuracia de bairro e menor que a de risco porque varios bairros possuem
   perfis financeiros parecidos.
5. Os 300 registros de teste ficaram com `embedding = null` durante a validacao
   para nao contaminar o teste. Depois da validacao, eles foram preenchidos
   para a demo final.

## 11. Conclusao

O ciclo 70/30 foi concluido.

O ciclo 70/30 foi executado com 700 registros treinados e 300 registros
reservados para teste. Depois da validacao, a base foi promovida para demo
final com 1000 embeddings preenchidos, permitindo que todos os clientes sejam
usados pela busca inteligente.

O sistema esta pronto para demonstracao com busca inteligente no frontend e no
Botpress, lembrando que a busca semantica opera apenas sobre os registros com
embedding preenchido.
