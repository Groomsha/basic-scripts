#!/usr/bin/env python3

"""
Project Name: 'basic-scripts'
Version: 0.3

Description:

Ihor Cheberiak (c) 2021
https://www.linkedin.com/in/ihor-cheberiak/
"""

import time as time_os
import os as terminal_os

dev_lvm = ""
kvm_vm_name = ""
dir_logs = "/var/log/"

touch_lvm_src = dev_lvm + kvm_vm_name


def main():
    virsh_command()
    lvm_command("remove")


def logs_creation(message):
    if terminal_os.path.isfile(dir_logs + kvm_vm_name + ".log"):
        access_type = "a"
    else:
        access_type = "w"
    
    with open(dir_logs + kvm_vm_name + ".log", access_type) as log:
        log.write("\n" + time_os.ctime() + " " + message)


def virsh_command():
    """ 
    """
    if terminal_os.popen("virsh domstate " + kvm_vm_name).read().split() == ["running"]:
        terminal_os.popen("virsh destroy " + kvm_vm_name).read()
    if terminal_os.popen("virsh domstate " + kvm_vm_name).read().split() != ["running"]:
        terminal_os.popen("virsh domblklist " + kvm_vm_name).read()


def lvm_command(command, size):
    """ command: (1) Создать блочное устройство LVM. (2) Удалить блочное устройство LVM_Snap.
        size: Размер блочного устройства для Virtual Machine в 'Байтах'. Из файла -raw_info. 
    """
    if command == "create":
        terminal_os.popen("lvcreate -n " + kvm_vm_name + "-L" + str(size) + "B " + dev_lvm).read()
    elif command == "remove":
        terminal_os.popen("lvremove -f " + touch_lvm_src)


main()
