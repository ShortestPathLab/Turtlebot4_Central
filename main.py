from http.server import HTTPServer

from Central_Controller import CentralController

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
