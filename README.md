🧾 Pagamentos Bot MG – Automação de Downloads
Automatizador de downloads de planilhas .xlsx do portal pagamentoderesolucoes.saude.mg.gov.br, com suporte a:

Pagamentos Orçamentários (1 por vez com tentativas e timeout configuráveis)

Restos a Pagar (até 10 municípios em paralelo)

Retry inteligente com backoff e logging estruturado

Timeout watchdog para evitar travamentos silenciosos

📁 Estrutura de Pastas
perl
Copy
Edit
pagamentos-bot/
│
├── main.py                      # Ponto de entrada
├── services/
│   └── downloader.py            # Lógica de scraping
├── utils/
│   └── logger.py                # Registro de erros
├── downloads/                   # Local onde os arquivos .xlsx são salvos
│   └── <timestamp>/
│       ├── Orcamentarios/
│       └── Restos_a_pagar/
├── logs/
│   └── bot.log                  # Log detalhado por município
├── .gitignore
└── README.md
⚙️ Requisitos
Python 3.9+

Google Chrome (ou Chromium) instalado

Ambiente virtual (recomendado)

📦 Instalação
bash
Copy
Edit
# Clone o repositório
git clone https://github.com/seuusuario/pagamentos-bot.git
cd pagamentos-bot

# Crie e ative o ambiente virtual
python -m venv .venv
source .venv/bin/activate  # Linux/Mac
.venv\Scripts\activate     # Windows

# Instale as dependências
pip install -r requirements.txt

# Instale os browsers do Playwright
playwright install
▶️ Execução
bash
Copy
Edit
python main.py
Por padrão, ele executa:

Downloads de Restos a Pagar com até 10 abas em paralelo

Após finalizar, executa Orçamentários um a um, com:

Timeout de 8 segundos

Até 10 tentativas com delay progressivo inteligente

Registro de erros por tentativa

🔍 Configurações Internas
Você pode ajustar as seguintes constantes em services/downloader.py:

python
Copy
Edit
TIMEOUT_EXECUCAO_ORCAMENTO = 8       # Timeout individual (em segundos)
MAX_TENTATIVAS = 10                  # Tentativas por município
WORKERS_RESTOS = 10                  # Paralelismo nos restos a pagar
📄 Logs
Todos os logs detalhados (tempo, tentativas, erros) são salvos em:

bash
Copy
Edit
logs/bot.log
E os arquivos .xlsx são salvos em:

javascript
Copy
Edit
downloads/<timestamp>/Orcamentarios/
downloads/<timestamp>/Restos_a_pagar/
❌ Tratamento de Erros
Timeouts superiores a 8s disparam nova tentativa automaticamente

Falhas de página ou de download são logadas com o município e tentativa

Logs completos por worker para facilitar debug

💡 Roadmap Futuro
 Melhor UI com Tkinter/CLI

 Integração com banco de dados para rastrear tentativas

 Dash de progresso em tempo real

 Modo headless com fallback automático

📜 Licença
MIT License © João Vitor
