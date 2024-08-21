#!/usr/bin/env python3
#
# bgiparser.py
# Parses backgrounditems.btm file to get items that runs when an user logs in.
#
# Copyright 2020-2023 Minoru Kobayashi <unknownbit@gmail.com> (@unkn0wnbit)
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
import argparse
import datetime
import json
import os
import struct
import sys

import nska_deserialize as nd

# global variables
VERSION = '20240821'
debug_mode = False


# setup arguments
def parse_arguments() -> argparse.Namespace:
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
    parser.add_argument('-v', '--version', action='version', version=f"%(prog)s {VERSION}", help='Show version.')
    return parser.parse_args()


def dbg_print(msg: str) -> None:
    if debug_mode:
        print(msg)


def convert_cfabsolute_time(abs_time: float) -> datetime.datetime:
    try:
        return datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc) + datetime.timedelta(seconds=abs_time)
    except (ValueError, OverflowError):
        return datetime.datetime(2001, 1, 1, tzinfo=datetime.timezone.utc)


def parse_bookmark_data(data: bytes) -> dict[str, str] | bool:
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
    dbg_print(f'Data Length: {hex(data_length)}')
    dbg_print(f'Version: {hex(version)}')
    dbg_print(f'Data Offset: {hex(data_offset)}')

    # BookmarkData Data
    toc_offset = struct.unpack_from('<I', data, data_offset)[0]
    dbg_print(f'First TOC Offset: {hex(toc_offset)}')

    while True:
        # BookmarkData TOC
        # TOC Header
        toc_data_length, toc_record_type, flags = struct.unpack_from('<IHH', data, data_offset + toc_offset)
        dbg_print('=' * 50)
        dbg_print(f'TOC Data Length: {hex(toc_data_length)}')
        dbg_print(f'TOC Record Type: {hex(toc_record_type)}')
        dbg_print(f'Flags: {hex(flags)}')

        # TOC Data
        level, next_toc_offset, record_num = struct.unpack_from('<III', data, data_offset + toc_offset + (4 + 2 + 2))
        dbg_print(f'Level: {hex(level)}')
        dbg_print(f'Offset of Next TOC: {hex(next_toc_offset)}')
        dbg_print(f'Number of Records: {record_num}')

        for record_count in list(range(record_num)):
            # TOC Data Record
            record_count += 1
            toc_data_record_record_type, toc_data_record_flags, record_data_offset = struct.unpack_from('<HHQ', data, data_offset + toc_offset + (4 + 2 + 2) + ((4 + 4 + 4) * record_count))
            dbg_print(f'TOC Data Record Record Type: {hex(toc_data_record_record_type)}')
            dbg_print(f'TOC Data Record Flags: {hex(toc_data_record_flags)}')
            dbg_print(f'TOC Data Record Offset of Record Data: {hex(record_data_offset)}')

            # Standard Data Record
            sdr_data_length, sdr_data_type = struct.unpack_from('<II', data, data_offset + record_data_offset)
            dbg_print(f'Standard Data Record Length of Data: {hex(sdr_data_length)}')
            dbg_print(f'Standard Data Record Data Type: {hex(sdr_data_type)}')

            # Standard Data Record Data
            sdr_data = struct.unpack_from(f'<{sdr_data_length}s', data, data_offset + record_data_offset + (4 + 4))[0]
            dbg_print(f'Standard Data Record Record Data: {sdr_data}')

            if toc_data_record_record_type == 0xf017 and sdr_data_type == 0x101:
                name = sdr_data.decode('utf-8')
            # elif toc_data_record_record_type == 0xf080 and sdr_data_type == 0x201:
            #     path = sdr_data.decode('utf-8').split(';')[-1].replace('\x00', '')
            elif toc_data_record_record_type == 0x1004 and sdr_data_type == 0x601:
                path_array = []
                path_str_offset_array = sdr_data
                while path_str_offset_array != b'':
                    path_part_offset = struct.unpack_from('<I', path_str_offset_array, 0)[0]
                    dbg_print(f'path_part_offset: {hex(path_part_offset)}')

                    path_part_str_length, unknown_data = struct.unpack_from('<II', data, data_offset + path_part_offset)
                    dbg_print(f'path_part_str_length: {hex(path_part_str_length)}')

                    path_part_str = struct.unpack_from('<%ds' % path_part_str_length, data, data_offset + path_part_offset + 4 + 4)[0]
                    dbg_print('path_part_str: {}'.format(path_part_str.decode('utf-8')))

                    path_array.append(path_part_str.decode('utf-8'))
                    dbg_print(f'path_arry: {path_array}')

                    path_str_offset_array = path_str_offset_array[4:]
                path = '/' + '/'.join(path_array)
            dbg_print('*' * 50)

        if next_toc_offset > 0:
            toc_offset = next_toc_offset
        elif name or path:
            return {'name': name, 'path': path}
        else:
            return False


