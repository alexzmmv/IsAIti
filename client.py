import socket

def tcp_client(ip, port):
    # Create a TCP/IP socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # Connect the socket to the port where the server is listening
    server_address = (ip, port)
    print(f"Connecting to {server_address[0]} port {server_address[1]}")
    sock.connect(server_address)
    message=""
    print("Connected to the server, wait for the server to send a message")
    while True:
        data = sock.recv(1024)
        print(f"The victim:{data.decode()}")
        if message == "exit chat":
            break
        message = input("Message: ")
        sock.sendall(message.encode())
        
    sock.close()

if __name__ == "__main__":
    #start the client with the server's IP and port number given in the command line arguments
    import sys
    ip = sys.argv[1]
    port = int(sys.argv[2])
    tcp_client(ip, port)