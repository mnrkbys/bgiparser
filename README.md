# bgiparser (backgrounditems.btm parser)

The entries of "Login Items" are stored in "~/Library/Application Support/com.apple.backgroundtaskmanagementagent/backgrounditems.btm" since macOS 10.13 High Sierra. This tool can parse it and output pairs of entry name and application path as JSON data.

## Requirement

- Python 3.5 or later
- ccl_bplist 0.21 or later

## Usage

```bash
$ python3 ./bgiparser.py -h
usage: bgiparser.py [-h] [-f FILE] [-o OUT] [-c] [--force] [--debug]

Parses backgrounditems.btm file.

optional arguments:
  -h, --help            show this help message and exit
  -f FILE, --file FILE  Path to backgrounditems.btm (default: User's file that
                        runs this script.)
  -o OUT, --out OUT     Path to output filename
  -c, --console         Output a result to console
  --force               Enable to overwrite existing data.
  --debug               Enable debug mode.
```

## Installation

```bash
$ git clone https://github.com/mnrkbys/bgiparser.git
$ git clone https://github.com/cclgroupltd/ccl-bplist.git
$ cd bgiparser
$ ln -s ../ccl-bplist/ccl_bplist.py ccl_bplist.py
```

## Example of execution

```bash
$ python3 ./bgiparser.py -f ./sample/sample_mymac/backgrounditems.btm -c
[
    {
        "name": "duet.app",
        "path": "/Applications/duet.app"
    },
    {
        "name": "",
        "path": "/Applications/Display Menu.app/Contents/Library/LoginItems/Display Menu Helper.app"
    },
    {
        "name": "",
        "path": "/Applications/KeepingYouAwake.app/Contents/Library/LoginItems/KeepingYouAwake Launcher.app"
    },
    {
        "name": "",
        "path": "/Applications/⌘英かな.app/Contents/Library/LoginItems/cmd-eikana-helper.app"
    },
    {
        "name": "",
        "path": "/Applications/Wallcat.app/Contents/Library/LoginItems/StartAtLoginHelperApp.app"
    },
    {
        "name": "V-CUBE ミーティング 5.app",
        "path": "/Applications/vrms5lite-helper.app"
    },
    {
        "name": "",
        "path": "/Applications/OneDrive.app"
    },
    {
        "name": "Box Sync",
        "path": "/Applications/Box Sync.app"
    },
    {
        "name": "",
        "path": "/Applications/Evernote.app/Contents/Library/LoginItems/EvernoteHelper.app"
    },
    {
        "name": "",
        "path": "/Applications/1Password 7.app/Contents/Library/LoginItems/1Password Launcher.app"
    },
    {
        "name": "",
        "path": "/Applications/Day One.localized/Day One.app/Contents/Library/LoginItems/Day One Helper.app"
    }
]
```

## Author

[Minoru Kobayashi](https://twitter.com/unkn0wnbit)

## License

[Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)
