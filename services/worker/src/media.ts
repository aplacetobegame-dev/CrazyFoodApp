export type PreparedPhoto = { bytes: Uint8Array; contentType: "image/jpeg" | "image/png" | "image/webp" };

const MAX_DIMENSION = 8000;

function concat(parts: Uint8Array[]): Uint8Array {
  const size = parts.reduce((sum, part) => sum + part.byteLength, 0);
  const out = new Uint8Array(size);
  let offset = 0;
  for (const part of parts) {
    out.set(part, offset);
    offset += part.byteLength;
  }
  return out;
}

function u16be(bytes: Uint8Array, offset: number): number {
  return ((bytes[offset] ?? 0) << 8) | (bytes[offset + 1] ?? 0);
}

function u32be(bytes: Uint8Array, offset: number): number {
  return (u16be(bytes, offset) << 16) | u16be(bytes, offset + 2);
}

function u32le(bytes: Uint8Array, offset: number): number {
  return (bytes[offset] ?? 0) | ((bytes[offset + 1] ?? 0) << 8) | ((bytes[offset + 2] ?? 0) << 16) | ((bytes[offset + 3] ?? 0) << 24);
}

function withinLimits(width: number, height: number): boolean {
  return width > 0 && height > 0 && width <= MAX_DIMENSION && height <= MAX_DIMENSION;
}

function stripJpeg(bytes: Uint8Array): PreparedPhoto | { error: string } {
  if (bytes[0] !== 0xff || bytes[1] !== 0xd8) return { error: "invalid_image" };
  const parts: Uint8Array[] = [bytes.subarray(0, 2)];
  let offset = 2;
  let width = 0;
  let height = 0;
  while (offset + 1 < bytes.length) {
    if (bytes[offset] !== 0xff) return { error: "invalid_image" };
    while (bytes[offset] === 0xff) offset += 1;
    const marker = bytes[offset] ?? 0;
    offset += 1;
    if (marker === 0xd9) break;
    if (marker === 0xda) {
      parts.push(Uint8Array.of(0xff, marker), bytes.subarray(offset));
      break;
    }
    if (offset + 2 > bytes.length) return { error: "invalid_image" };
    const length = u16be(bytes, offset);
    if (length < 2 || offset + length > bytes.length) return { error: "invalid_image" };
    const frame = marker >= 0xc0 && marker <= 0xcf && ![0xc4, 0xc8, 0xcc].includes(marker);
    if (frame) {
      height = u16be(bytes, offset + 3);
      width = u16be(bytes, offset + 5);
    }
    if (marker < 0xe0 || marker > 0xef) {
      parts.push(Uint8Array.of(0xff, marker), bytes.subarray(offset, offset + length));
    }
    offset += length;
  }
  if (!withinLimits(width, height)) return { error: "dimensions" };
  return { bytes: concat(parts), contentType: "image/jpeg" };
}

function stripPng(bytes: Uint8Array): PreparedPhoto | { error: string } {
  const signature = [137, 80, 78, 71, 13, 10, 26, 10];
  if (signature.some((value, index) => bytes[index] !== value)) return { error: "invalid_image" };
  const parts: Uint8Array[] = [bytes.subarray(0, 8)];
  let offset = 8;
  let width = 0;
  let height = 0;
  const drop = new Set(["tEXt", "zTXt", "iTXt", "eXIf", "tIME"]);
  while (offset + 12 <= bytes.length) {
    const length = u32be(bytes, offset);
    const type = String.fromCharCode(bytes[offset + 4] ?? 0, bytes[offset + 5] ?? 0, bytes[offset + 6] ?? 0, bytes[offset + 7] ?? 0);
    const end = offset + 12 + length;
    if (end > bytes.length) return { error: "invalid_image" };
    if (type === "IHDR") {
      width = u32be(bytes, offset + 8);
      height = u32be(bytes, offset + 12);
    }
    if (!drop.has(type)) parts.push(bytes.subarray(offset, end));
    offset = end;
    if (type === "IEND") break;
  }
  if (!withinLimits(width, height)) return { error: "dimensions" };
  return { bytes: concat(parts), contentType: "image/png" };
}

