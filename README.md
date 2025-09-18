# RAGnostics - Know if RAG will fail BEFORE you build it

**Version:** 1.1.0 (Now with directory scanning!)  
**License:** MIT (Free to use, modify, distribute)

A simple tool that analyzes your documents and queries to predict if RAG (Retrieval-Augmented Generation) is the right solution for your use case.

## Why This Exists

89% of RAG projects fail because they try to use RAG for the wrong type of data or queries. This tool tells you in 5 minutes what would otherwise take months and $50K-500K to discover.

## Features

- **Document Analysis** - Checks if your documents work with RAG
- **Query Analysis** - Determines if your queries can be answered by RAG  
- **Cost Estimation** - Shows real costs vs alternatives
- **Alternative Recommendations** - Suggests better solutions when RAG won't work
- **Directory Scanning** - Analyzes entire folder structures for RAG suitability
- **Correlation Detection** - Identifies impossible "correlate everything" attempts
- **Noise Level Assessment** - Warns when too many files will cause random results
- **Multi-format Analysis** - Detects mixed data types that confuse RAG

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

### Scan entire directories (NEW)
```bash
# Scan entire directory recursively
python3 ragnostics-core.py --scan-directory /path/to/documents

# Scan without subdirectories
python3 ragnostics-core.py --scan-directory ./docs --no-recursive

# Scan directory with correlation check
python3 ragnostics-core.py --scan-directory ./data --queries "Find patterns across all departments"
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

# Full directory analysis with queries
python3 ragnostics-core.py --scan-directory ./company_data \
  --queries-file queries.txt \
  --output analysis_report.txt

# Get JSON output for automation
python3 ragnostics-core.py --scan-directory ./data --json > analysis.json
```

## Directory Scanning (NEW in v1.1.0)

RAGnostics can now scan entire directory structures to detect common pitfalls when people try to "RAG everything":

### What It Detects

1. **Noise Problem** - When you have 10,000+ files, RAG returns random, irrelevant results
2. **Correlation Attempts** - Queries expecting RAG to "find patterns across all data" (RAG retrieves, it doesn't analyze)
3. **Mixed Data Chaos** - Spreadsheets mixed with PDFs confuse retrieval
4. **Cost Bombs** - Estimates real embedding costs for massive datasets

### Example Directory Scan Output

```
📁 Scanning directory: /home/user/company_data
  Found 15,234 files (2,341.5 MB)
  ⚠️  WARNING: EXTREME noise level detected!

🚨 CORRELATION WARNING:
   You appear to be trying to correlate data across directories.
   RAG does NOT correlate - it only retrieves similar text.
   Use data analytics tools for correlation.

Problems detected:
  ⚠️ 15,234 files - Extreme noise risk! RAG will return random results
  🚫 Deep directory structure suggests correlation attempt
  ⚠️ 45% structured data mixed with text - Will cause retrieval confusion

Recommendations:
  🚨 DO NOT USE RAG - Too many files will cause random, useless results
  ✅ Alternative: Use Elasticsearch with careful indexing
  ✅ For correlation: Use data warehouse + BI tools
  💰 Estimated embedding cost: $234/month minimum
```

### When NOT to Use RAG (Directory Scanning Reveals)

- **"Analyze all our data"** - RAG doesn't analyze, it retrieves
- **"Find correlations"** - That's what SQL/Pandas/Spark do
- **"10,000+ documents"** - Too much noise, results become random
- **"Mixed Excel + PDF + JSON"** - Each needs different handling

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

### Massive Directory (Correlation Attempt)
```
DIRECTORY ANALYSIS
Total files: 45,678
Noise level: EXTREME
Directory score: 5%

🚨 CORRELATION WARNING:
RAG does NOT correlate - it only retrieves similar text.

❌ RAG is NOT recommended for your use case
Instead use:
• Data warehouse + BI tools for correlation analysis
• Elasticsearch with careful curation
• Pandas/Spark for data processing
```

## Common Problems RAGnostics Detects

### Important Note on Tables and Math

Small tables (<50 rows) that fit in a single chunk CAN work with RAG for simple lookups.
RAG fails when you need:
- Aggregation across multiple tables/chunks
- Actual calculation execution (not just formula retrieval)
- Cross-references between distant data points

The tool is intentionally conservative to prevent costly failures.

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
| Correlation | "Find patterns across all data" | RAG doesn't analyze | BI tools |

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

### Directory scan taking forever
Large directories with thousands of files take time to analyze. Use `--no-recursive` to speed up:
```bash
python3 ragnostics-core.py --scan-directory ./huge_folder --no-recursive
```

## FAQ

**Q: Can RAG analyze all my company's data?**  
A: No! This is a common misconception. RAG retrieves similar text, it doesn't analyze or correlate. Use our `--scan-directory` feature to see why your massive dataset won't work with RAG.

**Q: Why does the tool say my 50,000 documents are "too noisy"?**  
A: With that many documents, RAG will retrieve random, barely-relevant chunks. It's like searching for a needle in a haystack where every piece of hay looks vaguely like a needle. You need curation or better search tools.

**Q: Can RAG find patterns across different data sources?**  
A: No. RAG retrieves text similar to your query. Finding patterns/correlations requires analytical tools (SQL, Pandas, Tableau). RAG is retrieval, not analysis.

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
python3 ragnostics-core.py --scan-directory ./docs --json | jq '.directory_analysis.rag_suitability_score'

# Fail CI if score too low
score=$(python3 ragnostics-core.py --scan-directory ./docs --json | jq '.directory_analysis.rag_suitability_score')
if [ "$score" -lt 70 ]; then
  echo "RAG feasibility too low: $score%"
  exit 1
fi
```

### Batch Directory Analysis
```bash
# Analyze multiple projects
for dir in project1 project2 project3; do
  echo "Analyzing $dir..."
  python3 ragnostics-core.py --scan-directory $dir --output $dir/rag-analysis.txt
done
```

### Correlation Detection
```bash
# Check if your queries expect impossible correlations
python3 ragnostics-core.py --scan-directory ./data \
  --queries "What patterns exist across all departments?" \
           "Correlate customer behavior with weather data" \
           "Find common themes in all documents"
```

## Want More Features?

The free version gives you the essential feasibility check. For detailed recommendations, cost analysis, and alternative architectures, check out [RAGnostics Pro](https://ragnostics.com).

### Free vs Pro

| Feature | Free | Pro |
|---------|------|-----|
| Basic feasibility score | ✅ | ✅ |
| Document analysis | ✅ | ✅ |
| Query analysis | ✅ | ✅ |
| Directory scanning | ✅ | ✅ |
| Correlation detection | ✅ | ✅ |
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

**Remember**: Not every problem needs RAG. Sometimes a simple database query or API call is the better solution. And sometimes, you just need to organize your data better before throwing AI at it.
