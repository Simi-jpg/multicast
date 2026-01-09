# imports
import socket
import select
import sys


# Command line arguments: argv[1] = client port; argv[2] = worker port

if len(sys.argv) != 3:
    print("Wrong arguments. Try python3 myWorkQueue.py clientPort workerPort")
    sys.exit(1)

# variables 
job_id = 1 # track the jobs we have received. Unique for all jobs. Increment after every new JOB request
jobs = [] # a list to store each job

# Question: can ports be the same or is that a case to handle?
HOST = "0.0.0.0"
CLIENT_PORT = int(sys.argv[1]) #client port is the first argument
WORKER_PORT = int(sys.argv[2]) #worker port is the second argument

# create both client and worker TCP sockets
client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
worker_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

# bind the sockets to their port (only one host but separate ports)
client_socket.bind((HOST, CLIENT_PORT))
worker_socket.bind((HOST, WORKER_PORT))

# listen for connections to the queue
client_socket.listen()
worker_socket.listen()

print("listening on interface ")

# keep a list of all connections that come into the queue
connections = [client_socket, worker_socket]
input = []


while True:

    readable, writable, exceptional = select.select(connections, [], [])

    for sock in readable:

        if sock == client_socket: # a client is trying to connect
            conn, addr = client_socket.accept() # accept the incoming client connection
            connections.append(conn) # add it to the list of connections

        elif sock == worker_socket: # a worker is trying to connect
            conn, addr = worker_socket.accept() # accept the incoming worker connection
            connections.append(conn) # add it to th elist of connections

        else:	# both worker and client are submitting a task request
            try:
                data = sock.recv(1024)

                if not data:	# empty data received
                    connections.remove(sock) # remove the socket from the list of connections and close the connection to the queue to free up space
                    sock.close()
                    continue
                    

                message = data.decode('UTF-8').strip() # remove any trailing or leading white spaces (\n)

                if message.startswith("JOB"): # if the client sends a job

		            # a new job will be added to the job list. Each new_job is a dictionary which has an id, the message and the status
                    new_job = {

                        "id": job_id,
                        "data": message[4:].strip(),	# start from idx 4 because message[0:3] is JOB and a space
                        "status": "waiting"             #default status is waiting
                    }

                    
                    jobs.append(new_job)	# add to the job list
                    response = str(job_id)		# send the id to the client
                    job_id += 1

                    sock.sendall((response + "\n").encode('utf-8')) # send the job id to the client

                elif message.startswith("STATUS"): # the client requests for the status of their job
                    
                    token = message.split()

                    if len(token) != 2 or not token[1].isdigit(): # only accepts two params and second param must be a digit (valid ID)
                        response = "Invalid request"
                        sock.sendall((response + "\n").encode('utf-8')) # send invalid request response. E.g client sends "STATUS " or "STATUS a"
                        continue

                    else:
                        get_id = int(token[1])	# get the job id
                        get_job = None

                        for j in jobs:	#search the list for jobs
                            if j["id"] == get_id:	# if the curr job_id = get_id, break out of loop
                                get_job = j
                                break
                        
                        if get_job:		# not None	
                            response = get_job["status"]
                        else:
                            response = "Job ID not found"

                        sock.sendall((response + "\n").encode('utf-8'))     # either send the job id or "Not Found"


                # WORKER: 		

                elif message.startswith("WORK"): # The worker submits a task request

                    # search through the job list and get the first job with a "waiting" status
                    next_job = None	
                   
                    for j in jobs:
                        if j["status"] == 'waiting':
                            next_job = j
                            break

                    if next_job: # we found a job. Change the status to in progress since the worker has received it 
                        next_job["status"] = "in progress"
                        response = f'JOB {next_job["id"]} {next_job["data"]}'	# send JOB id and message to the worker 

                    else:	# empty list or all tasks are done/ in-progress
                        response = "No jobs available"

                    sock.sendall((response + "\n").encode('utf-8')) # send response to worker

                elif message.startswith("DONE"):	# the worker tells the queue they are done. Sends DONE job_id
                    token = message.split() 

                    if len(token) != 2 or not token[1].isdigit():	# check it is the valid request format. Cannot be "DONE " or "DONE y"
                        response = "Invalid"
                        sock.sendall((response + "\n").encode('utf-8'))
                        continue

                    else:
                        get_id = int(token[1])  # the id 
                        found = False
                        

                        for j in jobs: # search the job list for the id and set the status to done
                            if j["id"] == get_id:
                                j["status"] = "done"
                                found = True
                                break      
                        response = "Changed status to Done" if found else "Job ID not found" # eror checking using boolean found to make sure we find the id

                    sock.sendall((response + "\n").encode('utf-8'))


                else: # invalid command. Sent none of the four valid requests (requests are case-sensitive)
                    # print("The message you sent is: ", message)
                    response = "The message you sent is " + message + ". Try again."

		            # send the response to the corresponding socket (client or worker) depending on what they ask for.
                    sock.sendall((response + "\n").encode('utf-8'))

            except Exception as e:
                    print(e)
