# Contributing to the Epstein Estate Document Dataset

Welcome contributions that improve the accessibility and cleanliness of this dataset. However, due to the sensitive nature of the content, I have strict guidelines for pull requests.

## What We Accept
*   **OCR Corrections:** Fixes to typos resulting from the Tesseract conversion (e.g., correcting "1lI" confusions), provided they match the original image source.
*   **Metadata improvements:** Adding structured data (dates, document types) to the CSV index.
*   **Formatting:** Improving the readability of markdown files without altering the semantic content.

## What We Do Not Accept
*   **PII Restoration:** Do not submit PRs that attempt to "fill in" redacted names or addresses.
*   **Speculative Annotations:** Do not add commentary, theories, or external context directly into the document text files. Keep annotations in separate metadata fields.
*   **Fine-tuned Models:** Do not upload LoRAs or model weights trained on this data.

## How to Submit
1.  Fork the repository.
2.  Make your changes to the text or CSV files.
3.  Submit a Pull Request with a clear description of the fix.
4.  Reference the original filename/page number in your PR description for verification.