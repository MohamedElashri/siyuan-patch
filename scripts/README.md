# Patch Generator Scripts

This directory contains automated tooling to generate and verify `patches/siyuan/math-renderer-registry.patch` against official SiYuan releases.

## Quick Start

To generate and verify the patch against the current version (default: `v3.8.8`):

```bash
python3 scripts/generate-patch.py
```

To target a specific release:

```bash
python3 scripts/generate-patch.py --version v3.8.9
```

## How It Works

1. Downloads the pristine SiYuan source archive for the requested release tag.
2. Applies the pluggable math renderer registry files:
   - `app/src/protyle/render/mathRendererRegistry.ts` (Registry interface & implementation)
   - `app/src/protyle/render/mathBoundaries.ts` (Cursor boundary handling for inline math)
   - `app/src/protyle/render/mathRender.ts` (Pre-KaTeX synchronous claim pass + fallback + export baking)
3. Modifies SiYuan integration points using unique string anchors with assertion checks:
   - `app/src/plugin/index.ts` (Exposes `registerMathRenderer` / `unregisterMathRenderer` on `Plugin`)
   - `app/src/plugin/uninstall.ts` (Automatically unregisters plugin renderers during teardown)
   - `app/src/protyle/export/index.ts` (Pre-bakes formulas into self-contained SVGs for HTML and PDF exports)
4. Validates the resulting git diff with `git apply --check` and outputs `patches/siyuan/math-renderer-registry.patch`.
