
import unittest
import logging
import os

import ftpshutil
import ftpshutil.ftpconfig as ftpconfig

import ftpshutil.dircrc as dircrc

from ftplib import *


class FtpMock(FTP):
    """
    This mock class replaces ftp lib connection.
    We want to write unit test here!
    """

    def __init__(self):
        self._files = {'/Test/file.txt' : 'contents'}
        self._dirs = ['/', '/Test']
        self._cwd = ''
    	
    def nlst(self, apath):
        result = []
        
        for afile in self._files:
            if afile.startswith(apath):
                result.append(afile)
                
        for adir in self._dirs:
            if adir.startswith(apath) and adir != apath:
                result.append(adir)
                
        return result
        
    def quit(self):
        pass
        
    def cwd(self, path):
        if not path.startswith("/"):
             path = os.path.join(self._cwd, path)
             
        if path in self._dirs:
            self._cwd = path
        else:
            raise error_perm("No such path: "+path)
        
    def mkd(self, adir):
        if not adir.startswith("/"):
             adir = os.path.join(self._cwd, adir)

        dst_dir = os.path.join(self._cwd, adir)
        if dst_dir not in self._dirs:
            self._dirs.append(dst_dir)
        
    def rmd(self, adir):
        if not adir.startswith("/"):
             adir = os.path.join(self._cwd, adir)

        self._dirs.remove(adir)
        
    def retrlines(self, cmd, callback = None):
        if cmd == "LIST":
            dirstring = "drwxr-sr-x    5 1176     1176         4096 Dec 19  2000 "
            filestring = '-rw-rw-r--    1 1176     1176         1063 Jun 15 10:18 '
            result = ''
        
            for afile in self._files:
                sp = os.path.split(afile)
                if sp[0] == self._cwd:
                    filestring = filestring + sp[1]
                    callback(filestring)
                    result += filestring + "\n"
                
            for adir in self._dirs:
                sp = os.path.split(adir)
                if sp[0] == self._cwd:
                    dirstring = dirstring + sp[1]
                    callback(dirstring)
                    result += dirstring + "\n"
        
            return result
        
    def storbinary(self, cmd, fp, blocksize=8192, callback=None, rest=None):
        sp = cmd.split(" ")
        if sp[0] == "STOR":
            afile = sp[1]

            if not afile.startswith("/"):
                afile = os.path.join(self._cwd, afile)

            contents = fp.read()
            self._files[afile] = contents
        fp.close()
        
    def retrbinary(self, cmd, callback=None, blocksize=8192, rest=None):
        sp = cmd.split(" ")
        if sp[0] == "RETR":
            afile = sp[1]
            if afile in self._files:
                callback(self._files[afile])

    def delete(self, path):
        if not path.startswith("/"):
             path = os.path.join(self._cwd, path)
        
        if path in self._files:
            self._files.pop(path)
        if path in self._dirs:
            self._dirs.remove(path)


class TestStringMethods(unittest.TestCase):

    ftp = None

    def setUp(self):
        if not TestStringMethods.ftp:

            config = ftpconfig.FtpConfig()
            config.read()

            TestStringMethods.ftp = ftpshutil.FTPShutil()
            TestStringMethods.ftp._ftp = FtpMock()

            logging.info("Connected") 

        if TestStringMethods.ftp.exists("/Test"):
            TestStringMethods.ftp.rmtree("/Test")

    def tearDown(self):
        TestStringMethods.ftp.quit()
        TestStringMethods.ftp = None

    def test_mkdir(self):
        TestStringMethods.ftp.mkdir("/Test")
                
        self.assertTrue( TestStringMethods.ftp._ftp._dirs == ['/','/Test'])
        self.assertTrue( TestStringMethods.ftp.exists("/Test") )
        self.assertTrue( TestStringMethods.ftp.isdir("/Test") )

    def test_rmtree(self):
        TestStringMethods.ftp.mkdir("/Test")
        TestStringMethods.ftp.rmtree("/Test")

        self.assertFalse( TestStringMethods.ftp.exists("/Test") )

    def test_makedirs(self):
        if TestStringMethods.ftp.exists("/Test"):
            TestStringMethods.ftp.rmtree("/Test")

        TestStringMethods.ftp.makedirs("/Test/uno")
        
        self.assertTrue( '/Test' in TestStringMethods.ftp._ftp._dirs)
        self.assertTrue( '/Test/uno' in TestStringMethods.ftp._ftp._dirs)

        self.assertTrue( TestStringMethods.ftp.exists("/Test") )
        self.assertTrue( TestStringMethods.ftp.exists("/Test/uno") )

        self.assertTrue( TestStringMethods.ftp.isdir("/Test") )
        self.assertTrue( TestStringMethods.ftp.isdir("/Test/uno") )

    def test_listdir_empty_dir(self):
        TestStringMethods.ftp.makedirs("/Test/uno")

        self.assertTrue("/Test/uno" in TestStringMethods.ftp._ftp._dirs)

        self.assertTrue( TestStringMethods.ftp.listdir("/Test/uno") == [])

    def test_write_read(self):
        TestStringMethods.ftp.makedirs("/Test/uno")
        TestStringMethods.ftp.write("/Test/uno/my_file", b"test")

        TestStringMethods.ftp.isfile("/Test/uno/my_file")

        self.assertTrue( TestStringMethods.ftp.read("/Test/uno/my_file") == b"test")

    def test_upload(self):
        TestStringMethods.ftp.makedirs("/Test")
        TestStringMethods.ftp.uploadfile("setup.py", "/Test/setup.py")

        self.assertTrue( TestStringMethods.ftp.isfile("/Test/setup.py") )

        with open("setup.py", 'rb') as fh:
            data = fh.read()

        self.assertTrue(TestStringMethods.ftp._ftp._files["/Test/setup.py"] == data)

    def test_crc(self):
        dircrc.create_dircrcs("test")

        crc_file = os.path.join("test", "crc_list.txt")
        self.assertTrue( os.path.isfile( crc_file))

        with open(crc_file, 'r') as fh:
            data = fh.read()

        example = """[CRC List]
./crc_list.txt = -2
./one_test_file.txt = 4227995677

"""

        self.assertTrue( example == data)


if __name__ == '__main__':
    unittest.main()
