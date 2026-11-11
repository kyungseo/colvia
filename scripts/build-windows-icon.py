"""Offline, source-only COFF icon resource generator; no runtime dependencies."""
import argparse
from pathlib import Path
import struct

MACHINES = {"amd64": (0x8664, 3), "arm64": (0xAA64, 2)}
SIZES = (16, 20, 24, 32, 40, 48, 64, 256)


def icon_images(raw):
    if len(raw) < 6 or struct.unpack_from("<HHH", raw) != (0, 1, len(SIZES)):
        raise ValueError("expected the complete Colvia ICO directory")
    images, end = [], 6 + 16 * len(SIZES)
    for i, size in enumerate(SIZES):
        entry = raw[6 + 16*i:22 + 16*i]
        w, h, colors, reserved, planes, bits, length, offset = struct.unpack("<BBBBHHII", entry)
        if ((w or 256, h or 256) != (size, size) or colors or reserved or planes != 1 or bits != 32 or
                offset != end or length < 33 or offset + length > len(raw)):
            raise ValueError("invalid, unordered or overlapping ICO image")
        data = raw[offset:offset+length]
        if (data[:8] != b"\x89PNG\r\n\x1a\n" or data[12:16] != b"IHDR" or
                struct.unpack_from(">II", data, 16) != (size, size)):
            raise ValueError("ICO directory does not match PNG dimensions")
        images.append((entry[:8], data)); end += length
    if end != len(raw):
        raise ValueError("unexpected ICO trailing bytes")
    return images


def resource_object(raw, architecture):
    machine, relocation_type = MACHINES[architecture]
    images = icon_images(raw)
    group = struct.pack("<HHH", 0, 1, len(images)) + b"".join(
        entry + struct.pack("<IH", len(data), i) for i, (entry, data) in enumerate(images, 1))
    # type -> ID -> neutral-language -> payload. One .rsrc section, no manifest.
    tree = {3: {i: {0: data} for i, (_, data) in enumerate(images, 1)}, 14: {101: {0: group}}}
    section = bytearray(); leaves = []; relocations = []

    def directory(node):
        start = len(section)
        section.extend(struct.pack("<IIHHHH", 0, 0, 0, 0, 0, len(node)))
        section.extend(bytes(8 * len(node)))
        for i, (key, value) in enumerate(sorted(node.items())):
            at = start + 16 + i*8
            if isinstance(value, dict):
                target = directory(value) | 0x80000000
            else:
                target = len(section); section.extend(bytes(16)); leaves.append((target, value))
            struct.pack_into("<II", section, at, key, target)
        return start

    directory(tree)
    for entry, data in leaves:
        section.extend(bytes((-len(section)) % 4))
        offset = len(section); section.extend(data)
        struct.pack_into("<IIII", section, entry, offset, len(data), 0, 0)
        relocations.append(struct.pack("<IIH", entry, 0, relocation_type))
    section.extend(bytes((-len(section)) % 4))
    rel = b"".join(relocations)
    symbol_offset = 60 + len(section) + len(rel)
    header = struct.pack("<HHIIIHH", machine, 1, 0, symbol_offset, 1, 0, 0)
    sh = struct.pack("<8sIIIIIIHHI", b".rsrc", 0, 0, len(section), 60,
                     60 + len(section), 0, len(relocations), 0, 0x40300040)
    symbol = struct.pack("<8sIhHBB", b".rsrc", 0, 1, 0, 3, 0)
    return header + sh + section + rel + symbol + struct.pack("<I", 4)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--icon", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    args.output.mkdir(parents=True, exist_ok=True)
    for architecture in MACHINES:
        (args.output / f"rsrc_windows_{architecture}.syso").write_bytes(resource_object(args.icon.read_bytes(), architecture))
