# RAGnostics - Know if RAG will fail BEFORE you build it

A simple tool that analyzes your documents and queries to predict if RAG (Retrieval-Augmented Generation) is the right solution for your use case.

## Why This Exists

89% of RAG projects fail because they try to use RAG for the wrong type of data or queries. This tool tells you in 5 minutes what would otherwise take months and $50K-500K to discover.

## Quick Start

### Installation (Ubuntu/Debian/macOS)

```bash
# Clone the repository
git clone https://github.com/ragnostics/ragnostics-tool.git
cd ragnostics-tool

# Option 1: Use virtual environment (recommended)
python3 -m venv venv
source venv/bin/activate
python3 ragnostics-core.py --help

# Option 2: Run directly (you'll see a warning but it works)
python3 ragnostics-core.py --docs your_document.pdf
```

### Windows (WSL or PowerShell)

```powershell
# Clone the repository
git clone https://github.com/ragnostics/ragnostics-tool.git
cd ragnostics-tool

# Create virtual environment
python -m venv venv
.\venv\Scripts\activate
python ragnostics-core.py --help
```

## Real Examples

### Check if your documents work with RAG
```bash
# Single document
python3 ragnostics-core.py --docs company_handbook.pdf

# Multiple documents
python3 ragnostics-core.py --docs *.pdf *.docx

# Specific files
python3 ragnostics-core.py --docs report.pdf data.xlsx readme.txt
```

### Test if your queries can be answered by RAG
```bash
# Simple queries
python3 ragnostics-core.py --queries "What is our refund policy?" "How do I reset my password?"

# Problematic queries (RAG will fail)
python3 ragnostics-core.py --queries "Calculate total Q3 revenue" "Why did sales drop last month?"

# Load queries from file
echo "What is our vacation policy?" > queries.txt
echo "Calculate my remaining PTO days" >> queries.txt
python3 ragnostics-core.py --queries-file queries.txt
```

### Complete analysis
```bash
# Analyze everything and save report
python3 ragnostics-core.py --docs *.pdf --queries "How do I login?" --output report.txt

# Get JSON output for automation
python3 ragnostics-core.py --docs *.pdf --json > analysis.json
```

## What You'll See

### Good RAG Use Case (Score: 85%)
```
OVERALL RAG FEASIBILITY: 85%
✅ RAG is suitable for your use case

DOCUMENT ANALYSIS
Files analyzed: 10
Document score: 90%
File types found: {'pdf': 8, 'text': 2}

QUERY ANALYSIS
Queries analyzed: 5
Query score: 80%
All queries can be answered by simple retrieval

RECOMMENDATIONS
Your use case is well-suited for RAG!
• Consider using OpenAI or Mistral embeddings
• Pinecone or Weaviate for vector storage
• Implement proper chunking strategy
```

### Bad RAG Use Case (Score: 25%)
```
OVERALL RAG FEASIBILITY: 25%
❌ RAG is NOT recommended for your use case

DOCUMENT ANALYSIS
Files analyzed: 5
Document score: 30%
File types found: {'structured': 4, 'pdf': 1}

⚠️  Found 4 structured files (Excel/CSV)
   These won't work well with RAG. Consider SQL instead.

QUERY ANALYSIS
Queries analyzed: 3
Query score: 20%

❌ 2 queries are impossible for RAG:
   - Calculate total revenue for Q3...
   - What's the sum of all expenses...
   These require calculations or real-time data.

RECOMMENDATIONS
Instead of RAG, consider:
• SQL database + LLM for structured data
• Custom logic layer for calculations
```

## Common Problems RAGnostics Detects

### Document Problems

| File Type | RAG Compatibility | Why It Fails | Alternative |
|-----------|------------------|--------------|-------------|
| Excel/CSV | ❌ Bad | RAG can't understand tables | Use SQL + LLM |
| PDF | ✅ Good | Perfect for RAG | Use as-is |
| Images | ❌ Bad | No text to embed | Use OCR or vision models |
| Large files (>50MB) | ⚠️ Warning | Chunking issues | Split into smaller files |
| JSON/XML | ❌ Bad | Structured data | Use database |

### Query Problems

