# /home/dijital/Documents/ragnostics-tool/ragnostics-core.py
"""
RAGnostics Core - Open Source RAG Feasibility Analyzer
MIT License - Free to use, modify, and distribute

This is the core functionality that anyone can use to get basic
RAG feasibility analysis. For advanced features, see ragnostics-pro.
"""

import os
import json
import hashlib
import mimetypes
from datetime import datetime
from collections import defaultdict
import argparse
import sys

class RAGAnalyzerCore:
    def __init__(self):
        self.supported_formats = {
            'text': ['.txt', '.md', '.rst'],
            'pdf': ['.pdf'],
            'office': ['.docx', '.doc', '.pptx', '.ppt'],
            'structured': ['.xlsx', '.xls', '.csv', '.json', '.xml'],
            'code': ['.py', '.js', '.java', '.cpp', '.c', '.go', '.rs'],
            'web': ['.html', '.htm', '.xml']
        }
    
    def analyze_documents(self, file_paths):
        """Basic document analysis - core functionality"""
        if not file_paths:
            return {"error": "No files provided"}
        
        analysis = {
            "total_files": len(file_paths),
            "file_types": defaultdict(int),
            "rag_compatibility": {},
            "warnings": [],
            "basic_score": 0
        }
        
        for file_path in file_paths:
            if not os.path.exists(file_path):
                analysis["warnings"].append(f"File not found: {file_path}")
                continue
            
            file_type = self._get_file_type(file_path)
            analysis["file_types"][file_type] += 1
            
            # Basic compatibility check
            compatibility = self._check_basic_compatibility(file_path, file_type)
            analysis["rag_compatibility"][file_path] = compatibility
        
        # Calculate basic score
        analysis["basic_score"] = self._calculate_basic_score(analysis)
        
        return analysis
    
    def analyze_queries(self, queries):
        """Basic query analysis - core functionality"""
        if not queries:
            return {"error": "No queries provided"}
        
        analysis = {
            "total_queries": len(queries),
            "complexity_scores": {},
            "problematic_patterns": [],
            "basic_score": 0
        }
        
        for i, query in enumerate(queries):
            score = self._analyze_query_complexity(query)
            analysis["complexity_scores"][f"query_{i+1}"] = {
                "query": query[:100] + "..." if len(query) > 100 else query,
                "complexity": score["complexity"],
                "issues": score["issues"]
            }
            
            if score["complexity"] == "high":
                analysis["problematic_patterns"].append(query[:50] + "...")
        
        # Calculate basic score
        analysis["basic_score"] = self._calculate_query_score(analysis)
        
        return analysis
    
    def _get_file_type(self, file_path):
        """Determine file type category"""
        ext = os.path.splitext(file_path)[1].lower()
        
        for category, extensions in self.supported_formats.items():
            if ext in extensions:
                return category
        return 'unknown'
    
    def _check_basic_compatibility(self, file_path, file_type):
        """Basic compatibility check for RAG"""
        file_size = os.path.getsize(file_path)
        
        compatibility = {
            "suitable_for_rag": True,
            "confidence": "medium",
            "issues": [],
            "size_mb": round(file_size / (1024 * 1024), 2)
        }
        
        # Size checks
        if file_size > 50 * 1024 * 1024:  # 50MB
            compatibility["issues"].append("Large file - may need chunking")
            compatibility["confidence"] = "low"
        
        # Format-specific checks
        if file_type == 'structured':
            compatibility["suitable_for_rag"] = False
            compatibility["issues"].append("Structured data - consider SQL instead")
            compatibility["confidence"] = "low"
        
        elif file_type == 'unknown':
            compatibility["suitable_for_rag"] = False
            compatibility["issues"].append("Unsupported file format")
            compatibility["confidence"] = "low"
        
        elif file_type == 'code':
            compatibility["issues"].append("Code files - may need specialized embedding")
        
        return compatibility
    
    def _analyze_query_complexity(self, query):
        """Analyze query complexity and RAG suitability"""
        query_lower = query.lower()
        
        # Patterns that indicate high complexity
        math_patterns = ['calculate', 'compute', 'sum', 'average', 'total', 'count', '+', '-', '*', '/']
        reasoning_patterns = ['why', 'because', 'reason', 'cause', 'analyze', 'compare', 'evaluate']
        temporal_patterns = ['latest', 'recent', 'current', 'today', 'yesterday', 'now']
        
        issues = []
        complexity = "low"
        
        # Check for mathematical operations
        if any(pattern in query_lower for pattern in math_patterns):
            issues.append("Contains mathematical operations - RAG cannot compute")
            complexity = "high"
        
        # Check for reasoning requirements
        if any(pattern in query_lower for pattern in reasoning_patterns):
            issues.append("Requires reasoning - RAG is retrieval-only")
            complexity = "medium"
        
        # Check for temporal requirements
        if any(pattern in query_lower for pattern in temporal_patterns):
            issues.append("Requires current data - RAG data may be stale")
            complexity = "medium"
        
        # Check for multi-step queries
        if ' and ' in query_lower or ' then ' in query_lower:
            issues.append("Multi-step query - may need decomposition")
            complexity = "medium"
        
        return {
            "complexity": complexity,
            "issues": issues
        }
    
    def _calculate_basic_score(self, analysis):
        """Calculate basic RAG feasibility score (0-100)"""
        score = 100
        
        # Penalize for structured files
        structured_ratio = analysis["file_types"]["structured"] / analysis["total_files"]
        score -= structured_ratio * 50
        
        # Penalize for unknown formats
        unknown_ratio = analysis["file_types"]["unknown"] / analysis["total_files"]
        score -= unknown_ratio * 30
        
        # Penalize for large files
        large_files = sum(1 for comp in analysis["rag_compatibility"].values() 
                         if comp.get("size_mb", 0) > 10)
        if large_files > 0:
            score -= (large_files / analysis["total_files"]) * 20
        
        return max(0, min(100, int(score)))
    
    def _calculate_query_score(self, analysis):
        """Calculate query suitability score (0-100)"""
        score = 100
        
        high_complexity = sum(1 for q in analysis["complexity_scores"].values() 
                             if q["complexity"] == "high")
        medium_complexity = sum(1 for q in analysis["complexity_scores"].values() 
                               if q["complexity"] == "medium")
        
        # Heavy penalty for high complexity queries
        if high_complexity > 0:
            score -= (high_complexity / analysis["total_queries"]) * 60
        
        # Medium penalty for medium complexity
        if medium_complexity > 0:
            score -= (medium_complexity / analysis["total_queries"]) * 30
        
        return max(0, min(100, int(score)))
    
    def generate_basic_report(self, doc_analysis, query_analysis):
        """Generate basic text report"""
        overall_score = (doc_analysis["basic_score"] + query_analysis["basic_score"]) / 2
        
        report = f"""
RAGnostics Core Analysis Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}

OVERALL RAG FEASIBILITY: {overall_score:.0f}%

DOCUMENT ANALYSIS:
- Total files: {doc_analysis['total_files']}
- Document score: {doc_analysis['basic_score']}%
- File types: {dict(doc_analysis['file_types'])}

QUERY ANALYSIS:
- Total queries: {query_analysis['total_queries']}
- Query score: {query_analysis['basic_score']}%
- Problematic queries: {len(query_analysis['problematic_patterns'])}

RECOMMENDATION:
"""
        
        if overall_score >= 70:
            report += "✅ RAG is likely suitable for your use case\n"
        elif overall_score >= 40:
            report += "⚠️ RAG may work with optimizations\n"
        else:
            report += "❌ RAG not recommended - consider alternatives\n"
        
        report += "\n💡 For detailed analysis, recommendations, and cost estimates, upgrade to RAGnostics Pro\n"
        
        return report

