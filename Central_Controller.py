import json
from http.server import BaseHTTPRequestHandler, HTTPServer
from typing import Dict, List
from urllib import parse as urlparse

from Execution_Policy import ExecutionPolicy
from Minimum_Communication_Policy import MCP


class CentralController(BaseHTTPRequestHandler):

    execution_policy: ExecutionPolicy = MCP("result.path", 2)

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

        # Fullfill agents request for position data
        position, timestep = self.execution_policy.get_next_position(agent_id)

        message["timestep"] = timestep
        message["position"] = position.toTuple()
        self.wfile.write(bytes(json.dumps(message), "utf-8"))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        data: Dict = json.loads(post_data)

        # Update execution policy with incoming agent data.
        self.execution_policy.update(data)
        
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(post_data)



if __name__ == "__main__":

    hostName: str = "0.0.0.0"
    serverPort: int = 8080

    server = HTTPServer((hostName, serverPort), CentralController)

    print(f"Server started http://{hostName}:{serverPort}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server")
    server.server_close()
    print("Server stopped")