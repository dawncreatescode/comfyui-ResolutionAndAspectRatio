import { app } from "../../scripts/app.js";

console.log("[SmartResolution] keywords_editor.js loaded");

const API = "/smart_resolution";

const STYLE = {
    overlay: `
        position: fixed; inset: 0; background: rgba(0,0,0,0.75);
        display: flex; align-items: center; justify-content: center; z-index: 9999;`,
    dialog: `
        background: #1a1a2e; color: #e0e0e0; border: 1px solid #444;
        border-radius: 8px; padding: 20px; width: 860px; max-width: 95vw;
        max-height: 82vh; display: flex; flex-direction: column; gap: 12px;
        font-family: monospace; font-size: 13px;`,
    input: `
        background: #252535; color: #e0e0e0; border: 1px solid #555;
        border-radius: 3px; padding: 3px 6px; width: 100%; box-sizing: border-box;
        font-family: monospace; font-size: 12px;`,
    btnPrimary: `
        background: #1a3a6a; color: #fff; border: 1px solid #3a6aaa;
        border-radius: 4px; padding: 6px 18px; cursor: pointer;`,
    btnSecondary: `
        background: #2e2e2e; color: #ccc; border: 1px solid #555;
        border-radius: 4px; padding: 6px 18px; cursor: pointer;`,
    btnAdd: `
        background: #1e3a1e; color: #8f8; border: 1px solid #3a6a3a;
        border-radius: 4px; padding: 5px 14px; cursor: pointer; align-self: flex-start;`,
    btnDel: `
        background: #5a1a1a; color: #faa; border: 1px solid #8a3a3a;
        border-radius: 3px; padding: 2px 7px; cursor: pointer;`,
};

function el(tag, style, attrs = {}) {
    const e = document.createElement(tag);
    if (style) e.style.cssText = style;
    Object.assign(e, attrs);
    return e;
}

function makeInput(value, placeholder = "") {
    const inp = el("input", STYLE.input, { value, placeholder });
    return inp;
}

function makeSelect(selected) {
    const sel = el("select", STYLE.input);
    for (const opt of ["limited", "all"]) {
        const o = document.createElement("option");
        o.value = o.textContent = opt;
        o.selected = opt === selected;
        sel.appendChild(o);
    }
    return sel;
}

function makeRow(tbody, entry = null) {
    const tr = document.createElement("tr");
    tr.style.borderBottom = "1px solid #2a2a3a";

    const ratioVal = Array.isArray(entry?.ratios)
        ? entry.ratios.join(", ")
        : (entry?.ratios ?? "");

    const inputs = {
        label:    makeInput(entry?.label ?? "", "label"),
        words:    makeInput((entry?.words ?? []).join(", "), "word1, word2, …"),
        ratios:   makeInput(ratioVal, "16:9, 21:9  or  $LANDSCAPE"),
        weights:  makeInput((entry?.weights ?? []).join(", "), "3, 2, 1  (optional)"),
        category: makeSelect(entry?.category ?? "all"),
    };

    for (const [key, widget] of Object.entries(inputs)) {
        const td = el("td", "padding: 4px;");
        widget.dataset.col = key;
        td.appendChild(widget);
        tr.appendChild(td);
    }

    const delTd = el("td", "padding: 4px; text-align: center;");
    const delBtn = el("button", STYLE.btnDel, { textContent: "✕", title: "Remove row" });
    delBtn.addEventListener("click", () => tr.remove());
    delTd.appendChild(delBtn);
    tr.appendChild(delTd);

    tbody.appendChild(tr);
    return inputs;
}

function collectRows(tbody) {
    return [...tbody.querySelectorAll("tr")].map(tr => {
        const get = col => tr.querySelector(`[data-col="${col}"]`)?.value?.trim() ?? "";

        const rawRatios = get("ratios");
        const ratios = rawRatios.startsWith("$")
            ? rawRatios
            : rawRatios.split(",").map(s => s.trim()).filter(Boolean);

        const rawWeights = get("weights");
        const weightArr = rawWeights
            ? rawWeights.split(",").map(s => parseFloat(s.trim())).filter(n => !isNaN(n))
            : [];

        return {
            label:    get("label"),
            words:    get("words").split(",").map(s => s.trim()).filter(Boolean),
            ratios,
            weights:  weightArr.length ? weightArr : null,
            category: get("category"),
        };
    });
}

