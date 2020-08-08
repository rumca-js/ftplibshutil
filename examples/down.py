#!/bin/python

import base64
import os
import re
import argparse
import logging

# requires github/rumca-js/ftplibshutil
import ftpshutil


def connect():
    mypass = "anonymouse@"
    myuser = "anonymouse@"
    myserver = 'server.com'

    ftp = ftpshutil.FTPShutil(myserver, user=myuser, passwd=mypass )     # connect to host, default port
    logging.info("Connected")
    return ftp


def read_args():

    parser = argparse.ArgumentParser(description='Download upload manager')
    parser.add_argument('-d','--download', dest='download', action="store_true", help='Download operation')
    parser.add_argument('-u', '--upload', dest='upload', action="store_true",  help='Upload operation)')

    args = parser.parse_args()
    return parser, args


def main():
    parser, args = read_args()

    if args.download:
        ftp = connect()
        ftp.downloadtree("/Documents", ".")
        ftp.downloadtree("/Backup", ".")
        ftp.downloadtree("/dyi-page", ".")
        ftp.quit()
    elif args.upload:
        ftp = connect()
        ftp.uploadtree("Documents", "/")
        ftp.uploadtree("Backup", "/")
        ftp.uploadtree("dyi-page", "/")
        ftp.quit()
    else:
        parser.print_help()


if __name__ == "__main__":
    # execute only if run as a script
    main()
