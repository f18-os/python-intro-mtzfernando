#! /usr/bin/env python3

import os
import re
import sys

def pipe(arg):                                          # Function to take care of the piping
    read, write = os.pipe()                             # Create the read and write pipe
    fc = os.fork()                                      # Fork a child off the child
    if fc == 0:
        os.close(1)                                     # Redirect to the pipe's output
        write = os.dup(write)
        os.set_inheritable(write, True)                 # Set it to inheritable
        for dir in re.split(":", os.environ['PATH']):   # try each directory in the path
            program = "%s/%s" % (dir, args[0])
            try:
                os.execve(program, (arg[0], arg[1]), os.environ)    # try to exec program
            except FileNotFoundError:                               # ...expected
                pass
    else:
        os.close(0)                                             # Redirect to the pipe's input
        read = os.dup(read)
        os.set_inheritable(read, True)                          # Set it to inheritable
        os.wait()                                               # Wait for child to finish
        for dir in re.split(":", os.environ['PATH']):           # try each directory in the path
            program = "%s/%s" % (dir, args[2])
            try:
                os.execle(program, arg[2], os.environ)          # try to exec program
            except FileNotFoundError:                           # ...expected
                pass

pid = os.getpid()
if "PS1" in os.environ:
    pass
else:
    os.environ['PS1'] = "$"
e = os.environ
while 1:
    os.write(1, e.get('PS1').encode())             # Print My shell
    command = os.read(0, 100).decode()              # Wait for command to execute

    if not command:
        sys.exit(0)
    args = command.split()                          # Split the command into a list
    if len(args) == 0:
        continue
    if args[0].lower() == 'exit':                   # If user types exit end the program
        sys.exit(0)

    rc = os.fork()                                  # Fork the process

    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)
    elif rc == 0:                                   # child
        if '|' in args:                             # Check if it is a pipe
            args.remove('|')                        # Remove the pipe from the list
            pipe(args)                              # Call pipe function
        if '>' in args:
            os.close(1)                             # redirect child's stdout
            sys.stdout = open(args.pop(), "w")
            fd = sys.stdout.fileno()
            os.set_inheritable(fd, True)
            args.remove('>')
        if '<' in args:
            os.close(0)                             # redirect child's stdin
            sys.stdin = open(args[2], "r")
            fd = sys.stdin.fileno()
            os.set_inheritable(fd, True)
            args.remove('<')

        if args[0].lower() == 'cd':
            if args[1] == '..':
                path = os.getcwd()
                last = path.rfind('/')
                path = path[0:last]
                os.chdir(path)
            else:
                os.chdir(args[1])
            if len(args) > 2:
                args.pop(0)
                args.pop(0)
            else:
                sys.exit(0)

        for dir in re.split(":", os.environ['PATH']):  # try each directory in the path
            program = "%s/%s" % (dir, args[0])
            try:
                if '/' in args[0]:
                    os.execve(args[0], args, os.environ)
                else:
                    os.execve(program, args, os.environ)    # try to exec program
            except FileNotFoundError:                   # ...expected
                pass

        os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
        sys.exit(1)                                    # terminate with error
    else:                                              # parent (forked ok)
        childPidCode = os.wait()
