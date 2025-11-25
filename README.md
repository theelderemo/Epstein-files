# U.S. House Oversight Epstein Estate Documents

## Overview

On **November 12, 2025**, the U.S. House Oversight Committee released over 20,000 pages of documents from the Epstein estate. While intended to serve the public interest, these records remain largely inaccessible as they are scattered across nested folders in mixed file formats.

This dataset aims to democratize access to these public government documents by organizing and converting them into a clean, standardized format suitable for open source investigation. It enables AI researchers and investigative journalists to perform exploratory analysis and build RAG systems capable of surfacing insights that would be impractical to uncover through manual review.

The dataset was originally shared on `r/LocalLLaMA` on November 16, 2025. This repository adopts the usage guidelines and metadata from that original release.

## Table of Contents
- [Overview](#overview)
- [Usage Guidelines](#usage-guidelines)
  - [User Responsibilities](#user-responsibilities)
  - [Prohibited Uses](#prohibited-uses)
- [Source](#source)
- [Preprocessing](#preprocessing)
- [Known Limitations](#known-limitations)
- [Legal and Copyright Status](#legal-and-copyright-status)
- [Content Warning](#content-warning)

## Usage Guidelines

This dataset is intended for research and exploratory analysis in support of investigative journalism, with a focus on:

*   Evaluating information retrieval and retrieval augmented generation (RAG) systems.
*   Developing and testing search, clustering, knowledge graph, and summarization tools.
*   Enabling transparent, reproducible research aligned with open science principles.

### User Responsibilities
*   **Treat individuals with respect:** Treat individuals mentioned in documents with respect; avoid sensationalism or misuse of sensitive material.
*   **Verify facts:** Clearly distinguish model-generated content and exploratory findings from verified facts. Cite primary sources where appropriate.
*   **Respect redactions:** Respect all existing redactions. Do not attempt to identify protected information.
*   **Ethical standards:** Adhere to journalistic and academic ethics standards.

### Prohibited Uses
*   **Finetuning language models.**
*   Harassment, doxing, or targeted attacks on any individual or group.
*   Attempts to deanonymize redacted information or circumvent existing redactions.
*   Presenting unverified allegations as factual claims.
*   Sensationalizing findings.

> **Note:** All use must comply with applicable law, institutional policies, and the terms of the original House release. See the [Legal](#legal-and-copyright-status) and [Ethical](#usage-guidelines) sections before working with this corpus.

## Source

All documents originate from the public release *"Oversight Committee Releases Additional Epstein Estate Documents"* published by the House Oversight Committee on **November 12, 2025**.

> **Disclaimer:** This dataset is an independent derivative collection and is not an official product of the U.S. House of Representatives or the Committee on Oversight and Government Reform.

## Preprocessing

*   **25,000+ plain text files** derived from the committee's public releases, organized into a single CSV.
*   **Image files** (~20,000 JPGs under `IMAGES/`) converted to text using the open source Tesseract OCR engine.
*   **Native text files** (under `TEXT/`) preserved as is.
*   **Filenames** retain original relative paths and naming conventions for cross-referencing.

## Known Limitations

The corpus may contain:
*   OCR noise and misrecognized characters.
*   Broken formatting.
*   Redaction blocks, stamps, or markers inherited from the original scans.

## Legal and Copyright Status

**Disclaimer: Nothing in this section constitutes legal advice.**

*   **Origin:** Original documents were created by various private individuals and entities, not by the dataset maintainer.
*   **Copyright:** Documents are sourced from releases by the U.S. House Committee on Oversight and Government Reform. Release pages carry standard copyright notices (© 2025), and individual documents may be protected by copyright held by original authors or rights holders.
*   **This dataset:**
    *   Does not assert ownership over underlying documents.
    *   Does not grant any license to reproduce, distribute, or create derivative works beyond what is permitted by law (e.g., fair use).
*   **Liability:** Users are solely responsible for ensuring compliance with applicable copyright law, privacy law, institutional policies, and the terms of the original release.

*If you plan to use this corpus in a public-facing product, for model training, or at scale, seek independent legal counsel.*

## Content Warning

> These documents contain material related to:
>
> *   **Sexual abuse, exploitation, and trafficking**
> *   **Violence and other highly sensitive topics**
> *   **Unverified allegations, opinions, and speculation**
>
> Please proceed with caution.
