"""
The CRC subsystem will use linux path separator.
"""

import argparse
import os
import sys
import zlib
import configparser
import glob
import io


CRC_FILE_NAME = "crc_list.txt"
CRC_4_DIR = -1
CRC_4_CRC = -2
SECTION_NAME = "CRC List"


class CrcFile(object):
    """
    We do not use ConfigParser here for writing.
     1. it does not allow for simple use of unix line endings on windows
     2. for case sensitivity we have to create lambda functions (ugly).
    """

    def calc_crc(afile):
        with open(afile, 'rb') as fh:
            data = fh.read()

            return zlib.crc32(data)

    def set_entries(self, file_map):
        self.themap = file_map

    def read(self, file_name):
        with open(file_name, 'rb') as fh:
            data = fh.read().decode('utf-8')

        cfg = configparser.ConfigParser()
        cfg.optionxform = lambda option: option
        cfg.read_string(data)

        self.themap = dict(cfg[SECTION_NAME])

    def read_data(self, data):
        cfg = configparser.ConfigParser()
        cfg.optionxform = lambda option: option
        cfg.read_string(data)

        self.themap = dict(cfg[SECTION_NAME])

    def write(self, file_name):

        with open(file_name, 'wb') as fh:
            text = "[{0}]\n".format(SECTION_NAME)
            fh.write(text.encode('utf-8'))

            keys = sorted(self.get_files())
            for key in keys:
                self.write_key(fh, key)

            keys = sorted(self.get_dirs())
            for key in keys:
                self.write_key(fh, key)

            fh.write("\n".encode('utf-8'))
    
    def write_key(self, fh, key):
        value = self.themap[key]
        text = "{0} = {1}\n".format(key, value)
        fh.write(text.encode('utf-8'))

    def get_files(self):
        files = []

        for item in self.themap:
            val = int(self.themap[item])
            if val != CRC_4_DIR:
                files.append(item)

        return files

    def get_dirs(self):
        dirs = []

        for item in self.themap:
            val = int(self.themap[item])
            if val == CRC_4_DIR:
                dirs.append(item)

        return dirs


def calc_dircrc(root, dirs, files):
    """ Calculate for this root"""
    file_map = {}
    for name in sorted(files):
        big_name = "/".join([root, name])
        if name != CRC_FILE_NAME:
            file_map[big_name] = CrcFile.calc_crc(big_name)
        else:
            file_map[big_name] = CRC_4_CRC

    for name in sorted(dirs):
        big_name = "/".join([root, name])
        file_map[big_name] = CRC_4_DIR

    return file_map


def calc_dircrc_recursive(directory):
    print("processing directory: {0}".format(directory))

    file_map = {}

    for root, dirs, files in os.walk(directory, topdown=False):
        single_dir_map = calc_dircrc(root, dirs, files)
        file_map.update(single_dir_map)

    return file_map


def create_dircrc(directory):
    file_map = calc_dircrc_recursive(directory)

    output_name = CRC_FILE_NAME

    crcfile = CrcFile()
    crcfile.set_entries(file_map)
    crcfile.write(os.path.join(directory, output_name))

    return file_map


def create_dircrcs(directory):
    for root, dirs, files in os.walk(directory, topdown=False):
        cur_path = os.getcwd()
        os.chdir(root)
        file_map = calc_dircrc(".", dirs, files)
        os.chdir(cur_path)

        output_name = CRC_FILE_NAME

        crcfile = CrcFile()
        crcfile.set_entries(file_map)
        crcfile.write( os.path.join(root, output_name))


def diff_dir(one_dir, two_dir):
    one_dir = dict(one_dir).keys()
    two_dir = dict(two_dir).keys()

    diff_one = one_dir - two_dir
    diff_two = two_dir - one_dir
    return diff_one, diff_two


def copy_sync(src_dir, dst_dir, dst_handle):
    dst_crc_list = os.path.join(dst_dir, CRC_FILE_NAME)
    if not dst_handle.exists(dst_crc_list):
        dst_handle.copytree(src, dst_dir)

    data = dst_handle.read(dst_crc_list)
    buf = io.BytesIO(data)

    config = configparser.ConfigParser()
    config.read(buf)
    dst_map = dict(config[SECTION_NAME])

    src_map = create_crc_file(src_dir)

    src_keys = src_map.keys()
    dst_keys = dst_map.keys()

    # Copy what we have more in source
    src_more = src_keys - dst_keys
    for item in src_more:
        dst_handle.copy(src_dir, dst_dir)

    # Remove what source does not have
    dst_more = dst_keys - src_keys
    for item in dst_more:
        dst_handle.remove(item)

    for item in src_keys:
        if item in dst_keys:
            if src_map[item] != dst_map[item]:
                dst_handle.copy(src_dir, dst_dir)


