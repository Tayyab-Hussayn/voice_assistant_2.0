import requests
import json
import time
import re
from typing import Dict, List, Any, Optional
from urllib.parse import quote_plus, urlparse
import hashlib
from bs4 import BeautifulSoup

class WebSearchSystem:
    """
    Web Search Integration with Kiro CLI capabilities
    Provides web search with result processing and source attribution
    """
    
    def __init__(self):
        self.search_history = []
        self.max_verbatim_words = 30  # Compliance limit
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        })
        self.search_engines = {
            "duckduckgo": {
                "url": "https://api.duckduckgo.com/",
                "params": {"format": "json", "no_html": "1", "skip_disambig": "1"}
            },
            "searx": {
                "url": "https://searx.be/search",
                "params": {"format": "json", "safesearch": "1"}
            }
        }
        
    def search_web(self, query: str, num_results: int = 10, engine: str = "duckduckgo") -> Dict[str, Any]:
        """
        Search the web for information
        
        Args:
            query: Search query
            num_results: Number of results to return
            engine: Search engine to use
        """
        start_time = time.time()
        
        try:
            if engine == "duckduckgo":
                results = self._search_duckduckgo(query, num_results)
            elif engine == "searx":
                results = self._search_searx(query, num_results)
            else:
                return {"success": False, "error": f"Unknown search engine: {engine}"}
            
            # Process and format results
            processed_results = self._process_search_results(results, query)
            
            search_result = {
                "success": True,
                "query": query,
                "num_results": len(processed_results),
                "results": processed_results,
                "search_time": time.time() - start_time,
                "engine": engine
            }
            
            # Add to search history
            self.search_history.append({
                "query": query,
                "timestamp": time.time(),
                "results_count": len(processed_results),
                "engine": engine
            })
            
            return search_result
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query": query,
                "search_time": time.time() - start_time
            }
    
    def _search_duckduckgo(self, query: str, num_results: int) -> List[Dict]:
        """Search using DuckDuckGo API"""
        try:
            params = self.search_engines["duckduckgo"]["params"].copy()
            params["q"] = query
            
            response = requests.get(
                self.search_engines["duckduckgo"]["url"],
                params=params,
                timeout=10,
                headers={"User-Agent": "JARVIS-AI-Assistant/1.0"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                results = []
                
                # Get instant answer if available
                if data.get("Abstract"):
                    results.append({
                        "title": data.get("Heading", "Instant Answer"),
                        "url": data.get("AbstractURL", ""),
                        "snippet": data.get("Abstract", ""),
                        "source": "DuckDuckGo Instant Answer"
                    })
                
                # Get related topics
                for topic in data.get("RelatedTopics", [])[:num_results]:
                    if isinstance(topic, dict) and topic.get("Text"):
                        results.append({
                            "title": topic.get("Text", "").split(" - ")[0],
                            "url": topic.get("FirstURL", ""),
                            "snippet": topic.get("Text", ""),
                            "source": "DuckDuckGo"
                        })
                
                return results[:num_results]
            
        except Exception as e:
            print(f"DuckDuckGo search failed: {e}")
        
        return []
    
    def _search_searx(self, query: str, num_results: int) -> List[Dict]:
        """Search using SearX API (fallback)"""
        try:
            params = self.search_engines["searx"]["params"].copy()
            params["q"] = query
            params["categories"] = "general"
            
            response = requests.get(
                self.search_engines["searx"]["url"],
                params=params,
                timeout=10,
                headers={"User-Agent": "JARVIS-AI-Assistant/1.0"}
            )
            
            if response.status_code == 200:
                data = response.json()
                
                results = []
                for result in data.get("results", [])[:num_results]:
                    results.append({
                        "title": result.get("title", ""),
                        "url": result.get("url", ""),
                        "snippet": result.get("content", ""),
                        "source": "SearX"
                    })
                
                return results
            
        except Exception as e:
            print(f"SearX search failed: {e}")
        
        return []
    
    def _process_search_results(self, results: List[Dict], query: str) -> List[Dict]:
        """Process and clean search results"""
        processed = []
        
        for i, result in enumerate(results, 1):
            # Clean and truncate snippet for compliance
            snippet = self._clean_text(result.get("snippet", ""))
            snippet = self._truncate_for_compliance(snippet)
            
            # Extract domain from URL
            domain = self._extract_domain(result.get("url", ""))
            
            processed_result = {
                "id": str(i),
                "title": self._clean_text(result.get("title", "")),
                "url": result.get("url", ""),
                "snippet": snippet,
                "domain": domain,
                "source": result.get("source", "Web"),
                "maxVerbatimWordLimit": self.max_verbatim_words,
                "publicDomain": False
            }
            
            processed.append(processed_result)
        
        return processed
    
    def _clean_text(self, text: str) -> str:
        """Clean text content"""
        if not text:
            return ""
        
        # Remove HTML tags
        text = re.sub(r'<[^>]+>', '', text)
        
        # Clean up whitespace
        text = re.sub(r'\s+', ' ', text)
        
        # Remove special characters that might cause issues
        text = re.sub(r'[^\w\s\-.,!?;:()\[\]{}"\']', '', text)
        
        return text.strip()
    
    def _truncate_for_compliance(self, text: str, max_words: int = None) -> str:
        """Truncate text to comply with verbatim limits"""
        if not text:
            return ""
        
        max_words = max_words or self.max_verbatim_words
        words = text.split()
        
        if len(words) <= max_words:
            return text
        
        return ' '.join(words[:max_words]) + '...'
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        if not url:
            return ""
        
        try:
            from urllib.parse import urlparse
            parsed = urlparse(url)
            return parsed.netloc
        except:
            return ""
    
    def get_search_history(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Get recent search history"""
        return self.search_history[-limit:] if limit > 0 else self.search_history
    
    def clear_search_history(self):
        """Clear search history"""
        self.search_history.clear()
    
    def fetch_content(self, url: str, mode: str = "selective", search_terms: str = None) -> Dict[str, Any]:
        """
        Fetch and extract content from a URL
        
        Args:
            url: URL to fetch
            mode: 'selective', 'truncated', or 'full'
            search_terms: Keywords for selective mode
        """
        try:
            response = self.session.get(url, timeout=10)
            response.raise_for_status()
            
            # Parse HTML content
            soup = BeautifulSoup(response.content, 'html.parser')
            
            # Remove script and style elements
            for script in soup(["script", "style"]):
                script.decompose()
            
            # Extract text content
            text = soup.get_text()
            
            # Clean up text
            lines = (line.strip() for line in text.splitlines())
            chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
            text = ' '.join(chunk for chunk in chunks if chunk)
            
            if mode == "full":
                return {
                    "success": True,
                    "content": text,
                    "url": url,
                    "title": soup.title.string if soup.title else "No title",
                    "mode": mode
                }
            elif mode == "truncated":
                return {
                    "success": True,
                    "content": text[:8000],
                    "url": url,
                    "title": soup.title.string if soup.title else "No title",
                    "mode": mode,
                    "truncated": len(text) > 8000
                }
            elif mode == "selective":
                if search_terms:
                    # Find relevant sections
                    relevant_content = self._extract_relevant_sections(text, search_terms)
                else:
                    # Return beginning of page
                    relevant_content = text[:2000]
                
                return {
                    "success": True,
                    "content": relevant_content,
                    "url": url,
                    "title": soup.title.string if soup.title else "No title",
                    "mode": mode,
                    "search_terms": search_terms
                }
            
        except requests.RequestException as e:
            return {
                "success": False,
                "error": f"Failed to fetch URL: {str(e)}",
                "url": url
            }
        except Exception as e:
            return {
                "success": False,
                "error": f"Content extraction failed: {str(e)}",
                "url": url
            }
    
    def _extract_relevant_sections(self, text: str, search_terms: str) -> str:
        """Extract sections around search terms"""
        terms = [term.strip().lower() for term in search_terms.split()]
        text_lower = text.lower()
        
        relevant_sections = []
        words = text.split()
        
        for i, word in enumerate(words):
            if any(term in word.lower() for term in terms):
                # Extract ~10 lines before and after
                start = max(0, i - 50)
                end = min(len(words), i + 50)
                section = ' '.join(words[start:end])
                relevant_sections.append(section)
        
        if relevant_sections:
            return '\n\n---\n\n'.join(relevant_sections[:3])  # Max 3 sections
        else:
            return text[:2000]  # Fallback to beginning

# Integration class for JARVIS
class WebSearch:
    """Web Search integration for JARVIS"""
    
    def __init__(self):
        self.search_system = WebSearchSystem()
    
    def search(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Main search interface for JARVIS"""
        return self.search_system.search_web(query, num_results)
    
    def quick_search(self, query: str) -> str:
        """Quick search with formatted response"""
        result = self.search_system.search_web(query, 3)
        
        if result["success"]:
            if result["results"]:
                response = f"🔍 Found {result['num_results']} results for '{query}':\n\n"
                
                for i, res in enumerate(result["results"], 1):
                    response += f"{i}. **{res['title']}**\n"
                    response += f"   {res['snippet']}\n"
                    response += f"   Source: {res['domain']}\n\n"
                
                return response
            else:
                return f"🔍 No results found for '{query}'"
        else:
            return f"❌ Search failed: {result['error']}"