function stripWebp(bytes: Uint8Array): PreparedPhoto | { error: string } {
  const tag = (offset: number) => String.fromCharCode(...bytes.subarray(offset, offset + 4));
  if (tag(0) !== "RIFF" || tag(8) !== "WEBP") return { error: "invalid_image" };
  const parts: Uint8Array[] = [bytes.subarray(0, 12)];
  let offset = 12;
  let width = 0;
  let height = 0;
  while (offset + 8 <= bytes.length) {
    const type = tag(offset);
    const size = u32le(bytes, offset + 4);
    const end = offset + 8 + size + (size % 2);
    if (end > bytes.length) return { error: "invalid_image" };
    if (type === "VP8X" && size >= 10) {
      width = 1 + (bytes[offset + 12] ?? 0) + ((bytes[offset + 13] ?? 0) << 8) + ((bytes[offset + 14] ?? 0) << 16);
      height = 1 + (bytes[offset + 15] ?? 0) + ((bytes[offset + 16] ?? 0) << 8) + ((bytes[offset + 17] ?? 0) << 16);
    }
    if (type === "VP8 " && size >= 10) {
      width = (bytes[offset + 14] ?? 0) | (((bytes[offset + 15] ?? 0) & 0x3f) << 8);
      height = (bytes[offset + 16] ?? 0) | (((bytes[offset + 17] ?? 0) & 0x3f) << 8);
    }
    if (type !== "EXIF" && type !== "XMP ") parts.push(bytes.subarray(offset, end));
    offset = end;
  }
  if (!withinLimits(width, height)) return { error: "dimensions" };
  const output = concat(parts);
  const size = output.length - 8;
  output[4] = size & 0xff;
  output[5] = (size >> 8) & 0xff;
  output[6] = (size >> 16) & 0xff;
  output[7] = (size >> 24) & 0xff;
  return { bytes: output, contentType: "image/webp" };
}

export function prepareCookedPhoto(bytes: Uint8Array): PreparedPhoto | { error: string } {
  if (bytes.byteLength === 0 || bytes.byteLength > 10 * 1024 * 1024) return { error: "file_size" };
  if (bytes[0] === 0xff && bytes[1] === 0xd8) return stripJpeg(bytes);
  if (bytes[0] === 137 && bytes[1] === 80) return stripPng(bytes);
  if (bytes[0] === 0x52 && bytes[1] === 0x49) return stripWebp(bytes);
  return { error: "invalid_image" };
}

export async function renderStillClip(photo: Uint8Array): Promise<Uint8Array> {
  const { spawn } = await import("node:child_process");
  const { mkdtemp, readFile, rm, writeFile } = await import("node:fs/promises");
  const { tmpdir } = await import("node:os");
  const { join } = await import("node:path");
  const dir = await mkdtemp(join(tmpdir(), "ff-clip-"));
  const input = join(dir, "photo.jpg");
  const output = join(dir, "clip.mp4");
  try {
    await writeFile(input, photo);
    await new Promise<void>((resolve, reject) => {
      const child = spawn("ffmpeg", [
        "-y", "-loop", "1", "-i", input, "-t", "4",
        "-vf", "scale=720:1280:force_original_aspect_ratio=decrease,pad=720:1280:(ow-iw)/2:(oh-ih)/2,format=yuv420p",
        "-c:v", "libx264", "-pix_fmt", "yuv420p", "-movflags", "+faststart", output,
      ], { stdio: "ignore" });
      child.on("error", reject);
      child.on("exit", (code) => (code === 0 ? resolve() : reject(new Error(`ffmpeg exited ${code}`))));
    });
    return new Uint8Array(await readFile(output));
  } finally {
    await rm(dir, { recursive: true, force: true });
  }
}
