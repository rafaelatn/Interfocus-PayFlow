-- Rode este arquivo no SQL Editor do Supabase.
-- Ele NAO cria a tabela do zero, porque voce ja tem a tabela inadimplencias.
-- Ele apenas prepara a tabela para busca com embeddings open source.

create extension if not exists vector;

alter table public.inadimplencias
add column if not exists embedding vector(384);

create index if not exists inadimplencia_embedding_hnsw_idx
on public.inadimplencias
using hnsw (embedding vector_cosine_ops);

-- Funcao chamada pelo backend na rota /ia/buscar-similares.
-- Ela compara o embedding da pergunta com os embeddings salvos na tabela.
create or replace function public.match_inadimplencias(
  query_embedding vector(384),
  match_count integer default 5
)
returns table (
  id text,
  nome_cliente text,
  dias_inadimplencia integer,
  tipo_risco text,
  valor_inadimplencia numeric,
  bairro text,
  similaridade double precision
)
language sql stable
as $$
  select
    i.id::text,
    i.nome_cliente,
    i.dias_inadimplencia,
    i.tipo_risco,
    i.valor_inadimplencia,
    i.bairro,
    1 - (i.embedding <=> query_embedding) as similaridade
  from public.inadimplencias i
  where i.embedding is not null
  order by i.embedding <=> query_embedding
  limit match_count;
$$;
