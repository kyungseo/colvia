#!/bin/bash
# This file and both catalogs are pinned by the release entry before invocation.
set -euo pipefail
[ "$#" -eq 4 ] || exit 64
root=$1; objects=$2; checksums=$3; scratch_parent=$4
for name in "$@"; do case "$name" in /*) ;; *) exit 65 ;; esac; done
for name in "$root" "$scratch_parent"; do
  [ -d "$name" ] && [ ! -L "$name" ] || exit 65
  parent=$name
  while [ "$parent" != / ]; do
    [ ! -L "$parent" ] && [ -d "$parent" ] || exit 65
    parent=${parent%/*}; [ -n "$parent" ] || parent=/
  done
done
for name in "$objects" "$checksums"; do
  [ -f "$name" ] && [ ! -L "$name" ] || exit 65
  [ "$(/usr/bin/stat -f '%l' "$name")" = 1 ] || exit 65
done
umask 077
scratch=$(/usr/bin/mktemp -d "$scratch_parent/check.XXXXXXXX")
trap '/bin/rm -f "$scratch/paths" "$scratch/raw" "$scratch/objects" "$scratch/sorted" "$scratch/hashes"; /bin/rmdir "$scratch"' EXIT
cd "$root"
# Separate commands preserve every exit status, including find and xargs.
/usr/bin/find -P . -print0 > "$scratch/paths"
/usr/bin/xargs -0 /usr/bin/stat -f '%HT|%OLp|%OMp|%l|%N|%Y' < "$scratch/paths" > "$scratch/raw"
/usr/bin/awk -F '|' 'BEGIN { OFS="|" }
 NF!=6 || $3!=0 || $5 !~ /^[A-Za-z0-9_.\/+@=,%-]+$/ { exit 65 }
 $1=="Regular File" && $4!=1 { exit 65 }
 $1=="Symbolic Link" { if ($6 !~ /^[A-Za-z0-9_.\/+@=,%-]+$/) exit 65; print $1,"-",$5,$6; next }
 $1!="Directory" && $1!="Regular File" { exit 65 }
 { print $1,$2,$5,$6 }' "$scratch/raw" > "$scratch/objects"
/usr/bin/sort "$scratch/objects" > "$scratch/sorted"
/usr/bin/cmp -s "$objects" "$scratch/sorted"
/usr/bin/shasum -a 256 -c "$checksums" > "$scratch/hashes"
