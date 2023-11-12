import socket
import readline

class ServerDirectoryCompleter:
    def __init__(self, client_socket):
        self.client_socket = client_socket
        self.directories = []

    def complete(self, text, state):
        current_input = readline.get_line_buffer().lstrip()

        if current_input.startswith("cd "):
            # For 'cd' commands, suggest directories from the server
            if not self.directories:
                self.update_directories()

            completions = [directory for directory in self.directories if directory.startswith(text)]
            return completions[state]

    def update_directories(self):
        self.client_socket.send("get_directories".encode('utf-8'))
        directories = self.client_socket.recv(4096).decode('utf-8').split('\n')
        self.directories = [directory for directory in directories if directory]  # Remove empty strings

def get_server_directory(client_socket):
    client_socket.send("getcwd".encode('utf-8'))
    server_directory = client_socket.recv(4096).decode('utf-8')
    return server_directory

def send_command(client_socket):
    completer = ServerDirectoryCompleter(client_socket)
    readline.set_completer(completer.complete)
    readline.parse_and_bind("tab: complete")

    try:
        while True:
            user_input = input('Enter command to execute on the server (or \'exit\' to quit, \'close\' to close the server): ')

            if not user_input:
                continue  # Ignore empty input

            if user_input.lower() == "exit":
                break  # Exit the loop if the user entered the exit command

            client_socket.send(user_input.encode('utf-8'))

            if user_input.lower() == "close":
                print("Closing the server as requested.")
                break  # Exit the loop to close the server

            result = client_socket.recv(4096).decode('utf-8')

            if user_input.lower().startswith("cd "):
                print(result)
                completer.update_directories()  # Request the server to update directories
                continue

            if user_input.lower() == "getcwd":
                current_server_directory = get_server_directory(client_socket)
                print(f"Server directory: {current_server_directory}")
                continue  # Skip the command execution for "getcwd"

            print(result)

    except KeyboardInterrupt:
        # Handle Ctrl+C gracefully
        pass
    finally:
        client_socket.close()

if __name__ == "__main__":
    server_host = input("Enter the server host: ")
    server_port = int(input("Enter the server port: "))  # Use the same port as in the server script

    client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client_socket.connect((server_host, server_port))

    send_command(client_socket)