import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from urllib import parse as urlparse
from typing import List, Tuple
from File_Handler import load_paths

X = Y = Theta = float
Position = Tuple[X, Y, Theta]

hostName: str = "localhost"
serverPort: int = 8080

agent_plans: List[List[Position]] = load_paths("result.path")
agent_timesteps: List[int] = [0 for _ in range(len(agent_plans))]
agent_positions: List[Position] = [None for _ in range(len(agent_plans))]
agent_status: List[str] = [None for _ in range(len(agent_plans))]

class CentralController(BaseHTTPRequestHandler):

    def do_GET(self):

        agent_id: List[int] = urlparse.parse_qs(urlparse.urlparse(self.path).query).get('agent_id', None)

        if not agent_id:
            return
        
        if not agent_id[0].isdigit():
            return
        
        agent_id = int(agent_id[0])

        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        message = {}
        message["agent_id"] = agent_id
        message["position"] = agent_plans[agent_id][0]
        self.wfile.write(bytes(json.dumps(message), "utf-8"))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data = json.loads(post_data)
        print(data)
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(post_data)


if __name__ == "__main__":
    server = HTTPServer((hostName, serverPort), CentralController)
    print(f"Server started http://{hostName}:{serverPort}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server")

    server.server_close()
    print("Server stopped")