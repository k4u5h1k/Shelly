#!/usr/bin/env python3
import threading
import random
import socket
import string
import sys
import time
import shutil
from readchar import readchar

cols = shutil.get_terminal_size().columns
fprint = lambda x: print(x,end='',flush=True)
clrline = lambda : fprint('\r'+' '*cols+'\r')

nickname = input('Enter a username: ')
nick_tosend = f'NICK {nickname} \n'
name_tosend = f'USER {nickname} macbook server {nickname}' + '\n'
join_channel = 'JOIN #kaushikschannel'
host = ('irc.freenode.net',6667)

connected = False
print('Type exit to leave the chatroom')
fprint('Connecting to server please wait for about 15 seconds.')

# Connect.
client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
client.connect((host[0], host[1]))

# Handshake.
client.send(name_tosend.encode())
client.send(nick_tosend.encode())
client.send((join_channel+' \r\n').encode())

client.setblocking(0)


def recieve():
    global justPrinted, logged_in, should_exit, msg
    client.settimeout(999999)
    while True:
        try:
            if msg!='exit':
                data = client.recv(512).decode('utf-8')
            else:
                break
            #fprint(data)
            if not logged_in:
                if join_channel in data:
                    logged_in = True
                    clrline()

                if 'Nickname is already in use' in data: 
                    clrline()
                    print("Nickname is already in use sorry!")
                    should_exit = True
                    break

            else:
                if justPrinted:
                    clrline()
                    justPrinted=False

                if logged_in and data.endswith('\r\n'):
                    for line in data.split('\n'):
                        if 'PRIVMSG #kaushikschannel' in line:
                            clrline()
                            print(line[1:line.index('!')]+line.split('PRIVMSG #kaushikschannel')[1])
                        elif 'QUIT' in line and msg !='exit':
                            clrline()
                            print(line[1:line.index('!')].rstrip()+' has disconnected.')
                    justPrinted = True

                    clrline()
                    fprint(f'You: {msg}')

                if data.startswith('PING '):
                    resp = data.strip('PING ');
                    client.send(('PONG ' + resp).encode())

                data=''

        except UnicodeDecodeError:
            continue
        except KeyboardInterrupt:
            continue

def start_send():
    global justPrinted, msg, recvt
    iswin = sys.platform.startswith('win')
    backspace = b'\x7f' if not iswin else b'\x08'
    while True:
        if msg=='exit':
            clrline()
            client.send(('QUIT'+' \r\n').encode())
            recvt.join()
            client.close()
            print()
            return
        clrline()
        fprint(f'You: {msg}')
        char = readchar.readchar()
        byte_char = lambda: char if type(char)==bytes else char.encode()
        actual_char = lambda: char.decode('utf-8') if type(char)==bytes else char

        if byte_char()==backspace:
            msg=msg[:-1]

        else:
            if actual_char()=='\n' or actual_char()=='\r':
                print()
                if msg!='':
                    # fprint(f'Sending {msg}',flush=True)
                    client.send(('PRIVMSG #kaushikschannel :'+msg+' \r\n').encode())
                    msg = ''

            elif actual_char() in string.printable:
                msg += actual_char()

justPrinted = False
logged_in = False
should_exit = False
msg = ''
recvt = threading.Thread(target=recieve)
recvt.daemon = True
recvt.start()
while not logged_in:
    time.sleep(0.5)
    if should_exit:
        raise KeyboardInterrupt
else:
    start_send()
