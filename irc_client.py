#!/usr/bin/env python3
import readline
import threading
import socket
import sys
import os
import signal
import time

nickname = input("Enter a username: ")
nick_tosend = f'NICK {nickname} \r\n'
name_tosend = 'USER ' + nickname + ' 0 * :' + 'blah' + '\r\n'
host = ('kaushik.me',4444)

# Connect.
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host[0], int(host[1])))

# Handshake.
client.send((nick_tosend).encode())
client.send((name_tosend).encode())
client.send(b'JOIN #general \r\n')

stop = False

data = ""
prevData = "not same as data"
def recvData():
    global data, stop
    if msg == 'exit':
        stop = True
        return
    data = client.recv(512).decode()
    for line in data.split('\n'):
        if 'PRIVMSG' in line:
            sender = line[1:line.index('!')]
            print('\n '+sender,":", line[line[1:].index(':')+2:],"\nmsg : ", end="")

msg = ""
prevMsg = "not same as msg"

def takeInput():
    global msg, stop
    msg = input("msg : ")
    if msg == 'exit':
        stop = True
        return

    client.send(('PRIVMSG #general :'+msg+' \r\n').encode())


# Output and ping/pong.
firstRun = True
try:
    while True:
        if msg != prevMsg:
            prevMsg = msg

            if not firstRun:
                if inputThread.isAlive():
                    inputThread.join()
            inputThread = threading.Thread(target=takeInput)
            inputThread.start()

        if data != prevData:
            prevData = data

            if not firstRun:
                if recvThread.isAlive():
                    recvThread.join()
            recvThread = threading.Thread(target=recvData)
            recvThread.start()

        time.sleep(100)

        firstRun = False

        # else:
        #     print(data)

        if stop:
            raise KeyboardInterrupt

        if data.startswith(ping):
            resp = data.strip('PING ');
            client.send(('PONG ' + resp).encode())
except KeyboardInterrupt:
    while recvThread.isAlive():
        recvThread.join(1)
    sys.exit()
