🚀 Broker Real-Time com FastAPI e WebSockets
Um sistema de mensageria simples e em tempo real, construído com FastAPI, que utiliza WebSockets para comunicação instantânea e SQLite para persistência de dados. O projeto funciona como um "broker" onde clientes podem se inscrever em tópicos para receber mensagens ao vivo.

🎯 Principais Funcionalidades
Comunicação em Tempo Real: Utiliza WebSockets para que os clientes recebam mensagens instantaneamente assim que são publicadas.

Sistema de Tópicos: As mensagens são organizadas por tópicos. Clientes podem se inscrever em qualquer tópico para receber apenas as mensagens relevantes.

Persistência de Dados: Todas as mensagens são salvas num banco de dados SQLite (banco.db), garantindo que o histórico não seja perdido.

Histórico de Mensagens: Ao se conectar a um tópico, o cliente recebe imediatamente todo o histórico de mensagens daquele tópico.

API para Publicação: Uma rota POST /send permite que mensagens sejam enviadas facilmente para qualquer tópico.

Interface Simples: Todo o frontend (HTML, CSS, JS) está contido no próprio arquivo broker.py, tornando o projeto um executável único e fácil de rodar.

🛠️ Tecnologias Utilizadas
Backend: Python 3

Framework: FastAPI

Servidor ASGI: Uvicorn

Banco de Dados: SQLite 3

Comunicação: WebSockets

Frontend: HTML, CSS, JavaScript (embutidos)

⚙️ Instalação e Configuração
Para executar este projeto, você precisará ter o Python 3 instalado.

1. Clone o repositório:
git clone https://github.com/miguelmantoani/fastapi-realtime-broker.git
cd fastapi-realtime-broker

2. Crie e ative um ambiente virtual (Recomendado):

Para Windows:
python -m venv venv
.\venv\Scripts\activate

Para macOS/Linux:
python3 -m venv venv
source venv/bin/activate

3. Instale as dependências a partir do arquivo requirements.txt:
pip install -r requirements.txt

(Nota: O banco de dados banco.db e a tabela messages são criados automaticamente na primeira vez que o broker.py é executado).

▶️ Como Executar a Aplicação
Com as dependências instaladas, inicie o servidor Uvicorn com o seguinte comando no seu terminal, dentro da pasta do projeto:

uvicorn broker:app --reload

Após executar o comando, a aplicação estará disponível em http://localhost:8000.

🕹️ Como Usar
1. Abra a Interface:
Acesse http://localhost:8000 no seu navegador.

2. Inscreva-se num Tópico:
Por padrão, você já está conectado ao tópico "geral". Para mudar, digite o nome de um novo tópico no campo "Tópico" e pressione Enter. A conexão WebSocket será reiniciada para o novo tópico e o histórico de mensagens dele será carregado.

3. Envie Mensagens:
Digite uma mensagem no campo "Mensagem" e clique em "Enviar". A mensagem será enviada para o tópico atual, salva no banco de dados, e todos os clientes conectados àquele tópico a receberão em tempo real.

4. API para Publicação:
Você também pode enviar mensagens através da API.

Endpoint: POST /send

Exemplo com curl: curl -X POST "http://localhost:8000/send?topic=financas&content=nova transacao recebida"

🤝 Como Contribuir
Faça um fork do projeto.

Crie uma nova branch (git checkout -b feature/minha-feature).

Faça o commit das suas alterações (git commit -m 'Adiciona minha-feature').

Faça o push para a branch (git push origin feature/minha-feature).

Abra um Pull Request.

Desenvolvido por Miguel Mantoani.