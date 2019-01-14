#!/usr/bin/python3
import subprocess as sp
from pref import preferences

currentSelected = ""
status = "disconnected"  # connected | disconnected | idle


def executeCommand(cmd=[""]):
    try:
        res = sp.run(
            cmd,
            shell=True,
            check=True,
            stdout=sp.PIPE,
            executable='/bin/bash')
        return res.stdout.splitlines()
    except sp.CalledProcessError as e:
        print("command '{}' return with error (code {}): {}".format(
            e.cmd, e.returncode, e.output))
        return []


def executeCommandRealTime(cmd=[""]):
    p = sp.Popen(
        cmd,
        stdout=sp.PIPE,
        stderr=sp.STDOUT,
        shell=True,
        executable='/bin/bash')
    return p.stdout
