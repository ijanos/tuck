#!/bin/env python3
"""tuck - symlink dotfiles

usage:
  tuck list
  tuck list <collection>
  tuck list <package> [package root]
  tuck list orphans
  tuck link <package> [package root]
  tuck sync <collection>

Tuck reads collections from tuck.conf
"""

import os
import sys
from configparser import ConfigParser
from enum import Enum, unique
import itertools as it


@unique
class Status(Enum):
    installed, partial, empty, notinstalled, missing = range(5)


def load_tuckfile():
    config = ConfigParser(allow_no_value=True)
    try:
        config.read_file(open("tuck.conf"))
    except EnvironmentError:
        print("Missing tuck.conf in current directory!")
        sys.exit(1)
    return config


def pretty_print_packagelist(packages):
    icon = {
        Status.installed:    "I",
        Status.empty:        "E",
        Status.notinstalled: " ",
        Status.partial:      "P",
        Status.missing:      "?"
    }
    for p in packages:
        print("[{}] {}".format(icon[package_status(p, '~')], p))


def package_status(package, root):
    if not os.path.exists(package):
        return Status.missing
    if not os.listdir(package):
        return Status.empty
    missing = False
    installed = False
    for (original, link) in iterate_package(package, root):
        if os.path.exists(link) and os.path.samefile(original, link):
            installed = True
        else:
            missing = True
    if missing and installed:
        return Status.partial
    elif installed:
        return Status.installed
    elif missing:
        return Status.notinstalled
    else:
        print("{} - uknown package status! Abort.".format(package))
        sys.exit(1)


def iterate_package(package, root):
    for dirpath, _, filenames in os.walk(package):
        for f in filenames:
            source = os.path.abspath(os.path.join(dirpath, f))
            # if filepath[:8] == ".config/":
            # TODO replace with $XDG_CONFIG_HOME if defined
            destination = os.path.expanduser(os.path.join(root, dirpath[len(package)+1:], f))
            yield (source, destination)


def link_packagefiles(package, root="~"):
    for (original, link) in iterate_package(package, root):
        print("\tLinking {} -> {}".format(link, original), end=' ')
        try:
            if os.path.exists(link):
                if os.path.samefile(link, original):
                    print("existed")
                    continue
                elif os.path.isdir(link):
                    print("SKIPPED\nTarget is a directory!")
                    continue
                elif os.path.islink(link):
                    os.unlink(link)
                    print("updated")
                else:
                    os.rename(link, link + ".tuck")
                    print("renamed existing file")
            elif os.path.islink(link):
                os.unlink(link)
                print("updated")
            if not os.path.exists(os.path.dirname(link)):
                os.makedirs(os.path.dirname(link))
            os.symlink(original, link)
            print("done")
        except PermissionError:
            print("Permission error")


def cmd_link(args):
    if not args:
        print("Which package?\nusage: tuck link <package> [package root]")
    else:
        if len(args) < 2:
            package_root = '~'
        else:
            package_root = args[1]
        link_package(args[0].strip("/"), package_root)


def link_package(package, root):
    ps = package_status(package, root)
    if ps == Status.empty:
        print("[{}] empty package!".format(package))
    elif ps == Status.installed:
        print("[{}] already installed".format(package))
    elif ps == Status.missing:
        print("[{}] no such package".format(package))
    else:
        print("[{}] installing:".format(package))
        link_packagefiles(package, root)


def cmd_list_package(package, root):
    for (src, dest) in iterate_package(package, root):
        mark = " "
        if os.path.exists(dest) and os.path.samefile(src, dest):
            mark = "x"
        print("[{}] {} -> {}".format(mark, src, dest))


def cmd_list(args):
    packages = [p for p in os.listdir(".") if os.path.isdir(p) and p[0] != '.']
    if not args:
        pretty_print_packagelist(packages)
    elif args[0] == "orphans":
        config = load_tuckfile()
        owned = set(it.chain.from_iterable([config[s] for s in config]))
        orphans = set(packages) - owned
        pretty_print_packagelist(orphans)
    else:
        config = load_tuckfile()
        query = args[0].strip("/")
        if query in config.sections():
            pretty_print_packagelist(config[query])
        elif query in packages:
            if len(args) > 1:
                package_root = args[1]
            else:
                package_root = '~'
            cmd_list_package(query, package_root)
        else:
            print("No such package or collection")


def cmd_sync(args):
    if not args:
        print("Which collection?\nusage: tuck sync <collection>")
        return
    config = load_tuckfile()
    if args[0] not in config.sections():
        print("No such collection in tuck.conf")
        return
    for package in config[args[0]]:
        root = config.get(args[0], package)
        if not root:
            root = "~"
        link_package(package, root)
    print("Sync complete.")


if __name__ == '__main__':
    commands = {
        'list': cmd_list,
        'sync': cmd_sync,
        'link': cmd_link
        }
    if len(sys.argv) < 2 or sys.argv[1] not in commands:
        print(__doc__)
    else:
        commands[sys.argv[1]](sys.argv[2:])
