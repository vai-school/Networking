import socket
import threading


class ChatClient:
    def __init__(self, name, host="localhost", port=5000):
        self.name = name
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.running = False

    def connect(self):
        self.sock.connect((self.host, self.port))
        self.sock.sendall(self.name.encode())  
        self.running = True
        print(f"[client] connected as {self.name}. Type /quit to leave.")

    def _receive_loop(self):
        """Runs in a background thread, printing whatever the server sends."""
        while self.running:
            try:
                data = self.sock.recv(1024)
            except OSError: #error Handling in case they leave chat suddenly
                break
            if not data:
                print("[client] server closed the connection")
                self.running = False
                break
            print(data.decode())

    def run(self):
        self.connect()
        threading.Thread(target=self._receive_loop, daemon=True).start() 
        #allows messages in background by running receive_loop

        try:
            while self.running:
                message = input()
                if message == "/quit":
                    break
                if message:
                    self.sock.sendall(message.encode())
        except (KeyboardInterrupt, EOFError):
            pass
        finally:
            self.close()

    def close(self):
        self.running = False
        self.sock.close()


if __name__ == "__main__":
    username = input("Your name: ").strip() or "anonymous"
    ChatClient(username).run()