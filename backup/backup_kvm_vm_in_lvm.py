#!/usr/bin/env python3

"""
"""

import os as terminal

dir_backup = ""
dir_logs = ""


def returning_command(dir_loc, command):
    return terminal.popen(command + " " + dir_loc).read()


print(returning_command(dir_backup, "ls -la"))
