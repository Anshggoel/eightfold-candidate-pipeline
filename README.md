# Multi-Source Candidate Data Transformer

This is a Python-based data pipeline designed to ingest candidate profiles from both structured (JSON) and unstructured (TXT) sources. It normalizes fields, resolves duplicates, and transforms the output layout dynamically using a runtime configuration file.

## 🚀 Key Modules Built
- **Flexible Data Parser:** Automatically detects whether the input file is structured JSON or rough recruiter text notes based on file extensions.
- **Data Normalizer:** Cleans messy user input data. For example, it converts various phone number formats into the global standard `E.164` format (+91...).
- **Smart Merging Engine:** Identifies duplicate candidates using their lowercase email ID as a primary key. It combines skills from different sources without losing data.
- **Dynamic Projections:** Reads a user-defined `config.json` at runtime to filter, rename, or hide profile fields instantly without touching the core code.
- **Reliability Metrics:** Implements tracking for data sources and calculates an overall confidence score (giving higher weight to verified JSON systems and lower weight to manual recruiter notes).

## 🛠️ System Architecture Flow
1. **Ingest & Detect:** Scans the folder and reads target `.json` and `.txt` files.
2. **Standardize:** Normalizes raw text fields and trims unnecessary spaces.
3. **Deduplicate:** Merges candidate data objects if the email IDs match.
4. **Reshape & Export:** Applies custom configuration rules to output the final mapped fields.

## 💻 How to Run Locally
Make sure Python 3 is installed on your computer. Execute the script from your terminal:
```bash
python pipeline.py
```
