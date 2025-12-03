import os
import io
import gradio as gr
import pandas as pd
import google.auth
from googleapiclient.discovery import build
from googleapiclient.http import MediaIoBaseDownload

# --- CONFIGURATION ---
# We read the File ID from an environment variable for safety
# You will set this in the Cloud Run settings later.
FILE_ID = os.environ.get("https://drive.google.com/file/d/1_FlSAVPEyPues75SUHc9Hv5La6YF-Dqr/view?usp=drive_link")

def download_from_drive(file_id):
    """Downloads a file from Google Drive into memory."""
    print(f"⏳ Connecting to Drive to fetch ID: {file_id}...")
    try:
        # 1. Get default cloud credentials (Service Account)
        creds, _ = google.auth.default()
        service = build('drive', 'v3', credentials=creds)

        # 2. Request the file
        request = service.files().get_media(fileId=file_id)
        
        # 3. Download the data into RAM (BytesIO)
        file_buffer = io.BytesIO()
        downloader = MediaIoBaseDownload(file_buffer, request)
        
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            # Optional: Print progress for large files
            # print(f"Download {int(status.progress() * 100)}%.")

        file_buffer.seek(0) # Reset pointer to start of file
        return file_buffer
    except Exception as e:
        print(f"❌ Drive API Error: {e}")
        return None

# --- LOAD DATA ---
print("🚀 Server starting...")

try:
    # Download file content directly to memory
    csv_buffer = download_from_drive(FILE_ID)
    
    if csv_buffer:
        df = pd.read_csv(csv_buffer, on_bad_lines='skip')
        df.columns = [c.lower() for c in df.columns]
        
        # Identify columns
        text_col = 'text' if 'text' in df.columns else df.columns[-1]
        name_col = 'filename' if 'filename' in df.columns else df.columns[0]
        print(f"✅ Success! Loaded {len(df)} documents.")
    else:
        raise Exception("Failed to download file.")

except Exception as e:
    print(f"❌ Critical Error: {e}")
    df = pd.DataFrame({"Error": ["Could not load data. Check permissions."]})
    text_col = "Error"
    name_col = "Error"

# --- APP LOGIC ---

def search_documents(query):
    if not query:
        return df.head(50)
    mask = df.astype(str).apply(lambda x: x.str.contains(query, case=False, na=False)).any(axis=1)
    return df[mask].head(1000)

def display_document(evt: gr.SelectData):
    try:
        # Filter the dataframe to match the current view? 
        # Simpler approach: Look up by index in the *original* dataframe if not filtered, 
        # but Gradio passes the specific row data.
        # To keep it robust, we'll just grab the row from the visible dataframe logic.
        # Note: In this simple version, we trust the row index aligns with the dataframe.
        # For a perfect implementation, you might want to lookup by ID.
        
        # Let's simplify: Gradio SelectData gives the index of the row clicked.
        # If the user searched, the index refers to the *search results*, not the full DF.
        # We need to handle this carefully.
        return "Please note: In this basic version, ensure you clear search before clicking row index for accurate mapping, or implement ID-based lookup."
    except:
        return "Error."

# Improved display logic to handle the dataframe being filtered
# We will use a wrapper to pass the current dataset state if possible, 
# or just assume the user understands the simple index mapping.
# For this code snippet, I'll stick to your original logic but make it robust.

def get_doc_content(evt: gr.SelectData, data_snapshot):
    # data_snapshot is the dataframe currently displayed
    try:
        row_index = evt.index[0]
        full_text = data_snapshot.iloc[row_index][text_col]
        doc_name = data_snapshot.iloc[row_index][name_col]
        return f"📄 File: {doc_name}\n\n{full_text}"
    except Exception as e:
        return f"Error retrieving document: {e}"

# --- USER INTERFACE ---

with gr.Blocks(title="Epstein Docs Browser", theme=gr.themes.Soft()) as demo:
    gr.Markdown("# 📂 Epstein Estate Document Browser")
    
    with gr.Row():
        search_box = gr.Textbox(label="Search", placeholder="Type here...", scale=3)
        search_btn = gr.Button("Search", variant="primary", scale=1)

    # State variable to hold the currently visible data (so clicks map correctly)
    current_data = gr.State(df.head(50))

    results_table = gr.Dataframe(
        value=df.head(50),
        headers=list(df.columns),
        datatype="str",
        label="Search Results",
        interactive=False,
        wrap=True
    )
    
    doc_viewer = gr.TextArea(label="Document Content", lines=20)

    # Search Function Wrapper
    def update_results(query):
        new_results = search_documents(query)
        return new_results, new_results # Update both table and state

    search_btn.click(fn=update_results, inputs=search_box, outputs=[results_table, current_data])
    search_box.submit(fn=update_results, inputs=search_box, outputs=[results_table, current_data])

    # Click Event
    results_table.select(fn=get_doc_content, inputs=[current_data], outputs=doc_viewer)

# REQUIRED FOR CLOUD RUN: server_name="0.0.0.0" and port=8080
if __name__ == "__main__":
    demo.launch(server_name="0.0.0.0", server_port=8080)
