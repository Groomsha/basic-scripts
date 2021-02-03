#!/usr/bin/env python3

"""
Project Name: 'basic-scripts'
Version: 1.1b

Description: Скрипт позволяет делать автоматические бекапы виртуальных машин 
используя его в CRON для гипервизора KVM размещенных на блочном устройстве LVM

Ihor Cheberiak (c) 2021
https://www.linkedin.com/in/ihor-cheberiak/
"""

import sys as path_os
import time as time_os
import os as terminal_os


dir_logs = "/var/log/"
kvm_vm_name, dev_lvm, size_snap, dir_backup = path_os.argv[1:]
folder_backup = kvm_vm_name + "_" + time_os.strftime("%d.%m.%Y")
touch_folder_src = dir_backup + folder_backup + "/" + kvm_vm_name


def main():
    logs_creation("Start Process Backup Virtual Machine: " + kvm_vm_name)
    terminal_os.popen("mkdir -p " + dir_backup + folder_backup + "/").read()
    logs_creation("Create Folder Backup VM: " + dir_backup + folder_backup)

    virsh_command()
    lvm_command("create", int(size_snap))
    virsh_restore()  


def logs_creation(message):
    if terminal_os.path.isfile(dir_logs + kvm_vm_name + ".log"):
        access_type = "a"
    else:
        access_type = "w"
    
    with open(dir_logs + kvm_vm_name + ".log", access_type) as log:
        log.write("\n" + time_os.ctime() + " " + message)


def virsh_command():
    """ Остонавливает виртуальную машину (VM) и собирает информацию
        для ее восстановления из Backup по надобности в будущем.
    """
    if terminal_os.popen("virsh domstate " + kvm_vm_name).read().split() == ["running"]:
        terminal_os.popen("virsh save " + kvm_vm_name + " " + touch_folder_src + ".vmstate --running").read()
        logs_creation("Process Create: " + kvm_vm_name + ".vmstate --running ======>> Завершено без ошибок!")
    if terminal_os.popen("virsh domstate " + kvm_vm_name).read().split() != ["running"]:
        terminal_os.popen("virsh dumpxml " + kvm_vm_name + " > " + touch_folder_src + ".xml") 
        terminal_os.popen("virsh domblkinfo " + kvm_vm_name + " " + dev_lvm + " > " + touch_folder_src + 
        "-raw_info" + " && " + "virsh vol-pool " + dev_lvm + " >> " + touch_folder_src + "-raw_info" + 
        " && " + "echo " + dev_lvm + " >> " + touch_folder_src + "-raw_info")
        logs_creation("Process Create: вспомагательных файлов для востоновления ======>> Завершено без ошибок!")


def lvm_command(command, ratio = 2):
    """ command: (1) Создать LVM_Snap. (2) Удалить LVM_Snap.
        ratio: Размер таблицы(буфера), на каждые 8Gb LVM c VM нужно 256M. ratio=2(16Gb LVM) 
    """
    if command == "create":
        terminal_os.popen("lvcreate -s -n " + dev_lvm + "_snap -L" + str(ratio*256) + "M " + dev_lvm).read()
        logs_creation("LVM Snapshot Create: " + dev_lvm + "_snap Size: " + str(ratio*256) + "M Target:" + dev_lvm)
    elif command == "remove":
        terminal_os.popen("lvremove -f " + dev_lvm + "_snap")
        logs_creation("LVM Snapshot Remove " + dev_lvm + "_snap")


def virsh_restore():
    """ Запускает виртуальную машину (VM) из сохраненного ранее состояния """
    if terminal_os.popen("virsh domstate " + kvm_vm_name).read().split() != ["running"]:
        logs_creation("Process Restore Virtual Machine: Начат процесс восстановления состояния вертуальной машины!")
        terminal_os.popen("virsh restore " + touch_folder_src + ".vmstate")
        archive_creation()
    else:
        logs_creation("Error Process Restore VM: Виртуальная машина не выключена, процесс восстановления прерван!")
        lvm_command("remove")


def archive_creation(compression = 3):
    """ compression: Степень сжатия .gz файла от 1 до 9. Чем выше степень,
        тем больше нужно мощностей процессора и времени на создание архива.
    """
    terminal_os.popen("dd if=" + dev_lvm + "_snap" + " | gzip -ck -" + str(compression) + " > " + touch_folder_src + ".gz").read()
    logs_creation("Process GZIP LVM Snapshot: для востоновления диска Virtual Machine ======>> Завершено без ошибок!")
    logs_creation("Allocated to LVM Snapshot: Информация Allocated должно быть < 100% для работоспособности Snapshot!")
    logs_creation(terminal_os.popen("lvdisplay " + dev_lvm + "_snap").read())
    lvm_command("remove")
    logs_creation("#"*120)


main()
