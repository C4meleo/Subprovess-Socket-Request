#!/bin/python3

import platform
import os
from sys import argv
import ipaddress
import subprocess
import socket
import joblib

def socket_windows(success_list, ip_str, min_port, max_port):
    range_port = max_port - min_port
    for port in range(min_port, max_port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        res = s.connect_ex((ip_str, port))
        s.close()
        if res == 0: 
            print(f"{ip_str}:{port} ONLINE")
            success_list.append((ip_str, port))
            continue
        else:
         # elif res == 111: 
            range_port -= 1
            if(range_port == 0):
                print(f"{ip_str}: OFFLINE")
            continue
        #else:
        #    print(f"{ip_str} OFFLINE : {res}")
        #    break               


def ping_windows(success_list, ip_str):
    try:
        subprocess.check_output(f"ping -n 1 -w 1 {ip_str}", shell=True, universal_newlines=True)
        print(f"{ip_str} ONLINE")
        success_list.append(ip_str)
    except:
        print(f"{ip_str} OFFLINE")

def socket_linux(success_list, ip_str, min_port, max_port):
    for port in range(min_port, max_port):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.settimeout(1)
        res = s.connect_ex((ip_str, port))
        s.close()
        if res == 0: 
            print(f"{ip_str}:{port} ONLINE")
            success_list.append((ip_str, port))
        elif res == 111: continue
        else:
            print(f"{ip_str} OFFLINE : {res}")
            break

def ping_linux(success_list, ip_str):
    try:
        subprocess.check_output(["ping", "-n", "-W1", "-i", "1", "-c", "1", ip_str])
        print(f"{ip_str} ONLINE")
        success_list.append(ip_str)
    except:
        print(f"{ip_str} OFFLINE")

def show_result (success_list) :
    print(f"\n\
###########################\n\
List of online IPs address :\n")

    for i, ip in enumerate(success_list):
        if type(ip) is tuple : print(f"{i+1}.\t{ip[0]}:{ip[1]}")
        else: print(f"{i+1}.\t{ip}")

    print("\
###########################\n")

def write_result (success_list):
    ind = argv.index("-o") + 1
    try:
        with open(argv[ind], "w") as f:
            for ip in success_list:
                if type(ip) is tuple: f.write(f"{ip[0]}:{ip[1]}\n")
                else: f.write(f"{ip}\n")
    except Exception as e:
        print(f"Error writing to file : {e}")
        exit(0)

# If there is the '-h' argument then the helper
if "-h" in argv:
    print("\n\
Get your IPs script by Joakim and Léo: \n\
Usage :\n\
./tp1.py (-p or -s) [-h]\n\
\n\
Thanks for using our script, hope you enjoy !\n")
    exit(0)
elif "-p" not in argv and "-s" not in argv:
    print("Error in usage:")
    print("\n\
Get your IPs script by Joakim and Léo: \n\
Usage :\n\
./tp1.py (-p or -s) [-h]\n\
\n\
Thanks for using our script, hope you enjoy !\n")
    exit(0)

if platform.system() == "Linux":
    import multiprocessing

    print(f"\n\
###########################\n\
Your system is on Linux on release : {platform.release()}\n\
###########################\n")

    file_path = "./"
    file_name = "tp1.txt"

    # Write ouput to the temp directory
    os.system(f"ip r > {file_path}{file_name}")

    # Get list of files in the temp directory
    curr_dir = os.listdir(file_path)
    
    # Check if output file exist
    bool = 0
    for file in curr_dir:
        print(file)
        if file == file_name:
            bool = 1

    # If file not found then exit script
    if bool == 0:
        print(f"Error while writing result file in {file_path}, exiting script...")
        exit(1)
    else:
        print(f"\n\
###########################\n\
Result file is correclty created !\n\
###########################\n")

    # Read ouput file
    with open(f"{file_path}{file_name}", "r") as f:
        output = f.readlines()[1:] # Get all lines except the first one

    network_list = []
    for line in output:
        arr = line.split(" ")

        # If error then it's an interface witout ip
        try:
            new_line = f"Int: {arr[2]}\tIp: {arr[8]}\n"
        except IndexError:
            continue

        network = dict()
        network["interface"] = arr[2]
        network["ip"] = arr[8]
        network["network"] = arr[0]
        
        network_list.append(network)

    print(f"\n\
###########################\n\
List of IPs address :\n")

    for i, network in enumerate(network_list):
        print(f"{i}. Int: {network['interface']}\tIp: {network['ip']}\tNetwork: {network['network']}\n")

    ind = input("Select network number OR an IP range (format: 10.0.0.1-10.0.0.6) : ")
    
    if "-s" in argv:
        port_range = input("Enter port range to scan : ")
        arr = port_range.split('-')
        min_port = int(arr[0])
        max_port = int(arr[1])

    try:
        chose_network = network_list[int(ind)]
        ip_range = ipaddress.IPv4Network(chose_network["network"])
    except:
        arr = ind.split('-')
        if len(arr) > 1:
            ip_range = range(int(ipaddress.IPv4Address(arr[0])), int(ipaddress.IPv4Address(arr[1])))
        else:
            print("Invalid selection, exiting...")
            exit(1)

    list_ip = []
    for ip in ip_range:
        if type(ip) is int:
            ip_str = str(ipaddress.IPv4Address(ip))
            if not ip_str.endswith(".0") and not ip_str.endswith(".255"):
                list_ip.append(ip_str)
        else:
            ip_str = str(ip)
            if not ip_str.endswith(".0") and not ip_str.endswith(".255"):
                list_ip.append(ip_str)

    manager = multiprocessing.Manager()
    success_list = manager.list()
    mid = len(list_ip) // 2
    
    if "-p" in argv:

        joblib.Parallel(n_jobs=10, prefer="threads")(joblib.delayed(ping_linux)(success_list, ip_str) for ip_str in list_ip)

    elif "-s" in argv:
        
        joblib.Parallel(n_jobs=10, prefer="threads")(joblib.delayed(socket_windows)(success_list, ip_str, min_port, max_port) for ip_str in list_ip)

    if "-o" in argv:
        write_result(success_list)
    else:
       show_result(success_list)
    
elif platform.system() == "Windows":
    print(f"\n\
#########################################\n\
Your system is on Windows on release : {platform.release()}\n\
#########################################\n")

    file_path = 'tmp/'
    file_name = "tp1.txt"

    if not os.path.exists(file_path):
        os.makedirs(file_path)
        print("The new directory is created!\n")

    # Write ouput to the temp directory
    os.system(f"ipconfig > {file_path}{file_name}")

    # Get list of files in the temp directory
    curr_dir = os.listdir(file_path)
    
    # Check if output file exist
    bool = 0
    for file in curr_dir:
        print(file)
        if file == file_name:
            bool = 1

    # If file not found then exit script
    if bool == 0:
        print(f"Error while writing result file in {file_path}, exiting script...")
        exit(1)
    else:
        print(f"\n\
##################################\n\
Result file is correclty created !\n\
##################################\n")

        # Read ouput file
        network_list = []
        with open(f"{file_path}{file_name}", "r") as f:
            lines = f.readlines()

            for i, line in enumerate(lines):
                if line.find("IPv4") != -1:
                    network = dict()
                    

                    network["ip"] = line.split(' ')[-1].rstrip()
                    network["network"] = lines[i+1].split(' ')[-1].rstrip()

                    c=1
                    while True:
                        if lines[i-c][0] != "\n" and lines[i-c][0] != " ":
                            network["interface"] = lines[i-c]
                            break
                        c+=1
                    
                    network_list.append(network)

        print(f"\n\
##########################################################\n\n\
List of IPs address :\n")

        for i, network in enumerate(network_list):
            print(f"{i}.\t{network['interface']}\t{network['ip']}\t{network['network']}\n")

        ind = input("\nSelect network number OR an IP range (format: 10.0.0.1-10.0.0.6) : ")

        if "-s" in argv:
            port_range = input("Enter port range to scan : ")
            arr = port_range.split('-')
            min_port = int(arr[0])
            max_port = int(arr[1])

        try:
            chose_network = network_list[int(ind)]
            ip_range = ipaddress.IPv4Network(chose_network["network"])
        except:
            arr = ind.split('-')
            if len(arr) > 1:
                ip_range = range(int(ipaddress.IPv4Address(arr[0])), int(ipaddress.IPv4Address(arr[1])))
            else:
                print("Invalid selection, exiting...")
                exit(1)

        list_ip = []
        for ip in ip_range:
            if type(ip) is int:
                ip_str = str(ipaddress.IPv4Address(ip))
                if not ip_str.endswith(".0") and not ip_str.endswith(".255"):
                    list_ip.append(ip_str)
            else:
                ip_str = str(ip)
                if not ip_str.endswith(".0") and not ip_str.endswith(".255"):
                    list_ip.append(ip_str)

        success_list = []
        mid = len(list_ip) // 2

        if "-p" in argv:
            
            joblib.Parallel(n_jobs=10, prefer="threads")(joblib.delayed(ping_windows)(success_list, ip_str) for ip_str in list_ip)
        
        elif "-s" in argv:
            joblib.Parallel(n_jobs=10, prefer="threads")(joblib.delayed(socket_windows)(success_list, ip_str, min_port, max_port) for ip_str in list_ip)

        if "-o" in argv:
            write_result(success_list)
        else:
            show_result(success_list)


else:
    print("Your OS is not supported, exiting script...")