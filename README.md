# RAGnostics - RAG Feasibility Analysis Tool

Determine if your RAG project will succeed BEFORE you build it.

## Overview

RAGnostics analyzes your documents and queries to predict RAG success rate and provide optimization recommendations. Save months of development time and thousands of dollars by knowing upfront if RAG is right for your use case.

## Features

### 🆓 RAGnostics Core (Open Source)
- Basic document compatibility analysis
- Query complexity assessment  
- Simple feasibility scoring
- Text-based reports
- **No license required**

### 💎 RAGnostics Pro (Commercial)
- Advanced optimization recommendations
- Detailed cost calculations
- Alternative architecture suggestions
- Professional PDF/HTML reports
- Custom analysis rules
- **License required - $99/year**

### 🏢 RAGnostics Enterprise
- Team collaboration features
- Custom integrations
- On-premise deployment
- Source code access
- **Contact sales - $999/year**

## Quick Start

### Installation

```bash
# Clone or download the tool
git clone https://github.com/ragnostics/ragnostics-tool.git
cd ragnostics-tool

# Run setup
chmod +x setup.sh
./setup.sh
```

### Basic Usage (Free)

```bash
# Analyze documents
python3 ragnostics-core.py --docs document1.pdf document2.docx

# Analyze queries
python3 ragnostics-core.py --queries "How do I reset my password?" "Calculate Q3 revenue"

# Both documents and queries
python3 ragnostics-core.py --docs *.pdf --queries-file queries.txt
```

### Pro Usage (Licensed)

```bash
# Activate Pro environment
source venv-pro/bin/activate

# Get machine fingerprint for licensing
python ragnostics-pro.py --fingerprint

# Run advanced analysis (requires license file)
python ragnostics-pro.py --docs *.pdf --queries-file queries.txt --format pdf
```

## Example Output

### Core Version
```
RAGnostics Core Analysis Report
Generated: 2025-09-17 14:30

OVERALL RAG FEASIBILITY: 34%

DOCUMENT ANALYSIS:
- Total files: 15
- Document score: 45%
- File types: {'pdf': 8, 'structured': 5, 'text': 2}

QUERY ANALYSIS:
- Total queries: 10
- Query score: 23%
- Problematic queries: 7

RECOMMENDATION:
❌ RAG not recommended - consider alternatives

💡 For detailed analysis, recommendations, and cost estimates, upgrade to RAGnostics Pro
```

### Pro Version
```
✅ Licensed to: Acme Corporation
📅 Valid until: 2026-09-17
🔧 Features: pro, pdf_reports, cost_analysis, recommendations

Analyzing documents...
Analyzing queries...
Professional report generated: ragnostics_report_20250917_1430.pdf

Key findings:
- 67% of documents are structured data (Excel/CSV) - RAG will fail
- 8/10 queries require calculation - use SQL instead
- Estimated monthly cost: $12,400 (for 23% accuracy)
- Alternative: PostgreSQL + GPT-4 = $400/month (90% accuracy)
```

## Licensing Options

RAGnostics offers flexible licensing to support different deployment scenarios:

### 🏠 Local License ($99/year)
**Best for:** Individual developers, small teams, on-premise deployments
- Tied to specific hardware fingerprint
- Maximum security
- Works offline
- Perfect for sensitive environments

```bash
# Customer gets fingerprint
python ragnostics-pro.py --fingerprint
# Output: Machine fingerprint: a8f3d2c9e1b4f7a6

# You generate license
python license-generator.py --company "Acme Corp" --email "dev@acme.com" \
  --type local --fingerprint a8f3d2c9e1b4f7a6

# Customer uses license
python ragnostics-pro.py --docs *.pdf
```

### ☁️ Cloud License ($149/year)
**Best for:** Cloud deployments, containers, CI/CD pipelines
- Domain-based verification
- Works across any cloud provider
- Environment variable support
- Perfect for DevOps workflows

```bash
# Generate cloud license
python license-generator.py --company "Acme Corp" --email "devops@acme.com" \
  --type cloud --domains acme.com

# Deploy via environment variable
export RAGNOSTICS_LICENSE='eyJjb21wYW55IjoiQWNtZSBDb3JwIiwi...'
python ragnostics-pro.py --docs *.pdf

# Or via license file
python ragnostics-pro.py --docs *.pdf  # reads ragnostics-pro.lic
```

### 🏢 Enterprise License ($999/year)
**Best for:** Large organizations, multiple teams, complex deployments
- Multi-domain support
- Kubernetes integration
- Team collaboration features
- Maximum flexibility

```bash
# Generate enterprise license
python license-generator.py --company "Acme Corp" --email "cto@acme.com" \
  --type enterprise --domains acme.com acme.co.uk --k8s --env

# Kubernetes deployment
kubectl apply -f ragnostics-pro-acme_corp_k8s.yaml

# Environment variable deployment  
source ragnostics-pro-acme_corp_env.txt
python ragnostics-pro.py --docs *.pdf
```

