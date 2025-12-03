import gradio as gr
import pandas as pd
import re
from pathlib import Path
import tempfile
import os

# --- CONFIGURATION ---

FILE_PATH = Path("EPS_FILES_20K_NOV2025.csv")
saved_items = []  # global in-memory list of saved docs: {filename, snippet, text}

print("⏳ Loading data... (This may take 10-20 seconds)")
try:
    df = pd.read_csv(FILE_PATH, on_bad_lines="skip")
    df.columns = [c.lower() for c in df.columns]

    text_col = "text" if "text" in df.columns else df.columns[-1]
    name_col = "filename" if "filename" in df.columns else df.columns[0]

    print(f"✅ Success! Loaded {len(df)} documents.")

except Exception as e:
    print(f"❌ Error loading file: {e}")
    df = pd.DataFrame({"error": ["File not found. Check path and that the CSV is in the repo."]})
    text_col = "error"
    name_col = "error"


# --- HELPERS ---

def base_view():
    """Default view: first 50 docs with short snippets."""
    out = df.head(50).copy()
    out["snippet"] = out[text_col].astype(str).str.slice(0, 280).str.replace("\n", " ")
    return out[[name_col, "snippet"]]


def make_snippet_from_text(full_text: str, terms):
    """Create a short snippet around the first occurrence of any term."""
    t = str(full_text)
    t_low = t.lower()
    positions = [t_low.find(term.lower()) for term in terms]
    positions = [p for p in positions if p != -1]
    first = min(positions) if positions else 0
    start = max(first - 120, 0)
    end = start + 280
    return t[start:end].replace("\n", " ")


# --- APP LOGIC ---

def search_documents(query: str):
    """
    Multi-term AND search on text_col.
    Shows filename + short snippet around first match.
    """
    if not query or len(query.strip()) < 2:
        return base_view()

    terms = [t.strip() for t in query.split() if t.strip()]
    if not terms:
        return base_view()

    def row_match(text):
        t = str(text).lower()
        return all(term.lower() in t for term in terms)

    matches = df[df[text_col].apply(row_match)].copy()
    matches["snippet"] = matches[text_col].apply(lambda t: make_snippet_from_text(t, terms))

    return matches.head(500)[[name_col, "snippet"]]


def display_document(evt: gr.SelectData, current_data, query: str):
    """
    When a row is clicked, show full text with basic highlighting.
    current_data is the table currently displayed (filename + snippet).
    """
    try:
        row_index = evt.index[0]
        row = current_data.iloc[row_index]
        doc_name = row[name_col]

        full_row = df[df[name_col] == doc_name].iloc[0]
        full_text = str(full_row[text_col])

        terms = [t.strip() for t in (query or "").split() if t.strip()]
        for term in terms:
            pattern = re.compile(re.escape(term), re.IGNORECASE)
            full_text = pattern.sub(lambda m: f"**{m.group(0)}**", full_text)

        header = f"📄 **File:** `{doc_name}`\n\n"
        return header + full_text

    except Exception as e:
        return f"Error retrieving document text: {e}"


def save_current_document(current_view_text: str, query: str):
    """
    Save the currently viewed document (from doc_viewer markdown) into saved_items.
    current_view_text starts with '📄 **File:** `FILENAME`' followed by text.
    """
    try:
        if not current_view_text.startswith("📄 **File:**"):
            # Nothing selected yet
            if saved_items:
                preview = pd.DataFrame(saved_items)[["filename", "snippet"]]
            else:
                preview = pd.DataFrame({"filename": ["<none>"], "snippet": ["No document selected."]})
            return preview

        # Extract filename between backticks
        match = re.search(r"`([^`]+)`", current_view_text)
        if not match:
            raise ValueError("Could not parse filename from viewer header.")

        doc_name = match.group(1)

        full_row = df[df[name_col] == doc_name].iloc[0]
        full_text = str(full_row[text_col])

        terms = [t.strip() for t in (query or "").split() if t.strip()]
        snippet = make_snippet_from_text(full_text, terms) if terms else full_text[:280].replace("\n", " ")

        saved_items.append(
            {
                "filename": doc_name,
                "snippet": snippet,
                "text": full_text,
            }
        )

        preview = pd.DataFrame(saved_items)[["filename", "snippet"]]
        return preview

    except Exception as e:
        if saved_items:
            return pd.DataFrame(saved_items)[["filename", "snippet"]]
        else:
            return pd.DataFrame(
                {"filename": ["<none>"], "snippet": [f"Error saving document: {e}"]}
            )


