#!/usr/bin/env python

# Import necessary libraries
import socket
import sys
import os
import signal
from threading import Timer

# Necessary steps for establishing client-server communication

host = "127.0.0.1"
port = 65432

try:
	s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
except socket.error:
	print('INITIAL: Failed to connect')
	sys.exit();

s.connect((host, port))

# Determine whether a client is currently being cattered to by the server

check = False

def sendWait():
	if check == False: 
		print("\nThe server is busy right now, please wait.")

t = Timer(1.0, sendWait) # Wait for a second to determine whether server is busy
t.start()

while True:
	data = s.recv(1024).decode() # Decode the server-sent data
	check = True # Set True if server is free
	print(str(data)) # Print the server's data

	

	try:
		message = input() # Take input from console

		if message == 'bye': # If the client inputs bye then terminate
			s.send(message.encode())
			sys.exit()

		else: # Send out the message otherwise
			s.send(message.encode())
	except socket.error: # On an error
		print("ERROR: Couldn't send")
		sys.exit()

s.close() # Close the socket
