# bgiparser (backgrounditems.btm/BackgroundItems-v*.btm parser)

The entries of "Login Items" are stored in "~/Library/Application Support/com.apple.backgroundtaskmanagementagent/backgrounditems.btm" since macOS 10.13 High Sierra. This tool can parse it and output pairs of entry name and application path as JSON data.

Apple has changed the location of the file that records Login Items in macOS 13 Ventura and the format has also been changed. This script supports the new format too.
New file location is "/private/var/db/com.apple.backgroundtaskmanagement/BackgroundItems-v*.btm".

By the way, you can also download another parsing tool from [here](https://github.com/objective-see/DumpBTM). Or just run `sfltool dumpbtm` on macOS 13.

## Requirement

- Python 3.5 or later
- [nska_deserialize](https://github.com/ydkhatri/nska_deserialize) 1.3.2 or later

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
$ pip install nska_deserialize
```

## Execution example 1

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

## Execution example 2

```bash
% python ./bgiparser.py -c -f /private/var/db/com.apple.backgroundtaskmanagement/BackgroundItems-v8.btm
{
    "D91E3B5A-648E-4747-92E7-F6F07E8EC600": [
        {
            "uuid": "1975D13A-A95B-471A-A8AD-FE8BCCE818E0",
            "teamIdentifier": "",
            "disposition": 10,
            "generation": 1,
            "modificationDate": 0.0,
            "associatedBundleIdentifiers": "",
            "url": "",
            "bundleIdentifier": "",
            "type": 32,
            "identifier": "Objective-See, LLC",
            "executablePath": "",
            "container": "",
            "developerName": "Objective-See, LLC",
            "executableModificationDate": 0.0,
            "items": [
                "com.objective-see.blockblock"
            ],
            "name": "Objective-See, LLC"
        },
        {
            "uuid": "D6E56BFF-5FE6-451E-9FA0-498699654772",
            "teamIdentifier": "",
            "disposition": 10,
            "generation": 2,
            "modificationDate": 0.0,
            "associatedBundleIdentifiers": "",
            "url": "",
            "bundleIdentifier": "",
            "type": 32,
            "identifier": "Logitech Inc.",
            "executablePath": "",
            "container": "",
            "developerName": "Logitech Inc.",
            "executableModificationDate": 0.0,
            "items": [
                "com.logi.optionsplus.updater"
            ],
            "name": "Logitech Inc."
        },
        {
            "uuid": "3F33A859-4972-4CDE-8175-B93EDD106649",
            "teamIdentifier": "",
            "disposition": 10,
            "generation": 1,
            "modificationDate": 0.0,
            "associatedBundleIdentifiers": "",
            "url": "",
...
```

## Limitation

BackgroundItems-v*.btm only has user UUIDs, not user IDs or usernames.
You can get the UUID corresponding to a username on localhost with the following command.
In other words, if you parse BackgroundItems-v*.btm obtained from other host, you cannot reliably identify the username.
```bash
% sudo dscl . read /Users/root generateduid
dsAttrTypeNative:generateduid: FFFFEEEE-DDDD-CCCC-BBBB-AAAA00000000
```

## TODO

- [ ] Confirm condition of each entry (enable or disable)
- [X] Support macOS 13

## Author

[Minoru Kobayashi](https://twitter.com/unkn0wnbit)

## License

[Apache License, Version 2.0](http://www.apache.org/licenses/LICENSE-2.0)
