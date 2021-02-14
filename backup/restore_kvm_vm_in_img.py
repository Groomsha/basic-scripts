#!/usr/bin/env python3

"""
Project Name: 'basic-scripts'
Version: 0.1

Description:

Ihor Cheberiak (c) 2021
https://www.linkedin.com/in/ihor-cheberiak/
"""

import time as time_os
import os as terminal_os
import argparse as parser
import subprocess as shell

help_parser = parser.ArgumentParser(description="")
help_parser.add_argument("-bakup", default=None, type=str, help="Example: /var/backup/prod-vm/srv-test-vm_01.01.2077/")

args_parser = help_parser.parse_args()
dir_backup = args_parser.bakup
print(args_parser)

dir_backup = input("Enter the path to the directory with the backup of the desired VM: ")
kvm_vm_name = str(dir_backup.split("/")[-2])[:-11]
dir_logs = "/var/log/"


def main():  
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
    #virsh vol-delete /var/kvm/vm-sources/_srv.img --pool vm-sources
    if command == "destroy":
        #virsh list --all | grep srv
        #virsh destroy srv4dc01-win2k16				>>>>>>>>>> shut off
        performance_shell("virsh destroy {0}".format(kvm_vm_name))
    elif command == "define":
        #virsh define /var/kvm/vm-backup/kvm-srv.xml
        performance_shell("virsh define {0}{1}.xml".format(dir_backup, kvm_vm_name))
    elif command == "restore":
        #virsh start srv
        #virsh domstate srv				>>>>>>>>>> running
        performance_shell("virsh restore {0}{1}.vmstate".format(dir_backup, kvm_vm_name))


def archive_creation(lvm):
    #logs_creation(["Process GUNZIP LVM Block Device: For disk recovery VM: " + kvm_vm_name])
    #gunzip -ck /var/kvm/vm-backup/kvm.img.gz > /var/kvm/vm-sources/_srv.img
    performance_shell("gunzip -ck {0}{1}.gz > {2}".format(dir_backup, kvm_vm_name, lvm))


if __name__ == '__main__':
    main()