#!/usr/bin/env python3
#
# bgiparser_foundation.py
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

try:
    import Foundation
except ImportError:
    sys.exit('Import Error: PyObjC is not installed.\nGet it from https://bitbucket.org/ronaldoussoren/pyobjc or from pip.')


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


# main
def main():
    login_items = list()

    args = parse_arguments()

    btm_file = os.path.abspath(args.file)
    if not (os.path.exists(btm_file) or os.path.isfile(btm_file)):
        sys.exit('btm file is not found or is not a file: {}'.format(btm_file))

    if args.out:
        out_file = os.path.abspath(args.out)
        if os.path.exists(out_file) and not args.force:
            sys.exit('output file already exists: {}'.format(out_file))

    data = Foundation.NSDictionary.dictionaryWithContentsOfFile_(btm_file)
    for obj in data['$objects']:
        properties = None

        if obj.isKindOfClass_(Foundation.NSClassFromString('NSData')):
            properties = Foundation.NSURL.resourceValuesForKeys_fromBookmarkData_(['NSURLBookmarkAllPropertiesKey'], obj)
        elif obj.isKindOfClass_(Foundation.NSClassFromString("NSDictionary")):
            if 'NS.data' in obj:
                properties = Foundation.NSURL.resourceValuesForKeys_fromBookmarkData_(['NSURLBookmarkAllPropertiesKey'], obj['NS.data'])

        if properties:
            name = properties['NSURLBookmarkAllPropertiesKey']['NSURLLocalizedNameKey']
            path = properties['NSURLBookmarkAllPropertiesKey']['_NSURLPathKey']
            login_items.append({'name': name, 'path': path})

    if args.console or args.debug:
        print(json.dumps(login_items, indent=4))

    if args.out:
        try:
            with open(out_file, 'wt') as out_fp:
                json.dump(login_items, out_fp, indent=4)
        except OSError as err:
            sys.exit(err)


if __name__ == "__main__":
    if sys.version_info[0:2] < (3, 5):
        sys.exit("This script needs greater than or equal to Python 3.5")

    main()
