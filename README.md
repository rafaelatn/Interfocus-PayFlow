# Backend PayFlow com FastAPI + Supabase

Esta pasta organiza o backend do PayFlow de forma simples para estudo.

O projeto usa:

- FastAPI para criar a API;
- Supabase para guardar a tabela `inadimplencias`;
- pgvector para salvar e comparar embeddings;
- sentence-transformers para gerar embeddings open source;
- um script Python para gerar CSV sintetico com pandas, numpy e faker.
- bairros reais de Marilia/SP para alimentar a coluna `bairro` e posicionar
  clientes no mapa do frontend.

## Ideia principal

Pense no sistema como uma loja:

- o Supabase e o armario onde ficam as fichas dos clientes;
- o SQL monta ou ajusta as prateleiras desse armario;
- o Python gera fichas falsas para teste;
- o FastAPI e o atendente que busca e salva informacoes;
- o embedding e uma etiqueta numerica que ajuda a encontrar fichas parecidas.

## Estrutura

```text
backend_payflow_fastapi/
  app/
    main.py
    config.py
    supabase_client.py
    schemas.py
    routes/
      health.py
      inadimplencia.py
      ia.py
    services/
      embeddings.py
  scripts/
    gerar_csv_inadimplencias.py
    preencher_embeddings.py
  sql/
    01_schema_supabase.sql
  .env.example
  requirements.txt
```

## 1. SQL nao e Python

O arquivo SQL fica em:

```text
sql/01_schema_supabase.sql
```

Ele deve ser colado no `SQL Editor` do Supabase.

Esse arquivo:

- habilita o `pgvector`;
- adiciona a coluna `embedding vector(384)` se ela ainda nao existir;
- cria um indice para busca mais rapida;
- cria a funcao `match_inadimplencias`, usada pela rota `/ia/buscar-similares`.

Ele nao gera CSV.

## 2. Python para gerar CSV

O script Python fica em:

```text
scripts/gerar_csv_inadimplencias.py
```

Ele gera um arquivo:

```text
csv_supabase/inadimplencia_sintetica.csv
```

Para rodar:

```powershell
python .\scripts\gerar_csv_inadimplencias.py
```

Depois importe o CSV no Supabase:

```text
Table Editor > inadimplencias > Insert > Import data from CSV
```

## 3. Configurar .env

Copie `.env.example` para `.env` e preencha:

```env
SUPABASE_URL=https://SEU-PROJETO.supabase.co
SUPABASE_SERVICE_ROLE_KEY=SUA_SERVICE_ROLE_KEY
SUPABASE_TABLE_INADIMPLENCIAS=inadimplencias
SUPABASE_MATCH_FUNCTION=match_inadimplencias
```

Use a `service_role key` apenas no backend. Nunca coloque essa chave no
frontend, no Botpress ou em repositorio publico.

## 4. Instalar dependencias

```powershell
pip install -r requirements.txt
```

## 5. Rodar o backend

```powershell
uvicorn app.main:app --reload
```

Depois abra a interface do PayFlow:

```text
http://127.0.0.1:8000/
```

A tela busca automaticamente os registros reais pela rota
`GET /inadimplencia?limite=1000`. Se o `.env` ainda nao estiver configurado
ou se a tabela estiver vazia, a interface mostra uma mensagem sem preencher
clientes ficticios.

Para testar as rotas no Swagger, abra:

```text
http://127.0.0.1:8000/docs
```

## 6. Preencher embeddings

Depois que os dados estiverem na tabela `inadimplencias`, rode:

```powershell
python .\scripts\preencher_embeddings.py
```

Esse script:

1. busca registros com `embedding = null`;
2. monta um texto com nome, dias, risco, valor e bairro;
3. gera o embedding com modelo open source;
4. salva o vetor na coluna `embedding`.

## 7. Atualizar bairros para Marilia/SP

Se a tabela ja existe no Supabase e ainda usa bairros/regioes genericas como
`Norte`, `Sul` ou `Centro`, rode:

```powershell
python .\scripts\atualizar_bairros_marilia.py --limite 200
```

O script troca a coluna `bairro` por bairros reais de Marilia/SP, escolhidos
aleatoriamente. Por padrao ele tambem limpa a coluna `embedding`, porque o
texto usado no machine learning inclui o bairro. Depois rode novamente o
treino:

```powershell
python .\scripts\preencher_embeddings.py
```

O frontend reconhece esses bairros e coloca os pontos no mapa de Marilia.

## 8. Ensinar e testar o machine learning

Neste projeto, "ensinar" significa gerar embeddings para os registros da
tabela. O modelo open source ja vem treinado; o seu dado entra no sistema
quando cada cliente vira um vetor salvo no Supabase.

Para separar 70% dos dados para treino e 30% para teste:

```powershell
python .\scripts\treinar_testar_split_70_30.py --limite 1000
```

Esse script deixa os 70% de treino com `embedding` preenchido e reserva os
30% de teste com `embedding = null`. Depois ele gera consultas a partir dos
registros de teste e mede se a busca encontra clientes parecidos dentro do
conjunto treinado.

Pelo terminal:

```powershell
python .\scripts\treinar_testar_machine_learning.py
```

Pelo Swagger:

```text
POST /ia/treinar-embeddings
POST /ia/testar-machine-learning
```

## 9. Buscar dados parecidos

Use a rota:

```text
POST /ia/buscar-similares
```

Exemplo de corpo:

```json
{
  "consulta": "clientes criticos com alto valor em atraso",
  "limite": 5
}
```

O backend transforma a frase em embedding e chama a funcao SQL
`match_inadimplencias`.

## Ordem recomendada

1. Rodar `sql/01_schema_supabase.sql` no SQL Editor.
2. Rodar `python .\scripts\gerar_csv_inadimplencias.py`.
3. Importar o CSV na tabela `inadimplencias`.
4. Criar o `.env`.
5. Rodar `pip install -r requirements.txt`.
6. Se a tabela ja existir, rodar `python .\scripts\atualizar_bairros_marilia.py --limite 200`.
7. Rodar `python .\scripts\preencher_embeddings.py`.
8. Rodar `python .\scripts\treinar_testar_machine_learning.py`.
9. Rodar `uvicorn app.main:app --reload`.
10. Abrir a interface em `/`.
11. Testar a API no Swagger em `/docs`.
