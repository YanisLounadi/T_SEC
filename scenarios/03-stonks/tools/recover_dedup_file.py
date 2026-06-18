#!/usr/bin/env python3
"""Recover a deleted, Data-Deduplication-optimized file from the Windows dedup
ChunkStore, using the $REPARSE_POINT of its (deleted) $MFT record.

Scenario 3 (Stonks) — recovers
  Finance/Reports/Annual/2024/Internal Consolidated Financial Statements 2024.docx
  (MFT entry #46, deleted) -> SHA-256 e51e773e5404f29cc2816cff3fbdcc8b2c28f9e8040a6e7fe926b21336b66513

Key insight: in the dedup container files (.ccc), `Ckhr` is a CHUNK HEADER
(0x58 bytes) and the chunk DATA FOLLOWS it. The stream-map of a file is itself a
chunk: the $REPARSE_POINT stores the stream-map hash; the matching `Ckhr` in the
Stream container is the header, and the `Smap` (chunk list) follows it.

Usage: python3 recover_dedup_file.py <D:_volume_root> <mft_entry> <out_file>
       (D:_volume_root must contain $MFT and System Volume Information/Dedup/...)
"""
import struct, sys, hashlib, glob, os

REC = 1024
CKHR_HDR = 0x58          # Ckhr header length (data follows)
SMAP_HDR = 8             # Smap header length (entries follow)
ENTRY    = 64            # stream-map entry length

def reparse_streammap_hash(mft, entry):
    rec = mft[entry*REC:(entry+1)*REC]
    assert rec[:4] == b'FILE', "not an MFT record"
    a = struct.unpack_from('<H', rec, 20)[0]
    while a < REC-4:
        atype = struct.unpack_from('<I', rec, a)[0]
        if atype == 0xFFFFFFFF: break
        alen = struct.unpack_from('<I', rec, a+4)[0]
        if alen == 0: break
        if atype == 0xC0:                       # $REPARSE_POINT (resident)
            coff = struct.unpack_from('<H', rec, a+20)[0]
            body = rec[a+coff:]                  # ReparseTag(4) Len(2) Resvd(2) Data(N)
            dlen = struct.unpack_from('<H', body, 4)[0]
            # the dedup reparse data ends with the 32-byte stream-map hash + 4-byte CRC
            return body[8 + dlen - 36 : 8 + dlen - 4]
        a += alen
    raise SystemExit("no $REPARSE_POINT on that MFT entry")

def main():
    vol, entry, out = sys.argv[1], int(sys.argv[2]), sys.argv[3]
    mft = open(os.path.join(vol, "$MFT"), "rb").read()
    ddp = glob.glob(os.path.join(vol, "System Volume Information/Dedup/ChunkStore/*.ddp"))[0]
    stream = open(glob.glob(ddp+"/Stream/*.ccc")[0], "rb").read()
    data   = open(glob.glob(ddp+"/Data/*.ccc")[0], "rb").read()

    smhash = reparse_streammap_hash(mft, entry)
    # locate the stream-map's Ckhr header (hash sits 0x38 into the Ckhr header)
    hpos = stream.find(smhash)
    assert hpos >= 0, "stream-map hash not found in Stream container"
    ckhr = hpos - 0x38
    smap = stream.find(b'Smap', ckhr)            # chunk list follows the Ckhr header
    nextc = stream.find(b'Ckhr', smap)
    entries = stream[smap+SMAP_HDR:nextc]
    nchunks = len(entries)//ENTRY
    print(f"[+] stream map @ {hex(smap)} -> {nchunks} chunk(s)")

    out_bytes = b''
    for i in range(nchunks):
        e = entries[i*ENTRY:(i+1)*ENTRY]
        dataoff = struct.unpack_from('<I', e, 8)[0]
        clen    = struct.unpack_from('<Q', e, 56)[0]
        assert data[dataoff:dataoff+4] == b'Ckhr'
        dlen = struct.unpack_from('<I', data, dataoff+12)[0]
        assert dlen == clen, (dlen, clen)
        chunk = data[dataoff+CKHR_HDR:dataoff+CKHR_HDR+dlen]
        print(f"    chunk{i}: off={hex(dataoff)} len={dlen}")
        out_bytes += chunk

    open(out, "wb").write(out_bytes)
    print(f"[+] wrote {len(out_bytes)} bytes -> {out}")
    print(f"[+] SHA-256: {hashlib.sha256(out_bytes).hexdigest()}")

if __name__ == "__main__":
    main()
