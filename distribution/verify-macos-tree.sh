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
# Both catalogs were authenticated before entering this script. Walk actual
# names as bytes, so even a filename containing a newline cannot forge a row.
cd "$root"
/usr/bin/perl -T - "$objects" <<'PERL'
use strict;
use warnings FATAL => 'all';
use Fcntl ':mode';

my ($catalog) = @ARGV;
open my $in, '<', $catalog or die "catalog open";
my %expected;
my $previous = '';
while (<$in>) {
    die "catalog newline" unless chomp;
    die "catalog order" unless $_ gt $previous;
    $previous = $_;
    die "duplicate object" if $expected{$_}++;
}
close $in or die "catalog read";
my @todo = ('.');
while (@todo) {
    my $path = pop @todo;
    my @s = lstat($path);
    die "metadata" unless @s && !($s[2] & 07000);
    my ($kind, $mode, $link) = ('', sprintf('%o', $s[2] & 0777), '');
    if (S_ISDIR($s[2])) {
        $kind = 'Directory';
        opendir my $dir, $path or die "directory open";
        local $! = 0;
        while (defined(my $name = readdir $dir)) {
            next if $name eq '.' || $name eq '..';
            die "name" unless $name =~ /\A[A-Za-z0-9_.+@=,%-]+\z/;
            push @todo, "$path/$name";
        }
        die "directory read" if $!;
        closedir $dir or die "directory close";
    } elsif (S_ISREG($s[2]) && $s[3] == 1) {
        $kind = 'Regular File';
    } elsif (S_ISLNK($s[2])) {
        $kind = 'Symbolic Link';
        $mode = '-';
        $link = readlink $path;
        die "link" unless defined $link && $link =~ m{\A[A-Za-z0-9_./+@=,%-]+\z};
    } else {
        die "unsupported object";
    }
    die "unexpected object" unless delete $expected{join('|', $kind, $mode, $path, $link)};
}
die "missing object" if %expected;
PERL
/usr/bin/shasum -a 256 -c "$checksums" > /dev/null
