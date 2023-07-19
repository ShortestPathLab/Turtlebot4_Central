import json
from http.server import BaseHTTPRequestHandler, HTTPServer


hostName = "localhost"
serverPort = 8080

class CentralController(BaseHTTPRequestHandler):

    def do_GET(self):
        self.send_response(200)
        self.send_header("Content-Type", "application/json")
        self.end_headers()
        self.wfile.write(bytes("10, 10, 9", "utf-8"))

    def do_POST(self):
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length)
        print(post_data)
        self.do_GET()
        

if __name__ == "__main__":
    server = HTTPServer((hostName, serverPort), CentralController)
    print(f"Server started http://{hostName}:{serverPort}")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server")

    server.server_close()
    print("Server stopped")