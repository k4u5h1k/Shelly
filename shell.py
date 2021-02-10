#!/usr/bin/env python3
import os
import re
import getpass
import sys


def cd(path):
    os.chdir(path)

def pwd():
    print(os.getcwd())

def whoami():
    print(getpass.getuser())

def ls():
    ls = os.listdir(os.curdir)
    max_file_len = max(len(name) for name in ls) + 5

    # I want list in three columns (neat stonk)
    counter = 0
    for obj in ls:
        print(obj.ljust(max_file_len),end="")
        counter+=1
        if counter%3==0:
            print()

def clear():
    # Got this using clear | hexdump -C
    print("\x1b\x5b\x48\x1b\x5b\x32\x4a", end="")    
    

up = '\x1b[A'
down = '\x1b[B'
left = '\x1b[D'
right = '\x1b[C'

# This will make available = ['cd', 'path', ... with all functions above next line]
available = []
local_locals = list(locals().items()).copy()
for key, value in local_locals:
    if callable(value) and value.__module__ == __name__:
        available.append(key)

class Exit(Exception):
    pass

def runShell():
    cwd = os.getcwd()
    dirname = os.path.split(cwd)[-1]
    user = getpass.getuser()
    PS1 = f"{user} {dirname} $ "

    # func_cleanup = re.compile(f"({'|'.join(available)})")

    command = input(PS1)

    possible_types = {1: 'Python', 2: 'Shell', 3: 'Invalid'}

    old_stdout = sys.stdout
    try:
        sys.stdout = None 
        splut = command.split()
        if command.split()[0] in available:
            command_type = 2
            if len(splut) == 1:
                command += '()'
        elif eval(command) is None:
            command_type = 1
    except:
        command_type = 3
    sys.stdout = old_stdout

    if command == 'exit' or command == 'quit':
        raise Exit
    elif command_type == 3:
        print(f"Invalid command {user}!")
    else:
        eval(command)

try:
    while True:
        runShell()

except (KeyboardInterrupt, EOFError, Exit):
    print("\b\bExiting cleanly")
    exit(1)