async function openEditor() {
    let keywords;
    try {
        const resp = await fetch(`${API}/keywords`);
        if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
        keywords = await resp.json();
    } catch (err) {
        alert(`Could not load keywords: ${err.message}`);
        return;
    }

    // ── Overlay + dialog ──────────────────────────────────────────────────────
    const overlay = el("div", STYLE.overlay);
    const dialog  = el("div", STYLE.dialog);
    overlay.appendChild(dialog);

    // Title
    const title = el("h3", "margin: 0; color: #a0c4ff; font-size: 15px;",
        { textContent: "Edit Keywords" });

    const hint = el("p", "margin: 0; font-size: 11px; color: #777;", {
        textContent:
            "Limited keywords activate in \u201cLimited\u201d and \u201cAll\u201d modes; All keywords only in \u201cAll\u201d mode. " +
            "Use $LANDSCAPE or $PORTRAIT as ratio values to reference the full ratio sets.",
    });

    // Table
    const tableWrap = el("div", "overflow-y: auto; flex: 1; min-height: 0;");
    const table = el("table", "width: 100%; border-collapse: collapse;");

    const thead = document.createElement("thead");
    thead.innerHTML = `<tr style="color:#999; text-align:left; border-bottom:1px solid #444;">
        <th style="padding:5px 4px; width:90px;">Label</th>
        <th style="padding:5px 4px;">Words (comma-separated)</th>
        <th style="padding:5px 4px; width:200px;">Ratios</th>
        <th style="padding:5px 4px; width:130px;">Weights</th>
        <th style="padding:5px 4px; width:75px;">Category</th>
        <th style="padding:5px 4px; width:28px;"></th>
    </tr>`;

    const tbody = document.createElement("tbody");
    table.append(thead, tbody);
    tableWrap.appendChild(table);

    for (const entry of keywords) makeRow(tbody, entry);

    // Add row button
    const addBtn = el("button", STYLE.btnAdd, { textContent: "+ Add row" });
    addBtn.addEventListener("click", () => makeRow(tbody));

    // Footer
    const footer = el("div", "display:flex; justify-content:flex-end; gap:8px; align-items:center;");
    const status = el("span", "flex:1; font-size:11px; color:#aaa;");

    const cancelBtn = el("button", STYLE.btnSecondary, { textContent: "Cancel" });
    cancelBtn.addEventListener("click", () => overlay.remove());

    const saveBtn = el("button", STYLE.btnPrimary, { textContent: "Save" });
    saveBtn.addEventListener("click", async () => {
        saveBtn.disabled = true;
        status.textContent = "Saving…";
        try {
            const resp = await fetch(`${API}/keywords`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify(collectRows(tbody)),
            });
            if (!resp.ok) throw new Error(`HTTP ${resp.status}`);
            status.textContent = "Saved.";
            setTimeout(() => overlay.remove(), 700);
        } catch (err) {
            status.textContent = `Error: ${err.message}`;
            saveBtn.disabled = false;
        }
    });

    footer.append(status, cancelBtn, saveBtn);

    // Close on backdrop click
    overlay.addEventListener("click", e => { if (e.target === overlay) overlay.remove(); });

    dialog.append(title, hint, tableWrap, addBtn, footer);
    document.body.appendChild(overlay);
}

// ── Register extension ────────────────────────────────────────────────────────
app.registerExtension({
    name: "SmartResolution.KeywordsEditor",
    async beforeRegisterNodeDef(nodeType, nodeData) {
        if (nodeData.name !== "ResolutionNode") return;

        const orig = nodeType.prototype.onNodeCreated;
        nodeType.prototype.onNodeCreated = function () {
            orig?.apply(this, arguments);
            this.addWidget("button", "Edit Keywords", "edit_keywords", openEditor);
        };
    },
});
