# This program will:
# * Connect to a router via Telnet and it will compare the running-config file
#   to the startup-config file on that device

import telnetlib
import os.path
import subprocess
import time
import sys


def ip_validity():
    global ip_address

    # Checking IP validity
    while True:
        ip_address = raw_input("Enter an IP address: ")

        # Checking octets
        a = ip_address.split('.')

        if (len(a) == 4) and (1 <= int(a[0]) <= 223) and (int(a[0]) != 127) and (int(a[0]) != 169 or int(a[1]) != 254) and (0 <= int(a[1]) <= 255 and 0 <= int(a[2]) <= 255 and 0 <= int(a[3]) <= 255):
            break

        else:
            print "\nThe IP address is INVALID! Please retry!\n"
            continue


def file_validity():
    while True:
        cfg_file = raw_input("Enter config file name and extension: ")

        # Changing exception message
        if os.path.isfile(cfg_file) is True:
            print "\nFile was found...\n"
            break

        else:
            print "\nFile %s does not exist! Please check and try again!\n" % cfg_file
            continue


def telnet(command):
    # Connecting to router via Telnet
    # Define telnet parameters
    username = 'teopy'
    password = 'python'

    # Specify the Telnet port (default is 23, anyway)
    port = 23

    # Specify the connection timeout in seconds for blocking operations, like
    # the connection attempt
    connection_timeout = 5

    # Specify a timeout in seconds. Read until the string is found or until
    # the timout has passed
    reading_timeout = 5

    # Logging into device
    connection = telnetlib.Telnet(ip_address, port, connection_timeout)

    # Waiting to be asked for an username
    router_output = connection.read_until("Username:", reading_timeout)
    # Enter the username when asked and a "\n" for Enter
    connection.write(username + "\n")

    # Waiting to be asked for a password
    router_output = connection.read_until("Password:", reading_timeout)
    # Enter the password when asked and a "\n" for Enter
    connection.write(password + "\n")
    time.sleep(1)

    # Setting terminal length for the entire output - disabling pagination
    connection.write("terminal length 0\n")
    time.sleep(1)

    # Entering global config mode
    connection.write("\n")
    connection.write(command + "\n")
    time.sleep(5)

    router_output = connection.read_very_eager()
    # print router_output

    # Closing the connection
    connection.close()

    return router_output

# User Options
try:
    # Entering user option
    while True:
        print """Use this tool to:
                 1: Compare running-config with startup-config
                 e: Exit program"""

        user_option = raw_input("Enter your choice: ")

        if user_option == "1":
            # Checking IP validity
            ip_validity()

            print "Please wait while the config file is being analyzed..."

            output_run = telnet("show running-config")
            output_start = telnet("show startup-config")

            # print output_run
            # print output_start

            # Creating and writing the command output to files
            file_run = open("file_run.txt", "w")

            print >>file_run, output_run

            file_start = open("file_start.txt", "w")

            print >>file_start, output_start

            # Closing both files after writing
            file_run.close()
            file_start.close()

            # Comparing the contents of the files and
            # saving the differences to a new file

            # First, reading the lines in each file and storing them as
            # elements of a list

            file_run = open("file_run.txt", "r")

            file_start = open("file_start.txt", "r")

            list_run = file_run.readlines()
            # print list_run

            list_start = file_start.readlines()
            # print list_start

            # Closing both files after reading
            file_run.close()
            file_start.close()

            for index, element in enumerate(list_run):
                if "version " in element and "!\r\n" == list_run[list_run.index(element) - 1]:
                    list_run[0:list_run.index(element)] = []

            # print list_run

            for index, element in enumerate(list_start):
                if "version " in element and "!\r\n" == list_start[list_start.index(element) - 1]:
                    list_start[0:list_start.index(element)] = []

            # print list_start

            file_diff = open("file_diff.txt", "w")

            # Finding lines in the running-config which are not present in the
            # startup-config
            run_diff = [x for x in list_run if x not in list_start]
            # print run_diff

            # Printing the lines to the file_diff.txt file
            for line in run_diff:
                print >>file_diff, "+" + line

            # Finding lines in the startup-config which are not present in the
            # running-config
            start_diff = [x for x in list_start if x not in list_run]
            # print start_diff

            # Printing the lines to the file_diff.txt file
            for line in start_diff:
                print >>file_diff, "-" + line

            file_diff.close()

        else:
            print "Exiting. Bye!"
            sys.exit()

except KeyboardInterrupt:
    print "Program aborted by user. Exiting. Bye!"
    sys.exit()
