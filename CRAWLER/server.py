#!/usr/bin/env python

# Import necessary libraries
import socket
import sys
from _thread import *
import threading
from queue import Queue
from spider import Spider
from domain import *
from general import *

lock = threading.Lock() # For ensuring that only one client can be catered at a time
PROJECT_NAME = 'hi'
NUMBER_OF_THREADS = 8
QUEUE_FILE = PROJECT_NAME + '/queue.txt'
CRAWLED_FILE = PROJECT_NAME + '/crawled.txt'
queue = Queue()


# Create worker threads (will die when main exits)
def create_workers():
	for _ in range(NUMBER_OF_THREADS):
		t = threading.Thread(target=work)
		t.daemon = True
		t.start()


# Do the next job in the queue
def work():
	while True:
		url = queue.get()
		Spider.crawl_page(threading.current_thread().name, url)
		queue.task_done()


# Each queued link is a new job
def create_jobs():
	for link in file_to_set(QUEUE_FILE):
		queue.put(link)
	queue.join()
	crawl()


# Check if there are items in the queue, if so crawl them
def crawl():
	queued_links = file_to_set(QUEUE_FILE)
	if len(queued_links) > 0:
		print(str(len(queued_links)) + ' links in the queue')
		create_jobs()
    
# Necessary steps for creation of socket and maintenance of client-server communication

host = '127.0.0.1'
port = 65432

s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

try: # Bind to the socket
    s.bind((host, port))
except socket.error:
    print("INITIAL: Binding failed")
    sys.exit()

s.listen(5) # Maintain a queue of clientsthat the server can cater to at the moment


def clientthread(conn, addr): # Function for communication between client and server
	#wait_msg = "\nPlease wait while the server crawls your threads\n"
	welcomemsg = '\nWelcome to the server, type bye to exit or type your url and hit enter!\n'
	conn.sendall(welcomemsg.encode()) # Send the initial message

	while True:
		data = conn.recv(1024).decode()
		exitCMD = 'bye'
		#print(data)

		if (data == exitCMD): # If the client sends a 'bye' then release the lock for the next client in queue and close this current connection
			lock.release();
			conn.close();
			break;
				
		else:
			HOMEPAGE = data
			DOMAIN_NAME = get_domain_name(HOMEPAGE)
			Spider(PROJECT_NAME, HOMEPAGE, DOMAIN_NAME)
			create_workers()
			#conn.sendall(wait_msg.encode())
			crawl()
			links = ''
			for x in file_to_set(CRAWLED_FILE):
				links += x 
				links += '\n'
			conn.sendall(links.encode()) #indent

		if not data: # Release the lock if not data is received from client and close the connection by breaking the loop
			lock.release()
			break;

		#print(str(data))
		#servdata = input()
		#conn.sendall(servdata.encode())

	conn.close()


while 1:
	conn, addr = s.accept() # Accept the connection
	lock.acquire() # Acquire the lock to cater one client at a time
	print('Connected with ' + addr[0] + ':' + str(addr[1]))
	start_new_thread(clientthread, (conn, addr)) # Call the function for communication

s.close()
