from http.server import HTTPServer
from Minimum_Communication_Policy import MCP

from Central_Controller import CentralController

if __name__ == "__main__":

    host_name: str = "0.0.0.0"
    server_port: int = 8080

    server = HTTPServer((host_name, server_port), CentralController)

    print(f"Server started http://{host_name}:{server_port}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("Stopping server")
    server.server_close()
    print("Server stopped")