def remove_crc_files():

    crc_file = CRC_FILE_NAME
    if os.path.isfile(crc_file):
        os.remove(crc_file)

    crc_files = glob.glob("*/"+crc_file, recursive=True)
    for crc_file in crc_files:
        os.remove(crc_file)


class Comparator(object):
    """ TODO switch to CrcFile.
     1. it does not allow for simple use of unix line endings on windows
     2. for case sensitivity we have to create lambda functions (ugly).
    """

    def __init__(self, first, second):
        self.data1 = first
        self.data2 = second

    def read(self):
        self.cfg1 = CrcFile()
        self.cfg1.read_data(self.data1)

        self.cfg2 = CrcFile()
        self.cfg2.read_data(self.data2)

    def is_diff(self):
        if self.data1 != self.data2:
            self.read()
            return True
        return False

    def is_same(self):
        if self.data1 == self.data2:
            return True

        self.read()
        return False

    def get_1st_files(self):
        return self.cfg1.get_files()

    def get_1st_dirs(self):
        return self.cfg1.get_dirs()

    def get_2st_files(self):
        return self.cfg2.get_files()

    def get_2st_dirs(self):
        return self.cfg2.get_dirs()

    def get_1st_more_dirs(self):
        return [item for item in self.get_1st_dirs() if item not in self.get_2nd_dirs() ]

    def get_1st_more_files(self):
        return [item for item in self.get_1st_files() if item not in self.get_2nd_files() ]

    def get_2nd_more_dirs(self):
        return [item for item in self.get_2nd_dirs() if item not in self.get_1st_dirs() ]

    def get_2nd_more_files(self):
        return [item for item in self.get_2nd_files() if item not in self.get_1st_files() ]

    def get_modified_files(self):
        files = []
        for item in self.cfg1[SECTION_NAME]:
            if item in self.cfg2[SECTION_NAME]:
                if self.cfg1[SECTION_NAME][item] != self.cfg2[SECTION_NAME][item]:
                    files.append(item)

        if self.data1 != self.data2:
            files.append(CRC_FILE_NAME)

        return files


def process_arguments():

    parser = argparse.ArgumentParser(description='Create a CRC inforation file for a dir')
    parser.add_argument('-d','--dir', dest='directory',
                        help='directory to process')
    parser.add_argument('-e','--each', dest='each', action="store_true",
                        help='Each directory contains its own crc file')
    parser.add_argument('--diff', dest='diff', nargs=2,
                        help='diff files')
    parser.add_argument('-r','--remove', dest='remove', action="store_true", help='Remove CRC files from that directory')

    args = parser.parse_args()
    return args, parser


def main():
    args, parser = process_arguments()

    directory = "."
    if args.directory:
        if os.path.isdir(args.directory):
            directory = args.directory
        else:
            print("Directory does not exist: {0}".format(args.directory))
            sys.exit(1)

        if not args.each:
            create_dircrc(directory)
        else:
            create_dircrcs(directory)

    elif args.diff:
        with open(args.diff[0], 'r') as fh:
            data1 = fh.read()

        with open(args.diff[1], 'r') as fh:
            data2 = fh.read()

        comp = Comparator(data1, data2)

        print(comp.get_1st_files() )
        print(comp.get_1st_dirs() )

        print(comp.get_2nd_files() )
        print(comp.get_2nd_dirs() )

        print("1st more files")
        print(comp.get_1st_more_files())
        print("2nd more files")
        print(comp.get_2nd_more_files())

        print("1st more dirs")
        print(comp.get_1st_more_dirs())
        print("2nd more dirs")
        print(comp.get_2nd_more_dirs())

        print("modified")
        print(comp.get_modified_files())

    elif args.remove:
        remove_crc_files()

    else:
        parser.print_help()


if __name__ == '__main__':
    main()

