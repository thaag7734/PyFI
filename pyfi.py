"""
PyFontInstaller is a small Python script to help install CFI fonts via ADB.

This script will take .ttf font files, change the filenames to adhere to
those that are supported by CFI (GitHub below), and move them into an output
directory. Optionally, the user may push the files over ADB to an Android
device.

CFI: https://github.com/nongthaihoang/custom_font_installer
PyFI: https://github.com/thaag7734/pyfi
"""

import os
import shutil
import argparse
import textwrap
import sys

DESC_TEXT = """
*************************************************
* PyFI v1.0 | https://github.com/thaag7734/pyfi *
*************************************************
A small Python script to help with the installation of
CFI fonts for Android devices connected over ADB.

Please note that only those filenames listed on the CFI
GitHub (https://github.com/nongthaihoang/custom_font_installer)
are currently supported, any other .ttf files present will almost definitely
break everything. This will be fixed in a future version."""
USAGE_EX = "".join(
    ["Usage examples:\n",
     "    python3 PyFI.py -p -e OpenMoji.ttf.........: Pushes OpenMoji.ttf to",
     " /sdcard/Fonts/[current directory name] as e.ttf",
     " and exits\n",
     "    python3 PyFI.py -i -m LiberationMono.ttf...: Renames and pushes",
     " all .ttf files to /sdcard/OhMyFont/CFI and exits\n",
     "    python3 PyFI.py -i -p -d -n OpenSans.......: Renames and pushes all",
     " .ttf files to CFI dir AND /sdcard/Fonts/OpenSans",
     " and exits"]
)

OUT_DIR = "PyFI_OUT"

ap = argparse.ArgumentParser(
    prog="PyFontConverter",
    formatter_class=argparse.RawDescriptionHelpFormatter,
    description=textwrap.dedent(DESC_TEXT),
    epilog=USAGE_EX
)

ap.add_argument(
    "-p", "--push",
    help = "Pushes created font files to /sdcard/Fonts/[font name],"
           + " creating it if it doesn't exist",
    action="store_true"
)
ap.add_argument(
    "-i", "--install",
    help = "Clears /sdcard/OhMyFont/CFI"
           + " and pushes created font files there",
    action="store_true"
)
ap.add_argument(
    "-n", "--name",
    help = "Manually set the name of the font"
           + " (normally defaults to the folder name)"
)

ftg = ap.add_mutually_exclusive_group()
ftg.add_argument(
    "-d", "--dir",
    help = "Renames all .ttf files in the current dir"
           + " and moves them to ./"
           + OUT_DIR,
    action = "store_true"
)
ftg.add_argument(
    "-e", "--emoji",
    help = "Takes a .ttf file and renames it to"
           + " e.ttf in the output dir"
)
ftg.add_argument(
    "-m", "--monospace",
    help = "Takes a .ttf file and renames it to"
           + " mo.ttf (ms.ttf for variable fonts) in the output dir"
)

if len(sys.argv) == 1:
    ap.print_help()
    sys.exit(1)

args = ap.parse_args()

name_conversions = {
    "Italic[wdth,wght]": "ssi",
    "[wdth,wght]": "ss",
    "BlackItalic": "bli",
    "Black": "bl",
    "ExtraBoldItalic": "ebi",
    "ExtraBold": "eb",
    "SemiBoldItalic": "sbi",
    "SemiBold": "sb",
    "BoldItalic": "bi",
    "Bold": "b",
    "ExtraLightItalic": "eli",
    "ExtraLight": "el",
    "LightItalic": "li",
    "Light": "l",
    "MediumItalic": "mi",
    "Medium": "m",
    "ThinItalic": "ti",
    "Thin": "t",
    "Italic": "i",
    "Regular": "r"
}

if not os.path.exists(OUT_DIR):
    os.mkdir(OUT_DIR)


def get_font_name():
    """Gets the font name from either the CWD or the -n option."""
    return (
        os.path.basename(os.getcwd()),
        args.name
    )[args.name is not None]


def push_files(to_path):
    """Pushes all files in CWD to to_path over adb."""
    font_name = get_font_name()

    os.system("adb shell mkdir -p " + to_path)
    for f in os.listdir(OUT_DIR):
        os.system(
            "adb push "
            + os.path.join(OUT_DIR, f)
            + " "
            + to_path
            + font_name
            + "/"
            + f
        )
    return font_name


def rename_file(name_from, name_to=""):
    """Renames ./name_from to OUT_DIR/name_to"""
    if name_to == "":
        name_to = "c" if "Condensed" in name_from else ""
        for before, after in name_conversions.items():
            if before in name_from:
                name_to += after
                break
        name_to += ".ttf"
    shutil.copy(name_from, os.path.join(OUT_DIR, name_to))


if args.emoji is not None:
    rename_file(args.emoji, "e.ttf")
if args.monospace is not None:
    out_name = "mo.ttf"
    if "[wdth,wght]" in args.monospace:
        out_name = "ms.ttf"
    rename_file(args.monospace, out_name)
if args.dir:
    for f in os.listdir():
        if f[-4:] == ".ttf":
            out_name = "c" if "Condensed" in f else ""
            for before, after in name_conversions.items():
                if before in f:
                    out_name += after
                    break
            out_name += ".ttf"
            shutil.copy(f, os.path.join(OUT_DIR, out_name))

if args.push:
    push_files("/sdcard/Fonts/")
    print("Done! Files pushed to /sdcard/Fonts/" + get_font_name() + "/")

if args.install:
    os.system("adb shell rm -rf /sdcard/OhMyFont/CFI/")
    push_files("/sdcard/OhMyFont/CFI/")
    print("Done! Please note that you have to reinstall the Magisk module\n"
          + "manually and reboot, as installation cannot be done over ADB.")
