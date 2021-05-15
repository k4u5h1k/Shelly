# Shelly
A no external dependancy, modular, single script, bash-like python REPL with realtime IRC chat and custom text editor `kedit`.

# Features
- All basic shell commands
- Python code interpretation
- Coloured prompt and error messages
- Tab completion
- Command specific help messages
- no external dependancies (custom implementations all the way)
- `shell.py` can be used alone! Meaning user may `rm -rf scripts`   
  if they do not desire chat and text editor functionality.

# Usage 
clone this repo and run `python3 shell.py`.

# Screenshots  

## Shell
![Screenshot 2021-04-23 at 11 49 16 PM](https://user-images.githubusercontent.com/59250093/116916069-771f8f80-ac6a-11eb-99db-32e94ee4c570.png)

## Chat
![Screenshot 2021-04-17 at 12 40 31 PM](https://user-images.githubusercontent.com/59250093/116916043-6cfd9100-ac6a-11eb-97ca-0a358c98f602.png)

## Editor
![Screenshot 2021-03-14 at 12 28 07 PM](https://user-images.githubusercontent.com/59250093/111060136-bd553f80-84c0-11eb-902f-5f4986d4f018.png)
![Screenshot 2021-03-14 at 12 28 27 PM](https://user-images.githubusercontent.com/59250093/111060146-c9410180-84c0-11eb-9fe3-8b10aeb4da98.png)

# TODO
- Pipe support.
- Redirect operator implementation. 
- sudo support. 
- chmod support. 
- Autojump support. 
- remote command execution (with consent) via IRC.  
- add support for running external binaries. 

# DEVELOPMENT
To add your own commands simply define them as a function above the `DEFINE YOUR FUNCTION ABOVE THIS LINE` line.

# CREDITS
- scripts/cow.py customized from https://github.com/VaasuDevanS/cowsay-python.
- readchar from https://github.com/magmax/python-readchar.
- .
