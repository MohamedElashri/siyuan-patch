# Patch Inventory and Architecture

This repository maintains a curated patch set applied to official [SiYuan Note](https://github.com/siyuan-note/siyuan) release tags via `git apply`. Builds are published for Desktop (Windows, macOS, Linux), Docker, iOS, and Android via GitHub Actions workflows.

---

## 1. Patches Summary

| Patch File | Purpose | Target Platforms | Description |
| :--- | :--- | :--- | :--- |
| `patches/siyuan/disable-update.patch` | Disable auto-update checks | All | Disables SiYuan's built-in update notifications. |
| `patches/siyuan/default-config.patch` | Default configuration adjustment | All | Adjusts default application settings. |
| `patches/siyuan/mock-vip-user.patch` | Unlock subscription features | All | Unlocks features (e.g. S3/WebDAV data sync). |
| `patches/siyuan/docker-build.patch` | Docker build and OCR validation | Docker | Adapts Dockerfile and verifies OCR runtime on Alpine runners. |
| **`patches/siyuan/math-renderer-registry.patch`** | **Pluggable Math Formula Renderer Registry** | **All (Desktop, Docker, Mobile)** | **Enables plugins to claim formulas before KaTeX, adds pre-baking for HTML & PDF exports, and manages plugin lifecycle.** |
| `patches/siyuan-ios/build-failed.patch` | iOS compilation fix | iOS | Resolves Xcode/iOS toolchain build issues. |
| `patches/siyuan-ios/text-menu-availability.patch` | iOS menu availability fix | iOS | Fixes text context menu behavior on iOS. |
| `patches/siyuan-android/debug-build.patch` | Android build customization | Android | Adjusts Gradle and build configuration. |

---

## 2. Pluggable Math Renderer Registry (`math-renderer-registry.patch`)

### Overview
By default, SiYuan Note exclusively uses KaTeX to render LaTeX formulas across all ~20 render sites in the Protyle editor and export pipelines.

The `math-renderer-registry.patch` provides a **generic, lightweight extension point** that allows third-party plugins (such as [siyuan-typst-plugin](https://github.com/LeonhardtHUST/siyuan-typst-plugin)) to render formulas using alternative engines (e.g., **Typst WASM**, MathJax, AsciiMath) without hardcoding engine-specific logic into SiYuan core.

### Key Capabilities and Improvements

1. **Synchronous Pre-KaTeX Claiming (Zero KaTeX Overhead)**:
   * During the synchronous pass of `mathRender(element)` in `app/src/protyle/render/mathRender.ts`, every unrendered `[data-subtype="math"]` node is presented to registered custom renderers via `canRender(context)`.
   * If a renderer claims the node, the node is marked `data-render="true"` and excluded from the KaTeX queue.
   * If all math nodes are claimed, **KaTeX's JS and CSS files are never requested or loaded at all**.

2. **Clean DOM Restoration and Fallback**:
   * Custom renderers execute asynchronously via `render(context): Promise<boolean | void>`.
   * If a custom renderer returns `false` or throws an error, the initial DOM state is restored and the element gracefully falls back to KaTeX in the same render pass.

3. **Universal Export Pre-baking (`bakeMathInHtml`)**:
   * Electron PDF preview windows and exported HTML run in isolated environments without plugin runtimes.
   * `bakeMathInHtml()` pre-renders formulas in the main window into self-contained inline SVGs, flattening any Shadow DOM boundaries.
   * Marked with `data-math-baked="true"` so PDF preview re-renders do not overwrite custom formulas. (Unlike naive `<svg>` matching, this avoids false positives with native KaTeX formulas containing square roots or delimiters).

4. **Automatic Plugin Lifecycle Management**:
   * When a plugin is uninstalled, disabled, or reloaded, `beginPluginTeardown()` in `app/src/plugin/uninstall.ts` automatically unregisters all math renderers registered by that plugin (`unregisterMathRenderersByPrefix(`${plugin.name}/`)`), preventing memory leaks and stale closures.

5. **Priority Ordering**:
   * Renderers can specify an optional `priority?: number` (higher numbers evaluated first).

---

### Plugin API Specification

#### Types
```typescript
export interface IMathRenderContext {
    /** Target DOM element: div[data-subtype="math"] (block) or span[data-subtype="math"] (inline) */
    element: HTMLElement;
    /** Raw data-content (as stored in SiYuan) */
    mathContent: string;
    /** Unescaped math text (if available) */
    text?: string;
    /** True if block-level math (div), false if inline math (span) */
    isBlock: boolean;
    /** True if width constraint should be adapted (e.g. PDF export) */
    maxWidth: boolean;
    /** Reusable helper to insert cursor boundary zero-width spaces for inline math */
    applyInlineMathBoundaries: () => void;
}

export interface IMathRenderer {
    /** Synchronous check to claim this math node */
    canRender: (context: IMathRenderContext) => boolean;
    /** Asynchronous render; return false or throw to trigger fallback to KaTeX */
    render: (context: IMathRenderContext) => Promise<boolean | void>;
    /** Optional export baking hook; if omitted, generic shadow DOM / SVG flattening is applied */
    bake?: (context: IMathRenderContext) => Promise<boolean | void>;
    /** Priority (higher numbers checked first, default 0) */
    priority?: number;
}
```

#### Plugin Usage Example (e.g. Typst Plugin)
```typescript
import { Plugin } from "siyuan";

export default class TypstPlugin extends Plugin {
    onload() {
        // Feature detection: Safe to run on official SiYuan (falls back gracefully)
        if (typeof (this as any).registerMathRenderer === "function") {
            (this as any).registerMathRenderer("typst", {
                priority: 10,
                canRender: (ctx) => {
                    // Check for Typst prefix or document typst-math attribute
                    return ctx.mathContent.startsWith("\\t") || Boolean(ctx.element.closest("[data-typst-math]"));
                },
                render: async (ctx) => {
                    const code = ctx.mathContent.startsWith("\\t") ? ctx.mathContent.slice(2) : ctx.mathContent;
                    const svg = await renderTypstToSvg(code);
                    if (!svg) return false; // Fallback to KaTeX if rendering fails

                    ctx.element.innerHTML = svg;
                    if (!ctx.isBlock) {
                        ctx.applyInlineMathBoundaries();
                    }
                    return true;
                }
            });
        }
    }
}
```

---

## 3. Patch Maintenance and Automation

To regenerate or verify `patches/siyuan/math-renderer-registry.patch` when updating SiYuan:

```bash
# Generate patch for latest target release (e.g. v3.8.8)
python3 scripts/generate-patch.py --version v3.8.8
```

The script automatically fetches the pristine source, applies modifications with strict anchor assertions, checks diffs with `git apply --check`, and outputs the updated patch.
