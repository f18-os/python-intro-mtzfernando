#! /usr/bin/env python3

import os, sys, time, re

pid = os.getpid()
while 1:
    os.write(1, "My Shell$ ".encode())
    command = os.read(0, 100).decode()
    args = command.split()

    if args[0].lower() == 'exit':
        os.write(1, "Exiting inside if!".encode())
        sys.exit(0)

    # if '<' in args:
    #     os.write(1, "< exists".encode())
    # if '>' in args:
    #     os.write(1, "> exists".encode())

    os.write(1, ("About to fork (pid:%d)\n" % pid).encode())

    rc = os.fork()

    if rc < 0:
        os.write(2, ("fork failed, returning %d\n" % rc).encode())
        sys.exit(1)

    elif rc == 0:                   # child
        os.write(1, ("Child: My pid==%d.  Parent's pid=%d\n" % (os.getpid(), pid)).encode())
        if '>' in args:
            os.close(1)  # redirect child's stdout
            sys.stdout = open(args[3], "w")
            fd = sys.stdout.fileno()  # os.open("p4-output.txt", os.O_CREAT)
            os.set_inheritable(fd, True)
            os.write(2, ("Child: opened fd=%d for writing\n" % fd).encode())
            args.remove('>')
            for dir in re.split(":", os.environ['PATH']):  # try each directory in the path
                program = "%s/%s" % (dir, args[0])
                # os.write(1, ("Child:  ...trying to exec %s\n" % program).encode())
                try:
                    os.execve(program, (args[0], args[1]), os.environ)  # try to exec program
                except FileNotFoundError:   # ...expected
                    pass                    # ...fail quietly
        if '<' in args:
            os.close(0)  # redirect child's stdout
            sys.stdout = open("p3-exec.py", "r")
            fd = sys.stdin.fileno()  # os.open("p4-output.txt", os.O_CREAT)
            # os.set_inheritable(fd, True)
            os.write(1, ("Child: opened fd=%d for writing\n" % fd).encode())
            args.remove('<')
            for dir in re.split(":", os.environ['PATH']):  # try each directory in the path
                program = "%s/%s" % (dir, args[0])
                # os.write(1, ("Child:  ...trying to exec %s\n" % program).encode())
                try:
                    os.execve(program, (args[0], args[1]), os.environ)  # try to exec program
                except FileNotFoundError:   # ...expected
                    pass


        os.write(2, ("Child:    Could not exec %s\n" % args[0]).encode())
        sys.exit(1)                 # terminate with error

    else:                           # parent (forked ok)
        os.write(1, ("Parent: My pid=%d.  Child's pid=%d\n" %
                     (pid, rc)).encode())
        childPidCode = os.wait()
        os.write(1, ("Parent: Child %d terminated with exit code %d\n" %
                     childPidCode).encode())
