import socket

# Set the same host and port your system uses
HOST = "127.0.0.1"   # localhost
PORT = 8000          # or whatever port you're using

sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
sock.bind((HOST, PORT))

print(f"Syslog server listening on {HOST}:{PORT}...\n")

while True:
    data, addr = sock.recvfrom(4096)
    print(f"[{addr}] {data.decode().strip()}")
