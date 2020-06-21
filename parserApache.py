# $ parseApache [-h|-B|-R|-n <minutes>] [-W <Warn threshold>] [-C <Critical threshold>] <apache log file name>
# Where:
# -h: print a usage information to the stdout and exits
# -B: prints the number of log entries per browser type and exits
# -R: Exits with WARNING or CRITICAL status if the number of log entries by the same source IP address is respectively above <Warn threshold> or <Critical threshold>
# -n <minutes>: Exits with WARNING or CRITICAL status if the number of log lines in some consecutive <minutes> was respectively above <Warn threshold> or <Critical threshold>
# If the command line does not satisfy the syntax, the file is not found or the warning or critical values don't make sense (i.e. warn is higher than critical), the UNKNOWN status should be returned.

from optparse import OptionParser
from datetime import datetime
from datetime import timedelta
import sys
import os.path
from os import path

parser = OptionParser()
# parser.add_option("-h", help="print a usage information")
parser.add_option("-B", action="store_true",
                  help="prints the number of log entries per browser type")
parser.add_option("-R", action="store_true",
                  help="Exits with WARNING or CRITICAL status if the number of log entries by the same source IP address is respectively above <Warn threshold> or <Critical threshold>")
parser.add_option("-n", action="store", type=int, help="Exits with WARNING or CRITICAL status if the number of log lines in some consecutive <minutes> was respectively above <Warn threshold> or <Critical threshold> (# go to the last date and make that the datetime, then subtract n minutes and go check backwards)")
parser.add_option("-W", action="store", type=int, help="Warn threshold")
parser.add_option("-C", action="store", type=int, help="Critical threshold")
# parser.add_option("-f", action="store", type="string", dest="filename")

(options, args) = parser.parse_args()


def checkFileExistence(filename):
    exists = path.exists(filename)
    if exists:
        pass
    else:
        print("UNKNOWN")
        exit(3)


def readFile(file):
    with open(file) as f:
        lines = f.readlines()
    return lines


def joinUrl(arr):
    line_arr = " "
    url_arr = []
    for index in range(7, len(arr)):
        url_arr.append(arr[index])
    line_arr = line_arr.join(url_arr)
    return line_arr


def getCount(elem_arr):
    elem_dic = {}
    for elem in elem_arr:
        if elem in elem_dic:
            elem_dic[elem] += 1
        else:
            elem_dic[elem] = 1
    return elem_dic


def printEntries(elem_dic):
    for k, v in elem_dic.items():
        print(k.rstrip() + " : " + str(v))


def checkEntriesWithThresholds(elem_dic, warnThreshold, criticalThreshold):
    warn_flag = False
    critical_flag = False
    for k, v in elem_dic.items():
        if v > warnThreshold:
            warn_flag = True
        if v > criticalThreshold:
            critical_flag = True
    return warn_flag, critical_flag


def checkThresholdFlags(warn_flag, critical_flag):
    if critical_flag:
        print("CRITICAL")
        exit(2)
    elif warn_flag:
        print("WARNING")
        exit(1)
    else:
        print("OK")
        exit(0)

# print(options)
# print(args)


warn_flag = False
critical_flag = False

if options.B == True:
    if len(args) == 0 or options.R == True or options.n != None:
        print("UNKNOWN")
        exit(3)

    # Read File
    filename = args[0]
    checkFileExistence(filename)
    lines = readFile(filename)

    browser_access_list = []
    for line in lines:
        browser_access_list.append(joinUrl(line.split("]")[1].split(" ")))
    browser_count_list = getCount(browser_access_list)

    # Check if total is equal to number of lines of entries
    countadorofski_browser = 0
    for elemInd in browser_count_list:
        countadorofski_browser += browser_count_list[elemInd]
    # print(countadorofski_browser)

    printEntries(browser_count_list)
    exit(0)

elif options.R == True:
    if len(args) == 0 or options.B == True or options.n != None:
        print("UNKNOWN")
        exit(3)

    if options.W == None and options.C == None:
        print("OK")
        exit(0)

    # Read File
    filename = args[0]
    checkFileExistence(filename)
    lines = readFile(filename)

    if options.W != None and options.C != None:
        warnThreshold = options.W
        criticalThreshold = options.C
        if warnThreshold > criticalThreshold:
            print("UNKNOWN")
            exit(3)
    elif options.W != None:
        warnThreshold = options.W
        criticalThreshold = float('inf')
    elif options.C != None:
        criticalThreshold = options.C
        warnThreshold = float('inf')

    ip_entries = []
    for line in lines:
        ip_entries.append(line.split(" ")[0])
    ip_entries_count = getCount(ip_entries)

    # Check if total is equal to number of lines of entries
    countadorofski_ip = 0
    for elemInd in ip_entries_count:
        countadorofski_ip += ip_entries_count[elemInd]
    # print(countadorofski_ip)

    # printEntries(ip_entries_count)
    warn_flag, critical_flag = checkEntriesWithThresholds(
        ip_entries_count, warnThreshold, criticalThreshold)
    checkThresholdFlags(warn_flag, critical_flag)
    # exit(0)


# go to the last date and make that the datetime, then subtract n minutes and go check backwards
elif options.n != None:
    if options.n <= 0 or len(args) == 0 or options.B == True or options.R == True:
        print("UNKNOWN")
        exit(3)
    if options.W == None and options.C == None:
        print("OK")
        exit(0)

    n_minutes = options.n

    if options.W != None and options.C != None:
        warnThreshold = options.W
        criticalThreshold = options.C
        if warnThreshold > criticalThreshold:
            print("UNKNOWN")
            exit(3)
    elif options.W != None:
        warnThreshold = options.W
        criticalThreshold = float('inf')
    elif options.C != None:
        criticalThreshold = options.C
        warnThreshold = float('inf')

    # Read File
    filename = args[0]
    checkFileExistence(filename)
    lines = readFile(filename)

    date_entries = []
    for line in lines:
        date_entries.append(line.split("[")[1].split(" ")[0])
    # print(date_entries)
    date_entries_count = getCount(date_entries)
    out_date = []
    count = 0
    for elem in date_entries:
        out_date.append(datetime.strptime(elem, "%d/%b/%Y:%H:%M:%S"))
        date = out_date[-1]
    # print(date)
    # print(out_date)
    date_plus_minutes = date - timedelta(minutes=n_minutes)
    # print(date_plus_minutes)
    count = 0
    for d in range(len(out_date)-1, -1, -1):
        if out_date[d] > date_plus_minutes:
            count += 1
    # print(count)
    if count > criticalThreshold:
        critical_flag = True
    elif count > warnThreshold:
        warn_flag = True
    checkThresholdFlags(warn_flag, critical_flag)
    # exit(0)
else:
    print("OK")
