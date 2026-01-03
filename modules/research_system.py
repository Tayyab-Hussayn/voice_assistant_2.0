import json
import time
from typing import Dict, List, Any, Optional
from datetime import datetime
import re

class ResearchSystem:
    """
    Research & Analysis System with Kiro CLI capabilities
    Provides automated research workflows and information synthesis
    """
    
    def __init__(self, web_search=None, ai_handler=None):
        self.web_search = web_search
        self.ai_handler = ai_handler
        self.research_sessions = {}
        self.analysis_cache = {}
        
    def start_research(self, topic: str, depth: str = "medium") -> Dict[str, Any]:
        """
        Start a comprehensive research session
        
        Args:
            topic: Research topic
            depth: Research depth (quick, medium, deep)
        """
        session_id = f"research_{int(time.time())}"
        
        research_plan = self._create_research_plan(topic, depth)
        
        session = {
            "id": session_id,
            "topic": topic,
            "depth": depth,
            "plan": research_plan,
            "results": [],
            "sources": [],
            "analysis": None,
            "created_at": datetime.now().isoformat(),
            "status": "active"
        }
        
        self.research_sessions[session_id] = session
        
        return {
            "success": True,
            "session_id": session_id,
            "plan": research_plan,
            "message": f"Research session started for '{topic}'"
        }
    
    def execute_research(self, session_id: str) -> Dict[str, Any]:
        """Execute research plan for a session"""
        if session_id not in self.research_sessions:
            return {"success": False, "error": "Research session not found"}
        
        session = self.research_sessions[session_id]
        
        try:
            # Execute each research step
            for step in session["plan"]["steps"]:
                result = self._execute_research_step(step)
                session["results"].append(result)
                
                if result["success"] and result.get("sources"):
                    session["sources"].extend(result["sources"])
            
            # Generate analysis
            analysis = self._analyze_research_results(session)
            session["analysis"] = analysis
            session["status"] = "completed"
            
            return {
                "success": True,
                "session_id": session_id,
                "results": session["results"],
                "analysis": analysis,
                "sources_count": len(session["sources"])
            }
            
        except Exception as e:
            session["status"] = "failed"
            return {"success": False, "error": str(e)}
    
    def quick_research(self, topic: str) -> str:
        """Quick research with immediate results"""
        if not self.web_search:
            return "❌ Web search not available"
        
        # Search for information
        search_result = self.web_search.search(topic, 5)
        
        if not search_result["success"]:
            return f"❌ Research failed: {search_result['error']}"
        
        if not search_result["results"]:
            return f"🔍 No information found for '{topic}'"
        
        # Format research summary
        response = f"🔬 Quick Research: {topic}\n\n"
        
        for i, result in enumerate(search_result["results"], 1):
            response += f"{i}. **{result['title']}**\n"
            response += f"   {result['snippet']}\n"
            response += f"   📍 {result['domain']}\n\n"
        
        response += f"📊 Found {len(search_result['results'])} sources"
        
        return response
    
    def analyze_content(self, content: str, analysis_type: str = "summary") -> Dict[str, Any]:
        """
        Analyze content with different analysis types
        
        Args:
            content: Content to analyze
            analysis_type: Type of analysis (summary, keywords, sentiment, structure)
        """
        try:
            if analysis_type == "summary":
                return self._summarize_content(content)
            elif analysis_type == "keywords":
                return self._extract_keywords(content)
            elif analysis_type == "sentiment":
                return self._analyze_sentiment(content)
            elif analysis_type == "structure":
                return self._analyze_structure(content)
            else:
                return {"success": False, "error": f"Unknown analysis type: {analysis_type}"}
                
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _create_research_plan(self, topic: str, depth: str) -> Dict[str, Any]:
        """Create research plan based on topic and depth"""
        base_queries = [topic]
        
        if depth == "quick":
            steps = [{"type": "search", "query": topic, "max_results": 3}]
        elif depth == "medium":
            steps = [
                {"type": "search", "query": topic, "max_results": 5},
                {"type": "search", "query": f"{topic} overview", "max_results": 3},
                {"type": "search", "query": f"{topic} examples", "max_results": 3}
            ]
        else:  # deep
            steps = [
                {"type": "search", "query": topic, "max_results": 8},
                {"type": "search", "query": f"{topic} overview", "max_results": 5},
                {"type": "search", "query": f"{topic} examples", "max_results": 5},
                {"type": "search", "query": f"{topic} best practices", "max_results": 3},
                {"type": "search", "query": f"{topic} latest trends", "max_results": 3}
            ]
        
        return {
            "topic": topic,
            "depth": depth,
            "steps": steps,
            "estimated_time": len(steps) * 2  # 2 seconds per step
        }
    
    def _execute_research_step(self, step: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single research step"""
        if step["type"] == "search" and self.web_search:
            result = self.web_search.search(step["query"], step.get("max_results", 5))
            
            if result["success"]:
                sources = [{"title": r["title"], "url": r.get("url", ""), "domain": r["domain"]} 
                          for r in result["results"]]
                
                return {
                    "success": True,
                    "step_type": "search",
                    "query": step["query"],
                    "results_count": len(result["results"]),
                    "sources": sources
                }
            else:
                return {
                    "success": False,
                    "step_type": "search",
                    "query": step["query"],
                    "error": result["error"]
                }
        
        return {"success": False, "error": "Unknown step type or missing dependencies"}
    
    def _analyze_research_results(self, session: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze collected research results"""
        total_sources = len(session["sources"])
        successful_steps = sum(1 for r in session["results"] if r["success"])
        
        # Extract key information
        domains = list(set(s["domain"] for s in session["sources"]))
        
        return {
            "topic": session["topic"],
            "total_sources": total_sources,
            "successful_steps": successful_steps,
            "unique_domains": len(domains),
            "top_domains": domains[:5],
            "research_quality": "high" if total_sources >= 10 else "medium" if total_sources >= 5 else "basic",
            "completed_at": datetime.now().isoformat()
        }
    
    def _summarize_content(self, content: str) -> Dict[str, Any]:
        """Generate content summary"""
        sentences = re.split(r'[.!?]+', content)
        word_count = len(content.split())
        
        # Simple extractive summary (first few sentences)
        summary_sentences = sentences[:3] if len(sentences) >= 3 else sentences
        summary = '. '.join(s.strip() for s in summary_sentences if s.strip()) + '.'
        
        return {
            "success": True,
            "summary": summary,
            "original_length": word_count,
            "summary_length": len(summary.split()),
            "compression_ratio": round(len(summary.split()) / word_count * 100, 1) if word_count > 0 else 0
        }
    
    def _extract_keywords(self, content: str) -> Dict[str, Any]:
        """Extract keywords from content"""
        # Simple keyword extraction
        words = re.findall(r'\b[a-zA-Z]{4,}\b', content.lower())
        
        # Count word frequency
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Get top keywords
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        return {
            "success": True,
            "keywords": [{"word": word, "frequency": freq} for word, freq in keywords],
            "total_words": len(words),
            "unique_words": len(word_freq)
        }
    
    def _analyze_sentiment(self, content: str) -> Dict[str, Any]:
        """Basic sentiment analysis"""
        positive_words = ['good', 'great', 'excellent', 'amazing', 'wonderful', 'fantastic', 'positive', 'success']
        negative_words = ['bad', 'terrible', 'awful', 'horrible', 'negative', 'failure', 'problem', 'issue']
        
        words = content.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        if positive_count > negative_count:
            sentiment = "positive"
        elif negative_count > positive_count:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        return {
            "success": True,
            "sentiment": sentiment,
            "positive_indicators": positive_count,
            "negative_indicators": negative_count,
            "confidence": abs(positive_count - negative_count) / max(len(words), 1)
        }
    
    def _analyze_structure(self, content: str) -> Dict[str, Any]:
        """Analyze content structure"""
        lines = content.split('\n')
        paragraphs = [p for p in content.split('\n\n') if p.strip()]
        sentences = re.split(r'[.!?]+', content)
        
        return {
            "success": True,
            "lines": len(lines),
            "paragraphs": len(paragraphs),
            "sentences": len([s for s in sentences if s.strip()]),
            "avg_sentence_length": round(len(content.split()) / max(len(sentences), 1), 1),
            "structure_type": "structured" if len(paragraphs) > 3 else "simple"
        }

# Integration class for JARVIS
class ResearchAnalysis:
    """Research & Analysis integration for JARVIS"""
    
    def __init__(self, web_search=None, ai_handler=None):
        self.research_system = ResearchSystem(web_search, ai_handler)
    
    def research(self, topic: str, depth: str = "medium") -> str:
        """Start and execute research"""
        # Start research session
        start_result = self.research_system.start_research(topic, depth)
        
        if not start_result["success"]:
            return f"❌ Failed to start research: {start_result['error']}"
        
        # Execute research
        execute_result = self.research_system.execute_research(start_result["session_id"])
        
        if not execute_result["success"]:
            return f"❌ Research failed: {execute_result['error']}"
        
        # Format results
        analysis = execute_result["analysis"]
        response = f"🔬 Research Complete: {topic}\n\n"
        response += f"📊 Quality: {analysis['research_quality'].title()}\n"
        response += f"📚 Sources: {analysis['total_sources']}\n"
        response += f"🌐 Domains: {analysis['unique_domains']}\n"
        response += f"✅ Steps: {analysis['successful_steps']}\n\n"
        
        if analysis['top_domains']:
            response += f"🔗 Top Sources: {', '.join(analysis['top_domains'][:3])}\n"
        
        return response
    
    def quick_research(self, topic: str) -> str:
        """Quick research wrapper"""
        return self.research_system.quick_research(topic)
    
    def analyze(self, content: str, analysis_type: str = "summary") -> str:
        """Content analysis wrapper"""
        result = self.research_system.analyze_content(content, analysis_type)
        
        if not result["success"]:
            return f"❌ Analysis failed: {result['error']}"
        
        if analysis_type == "summary":
            return f"📝 Summary ({result['compression_ratio']}% of original):\n{result['summary']}"
        elif analysis_type == "keywords":
            keywords = [f"{kw['word']} ({kw['frequency']})" for kw in result['keywords'][:5]]
            return f"🔑 Top Keywords: {', '.join(keywords)}"
        elif analysis_type == "sentiment":
            return f"😊 Sentiment: {result['sentiment'].title()} (confidence: {result['confidence']:.2f})"
        elif analysis_type == "structure":
            return f"📋 Structure: {result['paragraphs']} paragraphs, {result['sentences']} sentences"
        
        return str(result)