def parse_btm(btm_path: str) -> list | dict:
    with open(btm_path, 'rb') as f:
        plist = nd.deserialize_plist(f)
        dbg_print(f"Opened {btm_path}")

    # >= macOS 10.13 and <= macOS 12
    if isinstance(plist, dict) and plist['version'] == 2:
        dbg_print("Detected version: {}".format(plist['version']))
        entries = []
        login_item_entries = plist.get('backgroundItems', {}).get('allContainers', {})
        for item_num in list(range(len(login_item_entries))):
            bm_data = login_item_entries[item_num]['internalItems'][0]['bookmark']['data']
            login_item = {}
            if isinstance(bm_data, bytes):
                login_item = parse_bookmark_data(bm_data)
            elif isinstance(bm_data, dict):
                login_item = parse_bookmark_data(bm_data['NS.data'])

            if login_item:
                entries.append(login_item)

    # >= macOS 13
    elif isinstance(plist, list) and plist[0].get('version', 0) >= 3:
        dbg_print("Detected version: {}".format(plist[0]['version']))
        entries = {}
        for uuid in plist[1]['store']['itemsByUserIdentifier'].keys():
            dbg_print("=" * 50)
            dbg_print(f"User UUID: {uuid}")
            dbg_print("=" * 50)
            login_item = {uuid: [{}]}
            for item_number in list(range(len(plist[1]['store']['itemsByUserIdentifier'][uuid]))):
                dbg_print("-" * 20 + f" Item: {item_number} " + "-" * 20)
                item = {}
                for k, v in plist[1]['store']['itemsByUserIdentifier'][uuid][item_number].items():
                    if k not in ('lightweightRequirement', 'bookmark'):  # These keys contain bytes data.
                        if k in ('type', ):
                            dbg_print(f"{k}: 0x{v:X}")
                        elif k in ('modificationDate', 'executableModificationDate'):
                            dbg_print(f"{k}: {v} ({convert_cfabsolute_time(v).strftime('%Y-%m-%d %H:%M:%S.%f')})")
                        else:
                            dbg_print(f"{k}: {v}")

                        if k in ('sha256',) and isinstance(v, bytes):
                            v = v.hex()
                        item.update({k: v})

                login_item[uuid].append(item)

            if login_item[uuid]:
                entries.update(login_item)

    else:
        sys.exit(f'Unsupported btm file: {btm_path}')

    return entries


# main
def main() -> None:
    global debug_mode
    login_items = []
    out_file = None

    args = parse_arguments()
    debug_mode = args.debug

    btm_file = os.path.abspath(args.file)
    if not (os.path.exists(btm_file) or os.path.isfile(btm_file)):
        sys.exit(f'btm file is not found or is not a file: {btm_file}')

    if args.out:
        out_file = os.path.abspath(args.out)
        if os.path.exists(out_file) and not args.force:
            sys.exit(f'output file already exists: {out_file}')

    login_items = parse_btm(btm_file)

    if args.console or debug_mode:
        print(json.dumps(login_items, ensure_ascii=False, indent=4))

    if out_file:
        try:
            with open(out_file, "w") as out_fp:
                json.dump(login_items, out_fp, ensure_ascii=False, indent=4)
        except OSError:
            sys.exit(1)


if __name__ == "__main__":
    if sys.version_info[0:2] < (3, 10):
        sys.exit("This script needs greater than or equal to Python 3.5")

    main()
