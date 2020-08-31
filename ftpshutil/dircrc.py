
import argparse
import os
import sys
import zlib
import configparser
import glob
import io


crc_file_name = "crc_list.txt"
crc_4_dir = -1
section_name = "CRC List"


def file_crc(afile):
    with open(afile, 'rb') as fh:
        data = fh.read()

        return zlib.crc32(data)


def calc_dircrc(root, dirs, files):
    file_map = {}
    for name in sorted(files):
        big_name = os.path.join(root, name)
        if name != crc_file_name:
            file_map[big_name] = file_crc(big_name)
        else:
            file_map[big_name] = -2

    for name in sorted(dirs):
        big_name = os.path.join(root, name)
        file_map[big_name] = crc_4_dir

    return file_map


def calc_dircrc_recursive(directory):
    print("processing directory: {0}".format(directory))

    file_map = {}

    for root, dirs, files in os.walk(directory, topdown=False):
        single_dir_map = calc_dircrc(root, dirs, files)
        file_map.update(single_dir_map)

    return file_map


def save_map_file(file_name, file_map):
    config = configparser.ConfigParser()

    config[section_name] = file_map

    with open(file_name , 'w') as configfile:
        config.write(configfile)


def create_dircrc(directory):
    file_map = calc_dircrc_recursive(directory)

    output_name = crc_file_name
    save_map_file(os.path.join(directory, output_name), file_map)

    return file_map


def create_dircrcs(directory):
    for root, dirs, files in os.walk(directory, topdown=False):
        cur_path = os.getcwd()
        os.chdir(root)
        file_map = calc_dircrc(".", dirs, files)
        os.chdir(cur_path)

        output_name = crc_file_name
        save_map_file( os.path.join(root, output_name), file_map)


def diff_dir(one_dir, two_dir):
    one_dir = dict(one_dir).keys()
    two_dir = dict(two_dir).keys()

    diff_one = one_dir - two_dir
    diff_two = two_dir - one_dir
    return diff_one, diff_two


def copy_sync(src_dir, dst_dir, dst_handle):
    dst_crc_list = os.path.join(dst_dir, crc_file_name)
    if not dst_handle.exists(dst_crc_list):
        dst_handle.copytree(src, dst_dir)

    data = dst_handle.read(dst_crc_list)
    buf = io.BytesIO(data)

    config = configparser.ConfigParser()
    config.read(buf)
    dst_map = dict(config[section_name])

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

    crc_file = crc_file_name
    if os.path.isfile(crc_file):
        os.remove(crc_file)

    crc_files = glob.glob("*/"+crc_file, recursive=True)
    for crc_file in crc_files:
        os.remove(crc_file)


class Comparator(object):
    def __init__(self, first, second):
        self.data1 = first
        self.data2 = second

        self.cfg1 = configparser.ConfigParser()
        self.cfg1.read_string(self.data1)

        self.cfg2 = configparser.ConfigParser()
        self.cfg2.read_string(self.data2)

    def is_diff(self):
        if self.data1 != self.data2:
            return True
        return False

    def is_same(self):
        if self.data1 == self.data2:
            return True
        return False

    def get_1st_files(self):
        files = []

        for item in self.cfg1[section_name]:
            val = int(self.cfg1[section_name][item])
            if val != crc_4_dir:
                files.append(item)

        return files

    def get_1st_dirs(self):
        dirs = []

        for item in self.cfg1[section_name]:
            val = int(self.cfg1[section_name][item])
            if val == crc_4_dir:
                dirs.append(item)

        return dirs

    def get_2nd_files(self):
        files = []

        for item in self.cfg2[section_name]:
            val = int(self.cfg2[section_name][item])
            if val != crc_4_dir:
                files.append(item)

        return files

    def get_2nd_dirs(self):
        dirs = []
        for item in self.cfg2[section_name]:
            val = int(self.cfg2[section_name][item])
            if val == crc_4_dir:
                dirs.append(item)

        return dirs

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
        for item in self.cfg1[section_name]:
            if item in self.cfg2[section_name]:
                if self.cfg1[section_name][item] != self.cfg2[section_name][item]:
                    files.append(item)

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

