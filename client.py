import socket

# Constants
LOAD_BALANCER_IP = '127.0.0.1'  # Load balancer's IP address
LOAD_BALANCER_PORT = 80  # Load balancer's port
BUFFER_SIZE = 1024  # Buffer size for receiving data

# client data
CLIENT_TYPE = "desktop"
NETWORK_QUALITY = "high"
REQUESTED_CONTENT = "audio"


def main():
    try:
        # Create a socket to connect to the load balancer
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as client_socket:
            client_socket.connect((LOAD_BALANCER_IP, LOAD_BALANCER_PORT))

            # Send client data to the load balancer
            client_data = f"{CLIENT_TYPE},{NETWORK_QUALITY},{REQUESTED_CONTENT}"
            client_socket.sendall(client_data.encode())

            # Receive response from the load balancer
            response = client_socket.recv(BUFFER_SIZE).decode()
            print("Response from load balancer:", response)

            # Parse server info if a suitable server was found
            if "No suitable server" not in response:
                server_ip, server_port = response.split(':')
                print(f"Redirecting to server {server_ip}:{server_port}")

                # Optionally, connect to the selected server
                with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as server_socket:
                    server_socket.connect((server_ip, int(server_port)))
                    print(f"Connected to server {server_ip}:{server_port}")
                    # Example interaction with the selected server
                    server_socket.sendall(b"Hello, server!")
                    server_response = server_socket.recv(BUFFER_SIZE).decode()
                    print("Response from server:", server_response)
            else:
                print("No suitable server found. Exiting.")

    except Exception as e:
        print("An error occurred:", e)


if __name__ == "__main__":
    main()
