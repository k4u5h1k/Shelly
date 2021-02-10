#!/usr/bin/env python3
import os
import getpass

def cd(path):
    os.chdir(path)
try:
    while True:
        cwd = os.getcwd()
        dirname = os.path.split(cwd)[-1]
        user = getpass.getuser()
        PS1 = f"{user} {dirname} $ "
        command = input(PS1)
        try:
            eval(command)
        except:
            print(f"Invalid command {user}!")

except KeyboardInterrupt:
    print("\nExiting cleanly")
    exit(1)
