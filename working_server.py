import socket
import subprocess
import os

def start_server():
    host = '0.0.0.0'  # Listen on all available interfaces
    port = 12349  # Choose a port number

    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server_socket.bind((host, port))
    server_socket.listen(1)  # Listen for one incoming connection

    print(f"Server listening on {host}:{port}")

    while True:
        client_socket, client_address = server_socket.accept()
        print(f"Connection from {client_address}")

        current_directory = "C:/"

        try:
            while True:
                data = client_socket.recv(1024).decode('utf-8')

                if not data:
                    # No data received, indicating that the connection has been closed
                    print("Connection closed by the client.")
                    break

                print(f"Received command: {data}")

                if data.lower() == "getcwd":
                    client_socket.send(os.getcwd().encode('utf-8'))
                    continue  # Skip the command execution for "getcwd"
                elif data.lower() == "get_directories":
                    directories = "\n".join(os.listdir(current_directory))
                    client_socket.send(directories.encode('utf-8'))
                    continue  # Skip the command execution for "get_directories"

                if data.lower() == "exit":
                    break
                elif data.lower() == "close":
                    print("Closing the server as requested.")
                    client_socket.close()
                    server_socket.close()
                    exit()  # Terminate the server process
                elif data.startswith("cd "):
                    # Change the current working directory
                    new_dir = os.path.normpath(os.path.join(current_directory, data[3:]))
                    try:
                        os.chdir(new_dir)
                        current_directory = os.getcwd()
                        response = f"Changed directory to {current_directory}"
                    except FileNotFoundError:
                        response = f"Directory not found: {new_dir}"
                else:
                    try:
                        with subprocess.Popen(data, shell=True, cwd=current_directory, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) as process:
                            output, error = process.communicate()
                            response = f"Output:\n{output}\nError:\n{error}"
                    except Exception as e:
                        response = f"Error executing command: {e}"

                client_socket.send(response.encode('utf-8'))

        except Exception as e:
            print(f"Error: {e}")
        finally:
            client_socket.close()

if __name__ == "__main__":
    start_server()
