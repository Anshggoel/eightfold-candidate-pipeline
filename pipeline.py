import json
import re
import uuid
import os
import sys

class AdvancedCandidatePipeline:
    def __init__(self):
        # Canonical Warehouse
        self.canonical_store = {}

    def apply_normalization(self, value, rules):
        """Dynamic normalization based on config instructions"""
        if not value:
            return value
        
        # 1. Phone Normalization (E.164 standard formatting)
        if rules.get("format") == "E.164":
            cleaned = re.sub(r'\D', '', str(value))
            if len(cleaned) == 10:
                return f"+91{cleaned}"
            return f"+{cleaned}" if cleaned else value
            
        # 2. Text/Skills Case Normalization
        if rules.get("case") == "lowercase":
            if isinstance(value, list):
                return list(set([str(v).lower().strip() for v in value]))
            return str(value).lower().strip()
            
        return value

    def process_file(self, file_path):
        """Automatically detect file type and parse accordingly"""
        ext = os.path.splitext(file_path)[1].lower()
        
        if ext == '.json':
            self._parse_json(file_path)
        elif ext == '.txt':
            self._parse_txt(file_path)

    def _parse_json(self, file_path):
        try:
            with open(file_path, 'r') as f:
                data = json.load(f)
            for item in data.get("candidates", []):
                raw_email = item.get("email", "").lower().strip()
                
                # Validate incoming email formats using regex to prevent downstream processing errors
                if not raw_email or not re.match(r'[^@]+@[^@]+\.[^@]+', raw_email):
                    print(f" Skipping object due to invalid email address: '{raw_email}'")
                    continue
                
                email = raw_email
                
                self.canonical_store[email] = {
                    "candidate_id": str(uuid.uuid5(uuid.NAMESPACE_DNS, email)),
                    "full_name": item.get("name", "").strip(),
                    "emails": [email],
                    "phones": item.get("phone", ""),
                    "skills": item.get("skills", []),
                    "provenance": [{"field": "all", "source": "ATS_JSON", "confidence": 1.0}]
                }
        except Exception as e:
            print(f" Error parsing structured JSON: {e}")

    def _parse_txt(self, file_path):
        try:
            with open(file_path, 'r') as f:
                text = f.read()
            
            # Extract via Regex and enforce lowercase validation
            email_match = re.search(r'[\w\.-]+@[\w\.-]+\.\w+', text)
            if not email_match: return
            email = email_match.group(0).lower().strip()
            
            # Entity Extraction simulation for Unstructured notes
            extracted_skills = []
            if "machine learning" in text.lower(): extracted_skills.append("Machine Learning")
            if "agentic ai" in text.lower(): extracted_skills.append("Agentic AI")
            
            if email in self.canonical_store:
                # Merge logic with conflict resolution strategy
                existing = self.canonical_store[email]["skills"]
                self.canonical_store[email]["skills"] = list(set(existing + extracted_skills))
                self.canonical_store[email]["provenance"].append({"field": "skills", "source": "TXT_Notes", "confidence": 0.7})
            else:
                self.canonical_store[email] = {
                    "candidate_id": str(uuid.uuid5(uuid.NAMESPACE_DNS, email)),
                    "full_name": "Extracted Profile",
                    "emails": [email],
                    "phones": "",
                    "skills": extracted_skills,
                    "provenance": [{"field": "all", "source": "TXT_Notes", "confidence": 0.7}]
                }
        except Exception as e:
            print(f" Error parsing unstructured text: {e}")

    def generate_projection(self, config_path):
        """Dynamic engine that reshapes data exactly as requested by config rules"""
        with open(config_path, 'r') as f:
            config = json.load(f)
        
        fields_config = config.get("fields", [])
        on_missing = config.get("on_missing", "null") # Action matrix strategy
        
        final_records = []
        for email, record in self.canonical_store.items():
            projected = {}
            skip_record = False
            
            for field in fields_config:
                out_path = field.get("path")
                source_key = field.get("from", out_path)
                
                raw_val = record.get(source_key)
                
                # Enforce dynamic missing validation checks
                if raw_val is None or raw_val == "" or raw_val == []:
                    if on_missing == "omit":
                        skip_record = True
                        break
                    elif on_missing == "error":
                        raise ValueError(f" CRITICAL PIPELINE ERROR: Missing mandatory field '{source_key}' for {email}")
                    else:
                        raw_val = None
                
                # Apply dynamic transformations rules if defined inside the config
                if "normalization" in field and raw_val is not None:
                    raw_val = self.apply_normalization(raw_val, field["normalization"])
                    
                projected[out_path] = raw_val
            
            if skip_record: continue
            
            # Meta-provenance telemetry integration
            if config.get("include_confidence", True):
                scores = [p["confidence"] for p in record["provenance"]]
                projected["overall_confidence"] = round(sum(scores) / len(scores), 2)
                
            final_records.append(projected)
            
        return final_records

if __name__ == "__main__":
    pipeline = AdvancedCandidatePipeline()
    
    # Automated multi-source data ingestion sweep
    data_files = ['ats.json', 'recruiter_notes.txt']
    for file in data_files:
        if os.path.exists(file):
            pipeline.process_file(file)
            
    try:
        output_data = pipeline.generate_projection('config.json')
        print(json.dumps(output_data, indent=4))
    except Exception as error:
        print(error)
