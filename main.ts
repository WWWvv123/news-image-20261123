import { copyFileSync, existsSync, mkdirSync, readFileSync, statSync } from "node:fs";
import { dirname, join } from "node:path";
import { fileURLToPath } from "node:url";

const MAX_BYTES = 1024 * 1024;
const EXPECTED_SIZE = 1024;

function fail(message: string): never {
  console.error(`main.ts: ${message}`);
  process.exit(1);
}

function main(): void {
  const outDir = process.env.MAKEFUN_OUTPUT_DIR;
  if (!outDir) {
    fail("MAKEFUN_OUTPUT_DIR is not set");
  }

  const here = dirname(fileURLToPath(import.meta.url));
  const source = join(here, "entry.png");
  if (!existsSync(source)) {
    fail(`entry.png not found next to main.ts (${source})`);
  }

  mkdirSync(outDir, { recursive: true });
  const target = join(outDir, "entry.png");
  copyFileSync(source, target);

  const bytes = readFileSync(target);
  if (bytes.length > MAX_BYTES) {
    fail(`entry.png is ${bytes.length} bytes, over the 1 MiB limit`);
  }
  if (
    bytes.length < 33 ||
    bytes[0] !== 0x89 ||
    bytes[1] !== 0x50 ||
    bytes[2] !== 0x4e ||
    bytes[3] !== 0x47
  ) {
    fail("entry.png is not a PNG file");
  }
  const width = bytes.readUInt32BE(16);
  const height = bytes.readUInt32BE(20);
  const chunkType = bytes.toString("ascii", 12, 16);
  if (chunkType !== "IHDR") {
    fail(`entry.png first chunk is ${chunkType}, expected IHDR`);
  }
  if (width !== EXPECTED_SIZE || height !== EXPECTED_SIZE) {
    fail(`entry.png is ${width}x${height}, expected 1024x1024`);
  }

  const size = statSync(target).size;
  console.log(`main.ts: wrote ${target} (${size} bytes, 1024x1024 PNG)`);
}

main();
