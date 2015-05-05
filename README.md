# Tuck

Tuck creates symlinks to files. Useful when keeping your dotfiles in one place,
like a git repository.

# Features

- no install, one python file
- one simple and optional config file
- backup before overwrite
- no database
- no remote features


# Requirements

 - python 3.4

# Usage


`tuck list` list the packages and their status in the current directory  
`tuck list <package> [package root]` list of files and their status in a
  package. Defaults to $HOME
`tuck list <collection>` list packages and their status in a collection  
`tuck list orphans` list packages that are not in any collection  
`tuck link <package> [package root]` link files in a package
  realtive to `[package root]`, defaults to $HOME  
`tuck sync <collection>` link all packages in a collection

# License

See COPYING file.

# Similar tools

If you like the idea but Tuck is too simple for you, try one of these.

 * [GNU Stow](http://www.gnu.org/software/stow)
 * [dotfiles](https://github.com/jbernard/dotfiles)
 * [bookkeeper](https://github.com/hkupty/bookkeeper)
