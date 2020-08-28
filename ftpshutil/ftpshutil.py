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


def ftp_path_join(path1, path2, path3=None):
    # TODO this has to be written better
    if not path3:
        joined = os.path.join(path1, path2)
        return joined.replace("\\", "/")
    else:
        joined = os.path.join(path1, path2, path3)
        return joined.replace("\\", "/")


def walk_ftp_dir(ftp_shutil_obj, root_dir, topdown=True):
    dirs = []
    files = []
    lines = []
    clean_names = []

    ftp = ftp_shutil_obj.get_ftplib_handle()

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

    if not topdown:
        for inner_dir in dirs:
            for inner_root, inner_dirs, inner_files in walk_ftp_dir( ftp_shutil_obj, ftp_path_join(root_dir, inner_dir), topdown):
                yield ftp_path_join(root_dir,inner_root), inner_dirs, inner_files

    yield root_dir, dirs, files

    if topdown:
        for inner_dir in dirs:
            for inner_root, inner_dirs, inner_files in walk_ftp_dir( ftp_shutil_obj, ftp_path_join(root_dir, inner_dir), topdown):
                yield ftp_path_join(root_dir,inner_root), inner_dirs, inner_files


class FTPShutil(object):

    def __init__(self, host, user, passwd):
        self._ftp = FTP(host, user=user, passwd=passwd )     # connect to host, default port 

    def login(self, user, passwd):
        return self._ftp.login(user, passwd)

    def quit(self):
        self._ftp.quit()

    def get_ftplib_handle(self):
        return self._ftp

    def listdir(self, root_dir):
        lines = []
        dirs = []
        files = []

        ftp = self.get_ftplib_handle()
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

        return dirs, files

    def downloadfile(self, remote_file, local_file):
        logging.info("Downloading file: {0} -> {0}".format(remote_file, local_file) )

        split_name = os.path.split(remote_file)
        path = split_name[0]

        if path[0] != "/":
            path = "/"+path

        self._ftp.cwd(path)

        with open( local_file, 'wb') as fp:
            self._ftp.retrbinary('RETR {0}'.format(split_name[1]), fp.write)

    def downloadtree(self, directory, destination):
        '''
        @brief Probably best to supply directory as an absolute FTP path.
        '''
        logging.info("Downloading tree: {0} -> {1}".format(directory, destination))

        try:
            for root, dirs, files in walk_ftp_dir(self, directory):
                safe_root = root
                if safe_root.find('/') == 0:
                    safe_root = safe_root[1:]

                for adir in dirs:
                    pass

                for afile in files:
                    remote_file = ftp_path_join(safe_root, afile)

                    local_root_dir = os.path.join(destination, safe_root)

                    if not os.path.isdir(local_root_dir):
                        os.makedirs(local_root_dir)

                    self.downloadfile(remote_file, os.path.join(local_root_dir, afile))

        except Exception as e:
            print("Could not obtain directory {0}\n{1}".format(directory, str(e) ))

    def isfile(self, file_path):
        path, file_name = os.path.split(file_path)
        dirs, files = self.listdir(path)
        return file_name in files

    def isdir(self, dir_path):
        path, dir_name = os.path.split(dir_path)
        dirs, files = self.listdir(path)
        return dir_name in dirs

    def uploadfile(self, local_file, remote_file):
        '''
        @brief Better supply with absolute FTP paths
        '''
        logging.info("Uploading file: {0} -> {1}".format(local_file, remote_file))

        split_name = os.path.split(remote_file)
        self._ftp.cwd(split_name[0])
        self._ftp.storbinary('STOR {0}'.format(split_name[1]), open(local_file, 'rb'))

    def exists(self, path):
        '''
        @brief for FTP part.
        '''
        logging.debug("Checking if directory exists {0}".format(path))

        split_name = os.path.split(path)
        dir_list = self._ftp.nlst(split_name[0])

        dir_list = [ os.path.split(x)[1] for x in dir_list] 
        
        if not split_name[1] in dir_list:
            return False
        return True

    def safe_remove(self, path):
        try:
            if self.isfile(path):
                self._ftp.delete(path)
            elif self.isdir(path):
                self._ftp.rmd(path)
            else:
                raise IOError("FTP: Specified path does not exist: {0}".format(path))
        except Exception as E:
            print("Problem with removing: {0}".format(path))
            raise E

    def remove_file(self, path):
        try:
            path = os.path.normpath(path)
            path = path.replace("\\", "/")
            self._ftp.delete(path)
        except Exception as E:
            print("Problem with removing: {0}".format(path))
            raise E

    def remove_dir(self, path):
        try:
            path = os.path.normpath(path)
            path = path.replace("\\", "/")
            self._ftp.rmd(path)
        except Exception as E:
            print("Problem with removing: {0}".format(path))
            raise E

    def rmtree(self, directory):
        logging.info("Removing directory: {0}".format(directory))

        for root, dirs, files in walk_ftp_dir(self, directory, False):
            for afile in files:
                root_file = ftp_path_join(root, afile)
                self.remove_file(root_file)

            for adir in dirs:
                self.rmtree( ftp_path_join(root, adir))

        self.remove_dir(directory)

    def mkdirs(self, path):
        '''
        @brief for FTP part.    
        '''
        logging.info("Creating remote directory {0}".format(path))

        split_name = os.path.split(path)
        self._ftp.cwd(split_name[0])
        self._ftp.mkd(split_name[1])

    def rename(self, fromname, toname):
        logging.info("Rename file: {0} -> {1}".format(fromname, toname))

        self._ftp.rename(fromname, toname)

    def uploadtree(self, directory, destination):
        logging.info("Uploading tree: {0} -> {1}".format(directory, destination))

        lastdir = os.path.split(directory)[1]

        for root, dirs, files in os.walk(directory, topdown=True):

            inner_root = root.replace(directory, "")
            if len(inner_root) > 0:
                if inner_root[0] == '/' or inner_root[0] == '\\':
                    inner_root = inner_root[1:]

            remote_root = ftp_path_join(destination, lastdir, inner_root)

            if remote_root.endswith("/"):
                remote_root = remote_root[:-1]

            if not self.exists(remote_root):
                self.mkdirs(remote_root)

            for adir in dirs:
                dst_dir = ftp_path_join(remote_root, adir)
                
                if not self.exists(dst_dir):
                    self.mkdirs(dst_dir)

            for afile in files:
                remote_file = ftp_path_join(remote_root, afile)
                local_file = os.path.join(root, afile)
                self.uploadfile(local_file, remote_file)