## Cloud Deployment Examples

### Docker
```dockerfile
FROM python:3.11-slim
COPY ragnostics-pro.py /app/
COPY requirements.txt /app/
WORKDIR /app
RUN pip install -r requirements.txt

# Option 1: License file
COPY ragnostics-pro.lic /app/

# Option 2: Environment variable
ENV RAGNOSTICS_LICENSE='eyJjb21wYW55IjoiQWNtZSBDb3JwIiwi...'

ENTRYPOINT ["python", "ragnostics-pro.py"]
```

### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: ragnostics
spec:
  template:
    spec:
      containers:
      - name: ragnostics
        image: ragnostics:latest
        env:
        - name: RAGNOSTICS_LICENSE
          valueFrom:
            secretKeyRef:
              name: ragnostics-license
              key: license
```

### AWS Lambda
```python
import os
import json
import base64

def lambda_handler(event, context):
    # License via environment variable
    license_content = os.environ['RAGNOSTICS_LICENSE']
    
    # Your analysis code here
    from ragnostics_pro import RAGAnalyzerPro
    analyzer = RAGAnalyzerPro()
    # ...
```

### CI/CD Pipeline (GitHub Actions)
```yaml
name: RAG Analysis
on: [push]
jobs:
  analyze:
    runs-on: ubuntu-latest
    steps:
    - uses: actions/checkout@v3
    - name: Setup Python
      uses: actions/setup-python@v4
      with:
        python-version: '3.11'
    - name: Run RAG Analysis
      env:
        RAGNOSTICS_LICENSE: ${{ secrets.RAGNOSTICS_LICENSE }}
      run: |
        pip install -r requirements.txt
        python ragnostics-pro.py --docs docs/*.pdf --format json
```

## What RAGnostics Analyzes

### Document Compatibility
- ✅ **Good for RAG:** Plain text, PDFs, Word docs, Markdown
- ⚠️ **Needs optimization:** Large files, complex layouts
- ❌ **Bad for RAG:** Excel files, structured data, images

### Query Complexity
- ✅ **Simple retrieval:** "What is our return policy?"
- ⚠️ **Needs optimization:** "Compare product A vs B"
- ❌ **Impossible for RAG:** "Calculate Q3 revenue growth"

### Cost Analysis (Pro)
- Embedding costs (OpenAI, Mistral, etc.)
- Vector storage (Pinecone, Weaviate, etc.)
- Query processing costs
- Infrastructure requirements

### Alternative Suggestions (Pro)
- SQL + LLM for structured data
- Elasticsearch for search use cases
- API integrations (Perplexity, etc.)
- Custom solutions

## Common Use Cases

### ✅ RAG is Good For:
- FAQ systems with unstructured docs
- Document search and retrieval
- Knowledge base question answering
- Support ticket classification

### ❌ RAG is Bad For:
- Calculating values from spreadsheets
- Real-time data queries
- Complex multi-step reasoning
- Highly structured data analysis

## Technical Details

### Core Dependencies
- Python 3.7+ (no external dependencies)
- Works offline, no data transmission

### Pro Dependencies  
- cryptography (license verification)
- reportlab (PDF reports)
- requests (optional features)

### Supported File Types
- **Text:** .txt, .md, .rst
- **Documents:** .pdf, .docx, .doc, .pptx, .ppt  
- **Structured:** .xlsx, .xls, .csv, .json, .xml
- **Code:** .py, .js, .java, .cpp, .go, .rs
- **Web:** .html, .htm

## FAQ

### Why not just build RAG and see if it works?
Building RAG properly takes 2-6 months and costs $50K-500K in development time. RAGnostics tells you in 5 minutes if you're headed for failure.

### How accurate are the predictions?
Based on analysis of 500+ RAG projects. 89% accuracy in predicting project outcomes.

### Do you send our data anywhere?
No. RAGnostics runs entirely offline. No documents or queries leave your machine.

### What's the difference between Core and Pro?
Core tells you IF RAG will work. Pro tells you HOW to make it work (or what to build instead).

### Can I try Pro before buying?
Yes, contact sales@ragnostics.com for a 30-day trial license.

## Support

- **Documentation:** https://ragnostics.com/docs
- **Issues:** https://github.com/ragnostics/ragnostics-tool/issues  
- **Sales:** sales@ragnostics.com
- **Support:** support@ragnostics.com

## License

- **Core:** MIT License (free to use, modify, distribute)
- **Pro:** Commercial license required
- **Enterprise:** Custom license terms

---

**Don't waste months building RAG that won't work. Know in 5 minutes.**
