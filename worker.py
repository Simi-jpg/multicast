# imports
import socket
import sys
import multicast as mc
import time

# Command line arguments: argv[1] = queue IP and port, argv[2] = multicast port for listener, argv[3] = syslog port
if len(sys.argv) != 4:
    print("Wrong arguments. Try python3 worker.py queueIP:Port outputPort syslogPort")
    sys.exit(1)


HOST_PORT = sys.argv[1] # format IP:Port. Will split by ":"
OUTPUT_PORT = int(sys.argv[2])
SYSLOG_PORT = int(sys.argv[3])

# split IP_PORT into two arguments
try:
    tokens = HOST_PORT.split(":")
    HOST = tokens[0]
    PORT = int(tokens[1])
except Exception:
     print("Invalid format. Try IP:Port")
     sys.exit(1)

# create TCP socket and bind worker to the work_queue using argv[1]
sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock.connect((HOST, PORT))

# multicast UDP socket to process jobs
mc_sock = mc.multicastSenderSocket() # UDP port
mc_address = "239.0.0.1" # address given in the assignment

# set up syslog UDP socket
syslog_sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

# function that will send the worker log messages (fetching, starting, completed)
def send_msg(msg):
    syslog_sock.sendto(msg.encode(), (HOST, SYSLOG_PORT))


# messages may come in at the same time so this stores them. They are separated by "\n" as the assignment states that each client message ends with one
buffer_msg = ""

# work process
try:
    while True:

	    # Send WORK to queue
        sock.sendall(b"WORK\n") # ready to fetch a job
        data = sock.recv(1024).decode('utf-8')

        if not data: # no data was received
            break

        # queue is empty. Check back later
        if data == "No jobs available\n":
            continue
        # Send log message to syslog
        send_msg("Fetching data\n")
        buffer_msg += data  # add the job into the buffer

        while "\n" in buffer_msg: # split the messages in the buffer by \n since each job request ends with a \n
            line, buffer_msg = buffer_msg.split("\n", 1) #split once at a time
            line = line.strip() #remove \n and process

            if not line: # empty.
                continue

            if not line.startswith("JOB"):	# check in the case the worker fetched a non JOB request
                continue


            # process real job requests. Queue sends {JOB id message}
            msg_tok = line.split(" ", 2) # to avoid splitting the actual message. Only split to a max of 3 (JOB, id, data)

            if len(msg_tok) < 3: # For example we get "JOB 1 " from the queue (new line removed after strip). Worker should not print a space
                continue
                
            job_id = int(msg_tok[1])
            job_msg = msg_tok[2].split()
            print(job_id, job_msg)


            # log progress to syslog
            send_msg(f"Starting job {job_id}\n")

            # loop through job_msg and send each word to the multicaster every 0.25 seconds
            for word in job_msg:
                mc_sock.sendto(word.encode(), (mc_address, OUTPUT_PORT))
                time.sleep(0.25)

            # Completed the job. Log progress to syslog
            send_msg(f"Completed job {job_id}\n")


            # Send a done request to the queue
            sock.sendall(f"DONE {job_id}".encode())

        
except Exception as e:
    print(e)

# close all sockets
sock.close()
mc_sock.close()
syslog_sock.close()
