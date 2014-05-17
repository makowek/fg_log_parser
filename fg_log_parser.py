#!/usr/local/bin/python2.7
""" Fortigate Log Parser

Usage: fg_log_parser.py
  fg_log_parser.py (-f <logfile> | --file <logfile>)

Options:
    -h --help   Show this message.
    --version  shows version information
"""
__author__ = 'olivier'

from docopt import docopt
import shlex
import sys


def read_fg_firewall_log(logfile):
    """
    Reads fortigate firewall logfile. Returns a list with
    a dictionary for each line.
    """
    KVDELIM = '='  # key and value deliminator
    try:
        fh = open(logfile, "r")
    except Exception, e:
        print "Error: file %s not readable" % (logfile)
        print e.message
        sys.exit(2)

    loglist = []

    for line in fh:
        # lines are splited with shlex to recognise embeded substrings
        # such as key="valword1 valword2"
        keyvalues = {}
        for field in shlex.split(line):
            key, value = field.split(KVDELIM)
            keyvalues[key] = value
        loglist.append(keyvalues)
        keyvalues = {}
    fh.close()
    return loglist


def translate_protonr(protocolnr):
    """
    Translates port nr as names.

    Example:
        >>> translate_protonr(53)
        53
        >>> translate_protonr(1)
        'ICMP'
        >>> translate_protonr(6)
        'TCP'
        >>> translate_protonr(17)
        'UDP'
    """
    if int(protocolnr) == 1:
        return "ICMP"   # icmp has protonr 1
    elif int(protocolnr) == 6:
        return "TCP"    # tcp has protonr 6
    elif int(protocolnr) == 17:
        return "UDP"    # udp has protonr 17
    else:
        return protocolnr


def get_communication_matrix(loglist):
    """
    calculates a communication matrix from a loglist

    Example:
        TODO: add example
    """

    matrix = {}
    """
    for loop creates a dictionary with multiple levels
    l1: srcips (source ips)
        l2: dstips (destination ips)
            l3: dstport (destination port number)
                l4: proto (protocoll number)
                    l5: occurence count
    """
    for logline in loglist:
        srcip = logline['srcip']
        dstip = logline['dstip']
        dstport = logline['dstport']
        proto = translate_protonr(logline['proto'])
        # sentbyte = logline['sentbyte'] # not used now
        # rcvdbyte = logline['rcvdbyte'] # not used now
        if srcip not in matrix:
            matrix[srcip] = {}
        if dstip not in matrix[srcip]:
            matrix[srcip][dstip] = {}
        if dstport not in matrix[srcip][dstip]:
            matrix[srcip][dstip][dstport] = {}
        if proto not in matrix[srcip][dstip][dstport]:
            matrix[srcip][dstip][dstport][proto] = 1
        elif proto in matrix[srcip][dstip][dstport]:
            matrix[srcip][dstip][dstport][proto] += 1
    return matrix


def print_communication_matrix(matrix, indent=0):
    """
    prints the communication matrix in a nice format
    """
    # pprint(matrix)
    for key, value in matrix.iteritems():
        print '\t' * indent + str(key)
        if isinstance(value, dict):
            print_communication_matrix(value, indent+1)
        else:
            print '\t' * (indent+1) + str(value)
    return None


def main():
    """
    main function
    """
    # gets arguments from docopt
    arguments = docopt(__doc__)
    arguments = docopt(__doc__, version='Fortigate Log Parser 0.1')
    # assigns docopt argument to logfile
    logfile = arguments['<logfile>']

    if logfile is None:
        print __doc__
        sys.exit(2)

    # parse fortigate log
    loglist = read_fg_firewall_log(logfile)
    matrix = get_communication_matrix(loglist)
    print_communication_matrix(matrix)
    return 1

if __name__ == "__main__":
    sys.exit(main())
