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

help_parser.add_argument("vm_name", type=str, help="Example: srv4prod-vm")
help_parser.add_argument("bakup_folder", type=str, help="Example: /var/backup/prod-vm/")

args_parser = help_parser.parse_args()
print(args_parser)

dir_logs = "/var/log/"
kvm_vm_name = args_parser.vm_name
dir_backup = args_parser.bakup_folder

folder_backup = kvm_vm_name + "_" + time_os.strftime("%d.%m.%Y")
touch_folder_src = dir_backup + folder_backup + "/" + kvm_vm_name


def main():
    logs_creation(["#"*120])
    terminal_os._exit(0)


def logs_creation(messages):
    if terminal_os.path.isfile("{0}{1}.log".format(dir_logs, kvm_vm_name)):
        access_type = "a"
    else:
        access_type = "w"
    
    with open("{0}{1}.log".format(dir_logs, kvm_vm_name), access_type) as log:
        for message in messages:
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


def virsh_command():
    """ Остонавливает виртуальную машину (VM) и собирает информацию
        для ее восстановления из Backup по надобности в будущем.
    """
    if terminal_os.popen("virsh domstate " + kvm_vm_name).read().split() == ["работает"] :
        performance_shell("virsh save {0} {1}.vmstate --running".format(kvm_vm_name, touch_folder_src))
        #virsh shutdown srv
    if terminal_os.popen("virsh domstate " + kvm_vm_name).read().split() != ["работает"]:
        performance_shell("virsh dumpxml {0} > {1}.xml".format(kvm_vm_name, touch_folder_src))
        #virsh dumpxml srv > /var/kvm/vm-backup/srv_28.10.2019/kvm-srv.xml
        performance_shell("virsh domblkinfo {0} {1} > {2}-raw_info && virsh vol-pool {1} >> {2}-raw_info && echo {1} >> {2}-raw_info".format(kvm_vm_name, dev_lvm, touch_folder_src))
        #virsh domblkinfo srv /var/kvm/vm-sources/_srv.img > /var/kvm/vm-backup/srv_28.10.2019/kvm-disk
        #virsh vol-pool /var/kvm/vm-sources/_srv.img >> /var/kvm/vm-backup/srv_28.10.2019/kvm-disk
        #echo "/var/kvm/vm-sources/_srv.img" >> /var/kvm/vm-backup/srv_28.10.2019/kvm-disk
    
    #virsh domstate srv		>>>>>>>>>> shut off
    #virsh destroy srv		>>>>>>>>>> shut off

    #virsh start srv
    #virsh domstate srv		>>>>>>>>>> running

    #logs_creation(["Process Virsh Create: {0}.vmstate --running and creation of auxiliary files VM!".format(kvm_vm_name)])


def archive_creation(compression = 3):
    """ compression: Степень сжатия .gz файла от 1 до 9. Чем выше степень,
        тем больше нужно мощностей процессора и времени на создание архива.
    """
    #logs_creation(["Process GZIP LVM Snapshot: For disk recovery Virtual Machine " + kvm_vm_name])
    #dd if=/var/kvm/vm-sources/_srv.img | gzip -kc -3 > /var/kvm/vm-backup/srv_28.10.2019/kvm.img.gz
    performance_shell("dd if={0}_snap | gzip -ck -{1} > {2}.gz".format(dev_lvm, str(compression), touch_folder_src))


if __name__ == '__main__':
    main()