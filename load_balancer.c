#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <unistd.h>
#include <arpa/inet.h>

#define PORT 80
#define BUFFER_SIZE 1024
#define MAX_SERVERS 2

typedef struct {
    char ip[INET_ADDRSTRLEN];
    int port;
    char client_type[50];     // Expected client type (e.g., "mobile", "desktop")
    char network_quality[50]; // Expected network quality (e.g., "low", "high")
    char content_type[50];    // Supported content type (e.g., "video", "audio")
} Server;

// Server list with specific characteristics
Server servers[MAX_SERVERS] = {
    {"127.0.0.1", 81, "mobile", "low", "video"},
    {"127.0.0.1", 82, "desktop", "high", "audio"},
};

Server* select_server(const char *client_type, const char *network_quality, const char *requested_content) {
    int best_score = -1;
    Server *best_server = NULL;

    // Iterate through all servers to evaluate and find the best one
    for (int i = 0; i < MAX_SERVERS; i++) {
        int score = 0;

        // Compare server characteristics with client inputs
        if (strcmp(client_type, servers[i].client_type) == 0) {
            score += 20; // Higher score for matching client type
        }
        if (strcmp(network_quality, servers[i].network_quality) == 0) {
            score += 30; // Higher score for matching network quality
        }
        if (strstr(requested_content, servers[i].content_type)) {
            score += 50; // Higher score for matching content type
        }

        // Select the server with the highest score
        if (score > best_score) {
            best_score = score;
            best_server = &servers[i];
        }
    }

    // If no specific server is preferred, return the first one as a fallback
    return best_server ? best_server : &servers[0];
}

int main() {
    int server_fd, new_socket;
    struct sockaddr_in address;
    int addrlen = sizeof(address);
    char buffer[BUFFER_SIZE] = {0};

    // Create socket file descriptor
    if ((server_fd = socket(AF_INET, SOCK_STREAM, 0)) == 0) {
        perror("Socket failed");
        exit(EXIT_FAILURE);
    }

    // Bind the socket to the port
    address.sin_family = AF_INET;
    address.sin_addr.s_addr = INADDR_ANY;
    address.sin_port = htons(PORT);

    if (bind(server_fd, (struct sockaddr *)&address, sizeof(address)) < 0) {
        perror("Bind failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    // Start listening for connections
    if (listen(server_fd, 3) < 0) {
        perror("Listen failed");
        close(server_fd);
        exit(EXIT_FAILURE);
    }

    printf("Load balancer is running on port %d\n", PORT);

    while (1) {
        if ((new_socket = accept(server_fd, (struct sockaddr *)&address, (socklen_t *)&addrlen)) < 0) {
            perror("Accept failed");
            continue;
        }

        // Receive client information
        read(new_socket, buffer, BUFFER_SIZE);
        printf("Received client data: %s\n", buffer);

        // Parse client information (example format: "mobile,low,video1")
        char client_type[50], network_quality[50], requested_content[50];
        sscanf(buffer, "%49[^,],%49[^,],%49s", client_type, network_quality, requested_content);

        // Select the best server
        Server *best_server = select_server(client_type, network_quality, requested_content);
        if (best_server) {
            // Send the server information to the client
            snprintf(buffer, BUFFER_SIZE, "%s:%d", best_server->ip, best_server->port);
            send(new_socket, buffer, strlen(buffer), 0);
            printf("Redirected client to server %s:%d\n", best_server->ip, best_server->port);
        } else {
            // No suitable server found
            snprintf(buffer, BUFFER_SIZE, "No suitable server found");
            send(new_socket, buffer, strlen(buffer), 0);
            printf("No suitable server found for client\n");
        }

        close(new_socket);
    }

    close(server_fd);
    return 0;
}
