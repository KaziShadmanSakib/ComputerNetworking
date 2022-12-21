import socket
from urllib.parse import urlparse
from pathlib import Path
import os
import re

# taking input from a txt file
# and parsing the http url in the text file 
inputFile = open("inputUrl.txt", "r")
requestMsg = eval(inputFile.read())
url = urlparse(requestMsg.split()[1])
print(url)
print(requestMsg)
inputFile.close()

# gets the hostname and port to connect to a server
hostname = url.hostname
port = 80 if url.port is None else port

fileName = hostname+url.path+".txt"

# checks its caches if there exists any file named under it
#if the file exists then it checks that if the data is modified or not
#if it is modified then it fetches updated data and updates the file
if os.path.isfile(fileName):
	print("Cache file exists!")

	with open(fileName, 'r') as response:
		responseData = response.read()
		match = re.search(r'Last-Modified: (.*)', responseData)
		date = match.group(1).split('\\r\\n')[0]

		ifModifiedSince = 'If-Modified-Since: ' + date
		requestMsg = requestMsg.split('\r\n')
		requestMsg.insert(2, ifModifiedSince)
		requestMsg = '\\r\\n'.join(requestMsg)
		requestMsg = eval('\"' + requestMsg + '\"')
	try:
		clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		clientSocket.connect((hostname, port))
		clientSocket.send(requestMsg.encode())
		responseData = clientSocket.recv(1024).decode()
		
		print(responseData)
		notModified = int(responseData.split()[1])

		if notModified !=304:
			print("File is modified")
			cacheFile = open(fileName, 'w')
			cacheFile.write(responseData.replace('\r\n', '\\r\\n'))
			cacheFile.close()
	except:
		print("Error")
		clientSocket.close()

#else connect to the server and
#fetch the data response and
#save it to the local cache
else:
	print("Cache file does not exists!")

	try:
		clientSocket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		clientSocket.connect((hostname, port))
		clientSocket.send(requestMsg.encode())
		responseData = clientSocket.recv(1024).decode()
		
		cacheFile = open(fileName, 'w')
		cacheFile.write(responseData.replace('\r\n', '\\r\\n'))
		cacheFile.close()
		
		clientSocket.close()
		
	
	except:
		print("Connection failed!")
		clientSocket.close()
		exit()

#lastly displays the actual object/data
with open(fileName, 'r') as line:
	data = line.read().split('\\r\\n')[-1]
	print(data)