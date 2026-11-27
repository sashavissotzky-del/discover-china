// Width of a WebP file, read from its header (no extra packages needed).
import { readFileSync } from 'node:fs';

const cache = new Map<string, number>();

export default function sizeOf(path: string): number {
  if (cache.has(path)) return cache.get(path)!;
  let w = 0;
  try {
    const b = readFileSync(path);
    const kind = b.toString('ascii', 12, 16);
    if (kind === 'VP8 ') w = b.readUInt16LE(26) & 0x3fff;
    else if (kind === 'VP8L') w = 1 + (((b[22] & 0x3f) << 8) | b[21]);
    else if (kind === 'VP8X') w = 1 + b.readUIntLE(24, 3);
  } catch {}
  cache.set(path, w);
  return w;
}
