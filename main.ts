// Entry point for the news-image-20261120 competition.
//
// Copies the pre-drawn front page (entry.png, produced by draw.py in
// this same repository) into the output directory the grader provides.
// Node standard library only; no network, no writes outside the
// output directory.
import { copyFileSync, mkdirSync } from "node:fs";
import { join } from "node:path";
import { fileURLToPath } from "node:url";

// The grader runs this program twice and requires byte-identical
// output both times, so this is a plain copy: no timestamps, no
// randomness, nothing is generated at run time.
const here = fileURLToPath(new URL(".", import.meta.url));
const outDir = process.env.MAKEFUN_OUTPUT_DIR ?? "/output";

mkdirSync(outDir, { recursive: true });
copyFileSync(join(here, "entry.png"), join(outDir, "entry.png"));
