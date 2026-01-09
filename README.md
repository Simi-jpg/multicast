**To run the program, the required format for each python file is:**

Queue: python3 work_queue.py clientPort workerPort

Client: python3 myClient.py clientPort

Worker: python3 worker.py queueIP:port outputPort syslogPort

This project implements a distributed job processing system using Python sockets.
It supports multiple clients and multiple workers, coordinated by a central queue server.

**What the Program Does**

Clients submit text-based jobs to a queue
Workers request jobs, process them, and report completion
The queue tracks job states (waiting, in progress, done)
Workers multicast processed output to a listener
Worker activity is logged using syslog

**How It Works**

TCP sockets are used for reliable communication between clients, workers, and the queue
The queue server uses select() to handle multiple concurrent connections without threading
Jobs are only assigned if their status is waiting, preventing duplicate work
Workers poll the queue when idle and processes jobs independently
Messages are guaranteed to end with a newline (/n) to safely parse TCP streams
UDP multicast is used to broadcast worker output to all listeners without blocking workers

**Why This Design**

select() enables scalability without the complexity of threads
Explicit job states prevent race conditions (two workers won't work on the same client's request)
TCP ensures reliable job delivery and status updates
UDP multicast allows lightweight, non-blocking output distribution
Syslog provides centralized, system-level logging without custom log files
