#!/bin/python

"""
@author Piotr Zielinski (renegat0x0)
"""

import base64
import os
import re
import argparse
import logging

logging.basicConfig(level=logging.INFO)

from ftplib import *


def walk_ftp_dir(ftp, root_dir):
    dirs = []
    files = []
    lines = []
    clean_names = []

    ftp.cwd(root_dir)

    ftp.retrlines('LIST', lines.append)

    for line in lines:
        m = re.search("([a-z-]*\s*\d*\s*\w*\s*\w*\s*\d*\s*\w*\s*\d*\s*\d*[:]*\d*\s*)", line)
        fname = line[m.end(1):]

        if line.find("d") == 0:
            ftype = "dir"
        elif line.find('-') == 0:
            ftype = "file"
        else:
            ftype = "none"

        if ftype == "dir":
            dirs.append(fname)
        if ftype=="file":
            files.append(fname)

    yield root_dir, dirs, files

    for inner_dir in dirs:
        for inner_root, inner_dirs, inner_files in walk_ftp_dir( ftp, os.path.join(root_dir, inner_dir)):
            yield os.path.join(root_dir,inner_root), inner_dirs, inner_files


class FTPShutil(object):

    def __init__(self, host, user, passwd):
        self.ftp = FTP(host, user=user, passwd=passwd )     # connect to host, default port 

    def login(self, user, passwd):
        return self.ftp.login(user, passwd)

    def quit(self):
        self.ftp.quit()

    def download_dir(self, directory):

        for root, dirs, files in walk_ftp_dir(self.ftp, "/"+directory):
            for adir in dirs:
                pass

            for afile in files:
                root_file = os.path.join(root, afile)
                logging.info("Downloading file: {0}".format(root_file) )

                dst_root = os.getcwd()+ root

                if not os.path.isdir(dst_root):
                    os.makedirs(dst_root)

                self.ftp.cwd(root)
                dst_file = os.path.join(dst_root, afile)

                with open( dst_file, 'wb') as fp:
                    self.ftp.retrbinary('RETR {0}'.format(afile), fp.write)


    def upload_dir(self, directory):

        for root, dirs, files in os.walk(directory, topdown=True):

            for adir in dirs:
                self.ftp.cwd("/")
                dir_list = self.ftp.nlst(root)

                dst_dir = os.path.join(root, adir)
                
                logging.info("Checking if directory exists {0}".format(dst_dir))
                if not dst_dir in dir_list:
                    logging.info("Creating remote directory {0}".format(dst_dir))
                    self.ftp.mkd(dst_dir)

            for afile in files:
                remote_file = os.path.join(root, afile) 
                logging.info("Sending file: {0}".format(remote_file))
                self.ftp.cwd("/"+root)
                self.ftp.storbinary('STOR {0}'.format(afile), open(remote_file, 'rb'))
