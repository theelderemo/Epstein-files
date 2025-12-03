import os
import io
import gradio as gr
import pandas as pd
from google.cloud import storage

# --- CONFIGURATION ---
# We get these from Cloud Run Environment Variables
BUCKET_NAME = os.environ.get("BUCKET_NAME")
FILE_NAME = os.environ.get("FILE_NAME", "EPS_FILES_20K_NOV2025.csv")

# Global variable to store data
global_df = None

def load_data():
    """Downloads and loads data from Google Cloud Storage."""
    global global_df
    if global_df is not None:
        return global_df

    print(f"⏳ Connecting to GCS Bucket: {BUCKET_NAME}...")
    try:
        # 1. Initialize the GCS Client (Auto-auths with Cloud Run Service Account)
        storage_client = storage.Client()
        
        # 2. Get the bucket and file (blob)
        bucket = storage_client.bucket(BUCKET_NAME)
        blob = bucket.blob(FILE_NAME)
        
        # 3. Download directly to memory
        print("Downloading file (this is fast inside Google Cloud)...")
        data_bytes = blob.download_as_bytes()
        
        # 4. Load into Pandas
        print("Parsing CSV...")
        df = pd.read_csv(io.BytesIO(data_bytes), on_bad_lines='skip')
        df.columns = [c.lower() for c in df.columns]
        
        global_df = df
        print(f"✅ Data loaded! {len(df)} rows.")
        return global_df

    except Exception as e:
        print(f"❌ Error: {e}")
        # Return a dummy dataframe so the app doesn't crash on load
        return pd.DataFrame({"Error": [f"Could not load data: {e}"]})

# --- APP LOGIC ---

def search_documents(query):
    # Trigger load if first time
    df = load_data()
    
    if "Error" in df.columns:
        return df
        
    if not query:
        return df.head(50)
    
    # Case-insensitive search
    mask = df.astype(str).apply(lambda x: x.str.contains(query, case=False, na=False)).any(axis=1)
    return df[mask].head(1000)

def display_document(evt: gr.SelectData):
    df = load_data()
    try:
        row_index = evt.index[0]
        # Robust column finding
        text_col = 'text' if 'text' in df.columns else df.columns[-1]
        return df.iloc[row_index][text_col]
    except:
        return "Could not retrieve document text."

# --- USER INTERFACE ---

with gr.Blocks(title="Epstein Docs Browser", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📂 Epstein Estate Document Browser")
    gr.Markdown("Status: **Online** (Hosted on Google Cloud Run + Storage)")
    
    with gr.Row():
        search_box = gr.Textbox(label="Search", placeholder="Type here...", scale=3)
        search_btn = gr.Button("Search", variant="primary", scale=1)

    results_table = gr.Dataframe(
        headers=["Status"],
        value=[["System Ready. Search to begin."]],
        label="Search Results",
        interactive=False,
        wrap=True
    )
    
    doc_viewer = gr.TextArea(label="Document Content", lines=20)

    # Search Event
    search_btn.click(fn=search_documents, inputs=search_box, outputs=results_table)
    search_box.submit(fn=search_documents, inputs=search_box, outputs=results_table)
    
    # Click Event
    results_table.select(fn=display_document, outputs=doc_viewer)

# REQUIRED FOR CLOUD RUN
if __name__ == "__main__":
    port = int(os.environ.get("PORT", 8080))
    demo.launch(server_name="0.0.0.0", server_port=port, ssr_mode=False)
