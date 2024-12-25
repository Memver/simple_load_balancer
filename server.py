import socket
import sys

def start_server(host, port):
    print(f"Starting server on {host}:{port}...")
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(5)

    try:
        while True:
            client_socket, client_address = server_socket.accept()
            print(f"Connection from {client_address}")

            # Echo back received data
            data = client_socket.recv(1024)
            if data:
                print(f"Received: {data.decode('utf-8')} from {client_address}")
                client_socket.sendall(data)  # Echo the data back
            client_socket.close()
    except KeyboardInterrupt:
        print("Shutting down server...")
    finally:
        server_socket.close()

if __name__ == "__main__":
    host = "127.0.0.1"
    port = int(sys.argv[1])
    start_server(host, port)
