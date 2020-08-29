
import argparse
import os
import sys
import zlib
import configparser
import glob


crc_file_name = "crc_list.txt"


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
        file_map[big_name] = -1   # special value, CRC is positive in python3

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

    config["CRC List"] = file_map

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
    buf = io.StringIO(data)

    config = configparser.ConfigParser()
    config.read(buf)
    dst_map = dict(config["CRC List"])

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
        conf = configparser.ConfigParser()
        conf.read(args.diff[0])
        one = conf["CRC List"]

        conf = configparser.ConfigParser()
        conf.read(args.diff[1])
        two = conf["CRC List"]

        diff_one, diff_two = diff_dir( one, two)
        print(diff_one)
        print(diff_two)

    elif args.remove:
        remove_crc_files()

    else:
        parser.print_help()


if __name__ == '__main__':
    main()

