from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
import sqlite3
from datetime import datetime
from typing import List, Dict
import json

app = FastAPI()

# Banco SQLite local com tópico
conn = sqlite3.connect('banco.db', check_same_thread=False)
cursor = conn.cursor()

cursor.execute('''
CREATE TABLE IF NOT EXISTS messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,
    content TEXT NOT NULL,
    timestamp TEXT NOT NULL
)
''')
conn.commit()

class ConnectionManager:
    def __init__(self):
        self.active_connections: Dict[WebSocket, str] = {}  # websocket: topic

    async def connect(self, websocket: WebSocket):
        await websocket.accept()

    def disconnect(self, websocket: WebSocket):
        if websocket in self.active_connections:
            del self.active_connections[websocket]

    def add_topic(self, websocket: WebSocket, topic: str):
        self.active_connections[websocket] = topic

    async def broadcast(self, message: str, topic: str):
        disconnected = []
        for connection, conn_topic in self.active_connections.items():
            if conn_topic == topic:
                try:
                    await connection.send_text(message)
                except:
                    disconnected.append(connection)
        for conn in disconnected:
            self.disconnect(conn)

manager = ConnectionManager()

from fastapi import HTTPException
@app.post("/send")
async def send_message(topic: str, content: str):
    timestamp = datetime.utcnow().isoformat()

    try:
        cursor.execute(
            "INSERT INTO messages (topic, content, timestamp) VALUES (?, ?, ?)",
            (topic, content, timestamp)
        )
        conn.commit()  # commit obrigatório para salvar a alteração no banco
        
        cursor.execute("SELECT COUNT(*) FROM messages WHERE topic = ?", (topic,))
        total = cursor.fetchone()[0]
        
        data = {
            "topic": topic,
            "total_messages": total,
            "last_message": content,
            "last_timestamp": timestamp,
        }
        
        await manager.broadcast(json.dumps(data), topic)
        return {"message": "Enviado com sucesso"}

    except Exception as e:
        # Aqui capturamos qualquer erro e lançamos uma exceção HTTP para o cliente
        print(f"Erro ao salvar mensagem: {e}")
        raise HTTPException(status_code=500, detail=f"Erro interno: {e}")


def get_history(topic: str) -> List[Dict]:
    cursor.execute("SELECT content, timestamp FROM messages WHERE topic = ? ORDER BY timestamp", (topic,))
    rows = cursor.fetchall()
    return [{"content": row[0], "timestamp": row[1]} for row in rows]

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        topic_msg = await websocket.receive_text()
        manager.add_topic(websocket, topic_msg)

        # Envia o histórico completo para o cliente logo que conecta
        history = get_history(topic_msg)
        for msg in history:
            await websocket.send_text(json.dumps({
                "total_messages": len(history),
                "last_message": msg["content"],
                "last_timestamp": msg["timestamp"]
            }))

        while True:
            # Mantém conexão aberta, recebe mensagens do cliente (se quiser processar depois)
            await websocket.receive_text()

    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
async def get():
    html_content = """
    <!DOCTYPE html>
    <html>
        <head>
            <title>Dashboard Kafka-like Broker com Tópicos</title>
            <style>
                body { font-family: Arial, sans-serif; max-width: 600px; margin: auto; }
                #dashboard { border: 1px solid #ccc; padding: 10px; margin-bottom: 20px; }
                ul { max-height: 200px; overflow-y: auto; border: 1px solid #eee; padding: 10px; }
            </style>
        </head>
        <body>
            <h1>Enviar mensagem</h1>
            <label>Tópico: <input type="text" id="topicInput" value="geral" /></label><br><br>
            <input type="text" id="msgInput" autocomplete="off" placeholder="Mensagem"/>
            <button onclick="sendMessage()">Enviar</button>

            <h2>Dashboard</h2>
            <p><strong>Tópico atual:</strong> <span id="currentTopic">geral</span></p>
            <div id="dashboard">
                <p><strong>Total mensagens:</strong> <span id="totalMessages">0</span></p>
                <p><strong>Última mensagem:</strong> <span id="lastMessage">-</span></p>
                <p><strong>Último update:</strong> <span id="lastTimestamp">-</span></p>
            </div>

            <h2>Mensagens recebidas</h2>
            <ul id='messages'></ul>

            <script>
                let ws;
                let currentTopic = document.getElementById("topicInput").value;
                const totalMessagesEl = document.getElementById("totalMessages");
                const lastMessageEl = document.getElementById("lastMessage");
                const lastTimestampEl = document.getElementById("lastTimestamp");
                const currentTopicEl = document.getElementById("currentTopic");
                const messagesList = document.getElementById("messages");

                function connectWebSocket(topic) {
                    if(ws) {
                        ws.close();
                        messagesList.innerHTML = '';
                        totalMessagesEl.textContent = '0';
                        lastMessageEl.textContent = '-';
                        lastTimestampEl.textContent = '-';
                    }

                    ws = new WebSocket("ws://localhost:8000/ws");
                    ws.onopen = () => {
                        ws.send(topic); // envia o tópico para o backend
                        currentTopicEl.textContent = topic;
                    };
                    ws.onmessage = function(event) {
                        const data = JSON.parse(event.data);
                        totalMessagesEl.textContent = data.total_messages;
                        lastMessageEl.textContent = data.last_message;
                        lastTimestampEl.textContent = data.last_timestamp;

                        const li = document.createElement('li');
                        li.textContent = `${data.last_timestamp}: ${data.last_message}`;
                        messagesList.appendChild(li);
                    };
                    ws.onerror = (err) => console.error("Erro WebSocket:", err);
                    ws.onclose = () => console.log("WebSocket fechado");
                }

                document.getElementById("topicInput").addEventListener("change", (e) => {
                    currentTopic = e.target.value.trim() || "geral";
                    connectWebSocket(currentTopic);
                });

                async function sendMessage() {
                    const topic = document.getElementById("topicInput").value.trim() || "geral";
                    const content = document.getElementById("msgInput").value;
                    if(content === "") return;
                    const response = await fetch(`/send?topic=${encodeURIComponent(topic)}&content=${encodeURIComponent(content)}`, {method: "POST"});
                    if(response.ok){
                        document.getElementById("msgInput").value = "";
                    }
                }

                // conecta inicialmente no tópico padrão "geral"
                connectWebSocket(currentTopic);
            </script>
        </body>
    </html>
    """
    return HTMLResponse(content=html_content, status_code=200)
