#!/usr/bin/env python3
"""
RAGnostics Core - Open Source RAG Feasibility Analyzer
MIT License - Free to use, modify, and distribute

Analyzes documents and queries to predict if RAG will work for your use case.
Now includes directory scanning to detect correlation attempts and massive datasets.
"""

import os
import json
import sys
from datetime import datetime
from collections import defaultdict
import argparse
import mimetypes
from pathlib import Path

# Version
__version__ = "1.1.0"  # Updated for directory scanning

def check_environment():
    """Check if running in venv and provide setup instructions if not"""
    in_venv = hasattr(sys, 'real_prefix') or (hasattr(sys, 'base_prefix') and sys.base_prefix != sys.prefix)
    
    if not in_venv:
        print("⚠️  Not running in virtual environment")
        print("\nRecommended setup for Ubuntu/Debian:")
        print("  python3 -m venv venv")
        print("  source venv/bin/activate")
        print("  python3 ragnostics-core.py --help\n")
        print("Continuing anyway...\n")
        print("-" * 50)

class RAGAnalyzerCore:
    def __init__(self):
        self.supported_formats = {
            'text': ['.txt', '.md', '.rst', '.log'],
            'pdf': ['.pdf'],
            'office': ['.docx', '.doc', '.pptx', '.ppt', '.odt'],
            'structured': ['.xlsx', '.xls', '.csv', '.json', '.xml', '.sql'],
            'code': ['.py', '.js', '.java', '.cpp', '.c', '.go', '.rs', '.rb', '.php'],
            'web': ['.html', '.htm'],
            'image': ['.png', '.jpg', '.jpeg', '.gif', '.bmp', '.svg']
        }
    
    def scan_directory(self, directory_path, recursive=True, sample_size=100):
        """
        Scan entire directory structure for RAG suitability
        
        This is the NEW feature for detecting when people try to 
        "correlate everything" with RAG
        """
        path = Path(directory_path)
        
        if not path.exists():
            return {"error": f"Directory {directory_path} does not exist"}
        
        if not path.is_dir():
            return {"error": f"{directory_path} is not a directory"}
        
        stats = {
            'total_files': 0,
            'total_size_mb': 0,
            'file_types': defaultdict(int),
            'by_extension': defaultdict(int),
            'directory_depth': 0,
            'largest_files': [],
            'problematic_patterns': [],
            'rag_compatible_files': 0,
            'structured_data_files': 0,
            'subdirectories': 0,
            'noise_level': 'low',
            'correlation_warning': False,
            'recommendations': []
        }
        
        # File type categorization
        STRUCTURED_EXTENSIONS = {'.xlsx', '.xls', '.csv', '.tsv', '.db', '.sqlite'}
        COMPATIBLE_EXTENSIONS = {'.txt', '.md', '.pdf', '.docx', '.doc', '.rtf'}
        PROBLEMATIC_EXTENSIONS = {'.jpg', '.png', '.mp4', '.zip', '.exe', '.bin', '.dll'}
        
        # Scan configuration
        pattern = '**/*' if recursive else '*'
        files_to_analyze = []
        
        print(f"🔍 Scanning {directory_path}{'recursively' if recursive else ''}...")
        
        # First pass: collect all files
        for item in path.glob(pattern):
            if item.is_file():
                stats['total_files'] += 1
                
                # Get file info
                ext = item.suffix.lower()
                try:
                    size_mb = item.stat().st_size / (1024 * 1024)
                    stats['total_size_mb'] += size_mb
                except:
                    size_mb = 0
                
                stats['by_extension'][ext] += 1
                
                # Categorize
                if ext in STRUCTURED_EXTENSIONS:
                    stats['structured_data_files'] += 1
                    stats['file_types']['structured'] += 1
                elif ext in COMPATIBLE_EXTENSIONS:
                    stats['rag_compatible_files'] += 1
                    stats['file_types']['compatible'] += 1
                elif ext in PROBLEMATIC_EXTENSIONS:
                    stats['file_types']['problematic'] += 1
                else:
                    stats['file_types']['unknown'] += 1
                
                # Track large files
                if size_mb > 10:
                    stats['largest_files'].append({
                        'path': str(item.relative_to(path)),
                        'size_mb': round(size_mb, 2),
                        'extension': ext
                    })
                
                # Sample for deeper analysis
                if len(files_to_analyze) < sample_size and ext in COMPATIBLE_EXTENSIONS:
                    files_to_analyze.append(str(item))
            
            elif item.is_dir():
                stats['subdirectories'] += 1
                # Calculate depth
                depth = len(item.relative_to(path).parts)
                stats['directory_depth'] = max(stats['directory_depth'], depth)
        
        # Analyze patterns that indicate problems
        stats = self._analyze_directory_patterns(stats)
        
        # Generate recommendations
        stats['recommendations'] = self._generate_directory_recommendations(stats)
        
        # Calculate overall suitability
        stats['rag_suitability_score'] = self._calculate_directory_score(stats)
        
        return stats
    
    def _analyze_directory_patterns(self, stats):
        """Detect problematic patterns in directory structure"""
        
        # Check for noise problem (too many files)
        if stats['total_files'] > 10000:
            stats['noise_level'] = 'extreme'
            stats['problematic_patterns'].append(
                f"⚠️ {stats['total_files']:,} files - Extreme noise risk! RAG will return random results"
            )
            stats['correlation_warning'] = True
        elif stats['total_files'] > 1000:
            stats['noise_level'] = 'high'
            stats['problematic_patterns'].append(
                f"⚠️ {stats['total_files']:,} files - High noise risk, consider filtering"
            )
        elif stats['total_files'] > 100:
            stats['noise_level'] = 'medium'
        
        # Check for correlation attempts (multiple diverse directories)
        if stats['subdirectories'] > 20 and stats['directory_depth'] > 3:
            stats['correlation_warning'] = True
            stats['problematic_patterns'].append(
                "🚫 Deep directory structure suggests correlation attempt - RAG doesn't correlate, it retrieves"
            )
        
        # Check for mixed data problem
        if stats['structured_data_files'] > 0 and stats['rag_compatible_files'] > 0:
            ratio = stats['structured_data_files'] / stats['total_files']
            if ratio > 0.3:
                stats['problematic_patterns'].append(
                    f"⚠️ {ratio*100:.0f}% structured data mixed with text - Will cause retrieval confusion"
                )
        
        # Check for wrong file types dominating
        if stats['file_types'].get('problematic', 0) > stats['rag_compatible_files']:
            stats['problematic_patterns'].append(
                "❌ More non-text files than text files - RAG needs text!"
            )
        
        # Check for massive data volume
        if stats['total_size_mb'] > 1000:  # 1GB+
            stats['problematic_patterns'].append(
                f"⚠️ {stats['total_size_mb']/1024:.1f}GB of data - Embedding costs will be massive"
            )
        
        return stats
    
    def _generate_directory_recommendations(self, stats):
        """Generate specific recommendations based on directory analysis"""
        recommendations = []
        
        # Noise level recommendations
        if stats['noise_level'] == 'extreme':
            recommendations.append("🚨 DO NOT USE RAG - Too many files will cause random, useless results")
            recommendations.append("✅ Alternative: Use Elasticsearch with careful indexing")
            recommendations.append("✅ Alternative: Create curated subset of most important documents")
        elif stats['noise_level'] == 'high':
            recommendations.append("⚠️ Filter documents first - only include directly relevant files")
            recommendations.append("💡 Consider metadata filtering to reduce search space")
        
        # Correlation warning
        if stats['correlation_warning']:
            recommendations.append("❌ RAG CANNOT correlate across documents - it only retrieves similar text")
            recommendations.append("✅ For correlation: Use data warehouse + BI tools")
            recommendations.append("✅ For analysis: Export to pandas/SQL for actual correlation")
        
        # Structured data recommendations
        if stats['structured_data_files'] > stats['rag_compatible_files']:
            recommendations.append("📊 Mostly structured data detected")
            recommendations.append("✅ Use PostgreSQL + LLM for SQL generation instead")
            recommendations.append("✅ Or convert tables to narrative descriptions first")
        
        # Mixed content recommendations
        if len(stats['by_extension']) > 10:
            recommendations.append("🔀 Too many file types - RAG works best with consistent formats")
            recommendations.append("💡 Standardize to PDF or markdown for best results")
        
        # Cost recommendations
        if stats['total_size_mb'] > 100:
            est_cost = (stats['total_size_mb'] / 100) * 10  # Rough estimate
            recommendations.append(f"💰 Estimated embedding cost: ${est_cost:.0f}/month minimum")
            recommendations.append("💡 Consider starting with subset of most important docs")
        
        return recommendations
    
    def _calculate_directory_score(self, stats):
        """Calculate directory suitability score for RAG"""
        score = 100
        
        # Heavy penalties
        if stats['noise_level'] == 'extreme':
            score -= 60
        elif stats['noise_level'] == 'high':
            score -= 30
        elif stats['noise_level'] == 'medium':
            score -= 10
        
        # Correlation attempt penalty
        if stats['correlation_warning']:
            score -= 40
        
        # File type penalties
        if stats['total_files'] > 0:
            structured_ratio = stats['structured_data_files'] / stats['total_files']
            problematic_ratio = stats['file_types'].get('problematic', 0) / stats['total_files']
            
            score -= structured_ratio * 50
            score -= problematic_ratio * 30
        
        # No compatible files = fail
        if stats['rag_compatible_files'] == 0:
            score = 0
        
        return max(0, min(100, int(score)))
    
    def analyze_correlation_queries(self, queries):
        """
        Check if queries expect correlation across multiple sources
        This is a KEY feature for detecting impossible RAG use cases
        """
        correlation_indicators = [
            'across all', 'correlation between', 'compare across',
            'trend across', 'pattern in all', 'relationship between',
            'analyze all', 'find patterns', 'discover insights',
            'what do all', 'common themes', 'synthesize from all'
        ]
        
        correlation_warnings = []
        
        for query in queries:
            query_lower = query.lower()
            for indicator in correlation_indicators:
                if indicator in query_lower:
                    correlation_warnings.append({
                        'query': query[:100],
                        'problem': f"Expects correlation ('{indicator}') - RAG only retrieves, doesn't analyze",
                        'solution': 'Use data analytics tools or custom logic'
                    })
                    break
        
        return correlation_warnings
    
    # [Keep all existing methods from original file - they stay the same]
    # analyze_documents, analyze_queries, _get_file_type, etc.
    # Just copying the existing methods below...
    
    def analyze_documents(self, file_paths):
        """Analyze documents for RAG compatibility"""
        if not file_paths:
            return {"error": "No files provided", "basic_score": 0}
        
        analysis = {
            "total_files": 0,
            "valid_files": 0,
            "file_types": defaultdict(int),
            "rag_compatibility": {},
            "warnings": [],
            "errors": [],
            "basic_score": 0
        }
        
        for file_path in file_paths:
            # Handle wildcards and expand paths
            import glob
            expanded_paths = glob.glob(file_path) if '*' in file_path else [file_path]
            
            for path in expanded_paths:
                if not os.path.exists(path):
                    analysis["errors"].append(f"File not found: {path}")
                    continue
                
                if not os.path.isfile(path):
                    analysis["errors"].append(f"Not a file: {path}")
                    continue
                
                analysis["total_files"] += 1
                file_type = self._get_file_type(path)
                analysis["file_types"][file_type] += 1
                
                # Analyze individual file
                compatibility = self._check_basic_compatibility(path, file_type)
                analysis["rag_compatibility"][os.path.basename(path)] = compatibility
                
                if compatibility["suitable_for_rag"]:
                    analysis["valid_files"] += 1
        
        # Calculate score
        if analysis["total_files"] > 0:
            analysis["basic_score"] = self._calculate_document_score(analysis)
        
        return analysis
    
    def analyze_queries(self, queries):
        """Analyze queries for RAG compatibility"""
        if not queries:
            return {"error": "No queries provided", "basic_score": 100}
        
        analysis = {
            "total_queries": len(queries),
            "complexity_scores": {},
            "problematic_patterns": [],
            "impossible_queries": [],
            "correlation_attempts": [],  # NEW: Track correlation attempts
            "basic_score": 0
        }
        
        # Check for correlation attempts
        correlation_warnings = self.analyze_correlation_queries(queries)
        if correlation_warnings:
            analysis["correlation_attempts"] = correlation_warnings
            for warning in correlation_warnings:
                analysis["impossible_queries"].append(warning['query'][:50] + "...")
        
        for i, query in enumerate(queries):
            if not query or not query.strip():
                continue
                
            score = self._analyze_query_complexity(query)
            analysis["complexity_scores"][f"query_{i+1}"] = {
                "query": query[:100] + "..." if len(query) > 100 else query,
                "complexity": score["complexity"],
                "issues": score["issues"]
            }
            
            if score["complexity"] == "high":
                analysis["problematic_patterns"].append(query[:50] + "...")
                if "mathematical" in str(score["issues"]).lower() or "calculation" in str(score["issues"]).lower():
                    analysis["impossible_queries"].append(query[:50] + "...")
        
        analysis["basic_score"] = self._calculate_query_score(analysis)
        return analysis
    
    def _get_file_type(self, file_path):
        """Determine file type category"""
        ext = os.path.splitext(file_path)[1].lower()
        
        for category, extensions in self.supported_formats.items():
            if ext in extensions:
                return category
        
        # Try to guess from mimetype
        mime_type, _ = mimetypes.guess_type(file_path)
        if mime_type:
            if 'text' in mime_type:
                return 'text'
            elif 'image' in mime_type:
                return 'image'
        
        return 'unknown'
    
    def _check_basic_compatibility(self, file_path, file_type):
        """Check if file is compatible with RAG"""
        try:
            file_size = os.path.getsize(file_path)
        except:
            file_size = 0
        
        compatibility = {
            "suitable_for_rag": True,
            "confidence": "medium",
            "issues": [],
            "recommendations": [],
            "size_mb": round(file_size / (1024 * 1024), 2)
        }
        
        # Size checks
        if file_size > 50 * 1024 * 1024:  # 50MB
            compatibility["issues"].append("Large file (>50MB) - will need chunking strategy")
            compatibility["recommendations"].append("Split into smaller documents")
            compatibility["confidence"] = "low"
        elif file_size < 100:  # Less than 100 bytes
            compatibility["issues"].append("File too small - may be empty")
            compatibility["suitable_for_rag"] = False
            compatibility["confidence"] = "low"
        
        # Format-specific checks
        if file_type == 'structured':
            compatibility["suitable_for_rag"] = False
            compatibility["issues"].append("Structured data (Excel/CSV/JSON) - RAG can't handle tables well")
            compatibility["recommendations"].append("Use SQL database + LLM instead")
            compatibility["confidence"] = "high"
        
        elif file_type == 'image':
            compatibility["suitable_for_rag"] = False
            compatibility["issues"].append("Image file - no text to embed")
            compatibility["recommendations"].append("Use OCR first or vision models")
            compatibility["confidence"] = "high"
        
        elif file_type == 'unknown':
            compatibility["suitable_for_rag"] = False
            compatibility["issues"].append("Unknown file format")
            compatibility["recommendations"].append("Convert to PDF or text first")
            compatibility["confidence"] = "medium"
        
        elif file_type == 'code':
            compatibility["issues"].append("Code files need specialized embeddings")
            compatibility["recommendations"].append("Consider code-specific models like CodeBERT")
            compatibility["confidence"] = "medium"
        
        elif file_type == 'pdf':
            compatibility["confidence"] = "high"
            compatibility["recommendations"].append("Good for RAG - ensure text is extractable")
        
        return compatibility
    
    def _analyze_query_complexity(self, query):
        """Analyze if query can be answered by RAG"""
        query_lower = query.lower()
        
        # More nuanced patterns - distinguishing between retrieval and execution
        aggregation_patterns = ['sum of all', 'total across', 'average across', 'aggregate', 'combine all']
        execution_patterns = ['calculate', 'compute', 'solve for']
        simple_lookup = ['what is', 'find', 'show me', 'retrieve', 'get', 'list']
        
        # Keep existing patterns
        reasoning_patterns = [
            'why did', 'analyze why', 'root cause', 'explain why',
            'compare and contrast', 'evaluate', 'assess the impact',
            'predict', 'forecast', 'what will happen if'
        ]
        
        temporal_patterns = [
            'latest', 'most recent', 'current', 'today', 'yesterday',
            'this week', 'last month', 'real-time', 'now', 'at this moment'
        ]
        
        multi_step_patterns = [
            ' and then ', ' after that ', 'step by step',
            'first.*then', 'followed by'
        ]
        
        issues = []
        complexity = "low"
        
        # Check aggregation across multiple sources
        if any(pattern in query_lower for pattern in aggregation_patterns):
            issues.append("Requires aggregation across multiple sources - RAG retrieves but can't combine")
            complexity = "high"
        
        # Check execution needs
        elif any(pattern in query_lower for pattern in execution_patterns):
            issues.append("Requires execution - RAG retrieves formulas but can't run calculations")
            complexity = "high"
        
        # Check simple table lookup
        elif any(pattern in query_lower for pattern in simple_lookup) and 'table' in query_lower:
            issues.append("Table lookups work if table fits in single chunk (<50 rows)")
            complexity = "low"
        
        # Check for complex reasoning
        elif any(pattern in query_lower for pattern in reasoning_patterns):
            issues.append("Requires reasoning/analysis - RAG only retrieves, doesn't think")
            complexity = "medium"
        
        # Check for temporal requirements
        elif any(pattern in query_lower for pattern in temporal_patterns):
            issues.append("Requires current/real-time data - RAG data is static")
            complexity = "medium"
        
        # Check for multi-step queries
        elif any(pattern in query_lower for pattern in multi_step_patterns):
            issues.append("Multi-step query - needs decomposition")
            complexity = "medium"
        
        # Check query length
        if len(query) > 500:
            issues.append("Very long query - may need simplification")
            if complexity == "low":
                complexity = "medium"
        
        # Default if no issues found
        if not issues:
            issues = ["Query appears suitable for RAG"]
        
        return {
            "complexity": complexity,
            "issues": issues
        }
    
    def _calculate_document_score(self, analysis):
        """Calculate document suitability score (0-100)"""
        if analysis["total_files"] == 0:
            return 0
            
        score = 100
        
        # Heavy penalty for structured files
        if "structured" in analysis["file_types"]:
            structured_ratio = analysis["file_types"]["structured"] / analysis["total_files"]
            score -= structured_ratio * 60
        
        # Penalty for images
        if "image" in analysis["file_types"]:
            image_ratio = analysis["file_types"]["image"] / analysis["total_files"]
            score -= image_ratio * 50
        
        # Penalty for unknown formats
        if "unknown" in analysis["file_types"]:
            unknown_ratio = analysis["file_types"]["unknown"] / analysis["total_files"]
            score -= unknown_ratio * 40
        
        # Penalty for code files (need special handling)
        if "code" in analysis["file_types"]:
            code_ratio = analysis["file_types"]["code"] / analysis["total_files"]
            score -= code_ratio * 20
        
        # Bonus for PDF and text files
        good_formats = analysis["file_types"].get("pdf", 0) + analysis["file_types"].get("text", 0)
        if good_formats > 0:
            good_ratio = good_formats / analysis["total_files"]
            score += good_ratio * 10
        
        return max(0, min(100, int(score)))
    
    def _calculate_query_score(self, analysis):
        """Calculate query suitability score (0-100)"""
        if analysis["total_queries"] == 0:
            return 100
            
        score = 100
        
        # Heavy penalty for correlation attempts
        if analysis.get("correlation_attempts"):
            score -= len(analysis["correlation_attempts"]) * 20
        
        # Count complexity levels
        high_complexity = sum(1 for q in analysis["complexity_scores"].values() 
                             if q["complexity"] == "high")
        medium_complexity = sum(1 for q in analysis["complexity_scores"].values() 
                               if q["complexity"] == "medium")
        
        # Heavy penalty for high complexity (likely impossible)
        if high_complexity > 0:
            score -= (high_complexity / analysis["total_queries"]) * 70
        
        # Medium penalty for medium complexity
        if medium_complexity > 0:
            score -= (medium_complexity / analysis["total_queries"]) * 30
        
        return max(0, min(100, int(score)))
    
    def generate_report(self, doc_analysis=None, query_analysis=None, dir_analysis=None):
        """Generate human-readable report"""
        # Handle missing analyses
        if not doc_analysis:
            doc_analysis = {"basic_score": 100, "total_files": 0, "file_types": {}}
        if not query_analysis:
            query_analysis = {"basic_score": 100, "total_queries": 0, "problematic_patterns": []}
        
        # Calculate overall score
        scores_to_average = []
        if doc_analysis.get("total_files", 0) > 0:
            scores_to_average.append(doc_analysis["basic_score"])
        if query_analysis.get("total_queries", 0) > 0:
            scores_to_average.append(query_analysis["basic_score"])
        if dir_analysis and dir_analysis.get("rag_suitability_score") is not None:
            scores_to_average.append(dir_analysis["rag_suitability_score"])
        
        if scores_to_average:
            overall_score = sum(scores_to_average) / len(scores_to_average)
        else:
            overall_score = 0
        
        report = []
        report.append("=" * 60)
        report.append("RAGnostics Analysis Report")
        report.append("=" * 60)
        report.append(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        report.append(f"Version: {__version__}")
        report.append("")
        
        # Overall verdict with emoji
        report.append(f"OVERALL RAG FEASIBILITY: {overall_score:.0f}%")
        
        if overall_score >= 70:
            report.append("✅ RAG is suitable for your use case")
        elif overall_score >= 40:
            report.append("⚠️  RAG might work with significant optimization")
        else:
            report.append("❌ RAG is NOT recommended for your use case")
        
        report.append("")
        report.append("-" * 60)
        
        # NEW: Directory Analysis Section
        if dir_analysis and not dir_analysis.get("error"):
            report.append("DIRECTORY ANALYSIS")
            report.append("-" * 60)
            report.append(f"Total files: {dir_analysis['total_files']:,}")
            report.append(f"Total size: {dir_analysis['total_size_mb']:.1f} MB")
            report.append(f"Directory depth: {dir_analysis['directory_depth']} levels")
            report.append(f"Noise level: {dir_analysis['noise_level'].upper()}")
            report.append(f"Directory score: {dir_analysis['rag_suitability_score']}%")
            
            if dir_analysis['correlation_warning']:
                report.append("")
                report.append("🚨 CORRELATION WARNING:")
                report.append("   You appear to be trying to correlate data across directories.")
                report.append("   RAG does NOT correlate - it only retrieves similar text.")
                report.append("   Use data analytics tools for correlation.")
            
            if dir_analysis['problematic_patterns']:
                report.append("")
                report.append("Problems detected:")
                for pattern in dir_analysis['problematic_patterns']:
                    report.append(f"  {pattern}")
            
            if dir_analysis['recommendations']:
                report.append("")
                report.append("Directory-specific recommendations:")
                for rec in dir_analysis['recommendations'][:5]:  # Limit to top 5
                    report.append(f"  {rec}")
            
            report.append("")
        
        # Document Analysis
        if doc_analysis.get("total_files", 0) > 0:
            report.append("-" * 60)
            report.append("DOCUMENT ANALYSIS")
            report.append("-" * 60)
            report.append(f"Files analyzed: {doc_analysis['total_files']}")
            report.append(f"Document score: {doc_analysis['basic_score']}%")
            report.append(f"File types found: {dict(doc_analysis['file_types'])}")
            
            # Warnings
            if "structured" in doc_analysis["file_types"] and doc_analysis["file_types"]["structured"] > 0:
                report.append("")
                report.append(f"⚠️  Found {doc_analysis['file_types']['structured']} structured files (Excel/CSV)")
                report.append("   Small tables (<50 rows) can work if they fit in single chunks.")
                report.append("   Large tables or cross-table queries need SQL instead.")
            
            if "image" in doc_analysis["file_types"] and doc_analysis["file_types"]["image"] > 0:
                report.append("")
                report.append(f"⚠️  Found {doc_analysis['file_types']['image']} image files")
                report.append("   RAG needs text. Use OCR or vision models instead.")
            
            report.append("")
        
        # Query Analysis
        if query_analysis.get("total_queries", 0) > 0:
            report.append("-" * 60)
            report.append("QUERY ANALYSIS")
            report.append("-" * 60)
            report.append(f"Queries analyzed: {query_analysis['total_queries']}")
            report.append(f"Query score: {query_analysis['basic_score']}%")
            
            # NEW: Correlation attempts
            if query_analysis.get("correlation_attempts"):
                report.append("")
                report.append(f"❌ {len(query_analysis['correlation_attempts'])} queries expect correlation/analysis:")
                for attempt in query_analysis['correlation_attempts'][:3]:
                    report.append(f"   - \"{attempt['query'][:50]}...\"")
                    report.append(f"     Problem: {attempt['problem']}")
                report.append("   RAG cannot correlate data - use analytics tools instead.")
            
            if query_analysis.get("impossible_queries"):
                report.append("")
                report.append(f"❌ {len(query_analysis['impossible_queries'])} queries are impossible for RAG:")
                for q in query_analysis['impossible_queries'][:3]:
                    report.append(f"   - {q}")
                report.append("   These require calculations or real-time data.")
            
            if query_analysis.get("problematic_patterns"):
                report.append("")
                report.append(f"⚠️  {len(query_analysis['problematic_patterns'])} queries might fail:")
                for q in query_analysis['problematic_patterns'][:3]:
                    report.append(f"   - {q}")
            
            report.append("")
        
        # Recommendations
        report.append("-" * 60)
        report.append("RECOMMENDATIONS")
        report.append("-" * 60)
        
        if overall_score < 40:
            report.append("Instead of RAG, consider:")
            
            # Check what the main problems are
            has_structured = "structured" in doc_analysis.get("file_types", {})
            has_calculations = any("calculat" in str(q).lower() for q in query_analysis.get("problematic_patterns", []))
            has_correlation = query_analysis.get("correlation_attempts") or (dir_analysis and dir_analysis.get("correlation_warning"))
            
            if has_structured:
                report.append("• SQL database + LLM for structured data")
            if has_calculations:
                report.append("• Custom logic layer for calculations")
            if has_correlation:
                report.append("• Data warehouse + BI tools for correlation analysis")
                report.append("• Pandas/Spark for data processing")
            if dir_analysis and dir_analysis.get('noise_level') in ['high', 'extreme']:
                report.append("• Elasticsearch with careful curation")
                report.append("• Document management system with good search")
            if not has_structured and not has_calculations and not has_correlation:
                report.append("• Fine-tuned model for your specific use case")
                report.append("• Perplexity API for web-based queries")
        
        elif overall_score < 70:
            report.append("To improve RAG performance:")
            report.append("• Convert structured data to narrative text")
            report.append("• Simplify complex queries")
            report.append("• Use hybrid search (vector + keyword)")
            report.append("• Implement query preprocessing")
            if dir_analysis and dir_analysis.get('total_files', 0) > 1000:
                report.append("• Curate documents - quality over quantity")
        
        else:
            report.append("Your use case is well-suited for RAG!")
            report.append("• Consider using OpenAI or Mistral embeddings")
            report.append("• Pinecone or Weaviate for vector storage")
            report.append("• Implement proper chunking strategy")
        
        report.append("")
        report.append("-" * 60)
        report.append("For detailed analysis and cost estimates:")
        report.append("Visit https://ragnostics.com")
        report.append("-" * 60)
        
        return "\n".join(report)

def main():
    # Check environment first
    check_environment()
    
    parser = argparse.ArgumentParser(
        description='RAGnostics - Check if RAG is right for your project',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Analyze a single document
  python3 ragnostics-core.py --docs report.pdf
  
  # Analyze multiple documents  
  python3 ragnostics-core.py --docs *.pdf *.docx
  
  # NEW: Scan entire directory
  python3 ragnostics-core.py --scan-directory /path/to/documents
  
  # Scan directory with queries
  python3 ragnostics-core.py --scan-directory ./data --queries "Find patterns across all departments"
  
  # Analyze queries
  python3 ragnostics-core.py --queries "What is our refund policy?" "Calculate total revenue"
  
  # Save report
  python3 ragnostics-core.py --scan-directory ./docs --output analysis.txt
  
  # Get JSON output for integration
  python3 ragnostics-core.py --scan-directory ./data --json
        """
    )
    
    parser.add_argument('--docs', nargs='+', help='Document files to analyze')
    parser.add_argument('--scan-directory', help='Scan entire directory for RAG suitability')
    parser.add_argument('--no-recursive', action='store_true', help='Don\'t scan subdirectories')
    parser.add_argument('--queries', nargs='+', help='Sample queries your users would ask')
    parser.add_argument('--queries-file', help='Text file with queries (one per line)')
    parser.add_argument('--output', help='Save report to file')
    parser.add_argument('--json', action='store_true', help='Output as JSON')
    parser.add_argument('--version', action='version', version=f'RAGnostics Core {__version__}')
    
    args = parser.parse_args()
    
    # Show help if no arguments
    if not args.docs and not args.queries and not args.queries_file and not args.scan_directory:
        parser.print_help()
        print("\n❌ Error: Provide at least --docs, --queries, or --scan-directory")
        sys.exit(1)
    
    analyzer = RAGAnalyzerCore()
    
    # NEW: Directory scanning
    dir_analysis = None
    if args.scan_directory:
        print(f"📁 Scanning directory: {args.scan_directory}")
        dir_analysis = analyzer.scan_directory(
            args.scan_directory,
            recursive=not args.no_recursive
        )
        if dir_analysis.get("error"):
            print(f"❌ {dir_analysis['error']}")
            sys.exit(1)
        print(f"  Found {dir_analysis['total_files']:,} files ({dir_analysis['total_size_mb']:.1f} MB)")
        if dir_analysis['noise_level'] in ['high', 'extreme']:
            print(f"  ⚠️  WARNING: {dir_analysis['noise_level'].upper()} noise level detected!")
    
    # Analyze documents
    doc_analysis = None
    if args.docs:
        print("📄 Analyzing documents...")
        doc_analysis = analyzer.analyze_documents(args.docs)
        if doc_analysis.get("errors"):
            for error in doc_analysis["errors"]:
                print(f"  ❌ {error}")
    
    # Analyze queries
    query_analysis = None
    queries = []
    
    if args.queries:
        queries.extend(args.queries)
    
    if args.queries_file:
        if os.path.exists(args.queries_file):
            with open(args.queries_file, 'r') as f:
                queries.extend([line.strip() for line in f if line.strip()])
        else:
            print(f"❌ Queries file not found: {args.queries_file}")
    
    if queries:
        print(f"🔍 Analyzing {len(queries)} queries...")
        query_analysis = analyzer.analyze_queries(queries)
    
    # Generate output
    if args.json:
        result = {
            "timestamp": datetime.now().isoformat(),
            "version": __version__,
            "document_analysis": doc_analysis,
            "query_analysis": query_analysis,
            "directory_analysis": dir_analysis  # NEW
        }
        output = json.dumps(result, indent=2)
    else:
        output = analyzer.generate_report(doc_analysis, query_analysis, dir_analysis)
    
    # Save or print
    if args.output:
        with open(args.output, 'w') as f:
            f.write(output)
        print(f"\n✅ Report saved to {args.output}")
    else:
        print("\n" + output)

if __name__ == "__main__":
    main()
