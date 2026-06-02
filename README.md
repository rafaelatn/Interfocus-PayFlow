# PayFlow Interfocus

> Dashboard de gestão e cobrança de inadimplentes com mapa geográfico interativo, análise de risco e sugestões de mensagem por IA.

![HTML](https://img.shields.io/badge/HTML5-E34F26?style=flat&logo=html5&logoColor=white)
![CSS](https://img.shields.io/badge/CSS3-1572B6?style=flat&logo=css3&logoColor=white)
![JavaScript](https://img.shields.io/badge/JavaScript-F7DF1E?style=flat&logo=javascript&logoColor=black)
![Leaflet](https://img.shields.io/badge/Leaflet.js-199900?style=flat&logo=leaflet&logoColor=white)
![License](https://img.shields.io/badge/licença-MIT-blue?style=flat)

---

## Visão geral

O **PayFlow Interfocus** é um sistema front-end de cobrança voltado para o mercado brasileiro. Desenvolvido como uma Single Page Application (SPA) em HTML/CSS/JS puro — sem frameworks ou build tools — oferece uma interface profissional e responsiva para gestores de cobrança acompanharem inadimplentes, priorizarem ações e dispararem mensagens personalizadas por múltiplos canais.

---

## Funcionalidades

| Módulo | Descrição |
|---|---|
| **Dashboard** | KPIs em tempo real: total em aberto, clientes em atraso, alto risco. Feed de atividades e gráfico de evolução semanal. |
| **Clientes** | Tabela filtrável e pesquisável com classificação por risco (Alto / Médio / Baixo), valor da dívida, dias de atraso e bairro. |
| **Cobranças** | Perfil detalhado do cliente, sugestão de mensagem gerada por IA, seleção de canal (E-mail, SMS, WhatsApp, Carta) e histórico de contatos. |
| **Mapa** | Mapa interativo via Leaflet.js centralizado em Marília/SP. Pins coloridos por nível de risco, popups com resumo do cliente e filtro por categoria. |
| **Gerencial** | Dashboard executivo com taxa de inadimplência, tempo médio de pagamento, cobranças enviadas, taxa de recuperação e insights automáticos da IA. |

---

## Stack

- **HTML5 / CSS3 / JavaScript (ES6+)** — sem dependências de build
- **[Leaflet.js 1.9.4](https://leafletjs.com/)** — mapa interativo com tiles OpenStreetMap
- **[Plus Jakarta Sans](https://fonts.google.com/specimen/Plus+Jakarta+Sans)** — tipografia principal
- **[Fraunces](https://fonts.google.com/specimen/Fraunces)** — tipografia display / títulos
- **CSS Custom Properties** — sistema de design tokens (cores, raios, tipografia)

---

## Estrutura do projeto

```
payflow-interfocus/
│
├── index.html          # Aplicação completa (SPA single-file)
└── README.md
```

> O projeto foi intencionalmente construído em arquivo único para facilitar deploy estático e distribuição — sem etapa de build necessária.

---

## Como rodar

**Opção 1 — direto no navegador**

Abra o arquivo `index.html` em qualquer navegador moderno. Nenhuma instalação necessária.

**Opção 2 — servidor local (recomendado)**

```bash
# Python 3
python -m http.server 8080

# Node.js (npx)
npx serve .
```

Acesse `http://localhost:8080` no navegador.

**Opção 3 — GitHub Pages / Netlify / Vercel**

Faça upload do arquivo e aponte para `index.html` como entry point. O projeto funciona em qualquer hosting estático.

---

## Customização

Todos os dados dos clientes, atividades e regiões estão centralizados no bloco `DADOS` no início do `<script>`, facilitando a substituição por uma API real:

```javascript
// Substitua por fetch() de uma API REST
const CLIENTES = [
  {
    nome: 'João Oliveira',
    valor: 'R$ 500',
    valorNum: 500,
    venc: '01/02/2025',
    dias: 30,
    bairro: 'Centro',
    risco: 'alto',   // 'alto' | 'medio' | 'baixo'
    lat: -22.2130,
    lng: -49.9455,
    msg: '"Mensagem de cobrança personalizada..."',
    // ...
  },
  // ...
];
```

As cores do sistema são configuráveis via CSS custom properties no `:root`:

```css
:root {
  --brand:   #4B7BF5;   /* azul principal */
  --danger:  #F04D4D;   /* alto risco */
  --warn:    #F5A520;   /* médio risco */
  --ok:      #30C98A;   /* baixo risco */
}
```

---

## Mapa — observações técnicas

O mapa usa **Leaflet.js** com tiles do OpenStreetMap, centralizado nas coordenadas de **Marília/SP** (`lat: -22.2139, lng: -49.9458`). Para adaptar a outra cidade, altere as coordenadas e o zoom na função `initLeaflet()`:

```javascript
leafletMap = L.map('leaflet-map', {
  center: [-22.2139, -49.9458],  // ← altere aqui
  zoom: 13,                       // ← ajuste o zoom
});
```

O parâmetro `noWrap: true` no tile layer garante que o mapa não repita tiles lateralmente.

---

## Roadmap

- [ ] Integração com API REST (back-end Flask / Django)
- [ ] Autenticação de usuário (JWT)
- [ ] Disparo real de mensagens via WhatsApp Business API e SendGrid
- [ ] Exportação de relatório em PDF
- [ ] Modo claro (light theme)
- [ ] Testes automatizados (Playwright)

---

## Licença

Distribuído sob a licença **MIT**. Veja o arquivo `LICENSE` para detalhes.

---

<div align="center">
  Desenvolvido por <strong>Interfocus</strong>
</div>