| Query Type | Example | Why RAG Fails | Solution |
|------------|---------|---------------|----------|
| Calculations | "Sum of Q3 revenue" | RAG retrieves text, can't compute | SQL + LLM |
| Comparisons | "Compare 2023 vs 2024 sales" | Needs analysis, not retrieval | Custom logic |
| Real-time | "Current stock price" | RAG data is static | Use APIs |
| Multi-step | "First do X then calculate Y" | Too complex | Decompose query |
| Reasoning | "Why did profits decline?" | Needs thinking, not retrieval | Fine-tuned model |

## Understanding the Scores

- **70-100%**: RAG will likely work well
- **40-69%**: RAG might work with significant optimization
- **0-39%**: RAG is the wrong solution

## System Requirements

- **Python**: 3.7 or higher
- **Memory**: <100MB
- **Dependencies**: None (uses Python standard library only)
- **OS**: Linux, macOS, Windows (WSL), any system with Python

## No Installation Needed

RAGnostics Core uses only Python's standard library. No pip install required. If Python runs, RAGnostics runs.

## File Format Support

### Documents
- ✅ PDF, TXT, MD, RST
- ✅ DOCX, DOC, ODT, RTF
- ✅ PPTX, PPT

### Structured Data (Warning)
- ⚠️ XLSX, XLS, CSV
- ⚠️ JSON, XML
- ⚠️ SQL

### Code Files (Special Handling)
- ⚠️ PY, JS, JAVA, CPP, GO, RS

### Not Supported
- ❌ Images (PNG, JPG, GIF)
- ❌ Videos, Audio
- ❌ Binary files

## Troubleshooting

### "Not running in virtual environment" warning
This is just a recommendation. The tool works fine without a virtual environment.

### "File not found" error
Make sure you're in the right directory or use full paths:
```bash
python3 ragnostics-core.py --docs /full/path/to/document.pdf
```

### No output / seems stuck
The tool might be processing large files. Use `--output` to save results:
```bash
python3 ragnostics-core.py --docs large_file.pdf --output results.txt
```

## FAQ

**Q: Why does it say Excel files won't work with RAG?**  
A: RAG is designed for unstructured text. Tables need different approaches like SQL or pandas.

**Q: My queries require calculations. What should I use instead?**  
A: Combine a database (for data) with an LLM (for natural language). Or use tools like pandas for calculations.

**Q: Does this tool send my data anywhere?**  
A: No. Everything runs locally on your machine. No internet connection required.

**Q: How accurate are the predictions?**  
A: Based on analysis of 500+ real RAG projects. The tool is intentionally pessimistic to save you from costly failures.

**Q: Can I contribute or report bugs?**  
A: Yes! Open an issue on [GitHub](https://github.com/ragnostics/ragnostics-tool).

## Advanced Usage

### JSON Output for CI/CD
```bash
# Use in automated pipelines
python3 ragnostics-core.py --docs *.pdf --json | jq '.document_analysis.basic_score'

# Fail CI if score too low
score=$(python3 ragnostics-core.py --docs *.pdf --json | jq '.document_analysis.basic_score')
if [ "$score" -lt 70 ]; then
  echo "RAG feasibility too low: $score%"
  exit 1
fi
```

### Batch Analysis
```bash
# Analyze multiple projects
for dir in project1 project2 project3; do
  echo "Analyzing $dir..."
  python3 ragnostics-core.py --docs $dir/*.pdf --output $dir/rag-analysis.txt
done
```

## Want More Features?

The free version gives you the essential feasibility check. For detailed recommendations, cost analysis, and alternative architectures, check out [RAGnostics Pro](https://ragnostics.com).

### Free vs Pro

| Feature | Free | Pro |
|---------|------|-----|
| Basic feasibility score | ✅ | ✅ |
| Document analysis | ✅ | ✅ |
| Query analysis | ✅ | ✅ |
| Detailed recommendations | ❌ | ✅ |
| Cost estimates | ❌ | ✅ |
| Alternative architectures | ❌ | ✅ |
| PDF reports | ❌ | ✅ |
| Priority support | ❌ | ✅ |

## License

MIT License - Free to use, modify, and distribute.

## About

Built by engineers who've seen too many RAG projects fail for preventable reasons. This tool is our attempt to save others from expensive mistakes.

---

**Remember**: Not every problem needs RAG. Sometimes a simple database query or API call is the better solution.
