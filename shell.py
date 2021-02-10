#!/usr/bin/env python3

import os
import re
import sys
import platform
import readline
readline.parse_and_bind("tab: complete")

from cow import cow

# up = '\x1b[A'
# down = '\x1b[B'
# left = '\x1b[D'
# right = '\x1b[C'

reset = '\033[0m'
red = '\033[31m'
green = '\033[32m'
yellow = '\033[33m'
blue = '\033[34m'
purple = '\033[35m'
cyan = '\033[36m'

def cowsay(string):
    cow(string)


def cd(path):
    if os.path.isdir(path):
        os.chdir(path)
    else:
        print(f"{red}Not a valid directory path!{reset}")


def pwd():
    print(os.getcwd())


def whoami():
    print(os.getenv("USER"))


def ls():
    ls = os.listdir(os.curdir)
    max_file_len = max(len(name) for name in ls) + 5

    # I want list in three columns (neat stonk)
    counter = 0
    for obj in ls:
        print(obj.ljust(max_file_len),end="")
        counter+=1
        if counter%3==0 or counter == len(ls):
            print()


def clear():
    # Got this using clear | hexdump -C
    print("\x1b\x5b\x48\x1b\x5b\x32\x4a", end="")    


def touch(filename):
    if not os.path.exists(filename):
        open(filename, 'a').close()
    else:
        print(f"{red}file already exists{reset}")


def rm(filename):
    if os.path.exists(filename):
        os.remove(filename)
    else:
        print(f"{red}Not a valid file path!{reset}")

def cat(filename):
    if os.path.exists(filename):
        with open(filename) as handle:
            for line in handle:
                print(line.strip())

# This will make available = ['cd', 'path', ... with all functions above next line]
available = []
local_locals = list(locals().items()).copy()
for key, value in local_locals:
    if callable(value) and value.__module__ == __name__:
        available.append(key)

def runShell():
    cwd = os.getcwd()
    dirname = os.path.split(cwd)[-1]
    user = os.getenv('USER')
    PS1 = f"{cyan}{user}{reset} {green}{dirname}{reset} {purple}${reset} "

    # func_cleanup = re.compile(f"({'|'.join(available)})")

    command = input(PS1)

    # possible_types = {1: 'Python', 2: 'Shell', 3: 'Invalid'}

    old_stdout = sys.stdout
    try:
        sys.stdout = None 
        splitted = command.split(" ")
        print("splitted:", splitted)
        if splitted[0] in available:
            command_type = 2
            if len(splitted) == 1:
                command += '()'
            else:
                splitted.insert(1,"('")
                splitted.append("')")
                command = ''.join(splitted[:2])+' '.join(splitted[2:-1])+splitted[-1]
                print(command)
        elif exec(command) is None:
            command_type = 1
    except:
        command_type = 3
    sys.stdout = old_stdout

    if command == 'exit' or command == 'quit':
        raise KeyboardInterrupt
    elif command_type == 3:
        print(f"{red}Invalid command {user}!{reset}")
    else:
        exec(command)

try:
    while True:
        runShell()

except KeyboardInterrupt:
    print()
    print(yellow+"Exiting cleanly"+reset)
    print()
    exit(1)
