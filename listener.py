import multicast as mc
import sys

# Use the same multicast address and port your worker is sending to
OUTPUT_PORT = sys.argv[1]  # same as your worker’s OUTPUT_PORT
SOCK = "239.0.0.1"

# Create a receiver socket
mc_sock = mc.multicastReceiverSocket(SOCK, 7000)

while True:
    data, addr = mc_sock.recvfrom(1024)  # wait for a message
    print(f"{data.decode()}")
