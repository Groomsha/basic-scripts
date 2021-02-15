#!/usr/bin/env python3

"""
Project Name: 'basic-scripts'
Version: 1.0

Description: Скрипт позволяет востоновить бекапы виртуальных 
машин для гипервизора KVM размещенных в формате дискового образа.

Ihor Cheberiak (c) 2021
https://www.linkedin.com/in/ihor-cheberiak/
"""

import time as time_os
import os as terminal_os
import argparse as parser
import subprocess as shell

help_parser = parser.ArgumentParser(description="KVM restoring of Virtual Machines on the Disk Image (img, raw, qcow2)")
help_parser.add_argument("-backup", default=None, type=str, help="Example: /var/backup/prod-vm/srv-test-vm_01.01.2077/")

args_parser = help_parser.parse_args()
dir_backup = args_parser.backup
print(args_parser)

if dir_backup == None:
    dir_backup = input("Enter the path to the directory with the backup of the desired VM: ")


kvm_vm_name = str(dir_backup.split("/")[-2])[:-11]
dir_logs = "/var/log/"


def main():
    with open("{0}{1}-img_info".format(dir_backup, kvm_vm_name)) as backup:
        temp_str = ""
        for line in backup:
            temp_str += line

    *rest, pool, img = temp_str.split()
    
    logs_creation(["Start Process Restoring Virtual Machine: {0} {1}".format(kvm_vm_name, dir_backup)])

    virsh_command("destroy")
    virsh_command("delete", [pool, img])
    virsh_command("define")
    archive_creation(img)

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


def virsh_command(command, sources = None):
    """ Уничтажает виртуальную машину (VM), восстановление 
        из Backup и запускает виртуальную машину (VM)
    """
    if command == "destroy":
        performance_shell("virsh destroy {0}".format(kvm_vm_name))
    elif command == "delete":
        performance_shell("virsh vol-delete {1} --pool {0}".format(sources[0], sources[1]))
    elif command == "define":
        performance_shell("virsh define {0}{1}.xml".format(dir_backup, kvm_vm_name))
    elif command == "restore":
        performance_shell("virsh start {0}".format(kvm_vm_name))


def archive_creation(img):
    logs_creation(["Process GUNZIP Disk Image: For disk recovery VM: " + kvm_vm_name])
    performance_shell("gunzip -ck {0}{1}{3}.gz > {2}".format(dir_backup, kvm_vm_name, img, img[img.find("."):]))
    virsh_command("restore")


if __name__ == '__main__':
    main()