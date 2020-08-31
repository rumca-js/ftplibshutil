#!/bin/python

"""
@author Piotr Zielinski (renegat0x0)
"""

import base64
import os
import re
import argparse
import logging
import shutil

from io import BytesIO
import ftpshutil.dircrc as dircrc

logging.basicConfig(level=logging.INFO)

from ftplib import *


def ftp_path_join(*paths):
    """ FTP paths should have Linux OS separator? """
    joined = os.path.join(*paths)
    return joined.replace("\\", "/")


def normpath(path):
    """ FTP paths should have Linux OS separator? """
    path = os.path.normpath(path)
    path = path.replace("\\", "/")
    return path


def safe_root(path):
    """ os path join will not work on a directory that starts with root """

    if len(path) > 0:
        if path[0] == '/' or path[0] == '\\':
            path = path[1:]

    return path


def make_root(path):
    if path[0] != "/":
        path = "/"+path

    return path


def listdir_ex(ftplib, path):
    lines = []
    files = []
    dirs = []

    ftplib.cwd(path)

    ftplib.retrlines('LIST', lines.append)

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


def walk_ftp_dir(ftp_shutil_obj, root_dir, topdown=True):
    ftp = ftp_shutil_obj.get_ftplib_handle()

    dirs, files = listdir_ex(ftp, root_dir)

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
        dir_list = self._ftp.nlst(root_dir)
        dir_list = [ os.path.split(x)[1] for x in dir_list] 
        return dir_list

    def listdir_ex(self, root_dir):
        ftp = self.get_ftplib_handle()
        return listdir_ex(ftp, root_dir)

    def read(self, file_path):
        r = BytesIO()
        self._ftp.retrbinary('RETR {0}'.format(file_path), r.write)
        return r.getvalue()

    def isfile(self, file_path):
        path, file_name = os.path.split(file_path)
        dirs, files = self.listdir_ex(path)
        return file_name in files

    def isdir(self, dir_path):
        path, dir_name = os.path.split(dir_path)
        dirs, files = self.listdir_ex(path)
        return dir_name in dirs

    def exists(self, path):
        '''
        @brief for FTP part.
        '''
        logging.info("Checking if path exists {0}".format(path))

        split_name = os.path.split(path)

        try:
            dir_list = self.listdir(split_name[0])
        except Exception as E:
            print(E)
            return False

        if not split_name[1] in dir_list:
            return False
        return True

    def safe_remove(self, path):
        try:
            if self.isfile(path):
                self._ftp.delete(path)
            elif self.isdir(path):
                self.rmtree(path)
            else:
                raise IOError("FTP: Specified path does not exist: {0}".format(path))
        except Exception as E:
            print("Problem with removing: {0}".format(path))
            raise E

    def remove_file(self, path):
        try:
            path = normpath(path)
            self._ftp.delete(path)
        except Exception as E:
            print("Problem with removing: {0}".format(path))
            raise E

    def remove_dir(self, path):
        try:
            path = normpath(path)
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

    def makedirs(self, path):
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

    def uploadfile(self, local_file, remote_file):
        '''
        @brief Better supply with absolute FTP paths
        '''
        logging.info("Uploading file: {0} -> {1}".format(local_file, remote_file))

        split_name = os.path.split(remote_file)
        self._ftp.cwd(split_name[0])
        self._ftp.storbinary('STOR {0}'.format(split_name[1]), open(local_file, 'rb'))

    def downloadfile(self, remote_file, local_file):
        logging.info("Downloading file: {0} -> {0}".format(remote_file, local_file) )

        split_name = os.path.split(remote_file)
        path = split_name[0]

        path = make_root(path)

        self._ftp.cwd(path)

        with open( local_file, 'wb') as fp:
            self._ftp.retrbinary('RETR {0}'.format(split_name[1]), fp.write)

    def make_local(self, local_root_dir, remote_root_dir, rem_dirs, rem_files, crc_data = None):
        """
        @brief Adapts the local site according to the remote files.

        @TODO remove local directories that are not present on the remote site.
        @TODO remove local files that are not present on the remote site.
        """

        if crc_data is not None:
            rem_files = crc_data.get_1st_more_files()
            rem_dirs = crc_data.get_1st_more_dirs()
            rem_files.extend(crc_data.get_modified_files())

            redundant_things = crc_data.get_2nd_more_files()
            redundant_things.extend( crc_data.get_2nd_more_dirs())

            for redundant in redundant_things:
                redundant = os.path.join(local_root_dir, redundant)

                if os.path.isfile(redundant):
                    os.remove(redundant)
                else:
                    shutil.rmtree(redundant)

        for adir in rem_dirs:
            full_dir = os.path.join(local_root_dir, adir)
            if not os.path.isdir(full_dir):
                os.makedirs(full_dir)

        for afile in rem_files:
            remote_file = ftp_path_join(remote_root_dir, afile)
            local_file = os.path.join(local_root_dir, afile)

            if not os.path.isdir(local_root_dir):
                os.makedirs(local_root_dir)

            self.downloadfile(remote_file, local_file)

    def make_remote(self, remote_root_dir, local_root_dir, loc_dirs, loc_files, crc_data = None):
        """
        @brief Adapts the local site according to the remote files.

        @TODO remove local directories that are not present on the remote site.
        @TODO remove local files that are not present on the remote site.
        """

        if crc_data is not None:
            loc_files = crc_data.get_2nd_more_files()
            loc_dirs = crc_data.get_2nd_more_dirs()
            loc_files.extend(crc_data.get_modified_files())

            redundant_things = crc_data.get_1st_more_files()
            redundant_things.extend( crc_data.get_1st_more_dirs())

            for redundant in redundant_things:
                redundant = ftp_path_join(remote_root_dir, redundant)
                self.safe_remove(redundant)

        for adir in loc_dirs:
            full_dir = ftp_path_join(remote_root_dir, adir)
            if not self.exists(full_dir):
                self.makedirs(full_dir)

        for afile in loc_files:
            remote_file = ftp_path_join(remote_root_dir, afile)
            local_file = os.path.join(local_root_dir, afile)

            if not self.isdir(remote_root_dir):
                self.makedirs(remote_root_dir)

            self.uploadfile(local_file, remote_file)

    def downloadtree(self, directory, destination):
        '''
        @brief Probably best to supply directory as an absolute FTP path.
        '''
        logging.info("Downloading tree: {0} -> {1}".format(directory, destination))

        try:
            for root, dirs, files in walk_ftp_dir(self, directory):
                remote_root_dir = safe_root(root)
                local_root_dir = os.path.join(destination, remote_root_dir)

                self.make_local(local_root_dir, remote_root_dir, dirs, files)

        except Exception as e:
            print("Could not obtain directory {0}\n{1}".format(directory, str(e) ))

    def uploadtree(self, directory, destination):
        logging.info("Uploading tree: {0} -> {1}".format(directory, destination))

        lastdir = os.path.split(directory)[1]

        for root, dirs, files in os.walk(directory, topdown=True):

            inner_root = root.replace(directory, "")
            inner_root = safe_root(inner_root)

            remote_root = ftp_path_join(destination, lastdir, inner_root)

            if remote_root.endswith("/"):
                remote_root = remote_root[:-1]

            self.make_remote(remote_root, root, dirs, files)

    def diff_dircrc(self, local_crc_file, remote_crc_file):
        """
        @returns True if files are different, or one of the files is missing
                 False if both files are present and equal.
        """
        if os.path.isfile(local_crc_file):
            if self.exists(remote_crc_file):
                remote_crc = self.read(remote_crc_file)

                with open(local_crc_file, 'rb') as fh:
                    local_crc = fh.read()

                if remote_crc == local_crc:
                    return False

        return True

    def downloadtree_sync(self, directory, destination):
        '''
        @brief Probably best to supply directory as an absolute FTP path.
        '''
        logging.info("Downloading tree: {0} -> {1}".format(directory, destination))

        dircrc.create_dircrcs(destination)

        try:
            for root, dirs, files in walk_ftp_dir(self, directory, topdown=True):

                remote_root_dir  = safe_root(root)
                local_root_dir = os.path.join(destination, remote_root_dir)

                local_crc_file = os.path.join(local_root_dir, dircrc.crc_file_name)
                remote_crc_file = ftp_path_join(root, dircrc.crc_file_name)

                if not self.exists(remote_crc_file) or not os.path.isfile(local_crc_file):
                    logging.info("Processing directory: {0}".format(root))

                    if os.path.isdir(local_root_dir):
                        shutil.rmtree(local_root_dir)

                    self.make_local(local_root_dir, remote_root_dir, dirs, files)
                else:
                    remote_crc_data = self.read(remote_crc_file).decode("utf-8")
                    with open(local_crc_file, 'r') as fh:
                        local_crc_data = fh.read()

                    comp = dircrc.Comparator(remote_crc_data, local_crc_data)

                    if comp.is_same():
                        logging.info("Skipping directory: {0}".format(root))
                        continue

                    logging.info("Processing directory: {0}".format(root))

                    self.make_local(local_root_dir, remote_root_dir, dirs, files, comp)

        except Exception as e:
            print("Could not obtain directory {0}\n{1}".format(directory, str(e) ))

    def uploadtree_sync(self, directory, destination):
        logging.info("Uploading tree: {0} -> {1}".format(directory, destination))

        dircrc.create_dircrcs(directory)

        lastdir = os.path.split(directory)[1]

        for root, dirs, files in os.walk(directory, topdown=True):

            inner_root = root.replace(directory, "")
            inner_root = safe_root(inner_root)

            remote_root = ftp_path_join(destination, lastdir, inner_root)

            if remote_root.endswith("/"):
                remote_root = remote_root[:-1]

            remote_crc_file = ftp_path_join(remote_root, dircrc.crc_file_name)
            local_crc_file = os.path.join(root, dircrc.crc_file_name)

            if not self.exists(remote_crc_file) or not os.path.isfile(local_crc_file):
                logging.info("Processing directory: {0}".format(root))

                if self.isdir(remote_root):
                    self.rmtree(remote_root)

                self.make_remote(remote_root, root, dirs, files)

            else:
                remote_crc_data = self.read(remote_crc_file).decode("utf-8")
                with open(local_crc_file, 'r') as fh:
                    local_crc_data = fh.read()

                comp = dircrc.Comparator(remote_crc_data, local_crc_data)

                if comp.is_same():
                    logging.info("Skipping directory: {0}".format(root))
                    continue

                logging.info("Processing directory: {0}".format(root))

                self.make_remote(remote_root, root, dirs, files, comp)
