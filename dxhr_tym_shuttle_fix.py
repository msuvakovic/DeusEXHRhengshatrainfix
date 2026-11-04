#!/usr/bin/env python3
"""Deus Ex: Human Revolution Director's Cut - TYM shuttle fix (save edit).

Clears the Hengsha "Part 1 already set up" flag in one save so the game
re-runs its Hengsha setup (which starts the TYM shuttle and the metro trains)
the next time you walk out of the L.I.M.B. clinic.

Usage:
    python dxhr_tym_shuttle_fix.py <save file or save folder>

  <save file>    e.g. Steam/userdata/<id>/238010/remote/GAMER23_4
  <save folder>  that "remote" folder; the newest save in it is used

Close the game first. Backups (.bak-<time>) of the save and of "saveindex"
are written next to them before anything is changed.
Python 3 standard library only. Tested on the Steam Director's Cut only.
"""
import os
import shutil
import struct
import sys
import time
import zlib

CHOOSER_UID = 0xC0C8      # Hengsha scenario chooser (sha_city__masterunit)
PART1_DONE = 0x139C       # its "Part 1 done" sticky flag
INDEX_RECORD = 53         # saveindex: name[33], u32 size, u64 time, u32, u32


def pick_save(path):
    if os.path.isfile(path):
        return path
    saves = [os.path.join(path, f) for f in os.listdir(path)
             if f.startswith("GAME") and "." not in f
             and os.path.isfile(os.path.join(path, f))]
    if not saves:
        sys.exit("No GAME* save files found in %s" % path)
    return max(saves, key=os.path.getmtime)


def main():
    if len(sys.argv) != 2:
        sys.exit(__doc__)
    save = pick_save(sys.argv[1])
    folder, name = os.path.split(os.path.abspath(save))
    index = os.path.join(folder, "saveindex")
    if not os.path.isfile(index):
        sys.exit("saveindex not found next to %s" % save)

    raw = open(save, "rb").read()
    try:
        data = bytearray(zlib.decompress(raw))
    except zlib.error:
        sys.exit("%s is not a DXHR DC save (not zlib data)" % name)

    tag = struct.pack("<II", CHOOSER_UID, PART1_DONE)
    hits, i = [], data.find(tag)
    while i >= 0:
        if data[i + 8] == 1:
            hits.append(i + 8)
        i = data.find(tag, i + 1)
    if not hits:
        sys.exit("%s: the Part 1 flag is not set (or this is not a Hengsha "
                 "save). Nothing changed." % name)

    idx = bytearray(open(index, "rb").read())
    count = struct.unpack_from("<I", idx, 0)[0]
    slot = None
    for k in range(count):
        o = 4 + INDEX_RECORD * k
        if idx[o:o + 33].split(b"\0")[0].decode("latin1") == name:
            slot = o
    if slot is None:
        sys.exit("%s is not listed in saveindex. Nothing changed." % name)

    stamp = time.strftime("%Y%m%d-%H%M%S")
    shutil.copy2(save, save + ".bak-" + stamp)
    shutil.copy2(index, index + ".bak-" + stamp)

    for off in hits:
        data[off] = 0
    packed = zlib.compress(bytes(data), 6)   # same settings the game uses
    assert zlib.decompress(packed) == bytes(data)
    struct.pack_into("<I", idx, slot + 33, len(packed))
    open(save, "wb").write(packed)
    open(index, "wb").write(bytes(idx))

    print("Fixed %s: cleared %d copies of the Part 1 flag." % (name, len(hits)))
    print("Backups: %s.bak-%s and saveindex.bak-%s" % (name, stamp, stamp))
    print("Now: load this save, walk into the L.I.M.B. clinic and back out,")
    print("then go to the TYM station and ride the shuttle in the same session.")


if __name__ == "__main__":
    main()
