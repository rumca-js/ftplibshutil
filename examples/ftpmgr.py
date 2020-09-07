#!/bin/python

import base64
import os
import re
import argparse
import logging
import shutil
import subprocess

# requires github/rumca-js/ftplibshutil
import ftpshutil


def connect():
    myserver = 'server.com'
    myuser = 'user'
    mypass = 'password'

    ftp = ftpshutil.FTPShutil(myserver, user=myuser, passwd=mypass )     # connect to host, default port
    logging.info("Connected")
    return ftp


def get_download_locations():
    return {
        "/Documents" : "./",
        "/Backup" : "./",
        "/dyi-page" : "./",
        "/blog" : "./"
     }


def get_upload_locations():
    return {
        "Documents" : "/",
        "Backup" : "/",
        "dyi-page" : "/",
        "blog" : "/"
     }


def read_args():

    parser = argparse.ArgumentParser(description='Download upload manager')
    parser.add_argument('-d','--download', dest='download', action="store_true", help='Download operation')
    parser.add_argument('-u', '--upload', dest='upload', action="store_true",  help='Upload operation)')
    parser.add_argument('--up-sync', dest='upload_sync', action="store_true",  help='Upload operation)')
    parser.add_argument('--down-sync', dest='download_sync', action="store_true", help='Download operation')
    parser.add_argument('-t', dest='test', action="store_true", help='Test operation')

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

        for item in get_download_locations():
            print("Downloading: "+item)
            download_dir_clean(ftp, item, "."+item)

        ftp.downloadfile("/index.html", "./index.html")
        ftp.downloadfile("/.htaccess", "./.htaccess")

        ftp.quit()

    elif args.upload:

        subprocess.run(['python3','dyi-page.py'], cwd="dyi-page")

        if os.path.isdir("blog"):
            shutil.rmtree("blog")
        shutil.copytree("./dyi-page/blog-html", "blog")

        ftp = connect()

        #upload_dir_clean(ftp, "dyi-page/blog-html", "/blog-html")
        #swap_dirs(ftp, "/blog-html", "/blog")

        for item in get_upload_locations():
            print("Uploading: "+item)
            upload_dir_clean(ftp, item, "/"+item)

        ftp.uploadfile("index.html", "/index.html")
        ftp.uploadfile(".htaccess", "/.htaccess")

        ftp.quit()

    elif args.upload_sync:

        subprocess.run(['python3','dyi-page.py'], cwd="dyi-page")

        if os.path.isdir("blog"):
            shutil.rmtree("blog")
        shutil.copytree("./dyi-page/blog-html", "blog")

        ftp = connect()

        for item in get_upload_locations():
            print("Uploading: "+item)
            ftp.uploadtree_sync(item, "/")

        ftp.uploadfile("index.html", "/index.html")
        ftp.uploadfile(".htaccess", "/.htaccess")

        ftp.quit()

    elif args.download_sync:

        ftp = connect()

        for item in get_download_locations():
            print("Downloading: "+item)
            ftp.downloadtree_sync(item, "./")

        ftp.downloadfile("/index.html", "./index.html")
        ftp.downloadfile("/.htaccess", "./.htaccess")

        ftp.quit()

    elif args.test:
        ftp = connect()

        ftp.downloadtree_sync("/Test", "./")

        ftp.quit()

    else:
        parser.print_help()


if __name__ == "__main__":
    # execute only if run as a script
    main()
