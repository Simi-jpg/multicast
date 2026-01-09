import socket
import sys
import time


# create an INET, STREAMing socket
s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
IP = "127.0.0.1"
# now connect to the web server on port 80 - the normal http port
s.connect((IP, int(sys.argv[1])))

# file_reader.py
try:
    # Open the file in read mode
    with open("jobs.txt", "r") as file:
        # Read line by line
        for line in file:
            # Strip newline characters and print
            line.strip()

            if not line:
                continue

            s.sendall(line.encode() + b'\n')

            
            data = s.recv(1024)
            print('Received:')
            # It's in bytes, convert to text
            print(data.decode("utf-8") )

            time.sleep(1)


except FileNotFoundError:
    print("File not found. Please check the file name or path.")

except Exception as e:
    print("An error occurred:", e)



s.close()

