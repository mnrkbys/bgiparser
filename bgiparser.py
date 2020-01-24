#!/usr/bin/env python3
#
# bgiparser.py
# Parses backgrounditems.btm file to get items that runs when an user logs in.
#
# Copyright 2020 Minoru Kobayashi <unknownbit@gmail.com> (@unkn0wnbit)
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import os
import sys
import argparse
import json
import struct

try:
    import ccl_bplist
except ImportError:
    sys.exit('Import Error: ccl_bplist is not installed.\nGet it from https://github.com/cclgroupltd/ccl-bplist')

# global variables
debug_mode = False


# setup arguments
def parse_arguments():
    parser = argparse.ArgumentParser(description='Parses backgrounditems.btm file.')
    parser.add_argument('-f', '--file', action='store',
                        default='{}/Library/Application Support/com.apple.backgroundtaskmanagementagent/backgrounditems.btm'.format(os.environ['HOME']),
                        help='Path to backgrounditems.btm (default: User\'s file that runs this script.)')
    parser.add_argument('-o', '--out', action='store', default=None,
                        help='Path to output filename')
    parser.add_argument('-c', '--console', action='store_true', default=False,
                        help='Output a result to console')
    parser.add_argument('--force', action='store_true', default=False,
                        help='Enable to overwrite existing data.')
    parser.add_argument('--debug', action='store_true', default=False, help='Enable debug mode.')
    args = parser.parse_args()

    return args


def dbg_print(msg):
    if debug_mode:
        print(msg)


def get_login_items_entries(btm_file):
    with open(btm_file, 'rb') as fp:
        plist = ccl_bplist.load(fp)
        ns_keyed_archiver_obj = ccl_bplist.deserialise_NsKeyedArchiver(plist, parse_whole_structure=True)
        ccl_bplist.set_object_converter(ccl_bplist.NSKeyedArchiver_common_objects_convertor)
        return ns_keyed_archiver_obj['root']['backgroundItems']['allContainers']