def main():
    parser = argparse.ArgumentParser(description='RAGnostics Core - Basic RAG Feasibility Analysis')
    parser.add_argument('--docs', nargs='+', help='Document files to analyze')
    parser.add_argument('--queries', nargs='+', help='Sample queries to test')
    parser.add_argument('--queries-file', help='File containing queries (one per line)')
    parser.add_argument('--output', help='Output file for report')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    
    args = parser.parse_args()
    
    if not args.docs and not args.queries and not args.queries_file:
        parser.print_help()
        sys.exit(1)
    
    analyzer = RAGAnalyzerCore()
    
    # Analyze documents
    doc_analysis = {"basic_score": 100, "total_files": 0, "file_types": {}}
    if args.docs:
        print("Analyzing documents...")
        doc_analysis = analyzer.analyze_documents(args.docs)
    
    # Analyze queries
    queries = []
    if args.queries:
        queries.extend(args.queries)
    if args.queries_file and os.path.exists(args.queries_file):
        with open(args.queries_file, 'r') as f:
            queries.extend([line.strip() for line in f if line.strip()])
    
    query_analysis = {"basic_score": 100, "total_queries": 0, "complexity_scores": {}, "problematic_patterns": []}
    if queries:
        print("Analyzing queries...")
        query_analysis = analyzer.analyze_queries(queries)
    
    # Generate report
    if args.json:
        result = {
            "document_analysis": doc_analysis,
            "query_analysis": query_analysis,
            "timestamp": datetime.now().isoformat()
        }
        output = json.dumps(result, indent=2)
    else:
        output = analyzer.generate_basic_report(doc_analysis, query_analysis)
    
    # Output result
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"Report saved to {args.output}")
    else:
        print(output)

if __name__ == "__main__":
    main()
