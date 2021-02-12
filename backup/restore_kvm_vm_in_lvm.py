#!/usr/bin/env python3

"""
Project Name: 'basic-scripts'
Version: 0.9

Description:

Ihor Cheberiak (c) 2021
https://www.linkedin.com/in/ihor-cheberiak/
"""

import time as time_os
import os as terminal_os
import subprocess as shell


dir_backup = ""
kvm_vm_name = ""
dir_logs = "/var/log/"


def main():
    dir_backup = input("Enter the path to the directory with the backup of the desired VM: ")
    kvm_vm_name = str(dir_backup.split("/")[-2])[:-11]

    with open("{}{}-raw_info".format(dir_backup, kvm_vm_name)) as backup:
        temp_str = ""
        for line in backup:
            temp_str += line

    *rest, size_lvm, _, dev_lvm = temp_str.split()

    virsh_command("destroy")
    lvm_command("remove", dev_lvm)
    virsh_command("define")
    lvm_command("create", dev_lvm, size_lvm)

    logs_creation(["#"*100])
    terminal_os._exit(0)


def logs_creation(messages):
    if terminal_os.path.isfile("{}{}.log".format(dir_logs, kvm_vm_name)):
        access_type = "a"
    else:
        access_type = "w"
    
    with open("{}{}.log".format(dir_logs, kvm_vm_name), access_type) as log:
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


def virsh_command(command):
    """ 
    """
    if command == "destroy":
        performance_shell("virsh destroy {}".format(kvm_vm_name))
    elif command == "define":
        performance_shell("virsh define {}{}.xml".format(dir_backup, kvm_vm_name))
    elif command == "restore":
        performance_shell("virsh restore {}{}.vmstate".format(dir_backup, kvm_vm_name))


def lvm_command(command, lvm, size = None):
    """ command: (create) Создать блочное устройство LVM. (remove) Удалить блочное устройство LVM.
        size: Размер блочного устройства для Virtual Machine в 'Байтах'. Из файла -raw_info. 
    """
    if command == "create":
        performance_shell("sudo lvcreate -n {} -L{}B {}".format(kvm_vm_name, str(size), lvm.split("/")[-2]))
        archive_creation(lvm)
    elif command == "remove":
        performance_shell("sudo lvremove -f {}".format(lvm))


def archive_creation(lvm):
    performance_shell("gunzip -ck {}{}.gz > {}".format(dir_backup, kvm_vm_name, lvm))
    virsh_command("restore")


if __name__ == '__main__':
    main()
