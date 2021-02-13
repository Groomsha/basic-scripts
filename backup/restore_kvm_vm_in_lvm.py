#!/usr/bin/env python3

"""
Project Name: 'basic-scripts'
Version: 1.0

Description: Скрипт позволяет востоновить бекапы виртуальных 
машин для гипервизора KVM размещенных на блочном устройстве LVM.

Ihor Cheberiak (c) 2021
https://www.linkedin.com/in/ihor-cheberiak/
"""

import time as time_os
import os as terminal_os
import argparse as parser
import subprocess as shell

help_parser = parser.ArgumentParser(description="KVM restoring of Virtual Machines on the LVM block device")
help_parser.add_argument("-bakup", default=None, type=str, help="Example: /var/backup/prod-vm/srv-test-vm_01.01.2077/")

args_parser = help_parser.parse_args()
dir_backup = args_parser.bakup
print(args_parser)

dir_backup = input("Enter the path to the directory with the backup of the desired VM: ")
kvm_vm_name = str(dir_backup.split("/")[-2])[:-11]
dir_logs = "/var/log/"


def main():
    with open("{0}{1}-raw_info".format(dir_backup, kvm_vm_name)) as backup:
        temp_str = ""
        for line in backup:
            temp_str += line

    *rest, size_lvm, _, dev_lvm = temp_str.split()

    logs_creation(["Start Process Restoring Virtual Machine: {0} {1}".format(kvm_vm_name, dir_backup)])

    virsh_command("destroy")
    lvm_command("remove", dev_lvm)
    virsh_command("define")
    lvm_command("create", dev_lvm, size_lvm)

    logs_creation(["#"*120])
    print("Restore Сompleted!")
    
    terminal_os._exit(0)


def logs_creation(messages):
    if terminal_os.path.isfile("{0}{1}.log".format(dir_logs, kvm_vm_name)):
        access_type = "a"
    else:
        access_type = "w"
    
    with open("{0}{1}.log".format(dir_logs, kvm_vm_name), access_type) as log:
        for message in messages:
            print(time_os.ctime() + " " + message)
            log.write("\n" + time_os.ctime() + " " + message)


def performance_shell(command, wait_shell = True):
    shell_os = shell.Popen(command, stdout=shell.PIPE, stderr=shell.PIPE, shell=True, executable="/bin/bash", universal_newlines=True)

    if wait_shell:
        shell_os.wait()
    
    output, errors = shell_os.communicate()
    if len(str(output)) != 0:
        logs_creation(str(output.strip()).splitlines())
    if len(str(errors)) != 0:
        logs_creation(str(errors.strip()).splitlines())


def virsh_command(command):
    """ Уничтажает виртуальную машину (VM), восстановление 
        из Backup и запускает виртуальную машину (VM)
    """
    if command == "destroy":
        performance_shell("virsh destroy {0}".format(kvm_vm_name))
    elif command == "define":
        performance_shell("virsh define {0}{1}.xml".format(dir_backup, kvm_vm_name))
    elif command == "restore":
        performance_shell("virsh restore {0}{1}.vmstate".format(dir_backup, kvm_vm_name))


def lvm_command(command, lvm, size = None):
    """ command: (create) Создать блочное устройство LVM. (remove) Удалить блочное устройство LVM.
        size: Размер блочного устройства для Virtual Machine в 'Байтах'. Из файла -raw_info. 
    """
    if command == "create":
        performance_shell("sudo lvcreate -y -n {0} -L{1}B {2}".format(kvm_vm_name, str(size), lvm.split("/")[-2]))
        logs_creation(["LVM Block Device Create: {0} Size: {1} Byte Target: {2}".format(kvm_vm_name, str(size), lvm)])
        archive_creation(lvm)
    elif command == "remove":
        performance_shell("sudo lvremove -f {0}".format(lvm))
        logs_creation(["LVM Block Device Remove {0}".format(lvm)])


def archive_creation(lvm):
    logs_creation(["Process GUNZIP LVM Block Device: For disk recovery VM: " + kvm_vm_name])
    performance_shell("gunzip -ck {0}{1}.gz > {2}".format(dir_backup, kvm_vm_name, lvm))
    virsh_command("restore")


if __name__ == '__main__':
    main()
