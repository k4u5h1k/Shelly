#!/usr/bin/env python3
import threading
import random
import socket
import string
import sys
import time

nickname = input('Enter a username: ')
nick_tosend = f'NICK {nickname} \n'
# name_tosend = 'USER ' + nickname + ' 0 * :' + 'blah' + '\r\n'
name_tosend = f'USER {nickname} macbook server {nickname}' + '\n'
# host = ('kaushik.me',4444)
host = ('irc.freenode.net',6667)

connected = False
print('Connecting to server please wait.')

# Connect.
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host[0], host[1]))

# Handshake.
client.send((name_tosend).encode())
client.send((nick_tosend).encode())
client.send(b'JOIN #kaushikschannel \r\n')

data = ""
prevData = "not same as data"
def recvData():
    global data, connected
    data = client.recv(512).decode()
    data = random.choice(string.ascii_letters) + data

    if data.startswith('PING '):
        resp = data.strip('PING ');
        client.send(('PONG ' + resp).encode())

    if 'Nickname is already in use' in data:
        print("Nickname is already in use sorry!")

    if not connected:
        if 'JOIN #kaushikschannel' in data:
            print('Connected to server successfully!')    
            connected = True
        else:
            return

    for line in data[1:].split('\n'):
        if 'PRIVMSG #kaushikschannel' in line:
            print('\n ',line[1:line.index('!')]+line.split('PRIVMSG #kaushikschannel')[1],"\nmsg : ", end="")
            # sender = line[1:line.index('!')]
            # print('\n '+sender,":", line[line[1:].index(':')+2:],"\nmsg : ", end="")

msg = ""
prevMsg = "not same as msg"
def takeInput():
    global msg
    msg = random.choice(string.ascii_letters) + input("msg : ")
    client.send(('PRIVMSG #kaushikschannel :'+msg[1:]+' \r\n').encode())

# Output and ping/pong.
recvfirstRun = True
inpfirstRun = True
try:
    while True:
        if data != prevData:
            prevData = data
            if not recvfirstRun:
                if recvThread.is_alive():
                    recvThread.join()
            recvThread = threading.Thread(target=recvData)
            recvfirstRun = False
            recvThread.daemon = True
            recvThread.start()

        if connected and msg != prevMsg:
            prevMsg = msg
            if not inpfirstRun:
                if inputThread.is_alive():
                    inputThread.join()
            inputThread = threading.Thread(target=takeInput)
            inpfirstRun = False
            inputThread.daemon = True
            inputThread.start()

        if msg == 'exit':
            raise KeyboardInterrupt
            break

except KeyboardInterrupt:
        recvThread.join()
        inputThread.join()
    