def export_report():
    """
    Create a TXT report from all saved items and return the file path.
    Gradio will wrap this as a downloadable file.
    """
    if not saved_items:
        content = "No items saved.\n"
    else:
        lines = []
        for i, item in enumerate(saved_items, start=1):
            lines.append(f"=== Document {i} ===")
            lines.append(f"Filename: {item['filename']}")
            lines.append("Citation: U.S. House Oversight Epstein Estate Documents")
            lines.append("")
            lines.append(item["text"])
            lines.append("\n\n")
        content = "\n".join(lines)

    fd, path = tempfile.mkstemp(suffix=".txt")
    with os.fdopen(fd, "w", encoding="utf-8") as f:
        f.write(content)
    return path


# --- USER INTERFACE ---

with gr.Blocks(title="Epstein Docs Browser") as demo:
    # Content warning banner
    gr.Markdown(
        """
<div style="padding: 0.75rem 1rem; border-radius: 0.5rem; background-color: #2f0000; color: #ffd4d4; font-weight: 600;">
⚠️ CONTENT WARNING: This corpus contains graphic and highly sensitive material, including sexual abuse, exploitation, trafficking, and violence, as well as unverified allegations and speculation. Proceed with caution.
</div>
""",
    )

    gr.Markdown("# 📂 Epstein Estate Document Browser")

    # Responsible use summary
    gr.Markdown(
        """
### Responsible use (read before searching)
This dataset is a derivative collection of public documents released by the U.S. House Oversight Committee. It is intended **only** for research and exploratory analysis in support of public‑interest investigation.
- Do **not** use this corpus to fine‑tune or train generative models.
- Do **not** use it for doxing, harassment, or targeted attacks.
- Do **not** attempt to circumvent or reverse redactions.
- Do **not** present unverified allegations from these documents as established fact.
You are solely responsible for complying with applicable law, institutional policies, and the terms of the original House release. If you plan to use this corpus in a public‑facing product or at scale, seek independent legal advice.
"""
    )

    gr.Markdown(
        "Search 20,000+ documents. "
        "**Multiple words are treated as AND (all must appear). "
        "Click a row to read the full file below.**"
    )

    with gr.Row():
        search_box = gr.Textbox(
            label="Search (Keywords, Names, Flight Logs)",
            placeholder="Type here...",
            scale=3,
        )
        search_btn = gr.Button("Search", variant="primary", scale=1)

    summary = gr.Markdown("")

    with gr.Row():
        results_table = gr.Dataframe(
            headers=[name_col, "snippet"],
            datatype="str",
            label="Search Results (Click a row to view)",
            interactive=False,
            wrap=True,
        )

    with gr.Row():
        doc_viewer = gr.Markdown(
            label="Document Content",
            value="Select a document above to read it here...",
        )

    with gr.Row():
        save_btn = gr.Button("Save current document to notebook")
        downloaded_file = gr.File(label="Download saved items (.txt)")
    saved_preview = gr.Dataframe(
        headers=["filename", "snippet"],
        datatype="str",
        label="Saved items (research notebook)",
        interactive=False,
        wrap=True,
    )

    # --- INTERACTIONS ---

    def run_search_and_summary(query):
        res = search_documents(query)
        return res, f"**{len(res)}** results shown."

    search_btn.click(
        fn=run_search_and_summary,
        inputs=search_box,
        outputs=[results_table, summary],
    )
    search_box.submit(
        fn=run_search_and_summary,
        inputs=search_box,
        outputs=[results_table, summary],
    )

    demo.load(
        fn=lambda: (base_view(), "**50** documents shown (initial sample)."),
        inputs=None,
        outputs=[results_table, summary],
    )

    # Row click -> update viewer
    results_table.select(
        fn=display_document,
        inputs=[results_table, search_box],
        outputs=doc_viewer,
    )

    # Save current viewer doc -> update saved_preview
    save_btn.click(
        fn=save_current_document,
        inputs=[doc_viewer, search_box],
        outputs=saved_preview,
    )

    # Download TXT of saved items
    download_btn = gr.Button("Generate TXT report from saved items")
    download_btn.click(
        fn=export_report,
        inputs=None,
        outputs=downloaded_file,
    )


if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=7860)
