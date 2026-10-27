#!/usr/bin/env python3
"""
generate-patch.py: Generates and verifies patches/siyuan/math-renderer-registry.patch
against an official SiYuan release tag.

Usage:
  python3 scripts/generate-patch.py [--version v3.8.8] [--output patches/siyuan/math-renderer-registry.patch]
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

TS_MATH_REGISTRY = """/**
 * Math formula renderer registry (mathRendererRegistry)
 *
 * Allows plugins to claim formula rendering before KaTeX runs.
 * - canRender: synchronous, lightweight claim check before KaTeX JS/CSS are loaded.
 * - render: asynchronous render execution. Returns boolean (false triggers KaTeX fallback) or throws error.
 * - bake: optional export baking hook to serialize custom formula to static HTML/SVG.
 * - priority: optional priority ordering (higher priority renderers are checked first, default 0).
 */

export interface IMathRenderContext {
    /** Target DOM element: div[data-subtype="math"] (block) or span[data-subtype="math"] (inline) */
    element: HTMLElement;
    /** Raw data-content (same as KaTeX input) */
    mathContent: string;
    /** Unescaped math expression if available */
    text?: string;
    /** Whether this is a block formula (DIV) or inline formula (SPAN) */
    isBlock: boolean;
    /** Whether width adaptation is requested (e.g. for PDF export) */
    maxWidth: boolean;
    /**
     * Helper to apply native cursor boundary zero-width spaces/newlines for inline math.
     * Can be invoked by custom renderers after setting inner HTML to ensure standard caret movement.
     */
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

interface IRegisteredRenderer {
    id: string;
    renderer: IMathRenderer;
    priority: number;
}

const renderers: IRegisteredRenderer[] = [];

/**
 * Register a math renderer. Re-registering with the same ID replaces the previous renderer.
 */
export const registerMathRenderer = (id: string, renderer: IMathRenderer) => {
    const priority = typeof renderer.priority === "number" ? renderer.priority : 0;
    const index = renderers.findIndex(item => item.id === id);
    if (index > -1) {
        renderers[index] = {id, renderer, priority};
    } else {
        renderers.push({id, renderer, priority});
    }
    renderers.sort((a, b) => b.priority - a.priority);
};

/**
 * Unregister a math renderer by ID.
 */
export const unregisterMathRenderer = (id: string) => {
    const index = renderers.findIndex(item => item.id === id);
    if (index > -1) {
        renderers.splice(index, 1);
    }
};

/**
 * Unregister all math renderers whose ID starts with the specified prefix (e.g. "pluginName/").
 */
export const unregisterMathRenderersByPrefix = (prefix: string) => {
    for (let i = renderers.length - 1; i >= 0; i--) {
        if (renderers[i].id.startsWith(prefix)) {
            renderers.splice(i, 1);
        }
    }
};

/**
 * Find the highest priority renderer that claims the node.
 */
export const findMathRenderer = (context: IMathRenderContext): IMathRenderer | undefined => {
    for (const item of renderers) {
        try {
            if (item.renderer.canRender(context)) {
                return item.renderer;
            }
        } catch (error) {
            console.warn(`[mathRendererRegistry] Renderer [${item.id}] canRender failed:`, error);
        }
    }
    return undefined;
};

/**
 * Retrieve a registered renderer by ID.
 */
export const getMathRenderer = (id: string): IMathRenderer | undefined => {
    return renderers.find(item => item.id === id)?.renderer;
};
"""

TS_MATH_BOUNDARIES = """import {hasNextSibling, hasPreviousSibling} from "../wysiwyg/getBlock";
import {Constants} from "../../constants";

/**
 * Handle cursor boundary characters after inline math rendering.
 * Keeps cursor navigation, deletion, and selection identical to native SiYuan.
 */
export const applyInlineMathBoundaries = (mathElement: HTMLElement) => {
    const parentTagName = mathElement.parentElement?.tagName || "";
    const nextSibling = hasNextSibling(mathElement) as HTMLElement;
    if (!nextSibling) {
        // Table cell cursor handling https://ld246.com/article/1629191424824
        if (parentTagName !== "TH" && parentTagName !== "TD") {
            // Cannot move cursor to end https://github.com/siyuan-note/siyuan/issues/2112
            mathElement.insertAdjacentText("afterend", "\\n");
        } else {
            mathElement.insertAdjacentText("afterend", Constants.ZWSP);
        }
    } else if (nextSibling && nextSibling.nodeType !== 3 &&
        (
            nextSibling.getAttribute("data-type")?.indexOf("inline-math") > -1 ||
            nextSibling.classList.contains("img")
        )) {
        // Adjacent math formula cursor movement / deletion
        mathElement.after(document.createTextNode(Constants.ZWSP));
    } else if (nextSibling &&
        !/^[\\u200B\\uFEFF]*\\n/.test(nextSibling.textContent) &&
        nextSibling.textContent !== Constants.ZWSP) {
        // Extra br on deleting character after math formula https://ld246.com/article/1647157880974
        mathElement.insertAdjacentHTML("beforeend", "&#xFEFF;");
    }
    // Cannot move cursor to start of paragraph https://ld246.com/article/1623551823742
    if (mathElement.previousSibling?.textContent.endsWith("\\n")) {
        mathElement.insertAdjacentText("beforebegin", Constants.ZWSP);
    } else if (!hasPreviousSibling(mathElement) && ["TH", "TD"].includes(parentTagName)) {
        mathElement.insertAdjacentText("afterbegin", Constants.ZWSP);
    } else if (!hasPreviousSibling(mathElement)) {
        mathElement.insertAdjacentText("beforebegin", Constants.ZWSP);
    }
};
"""

TS_MATH_RENDER = """import {addScript} from "../util/addScript";
import {addStyle} from "../util/addStyle";
import {Constants} from "../../constants";
import {hasClosestBlock} from "../util/hasClosest";
import {looseJsonParse} from "../../util/functions";
import {genRenderFrame} from "./util";
import {getHostCapabilities} from "../../util/hostCapabilities";
import {getMathRenderSecurity} from "./mathRenderSecurity";
import {isFoldedRenderContent} from "./foldedContent";
import {applyInlineMathBoundaries} from "./mathBoundaries";
import {findMathRenderer, IMathRenderContext, IMathRenderer} from "./mathRendererRegistry";

const fitMathWidth = (mathElement: HTMLElement, blockElement: HTMLElement | false, isBlock: boolean) => {
    return new Promise<void>((resolve) => {
        setTimeout(() => {
            if (isBlock) {
                const katexElement = mathElement.querySelector(".katex-display") as HTMLElement;
                if (katexElement && katexElement.clientWidth < katexElement.scrollWidth) {
                    katexElement.firstElementChild?.setAttribute("style", `font-size:${katexElement.clientWidth * 100 / katexElement.scrollWidth}%`);
                }
            } else if (blockElement && mathElement.offsetWidth > blockElement.clientWidth) {
                mathElement.firstElementChild?.setAttribute("style", `font-size:${blockElement.clientWidth * 100 / mathElement.offsetWidth}%`);
            }
            resolve();
        });
    });
};

export const mathRender = (element: Element, cdn = Constants.PROTYLE_CDN, maxWidth = false) => {
    const mathElements = (element.getAttribute("data-subtype") === "math" ?
        [element] : Array.from(element.querySelectorAll('[data-subtype="math"]')))
        .filter(item => !isFoldedRenderContent(item));
    if (mathElements.length === 0) {
        return;
    }

    // Synchronous claim phase: evaluate registered custom renderers before KaTeX CSS/JS are loaded.
    const claimedMathElements: {
        element: HTMLElement;
        renderer: IMathRenderer;
        context: IMathRenderContext;
        initialHTML: string;
    }[] = [];
    const unrenderedMathElements: HTMLElement[] = [];

    mathElements.forEach((mathElement: HTMLElement) => {
        if (mathElement.getAttribute("data-render") === "true") {
            return;
        }
        const rawContent = mathElement.getAttribute("data-content") || "";
        const context: IMathRenderContext = {
            element: mathElement,
            mathContent: rawContent,
            text: typeof (window as any).Lute !== "undefined" && (window as any).Lute.UnEscapeHTMLStr ?
                (window as any).Lute.UnEscapeHTMLStr(rawContent) : undefined,
            isBlock: mathElement.tagName === "DIV",
            maxWidth,
            applyInlineMathBoundaries: () => applyInlineMathBoundaries(mathElement),
        };
        const renderer = findMathRenderer(context);
        if (renderer) {
            mathElement.setAttribute("data-render", "true");
            claimedMathElements.push({
                element: mathElement,
                renderer,
                context,
                initialHTML: mathElement.innerHTML,
            });
        } else {
            unrenderedMathElements.push(mathElement);
        }
    });

    if (unrenderedMathElements.length === 0 && claimedMathElements.length === 0) {
        return;
    }

    const katexPass = (targets: HTMLElement[]) => {
        if (targets.length === 0) {
            return Promise.resolve();
        }
        addStyle(`${cdn}/js/katex/katex.min.css?v=0.19.0`, "protyleKatexStyle");
        return addScript(`${cdn}/js/katex/katex.min.js?v=0.19.0`, "protyleKatexScript").then(() => {
            return addScript(`${cdn}/js/katex/mhchem.min.js?v=0.19.0`, "protyleKatexMhchemScript").then(() => {
                const resizePromises: Promise<void>[] = [];
                targets.forEach((mathElement: HTMLElement) => {
                    mathElement.setAttribute("data-render", "true");
                    let macros = {};
                    try {
                        macros = looseJsonParse(window.siyuan.config.editor.katexMacros || "{}");
                    } catch (e) {
                        console.warn("KaTex macros is not JSON", e);
                    }
                    const isBlock = mathElement.tagName === "DIV";
                    const remoteKernel = getHostCapabilities().remoteKernel;
                    const security = getMathRenderSecurity(remoteKernel,
                        Boolean(mathElement.closest('[data-protyle-lite-render="safe"]')));
                    try {
                        let mathHTML = window.katex.renderToString(Lute.UnEscapeHTMLStr(mathElement.getAttribute("data-content")), {
                            displayMode: isBlock,
                            output: "html",
                            macros,
                            trust: security.trust, // REF: https://katex.org/docs/supported#html
                            strict: (errorCode) => errorCode === "unicodeTextInMathMode" ? "ignore" : "warn",
                        });
                        if (security.sanitize) {
                            mathHTML = window.DOMPurify.sanitize(mathHTML);
                        }
                        const blockElement = hasClosestBlock(mathElement);
                        if (isBlock) {
                            genRenderFrame(mathElement);
                            mathElement.firstElementChild.firstElementChild.classList.remove("ft__error");
                            mathElement.firstElementChild.firstElementChild.setAttribute("contenteditable", "false");
                            mathElement.firstElementChild.firstElementChild.innerHTML = mathHTML;
                            // https://github.com/siyuan-note/siyuan/issues/3541
                            const baseElements = mathElement.querySelectorAll(".katex-html > .katex-base");
                            if (baseElements.length > 0) {
                                baseElements[baseElements.length - 1].insertAdjacentHTML("afterend", "<span class='fn__flex-1'></span>");
                            }
                            // https://github.com/siyuan-note/siyuan/issues/4334
                            const newlineElement = mathElement.querySelector(".katex-html > .katex-newline");
                            if (newlineElement) {
                                newlineElement.parentElement.style.display = "block";
                            }
                        } else {
                            mathElement.classList.remove("ft__error");
                            mathElement.innerHTML = mathHTML;
                            if (blockElement && mathElement.getBoundingClientRect().width > blockElement.clientWidth) {
                                mathElement.style.maxWidth = "100%";
                                mathElement.style.overflowX = "auto";
                                mathElement.style.overflowY = "hidden";
                                mathElement.style.display = "inline-block";
                            } else {
                                mathElement.style.maxWidth = "";
                                mathElement.style.overflowX = "";
                                mathElement.style.overflowY = "";
                                mathElement.style.display = "";
                            }
                            applyInlineMathBoundaries(mathElement);
                        }

                        // 导出 PDF 时等待公式完成宽度适配后再继续
                        if (maxWidth) {
                            resizePromises.push(fitMathWidth(mathElement, blockElement, isBlock));
                        }
                    } catch (e) {
                        if (isBlock) {
                            genRenderFrame(mathElement);
                            mathElement.firstElementChild.firstElementChild.setAttribute("contenteditable", "false");
                            mathElement.firstElementChild.firstElementChild.textContent = e.message;
                            mathElement.firstElementChild.firstElementChild.classList.add("ft__error");
                        } else {
                            mathElement.textContent = e.message;
                            mathElement.classList.add("ft__error");
                        }
                    }
                });
                return Promise.all(resizePromises).then((): undefined => undefined);
            });
        });
    };

    // Execute custom renderers asynchronously. If any renderer fails or declines, roll back DOM and fallback to KaTeX.
    const failedMathElements: HTMLElement[] = [];
    const claimedPromise = Promise.all(claimedMathElements.map(item =>
        Promise.resolve().then(() => item.renderer.render(item.context)).then((rendered) => {
            if (rendered === false) {
                throw new Error("Renderer declined");
            }
        }).catch((error) => {
            console.warn("[mathRender] Custom renderer failed, fallback to KaTeX:", error);
            item.element.removeAttribute("data-render");
            item.element.removeAttribute("data-math-baked");
            item.element.innerHTML = item.initialHTML;
            failedMathElements.push(item.element);
        })
    )).then(() => failedMathElements.length > 0 ? katexPass(failedMathElements) : undefined);

    return Promise.all([katexPass(unrenderedMathElements), claimedPromise]).then((): undefined => undefined);
};

/**
 * Helper to recursively flatten any ShadowRoot instances within an element into inline DOM.
 */
const flattenShadowRoots = (root: Node) => {
    if (!root) return;
    const walker = document.createTreeWalker(root, NodeFilter.SHOW_ELEMENT);
    const elementsWithShadow: HTMLElement[] = [];
    let currentNode = walker.currentNode as HTMLElement;
    while (currentNode) {
        if (currentNode.shadowRoot) {
            elementsWithShadow.push(currentNode);
        }
        currentNode = walker.nextNode() as HTMLElement;
    }
    elementsWithShadow.forEach((el) => {
        if (el.shadowRoot) {
            flattenShadowRoots(el.shadowRoot);
            const wrapper = document.createElement("span");
            wrapper.className = "protyle-math__baked";
            wrapper.innerHTML = el.shadowRoot.innerHTML;
            el.replaceWith(wrapper);
        }
    });
};

/**
 * Export baking: Renders math formulas in an HTML fragment into static, self-contained inline SVG/HTML.
 * Ensures HTML exports and Electron PDF preview windows (which run in separate processes without
 * plugin runtimes) can display formulas without external runtimes.
 */
export const bakeMathInHtml = async (html: string) => {
    if (!html || !html.includes('data-subtype="math"')) {
        return html;
    }
    try {
        const container = document.createElement("div");
        container.className = "protyle-wysiwyg";
        container.innerHTML = html;
        const mathElements = Array.from(container.querySelectorAll('[data-subtype="math"]')) as HTMLElement[];
        if (mathElements.length === 0) {
            return html;
        }

        await mathRender(container, Constants.PROTYLE_CDN, true);

        for (const el of mathElements) {
            const context: IMathRenderContext = {
                element: el,
                mathContent: el.getAttribute("data-content") || "",
                text: typeof (window as any).Lute !== "undefined" && (window as any).Lute.UnEscapeHTMLStr ?
                    (window as any).Lute.UnEscapeHTMLStr(el.getAttribute("data-content") || "") : undefined,
                isBlock: el.tagName === "DIV",
                maxWidth: true,
                applyInlineMathBoundaries: () => applyInlineMathBoundaries(el),
            };
            const renderer = findMathRenderer(context);
            if (renderer && typeof renderer.bake === "function") {
                try {
                    await renderer.bake(context);
                } catch (e) {
                    console.warn("[export] Custom renderer bake failed:", e);
                }
            }
            flattenShadowRoots(el);
            el.setAttribute("data-math-baked", "true");
            el.setAttribute("data-render", "true");
        }
        return container.innerHTML;
    } catch (e) {
        console.warn("[export] bake math failed:", e);
        return html;
    }
};

(window as any).__siyuanBakeMathForExport = bakeMathInHtml;
"""

def modify_plugin_index(src_content: str) -> str:
    import_anchor = 'import type {TCustomBlockRender} from "./customBlockRender";\n'
    assert import_anchor in src_content, 'import_anchor not found in plugin/index.ts'
    new_imports = import_anchor + '''import type {IMathRenderer} from "../protyle/render/mathRendererRegistry";
import {
    registerMathRenderer as registerMathRendererRegistry,
    unregisterMathRenderer as unregisterMathRendererRegistry,
} from "../protyle/render/mathRendererRegistry";
'''
    res = src_content.replace(import_anchor, new_imports)

    method_anchor = '''    public uninstall(): Promise<void> | void {
        // 卸载
    }
'''
    assert method_anchor in res, 'method_anchor not found in plugin/index.ts'
    new_methods = method_anchor + '''
    /**
     * 注册数学公式渲染器：在 KaTeX 渲染前认领公式节点。
     * 认领成功后该节点不会触发 KaTeX 的加载与渲染，渲染失败自动回退 KaTeX。
     * @param id 渲染器标识（按插件名自动命名空间化，避免插件间冲突）
     * @param renderer 渲染器实现
     */
    public registerMathRenderer(id: string, renderer: IMathRenderer) {
        registerMathRendererRegistry(`${this.name}/${id}`, renderer);
    }

    /**
     * 注销数学公式渲染器
     * @param id 注册时使用的标识
     */
    public unregisterMathRenderer(id: string) {
        unregisterMathRendererRegistry(`${this.name}/${id}`);
    }
'''
    return res.replace(method_anchor, new_methods)

def modify_plugin_uninstall(src_content: str) -> str:
    u_import_anchor = 'import {isSettingsWindow} from "../config/setting/windowContext";\n'
    assert u_import_anchor in src_content, 'u_import_anchor not found in plugin/uninstall.ts'
    res = src_content.replace(u_import_anchor, u_import_anchor + 'import {unregisterMathRenderersByPrefix} from "../protyle/render/mathRendererRegistry";\n')

    teardown_anchor = '    runCleanup(plugin, "tracked ranges", () => releaseTrackedRangesByPlugin(plugin));\n'
    assert teardown_anchor in res, 'teardown_anchor not found in plugin/uninstall.ts'
    return res.replace(teardown_anchor, teardown_anchor + '    runCleanup(plugin, "math renderers", () => unregisterMathRenderersByPrefix(`${plugin.name}/`));\n')

def modify_export_index(src_content: str) -> str:
    e_import_anchor = 'import {fetchPost, fetchSyncPost} from "../../util/fetch";\n'
    assert e_import_anchor in src_content, 'e_import_anchor not found in export/index.ts'
    res = src_content.replace(e_import_anchor, e_import_anchor + 'import {bakeMathInHtml} from "../render/mathRender";\n')

    e_renderpdf_anchor = """    const html = `<!DOCTYPE html>
<html lang="${window.siyuan.config.appearance.lang}" data-theme-mode="light" data-light-theme="""
    assert res.count(e_renderpdf_anchor) == 1, 'e_renderpdf_anchor not unique'
    renderpdf_inject = """    // 应用内预取导出内容并烘焙公式：Electron 预览窗口是独立进程，无法运行 Typst 渲染器，
    // 因此在主窗口把公式渲染为内联 SVG 后注入预览页。
    let bakedPreviewContent = "";
    try {
        const previewResponse = await new Promise<any>((resolve) => {
            fetchPost("/api/export/exportPreviewHTML", {
                id,
                keepJSEmbed: true,
                keepFold: localData.keepFold,
                pdf: true,
                excludeTitleImage: localData.titleImage === false,
                addTitle: window.siyuan.config.export.addTitle,
                customTitle: "",
                merge: localData.mergeSubdocs,
                mergeDocHeadingMode: localData.mergeDocHeadingMode,
                mergeContentHeadingMode: localData.mergeContentHeadingMode,
            }, (response: any) => resolve(response));
        });
        if (previewResponse && previewResponse.code === 0 && previewResponse.data) {
            bakedPreviewContent = await bakeMathInHtml(previewResponse.data.content);
        }
    } catch (e) {
        console.warn("[export] prefetch preview content failed:", e);
    }
    const html = `<!DOCTYPE html>
<html lang="${window.siyuan.config.appearance.lang}" data-theme-mode="light" data-light-theme="""
    res = res.replace(e_renderpdf_anchor, renderpdf_inject)

    e_preview_anchor = """    const renderPreview = async (data) => {
        previewElement.innerHTML = '<div style="padding:8px 0 0 0" class="protyle-wysiwyg"""
    assert res.count(e_preview_anchor) == 1, 'e_preview_anchor not unique'
    preview_inject = """    const __bakedMathContent = ${JSON.stringify(bakedPreviewContent)};
    const renderPreview = async (data) => {
        if (typeof __bakedMathContent === "string" && __bakedMathContent) {
            data = Object.assign({}, data, {content: __bakedMathContent});
        }
        previewElement.innerHTML = '<div style="padding:8px 0 0 0" class="protyle-wysiwyg"""
    res = res.replace(e_preview_anchor, preview_inject)

    e_skip_anchor = """        previewElement.querySelectorAll('[data-type="NodeMathBlock"]').forEach((item) => {
            // 超级块内不能移除 width https://github.com/siyuan-note/siyuan/issues/14318
            item.removeAttribute('data-render');
        })"""
    assert res.count(e_skip_anchor) == 1, 'e_skip_anchor not unique'
    skip_inject = """        previewElement.querySelectorAll('[data-type="NodeMathBlock"]').forEach((item) => {
            if (item.getAttribute("data-math-baked") === "true" || item.querySelector('[data-math-baked="true"]')) {
                // 已在主窗口烘焙为内联 SVG，保留 data-render 以免被 KaTeX 覆盖
                return;
            }
            // 超级块内不能移除 width https://github.com/siyuan-note/siyuan/issues/14318
            item.removeAttribute('data-render');
        })"""
    res = res.replace(e_skip_anchor, skip_inject)

    e_export_anchor = """    } : {js: "", css: ""};
    const html = `<!DOCTYPE html>"""
    assert res.count(e_export_anchor) == 1, 'e_export_anchor not unique'
    export_inject = """    } : {js: "", css: ""};
    // 数学公式应用内预烘焙（导出产物自包含，不依赖导出端脚本）
    if (data && data.data && typeof data.data.content === "string") {
        data.data.content = await bakeMathInHtml(data.data.content);
    }
    const html = `<!DOCTYPE html>"""
    return res.replace(e_export_anchor, export_inject)

def main():
    parser = argparse.ArgumentParser(description="Generate and verify math-renderer-registry.patch")
    parser.add_argument("--version", default="v3.8.8", help="SiYuan tag to base patch on (default: v3.8.8)")
    parser.add_argument("--output", default="patches/siyuan/math-renderer-registry.patch", help="Output patch file path")
    args = parser.parse_args()

    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    out_path = os.path.join(repo_root, args.output) if not os.path.isabs(args.output) else args.output

    with tempfile.TemporaryDirectory() as tmpdir:
        src_dir = os.path.join(tmpdir, "siyuan-src")
        os.makedirs(src_dir, exist_ok=True)
        print(f"Downloading SiYuan {args.version}...")
        tar_url = f"https://codeload.github.com/siyuan-note/siyuan/tar.gz/refs/tags/{args.version}"
        cmd = f"curl -sL {tar_url} | tar -xz -C {src_dir} --strip-components=1"
        subprocess.run(cmd, shell=True, check=True)

        subprocess.run(["git", "init", "-q"], cwd=src_dir, check=True)
        subprocess.run(["git", "config", "core.autocrlf", "false"], cwd=src_dir, check=True)
        subprocess.run(["git", "add", "-A"], cwd=src_dir, check=True)
        subprocess.run(["git", "-c", "user.email=patch@local", "-c", "user.name=patch", "commit", "-qm", "base"], cwd=src_dir, check=True)

        # Write new files
        reg_path = os.path.join(src_dir, "app/src/protyle/render/mathRendererRegistry.ts")
        os.makedirs(os.path.dirname(reg_path), exist_ok=True)
        with open(reg_path, "w", encoding="utf-8") as f:
            f.write(TS_MATH_REGISTRY)

        bound_path = os.path.join(src_dir, "app/src/protyle/render/mathBoundaries.ts")
        with open(bound_path, "w", encoding="utf-8") as f:
            f.write(TS_MATH_BOUNDARIES)

        render_path = os.path.join(src_dir, "app/src/protyle/render/mathRender.ts")
        with open(render_path, "w", encoding="utf-8") as f:
            f.write(TS_MATH_RENDER)

        # Modify existing files
        p_index_path = os.path.join(src_dir, "app/src/plugin/index.ts")
        with open(p_index_path, "r", encoding="utf-8") as f:
            p_index = f.read()
        with open(p_index_path, "w", encoding="utf-8") as f:
            f.write(modify_plugin_index(p_index))

        p_uninst_path = os.path.join(src_dir, "app/src/plugin/uninstall.ts")
        with open(p_uninst_path, "r", encoding="utf-8") as f:
            p_uninst = f.read()
        with open(p_uninst_path, "w", encoding="utf-8") as f:
            f.write(modify_plugin_uninstall(p_uninst))

        e_index_path = os.path.join(src_dir, "app/src/protyle/export/index.ts")
        with open(e_index_path, "r", encoding="utf-8") as f:
            e_index = f.read()
        with open(e_index_path, "w", encoding="utf-8") as f:
            f.write(modify_export_index(e_index))

        subprocess.run(["git", "add", "-A"], cwd=src_dir, check=True)
        diff = subprocess.run(["git", "diff", "--cached"], cwd=src_dir, check=True, capture_output=True, text=True).stdout

        os.makedirs(os.path.dirname(out_path), exist_ok=True)
        with open(out_path, "w", encoding="utf-8") as f:
            f.write(diff)
        print(f"Patch written to: {out_path} ({len(diff)} bytes)")

        # Verify git apply
        subprocess.run(["git", "reset", "--hard", "HEAD"], cwd=src_dir, check=True)
        subprocess.run(["git", "clean", "-fd"], cwd=src_dir, check=True)
        chk = subprocess.run(["git", "apply", "--check", out_path], cwd=src_dir, capture_output=True, text=True)
        if chk.returncode != 0:
            print("ERROR: git apply --check failed:\n" + chk.stderr)
            sys.exit(1)
        print("Verification: git apply --check OK")

if __name__ == "__main__":
    main()
