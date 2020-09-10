
import unittest
import logging
import os

import ftpshutil
import ftpshutil.ftpconfig as ftpconfig

import ftpshutil.dircrc as dircrc


class TestStringMethods(unittest.TestCase):

    ftp = None

    def setUp(self):
        if not TestStringMethods.ftp:

            config = ftpconfig.FtpConfig()
            config.read()

            TestStringMethods.ftp = ftpshutil.FTPShutil(config.get("server"), 
                                                        user=config.get("user"), 
                                                        passwd=config.get("password") )

            logging.info("Connected") 

        if TestStringMethods.ftp.exists("/Test"):
            TestStringMethods.ftp.rmtree("/Test")

    def tearDown(self):
        TestStringMethods.ftp.quit()
        TestStringMethods.ftp = None

    def test_mkdir(self):
        TestStringMethods.ftp.mkdir("/Test")

        self.assertTrue( TestStringMethods.ftp.exists("/Test") )

    def test_rmtree(self):
        TestStringMethods.ftp.mkdir("/Test")
        TestStringMethods.ftp.rmtree("/Test")

        self.assertFalse( TestStringMethods.ftp.exists("/Test") )

    def test_makedirs(self):
        TestStringMethods.ftp.makedirs("/Test/uno")

        self.assertTrue( TestStringMethods.ftp.exists("/Test") )
        self.assertTrue( TestStringMethods.ftp.exists("/Test/uno") )

    def test_listdir_empty_dir(self):
        TestStringMethods.ftp.makedirs("/Test/uno")

        self.assertTrue( TestStringMethods.ftp.listdir("/Test/uno") == [])

    def test_write_read(self):
        TestStringMethods.ftp.makedirs("/Test/uno")
        TestStringMethods.ftp.write("/Test/uno/my_file", b"test")

        self.assertTrue( TestStringMethods.ftp.read("/Test/uno/my_file") == b"test")

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
