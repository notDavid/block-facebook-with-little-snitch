#!/usr/bin/env python3

import os
import sys
import subprocess
import ipcalc       # pip3 install ipcalc

# https://help.obdev.at/littlesnitch/ref-lsrules-file-format

BASEDIR_PATH = os.path.dirname(os.path.realpath(__file__))


def main():
    returncode, stdout = run_whois()
    if returncode == 0:
        ips = strip_crap(stdout)
        ips = convert_iprange(ips)
        write_file(ips)
        print_success("Done!")


def write_file(ips):
    f = open(BASEDIR_PATH + "/Blockfacebook.template", "r")
    template = f.read()
    f.close()

    data = template.replace("xxxx", ips)

    f = open(BASEDIR_PATH + "/Blockfacebook.lsrules", "w+")
    f.write(data)
    f.close()


def convert_iprange(iprange):
    ipls = ""
    ips = iprange.split()
    ips.sort()
    for ip in ips:
        subnet = ipcalc.Network(ip)
        if (ipls != ""):
            ipls += ", "
        ipls += str(subnet[0]) + "-" + str(subnet[-1])

    return(ipls)


def strip_crap(strOut):
    lines = strOut.splitlines()
    allowedChars = "1234567890./ "
    iprange = ""
    for line in lines:
        ignoreline = False
        for letter in line:
            if letter not in allowedChars:
                ignoreline = True
                break
        if not ignoreline:
            iprange += line

    return(iprange)


def run_whois():
    # AS32934 = Facebook ASN
    returncode, stdout = run_shell("whois -h whois.radb.net '!gAS32934' ")
    return (returncode, stdout)


def run_shell(cmd):
    returncode = -1
    stdout = ""
    try:
        result = subprocess.run(cmd, shell=True, stdout=subprocess.PIPE)
        returncode = result.returncode
        stdout = result.stdout.decode('utf-8')
        if returncode != 0:
            print_failure("whois command failed")
        return (returncode, stdout)

    except Exception:
        print_failure("whois command failed")
        return (returncode, stdout)


class Colors(object):
    PROMPT = "\033[94m"
    SUCCESS = "\033[92m"
    FAIL = "\033[91m"
    ENDC = "\033[0m"


def supports_color():
    sys_platform = sys.platform
    supported = sys_platform != "Pocket PC" and (sys_platform != "win32" or "ANSICON" in os.environ)

    atty_connected = hasattr(sys.stdout, "isatty") and sys.stdout.isatty()
    return supported and atty_connected


def colorize(text, color):
    if not supports_color():
        return text
    return color + text + Colors.ENDC


def print_success(text):
    print(colorize(text, Colors.SUCCESS))


def print_failure(text):
    print(colorize(text, Colors.FAIL))


if __name__ == "__main__":
    main()
