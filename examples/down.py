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
    parser.add_argument('-t', '--test', dest='test', action="store_true",  help='Test operation)')

    args = parser.parse_args()
    return parser, args


def download_dir_clean(ftp, remote_dir, local_dir):
    if os.path.isdir(local_dir):
        shutil.rmtree(local_dir)
    ftp.downloadtree(remote_dir, ".")


def upload_dir_clean(ftp, local_dir, remote_dir):
    if ftp.exists(remote_dir):
        ftp.rmtree(remote_dir)
    ftp.uploadtree(local_dir, "/")


def swap_dirs(ftp, from_dir, to_dir):
    if ftp.exists(to_dir):
        ftp.rename(to_dir, "/tmp")

    ftp.rename(from_dir, to_dir)

    if ftp.exists("/tmp"):
        ftp.rmtree("/tmp")


def main():
    parser, args = read_args()

    if args.download:
        ftp = connect()

        download_dir_clean(ftp, "/Documents", "./Documents")
        download_dir_clean(ftp, "/Backup", "./Backup")
        download_dir_clean(ftp, "/dyi-page", "./dyi-page")

        if os.path.isdir("./Backup"):
            shutil.rmtree("./Backup")
        ftp.downloadtree("/Backup", ".")

        if os.path.isdir("./dyi-page"):
            shutil.rmtree("./dyi-page")
        ftp.downloadtree("/dyi-page", ".")

        ftp.downloadfile("/index.html", "./index.html")
        ftp.downloadfile("/.htaccess", "./.htaccess")

        ftp.quit()

    elif args.upload:
        ftp = connect()

        upload_dir_clean(ftp, "Documents", "/Documents")
        upload_dir_clean(ftp, "Backup", "/Backup")
        upload_dir_clean(ftp, "dyi-page", "/dyi-page")
        upload_dir_clean(ftp, "dyi-page/blog-html", "/blog-html")

        swap_dirs(ftp, "/blog-html", "/blog")

        ftp.uploadfile("index.html", "/index.html")
        ftp.uploadfile(".htaccess", "/.htaccess")

        ftp.quit()
    elif args.test:
        ftp = connect()

        print( ftp.read("index.html") )

        ftp.quit()
    else:
        parser.print_help()


if __name__ == "__main__":
    # execute only if run as a script
    main()
