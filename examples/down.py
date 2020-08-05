#!/bin/python

import base64
import os
import re
import argparse
import logging

import ftpshutil


def connect():
    myuser = 'anonymous'
    mypass = 'anonymous'

    ftp = ftpshutil.FTPShutil('someserver.com', user=myuser, passwd=mypass )     # connect to host, default port
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
        ftp.download_dir("Documents")
        ftp.download_dir("Backup")
        ftp.quit()
    elif args.upload:
        ftp = connect()
        ftp.upload_dir("Documents")
        ftp.upload_dir("Backup")
        ftp.quit()
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
