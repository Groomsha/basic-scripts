#!/usr/bin/env python3

"""
"""

import os 
myCmd = os.popen('ls -la').read()

print(myCmd)