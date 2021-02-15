#!/usr/bin/env python3

"""
Project Name: 'basic-scripts'
Version: 1.0

Description: Скрипт позволяет делать автоматические бекапы виртуальных машин 
используя его в CRON для гипервизора KVM размещенных в формате дискового образа.

Ihor Cheberiak (c) 2021
https://www.linkedin.com/in/ihor-cheberiak/
"""

import time as time_os
import os as terminal_os
import argparse as parser
import subprocess as shell


help_parser = parser.ArgumentParser(description="KVM backup of Virtual Machines on the Disk Image (img, raw, qcow2)")

help_parser.add_argument("vm_name", type=str, help="Example: srv4prod-vm")
help_parser.add_argument("img_dev", type=str,  help="Example: /kvm/image/prod-vm.img | .raw | .qcow2")
help_parser.add_argument("bakup_folder", type=str, help="Example: /var/backup/prod-vm/")

args_parser = help_parser.parse_args()
print(args_parser)

dir_logs = "/var/log/"
kvm_vm_name = args_parser.vm_name
img_dir = args_parser.img_dev
dir_backup = args_parser.bakup_folder

folder_backup = kvm_vm_name + "_" + time_os.strftime("%d.%m.%Y")
touch_folder_src = dir_backup + folder_backup + "/" + kvm_vm_name


def main():
    virsh_command()
    archive_creation()

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


def virsh_command(command = None):
    """ Остонавливает виртуальную машину (VM) и собирает информацию
        для ее восстановления из Backup по надобности в будущем.
    """
    if terminal_os.popen("virsh domstate " + kvm_vm_name).read().split() == ["running"] :
        performance_shell("virsh shutdown {0}".format(kvm_vm_name))
    if terminal_os.popen("virsh domstate " + kvm_vm_name).read().split() != ["running"]:
        performance_shell("virsh dumpxml {0} > {1}.xml".format(kvm_vm_name, touch_folder_src))
        performance_shell("virsh domblkinfo {0} {1} > {2}-{3}_info && virsh vol-pool {1} >> {2}-{3}_info && echo {1} >> {2}-{3}_info".format(kvm_vm_name, img_dir, touch_folder_src, img_dir[img_dir.find(".")-1:])) 
    
    logs_creation(["Process Virsh: Shutdown VM and creation of auxiliary files VM!".format(kvm_vm_name)])

    if command == "start":
        performance_shell("virsh start {0}".format(kvm_vm_name))
        logs_creation(["Process Virsh: Start VM {0} - Running".format(kvm_vm_name)])


def archive_creation(compression = 3):
    """ compression: Степень сжатия .gz файла от 1 до 9. Чем выше степень,
        тем больше нужно мощностей процессора и времени на создание архива.
    """
    logs_creation(["Process GZIP Disk Image: For disk recovery Virtual Machine " + kvm_vm_name])
    performance_shell("dd if={0} | gzip -kc -{1} > {2}{3}.gz".format(img_dir, str(compression), touch_folder_src, img_dir[img_dir.find("."):]))
    virsh_command("start")


if __name__ == '__main__':
    main()