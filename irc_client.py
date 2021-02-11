#!/usr/bin/env python3
import readline
import threading
import socket
import sys

ping = 'PING '
pong = 'PONG '
nickname = input('Enter a username: ')
nick_tosend = f'NICK {nickname} \r\n'
name_tosend = 'USER ' + nickname + ' 0 * :' + 'blah' + '\r\n'
host = ('kaushik.me',4444)

# Connect.
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host[0], host[1]))

# Handshake.
client.send((nick_tosend).encode())
client.send((name_tosend).encode())
client.send(b'JOIN #general \r\n')

data = ""
prevData = "not same as data"
def recvData():
    global data
    data = client.recv(512).decode()
    for line in data.split('\n'):
        if 'PRIVMSG' in line:
            sender = line[1:line.index('!')]
            print('\n '+sender,":", line[line[1:].index(':')+2:],"\nmsg : ", end="")

msg = ""
prevMsg = "not same as msg"
def takeInput():
    global msg
    msg = input("msg : ")
    client.send(('PRIVMSG #general :'+msg+' \r\n').encode())

# Output and ping/pong.
firstRun = True
while True:
    if data != prevData:
        prevData = data
        if not firstRun:
            if recvThread.isAlive():
                recvThread.join()
        recvThread = threading.Thread(target=recvData)
        recvThread.daemon = True
        recvThread.start()

    # else:
    #     print(data)

    
    if msg != prevMsg:
        prevMsg = msg
        if not firstRun:
            if inputThread.isAlive():
                inputThread.join()
        inputThread = threading.Thread(target=takeInput)
        inputThread.daemon = True
        inputThread.start()

    firstRun = False

    if data.startswith(ping):
        resp = data.strip('PING ');
        client.send(('PONG ' + resp).encode())

    if msg == 'exit':
        recvThread.join()
        inputThread.join()
        break
