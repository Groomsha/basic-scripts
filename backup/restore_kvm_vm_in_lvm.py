#!/usr/bin/env python3

"""
Project Name: 'basic-scripts'
Version: 0.4

Description:

Ihor Cheberiak (c) 2021
https://www.linkedin.com/in/ihor-cheberiak/
"""

import time as time_os
import os as terminal_os
import subprocess as shell


dev_lvm = ""
kvm_vm_name = ""
dir_logs = "/var/log/"


def main():
    virsh_command()
    lvm_command("remove")


def logs_creation(messages):
    if terminal_os.path.isfile(dir_logs + kvm_vm_name + ".log"):
        access_type = "a"
    else:
        access_type = "w"
    
    with open(dir_logs + kvm_vm_name + ".log", access_type) as log:
        for message in messages:
            log.write("\n" + time_os.ctime() + " " + message)


def performance_shell(command, wait_shell = True):
    shell_os = shell.Popen(command, stdout=shell.PIPE, stderr=shell.PIPE, shell=True, executable="/bin/bash", universal_newlines=True)

    if wait_shell:
        shell_os.wait()
    
    output, errors = shell_os.communicate()
    if len(str(output)) != 0:
        logs_creation(str(output).splitlines())
    if len(str(errors)) != 0:
        logs_creation(str(errors).splitlines())


def virsh_command():
    """ 
    """
    if terminal_os.popen("virsh domstate " + kvm_vm_name).read().split() == ["running"]:
        performance_shell("virsh destroy " + kvm_vm_name)
    if terminal_os.popen("virsh domstate " + kvm_vm_name).read().split() != ["running"]:
        performance_shell("virsh domblklist " + kvm_vm_name)


def lvm_command(command, size):
    """ command: (1) Создать блочное устройство LVM. (2) Удалить блочное устройство LVM_Snap.
        size: Размер блочного устройства для Virtual Machine в 'Байтах'. Из файла -raw_info. 
    """
    if command == "create":
        performance_shell("sudo lvcreate -n " + kvm_vm_name + " -L" + str(size) + "B " + dev_lvm)
    elif command == "remove":
        performance_shell("sudo lvremove -f " + dev_lvm)


if __name__ == '__main__':
    main()
