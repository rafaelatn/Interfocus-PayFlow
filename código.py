import pandas as pd
import numpy as np 
from faker import Faker 
import random

fake = Faker('pt_BR')
random.seed(42)
N = 1200

nomes = [fake.name() for _ in range(N)] 
regioes = np.random.choice(['Norte', 'Sul', 'Leste', 'Oeste', 'Centro'], size=N, p=[0.15, 0.25, 0.20, 0.20, 0.20])

dias_raw = np.random.exponential(scale=120, size=N) 
dias = np.clip(dias_raw, 1,730).astype(int)

def classificar_risco(d): 
    if d <= 30: 
        probs = {'Baixo':0.75,'Médio':0.20,'Alto':0.04,'Crítico':0.01}
    elif d <= 90: 
        probs = {'Baixo':0.15,'Médio':0.55,'Alto':0.25,'Crítico':0.05}
    elif d <= 180: 
        probs = {'Baixo':0.05,'Médio':0.25,'Alto':0.50,'Crítico':0.20}
    elif d <= 365: 
        probs = {'Baixo':0.02,'Médio':0.10,'Alto':0.45,'Crítico':0.43}
    else: 
        probs = {'Baixo':0.01,'Médio':0.05,'Alto':0.25,'Crítico':0.69} 
    cats = list(probs.keys())
    pesos = list(probs.values()) 
    return np.random.choice(cats, p=pesos) 
riscos = [classificar_risco(d) for d in dias]

def taxa_juros(r): 
    return {'Baixo':0.02,'Médio':0.035,'Alto':0.055,'Crítico':0.08}[r]
def mensalidade_base(r): 
    ranges = {'Baixo':(200,800),'Médio':(400,1500),'Alto':(800,3000),'Crítico':(1500,8000)} 
    lo, hi = ranges[r] 
    base = np.random.uniform(lo, hi) 
    ruido = np.random.lognormal(mean=0, sigma=0.2) # variação ~±20% 
    return base * ruido 
def calcular_valor(d, r): 
    meses = d / 30 
    return round(mensalidade_base(r) * ((1 + taxa_juros(r)) ** meses), 2) 
valores = [calcular_valor(d, r) for d, r in zip(dias, riscos)]

df = pd.DataFrame({ 'nome_cliente': nomes, 'valor_inadimplencia': valores,
'dias_inadimplencia': dias, 'tipo_risco': riscos, 'regiao': regioes, }) # Amostra exatamente 1000 linhas (sem repetição) 
df = df.sample(1000, random_state=42).reset_index(drop=True) # utf-8-sig garante que acentos abram corretamente no Excel 
df.to_csv('C:/Users/Aula/Downloads/csv_supabase/inadimplencia_sintetica.csv', index=False, encoding='utf-8-sig')