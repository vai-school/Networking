import socket #allows for the networking and is absoluetly needed for the networking
import threading


class ChatServer:
    def __init__(self, host="0.0.0.0", port=5000): #defaults
        self.host = host
        self.port = port
        self.clients = {}
        self.lock = threading.Lock() #needed so threads don't get mixed up and overlap
        self.server_socket = None

    def start(self):
        self.server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM) #creates the socket 
        self.server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1) #prevents errors by setting socket
        self.server_socket.bind((self.host, self.port))
        self.server_socket.listen()
        print(f"[server] listening on {self.host}:{self.port}")


        #This code just catches the closing of the server to replace the error that
        #Vs Code gives. Because it looks nice. 
        try:
            self._accept_loop()
        except KeyboardInterrupt:
            print("\nshutting down")
        finally:
            self.server_socket.close()

    def _accept_loop(self):
        while True:
            conn, addr = self.server_socket.accept()
            print(f"[server] connection from {addr}")
            #The threads basically adds the clients and handles them, Threads are what allows multiple to happen at once,
            thread = threading.Thread(target=self._handle_client, args=(conn,), daemon=True)
            thread.start()

    def _handle_client(self, conn):
        try: #prevents crashing of threads
            # The first thing a client sends is its username
            name = conn.recv(1024).decode().strip() #prevents crashing of threads
            if not name:
                conn.close()
                return

            with self.lock:
                self.clients[conn] = name
            #Join chat message sender=conn makes it so the user doesn't see it
            self.broadcast(f"*** {name} joined the chat ***", sender=conn) 

            while True: #main loop for client
                data = conn.recv(1024)
                if not data: # client disconnected
                    break
                message = data.decode().strip()
                self.broadcast(f"{name}: {message}", sender=conn)
        except OSError:
            pass
        finally:
            self._remove_client(conn)

    def _remove_client(self, conn):
        with self.lock:
            name = self.clients.pop(conn, None) 
            #pops to get the name
        conn.close()
        if name:
            #Uses the name that was popped/ disconnected
            print(f"[server] {name} left")
            self.broadcast(f"*** {name} left the chat ***")


    #sends the message to everyone except the user. 
    def broadcast(self, message, sender=None):
        """Send message to everyone except the sender."""
        with self.lock:
            targets = [c for c in self.clients if c is not sender]
        for conn in targets:
            try:
                conn.sendall(message.encode())
            except OSError:
                pass


if __name__ == "__main__":
    ChatServer().start()