def parse_bookmark_data(data):
    # Parses data according to the url below:
    # https://michaellynn.github.io/2015/10/24/apples-bookmarkdata-exposed/

    name = ''
    path = ''

    # BookmarkData Header
    magic, data_length, version, data_offset = struct.unpack_from('<4sIII', data, 0)
    dbg_print('-' * 50)

    if magic != b'book':
        dbg_print('[Error] magic is not \'book\': {}'.format(magic.decode('utf-8')))
        return False

    dbg_print('Magic: {}'.format(magic.decode('utf-8')))
    dbg_print('Data Length: {}'.format(hex(data_length)))
    dbg_print('Version: {}'.format(hex(version)))
    dbg_print('Data Offset: {}'.format(hex(data_offset)))

    # BookmarkData Data
    toc_offset = struct.unpack_from('<I', data, data_offset)[0]
    dbg_print('First TOC Offset: {}'.format(hex(toc_offset)))

    while True:
        # BookmarkData TOC
        # TOC Header
        toc_data_length, toc_record_type, flags = struct.unpack_from('<IHH', data, data_offset + toc_offset)
        dbg_print('=' * 50)
        dbg_print('TOC Data Length: {}'.format(hex(toc_data_length)))
        dbg_print('TOC Record Type: {}'.format(hex(toc_record_type)))
        dbg_print('Flags: {}'.format(hex(flags)))

        # TOC Data
        level, next_toc_offset, record_num = struct.unpack_from('<III', data, data_offset + toc_offset + (4 + 2 + 2))
        dbg_print('Level: {}'.format(hex(level)))
        dbg_print('Offset of Next TOC: {}'.format(hex(next_toc_offset)))
        dbg_print('Number of Records: {}'.format(record_num))

        for record_count in list(range(record_num)):
            # TOC Data Record
            record_count += 1
            toc_data_record_record_type, toc_data_record_flags, record_data_offset = struct.unpack_from('<HHQ', data, data_offset + toc_offset + (4 + 2 + 2) + ((4 + 4 + 4) * record_count))
            dbg_print('TOC Data Record Record Type: {}'.format(hex(toc_data_record_record_type)))
            dbg_print('TOC Data Record Flags: {}'.format(hex(toc_data_record_flags)))
            dbg_print('TOC Data Record Offset of Record Data: {}'.format(hex(record_data_offset)))

            # Standard Data Record
            sdr_data_length, sdr_data_type = struct.unpack_from('<II', data, data_offset + record_data_offset)
            dbg_print('Standard Data Record Length of Data: {}'.format(hex(sdr_data_length)))
            dbg_print('Standard Data Record Data Type: {}'.format(hex(sdr_data_type)))

            # Standard Data Record Data
            sdr_data = struct.unpack_from('<{}s'.format(sdr_data_length), data, data_offset + record_data_offset + (4 + 4))[0]
            dbg_print('Standard Data Record Record Data: {}'.format(sdr_data))

            if toc_data_record_record_type == 0xf017 and sdr_data_type == 0x101:
                name = sdr_data.decode('utf-8')
            # elif toc_data_record_record_type == 0xf080 and sdr_data_type == 0x201:
            #     path = sdr_data.decode('utf-8').split(';')[-1].replace('\x00', '')
            elif toc_data_record_record_type == 0x1004 and sdr_data_type == 0x601:
                path_array = list()
                path_str_offset_array = sdr_data
                while path_str_offset_array != b'':
                    path_part_offset = struct.unpack_from('<I', path_str_offset_array, 0)[0]
                    dbg_print('path_part_offset: {}'.format(hex(path_part_offset)))

                    path_part_str_length, unknown_data = struct.unpack_from('<II', data, data_offset + path_part_offset)
                    dbg_print('path_part_str_length: {}'.format(hex(path_part_str_length)))

                    path_part_str = struct.unpack_from('<%ds' % path_part_str_length, data, data_offset + path_part_offset + 4 + 4)[0]
                    dbg_print('path_part_str: {}'.format(path_part_str.decode('utf-8')))

                    path_array.append(path_part_str.decode('utf-8'))
                    dbg_print('path_arry: {}'.format(path_array))

                    path_str_offset_array = path_str_offset_array[4:]
                path = '/' + '/'.join(path_array)
            dbg_print('*' * 50)

        if next_toc_offset > 0:
            toc_offset = next_toc_offset
        else:
            if name or path:
                return {'name': name, 'path': path}
            else:
                return False


# main
def main():
    global debug_mode
    login_items = list()

    args = parse_arguments()
    debug_mode = args.debug

    btm_file = os.path.abspath(args.file)
    if not (os.path.exists(btm_file) or os.path.isfile(btm_file)):
        sys.exit('btm file is not found or is not a file: {}'.format(btm_file))

    if args.out:
        out_file = os.path.abspath(args.out)
        if os.path.exists(out_file) and not args.force:
            sys.exit('output file already exists: {}'.format(out_file))

    login_items_entries = get_login_items_entries(btm_file)

    for item_num in list(range(len(login_items_entries))):
        if type(login_items_entries[item_num]['internalItems'][0]['bookmark']['data']) == bytes:
            login_item = parse_bookmark_data(login_items_entries[item_num]['internalItems'][0]['bookmark']['data'])
        elif type(login_items_entries[item_num]['internalItems'][0]['bookmark']['data']) == ccl_bplist.NsKeyedArchiverDictionary:
            login_item = parse_bookmark_data(login_items_entries[item_num]['internalItems'][0]['bookmark']['data']['NS.data'])

        if login_item:
            login_items.append(login_item)

    if args.console or debug_mode:
        print(json.dumps(login_items, ensure_ascii=False, indent=4))

    if args.out:
        try:
            with open(out_file, 'wt') as out_fp:
                json.dump(login_items, out_fp, ensure_ascii=False, indent=4)
        except OSError as err:
            sys.exit(err)


if __name__ == "__main__":
    if sys.version_info[0:2] < (3, 5):
        sys.exit("This script needs greater than or equal to Python 3.5")

    main()
