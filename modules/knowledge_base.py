import json
import sqlite3
import hashlib
import time
from typing import Dict, List, Any, Optional, Tuple
from datetime import datetime
import numpy as np
import re
from pathlib import Path

class KnowledgeBase:
    """
    Knowledge Base Foundation with vector database capabilities
    Provides persistent knowledge storage and retrieval
    """
    
    def __init__(self, db_path: str = "knowledge_base.db"):
        self.db_path = db_path
        self.conn = None
        self._init_database()
        
    def _init_database(self):
        """Initialize SQLite database with knowledge tables"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        # Create tables
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS knowledge_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                content_hash TEXT UNIQUE,
                title TEXT,
                content TEXT,
                source TEXT,
                category TEXT,
                tags TEXT,
                embedding_vector TEXT,
                created_at TEXT,
                updated_at TEXT,
                access_count INTEGER DEFAULT 0
            );
            
            CREATE TABLE IF NOT EXISTS knowledge_relations (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                entry_id_1 INTEGER,
                entry_id_2 INTEGER,
                relation_type TEXT,
                strength REAL,
                created_at TEXT,
                FOREIGN KEY (entry_id_1) REFERENCES knowledge_entries (id),
                FOREIGN KEY (entry_id_2) REFERENCES knowledge_entries (id)
            );
            
            CREATE TABLE IF NOT EXISTS search_history (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                query TEXT,
                results_count INTEGER,
                timestamp TEXT
            );
            
            CREATE INDEX IF NOT EXISTS idx_content_hash ON knowledge_entries(content_hash);
            CREATE INDEX IF NOT EXISTS idx_category ON knowledge_entries(category);
            CREATE INDEX IF NOT EXISTS idx_tags ON knowledge_entries(tags);
        """)
        self.conn.commit()
    
    def add_knowledge(self, title: str, content: str, source: str = "", 
                     category: str = "general", tags: List[str] = None) -> Dict[str, Any]:
        """Add knowledge entry to the database"""
        try:
            # Generate content hash for deduplication
            content_hash = hashlib.md5(content.encode()).hexdigest()
            
            # Check if entry already exists
            existing = self.conn.execute(
                "SELECT id FROM knowledge_entries WHERE content_hash = ?", 
                (content_hash,)
            ).fetchone()
            
            if existing:
                return {
                    "success": True,
                    "entry_id": existing["id"],
                    "message": "Knowledge entry already exists",
                    "duplicate": True
                }
            
            # Generate simple embedding (word frequency vector)
            embedding = self._generate_embedding(content)
            
            # Insert new entry
            tags_str = json.dumps(tags or [])
            timestamp = datetime.now().isoformat()
            
            cursor = self.conn.execute("""
                INSERT INTO knowledge_entries 
                (content_hash, title, content, source, category, tags, embedding_vector, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (content_hash, title, content, source, category, tags_str, 
                  json.dumps(embedding.tolist()), timestamp, timestamp))
            
            self.conn.commit()
            
            return {
                "success": True,
                "entry_id": cursor.lastrowid,
                "message": "Knowledge entry added successfully",
                "duplicate": False
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def search_knowledge(self, query: str, limit: int = 10, 
                        category: str = None) -> Dict[str, Any]:
        """Search knowledge base using text and vector similarity"""
        try:
            # Log search
            self.conn.execute(
                "INSERT INTO search_history (query, timestamp) VALUES (?, ?)",
                (query, datetime.now().isoformat())
            )
            
            # Generate query embedding
            query_embedding = self._generate_embedding(query)
            
            # Build SQL query
            sql = """
                SELECT id, title, content, source, category, tags, embedding_vector, 
                       created_at, access_count
                FROM knowledge_entries
                WHERE 1=1
            """
            params = []
            
            # Add category filter
            if category:
                sql += " AND category = ?"
                params.append(category)
            
            # Add text search
            sql += " AND (title LIKE ? OR content LIKE ?)"
            search_term = f"%{query}%"
            params.extend([search_term, search_term])
            
            sql += " ORDER BY access_count DESC LIMIT ?"
            params.append(limit)
            
            results = self.conn.execute(sql, params).fetchall()
            
            # Calculate similarity scores and rank results
            scored_results = []
            for row in results:
                entry_embedding = np.array(json.loads(row["embedding_vector"]))
                similarity = self._cosine_similarity(query_embedding, entry_embedding)
                
                scored_results.append({
                    "id": row["id"],
                    "title": row["title"],
                    "content": row["content"][:200] + "..." if len(row["content"]) > 200 else row["content"],
                    "source": row["source"],
                    "category": row["category"],
                    "tags": json.loads(row["tags"]),
                    "similarity": similarity,
                    "access_count": row["access_count"],
                    "created_at": row["created_at"]
                })
            
            # Sort by similarity
            scored_results.sort(key=lambda x: x["similarity"], reverse=True)
            
            # Update search history with results count
            self.conn.execute(
                "UPDATE search_history SET results_count = ? WHERE query = ? AND timestamp = (SELECT MAX(timestamp) FROM search_history WHERE query = ?)",
                (len(scored_results), query, query)
            )
            self.conn.commit()
            
            return {
                "success": True,
                "query": query,
                "results": scored_results,
                "total_results": len(scored_results)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_knowledge(self, entry_id: int) -> Dict[str, Any]:
        """Get specific knowledge entry by ID"""
        try:
            result = self.conn.execute("""
                SELECT id, title, content, source, category, tags, created_at, updated_at, access_count
                FROM knowledge_entries WHERE id = ?
            """, (entry_id,)).fetchone()
            
            if not result:
                return {"success": False, "error": "Knowledge entry not found"}
            
            # Update access count
            self.conn.execute(
                "UPDATE knowledge_entries SET access_count = access_count + 1 WHERE id = ?",
                (entry_id,)
            )
            self.conn.commit()
            
            return {
                "success": True,
                "entry": {
                    "id": result["id"],
                    "title": result["title"],
                    "content": result["content"],
                    "source": result["source"],
                    "category": result["category"],
                    "tags": json.loads(result["tags"]),
                    "created_at": result["created_at"],
                    "updated_at": result["updated_at"],
                    "access_count": result["access_count"] + 1
                }
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_knowledge(self, entry_id: int, **kwargs) -> Dict[str, Any]:
        """Update knowledge entry"""
        try:
            # Get current entry
            current = self.conn.execute(
                "SELECT * FROM knowledge_entries WHERE id = ?", (entry_id,)
            ).fetchone()
            
            if not current:
                return {"success": False, "error": "Knowledge entry not found"}
            
            # Build update query
            update_fields = []
            params = []
            
            for field in ["title", "content", "source", "category"]:
                if field in kwargs:
                    update_fields.append(f"{field} = ?")
                    params.append(kwargs[field])
            
            if "tags" in kwargs:
                update_fields.append("tags = ?")
                params.append(json.dumps(kwargs["tags"]))
            
            if not update_fields:
                return {"success": False, "error": "No fields to update"}
            
            # Update embedding if content changed
            if "content" in kwargs:
                embedding = self._generate_embedding(kwargs["content"])
                update_fields.append("embedding_vector = ?")
                params.append(json.dumps(embedding.tolist()))
            
            update_fields.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(entry_id)
            
            sql = f"UPDATE knowledge_entries SET {', '.join(update_fields)} WHERE id = ?"
            self.conn.execute(sql, params)
            self.conn.commit()
            
            return {"success": True, "message": "Knowledge entry updated"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_knowledge(self, entry_id: int) -> Dict[str, Any]:
        """Delete knowledge entry"""
        try:
            # Check if entry exists
            existing = self.conn.execute(
                "SELECT id FROM knowledge_entries WHERE id = ?", (entry_id,)
            ).fetchone()
            
            if not existing:
                return {"success": False, "error": "Knowledge entry not found"}
            
            # Delete relations
            self.conn.execute(
                "DELETE FROM knowledge_relations WHERE entry_id_1 = ? OR entry_id_2 = ?",
                (entry_id, entry_id)
            )
            
            # Delete entry
            self.conn.execute("DELETE FROM knowledge_entries WHERE id = ?", (entry_id,))
            self.conn.commit()
            
            return {"success": True, "message": "Knowledge entry deleted"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_stats(self) -> Dict[str, Any]:
        """Get knowledge base statistics"""
        try:
            # Get basic stats
            total_entries = self.conn.execute("SELECT COUNT(*) as count FROM knowledge_entries").fetchone()["count"]
            total_searches = self.conn.execute("SELECT COUNT(*) as count FROM search_history").fetchone()["count"]
            
            # Get category distribution
            categories = self.conn.execute("""
                SELECT category, COUNT(*) as count 
                FROM knowledge_entries 
                GROUP BY category 
                ORDER BY count DESC
            """).fetchall()
            
            # Get most accessed entries
            top_entries = self.conn.execute("""
                SELECT title, access_count 
                FROM knowledge_entries 
                ORDER BY access_count DESC 
                LIMIT 5
            """).fetchall()
            
            return {
                "success": True,
                "total_entries": total_entries,
                "total_searches": total_searches,
                "categories": [{"category": row["category"], "count": row["count"]} for row in categories],
                "top_entries": [{"title": row["title"], "access_count": row["access_count"]} for row in top_entries]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _generate_embedding(self, text: str) -> np.ndarray:
        """Generate simple word frequency embedding"""
        # Simple bag-of-words embedding (100 dimensions)
        words = re.findall(r'\b[a-zA-Z]{2,}\b', text.lower())
        
        # Create frequency vector
        word_freq = {}
        for word in words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        # Convert to fixed-size vector (top 100 most common words)
        common_words = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:100]
        
        # Create 100-dimensional vector
        embedding = np.zeros(100)
        for i, (word, freq) in enumerate(common_words):
            if i < 100:
                embedding[i] = freq
        
        # Normalize
        norm = np.linalg.norm(embedding)
        if norm > 0:
            embedding = embedding / norm
        
        return embedding
    
    def _cosine_similarity(self, vec1: np.ndarray, vec2: np.ndarray) -> float:
        """Calculate cosine similarity between two vectors"""
        dot_product = np.dot(vec1, vec2)
        norm1 = np.linalg.norm(vec1)
        norm2 = np.linalg.norm(vec2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def close(self):
        """Close database connection"""
        if self.conn:
            self.conn.close()

# Integration class for JARVIS
class KnowledgeManager:
    """Knowledge Management integration for JARVIS"""
    
    def __init__(self, db_path: str = "jarvis_knowledge.db"):
        self.kb = KnowledgeBase(db_path)
    
    def add(self, title: str, content: str, source: str = "", category: str = "general") -> str:
        """Add knowledge entry"""
        result = self.kb.add_knowledge(title, content, source, category)
        
        if result["success"]:
            if result["duplicate"]:
                return f"📚 Knowledge already exists: {title}"
            else:
                return f"✅ Added knowledge: {title} (ID: {result['entry_id']})"
        else:
            return f"❌ Failed to add knowledge: {result['error']}"
    
    def search(self, query: str, limit: int = 5) -> str:
        """Search knowledge base"""
        result = self.kb.search_knowledge(query, limit)
        
        if not result["success"]:
            return f"❌ Search failed: {result['error']}"
        
        if not result["results"]:
            return f"🔍 No knowledge found for '{query}'"
        
        response = f"🧠 Knowledge Search: {query}\n\n"
        
        for i, entry in enumerate(result["results"], 1):
            response += f"{i}. **{entry['title']}** (similarity: {entry['similarity']:.2f})\n"
            response += f"   {entry['content']}\n"
            response += f"   📂 {entry['category']} | 🔗 {entry['source']}\n\n"
        
        return response
    
    def get(self, entry_id: int) -> str:
        """Get specific knowledge entry"""
        result = self.kb.get_knowledge(entry_id)
        
        if not result["success"]:
            return f"❌ {result['error']}"
        
        entry = result["entry"]
        response = f"📖 {entry['title']}\n\n"
        response += f"{entry['content']}\n\n"
        response += f"📂 Category: {entry['category']}\n"
        response += f"🔗 Source: {entry['source']}\n"
        response += f"👁️ Views: {entry['access_count']}\n"
        response += f"📅 Created: {entry['created_at'][:10]}"
        
        return response
    
    def stats(self) -> str:
        """Get knowledge base statistics"""
        result = self.kb.get_stats()
        
        if not result["success"]:
            return f"❌ {result['error']}"
        
        response = f"📊 Knowledge Base Stats\n\n"
        response += f"📚 Total Entries: {result['total_entries']}\n"
        response += f"🔍 Total Searches: {result['total_searches']}\n\n"
        
        if result["categories"]:
            response += "📂 Categories:\n"
            for cat in result["categories"][:5]:
                response += f"  • {cat['category']}: {cat['count']}\n"
        
        if result["top_entries"]:
            response += "\n🔥 Most Accessed:\n"
            for entry in result["top_entries"]:
                response += f"  • {entry['title']} ({entry['access_count']} views)\n"
        
        return response
    
    def update(self, entry_id: int, title: str = None, content: str = None, 
               source: str = None, category: str = None) -> str:
        """Update knowledge entry"""
        update_data = {}
        if title: update_data["title"] = title
        if content: update_data["content"] = content
        if source: update_data["source"] = source
        if category: update_data["category"] = category
        
        if not update_data:
            return "❌ No fields to update"
        
        result = self.kb.update_knowledge(entry_id, **update_data)
        
        if result["success"]:
            return f"✅ Updated knowledge entry {entry_id}"
        else:
            return f"❌ Update failed: {result['error']}"
    
    def delete(self, entry_id: int) -> str:
        """Delete knowledge entry"""
        result = self.kb.delete_knowledge(entry_id)
        
        if result["success"]:
            return f"🗑️ Deleted knowledge entry {entry_id}"
        else:
            return f"❌ Delete failed: {result['error']}"
    
    def list_entries(self, category: str = None, limit: int = 10) -> str:
        """List knowledge entries"""
        try:
            sql = "SELECT id, title, category, created_at, access_count FROM knowledge_entries"
            params = []
            
            if category:
                sql += " WHERE category = ?"
                params.append(category)
            
            sql += " ORDER BY created_at DESC LIMIT ?"
            params.append(limit)
            
            results = self.kb.conn.execute(sql, params).fetchall()
            
            if not results:
                return f"📚 No knowledge entries found" + (f" in category '{category}'" if category else "")
            
            response = f"📚 Knowledge Entries" + (f" - {category}" if category else "") + f":\n\n"
            
            for row in results:
                response += f"🆔 {row['id']} | **{row['title']}**\n"
                response += f"   📂 {row['category']} | 👁️ {row['access_count']} views\n"
                response += f"   📅 {row['created_at'][:10]}\n\n"
            
            return response
            
        except Exception as e:
            return f"❌ List failed: {str(e)}"
    
    def categories(self) -> str:
        """List all categories"""
        try:
            results = self.kb.conn.execute("""
                SELECT category, COUNT(*) as count, MAX(created_at) as latest
                FROM knowledge_entries 
                GROUP BY category 
                ORDER BY count DESC
            """).fetchall()
            
            if not results:
                return "📂 No categories found"
            
            response = "📂 Knowledge Categories:\n\n"
            
            for row in results:
                response += f"📁 **{row['category']}** ({row['count']} entries)\n"
                response += f"   📅 Latest: {row['latest'][:10]}\n\n"
            
            return response
            
        except Exception as e:
            return f"❌ Categories failed: {str(e)}"
    
    def export_knowledge(self, category: str = None) -> str:
        """Export knowledge entries to JSON"""
        try:
            sql = "SELECT * FROM knowledge_entries"
            params = []
            
            if category:
                sql += " WHERE category = ?"
                params.append(category)
            
            results = self.kb.conn.execute(sql, params).fetchall()
            
            if not results:
                return "📚 No entries to export"
            
            # Convert to JSON
            entries = []
            for row in results:
                entries.append({
                    "id": row["id"],
                    "title": row["title"],
                    "content": row["content"],
                    "source": row["source"],
                    "category": row["category"],
                    "tags": json.loads(row["tags"]),
                    "created_at": row["created_at"],
                    "access_count": row["access_count"]
                })
            
            # Save to file
            filename = f"knowledge_export_{category or 'all'}_{int(time.time())}.json"
            with open(filename, 'w') as f:
                json.dump(entries, f, indent=2)
            
            return f"📤 Exported {len(entries)} entries to {filename}"
            
        except Exception as e:
            return f"❌ Export failed: {str(e)}"
    
    def import_knowledge(self, filename: str) -> str:
        """Import knowledge entries from JSON"""
        try:
            with open(filename, 'r') as f:
                entries = json.load(f)
            
            imported = 0
            duplicates = 0
            
            for entry in entries:
                result = self.kb.add_knowledge(
                    entry["title"],
                    entry["content"],
                    entry.get("source", ""),
                    entry.get("category", "general"),
                    entry.get("tags", [])
                )
                
                if result["success"]:
                    if result["duplicate"]:
                        duplicates += 1
                    else:
                        imported += 1
            
            return f"📥 Imported {imported} entries, {duplicates} duplicates skipped"
            
        except Exception as e:
            return f"❌ Import failed: {str(e)}"
    
    def backup(self) -> str:
        """Create full knowledge base backup"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_file = f"knowledge_backup_{timestamp}.json"
            
            # Export all data
            all_entries = self.kb.conn.execute("SELECT * FROM knowledge_entries").fetchall()
            search_history = self.kb.conn.execute("SELECT * FROM search_history").fetchall()
            
            backup_data = {
                "timestamp": timestamp,
                "entries": [dict(row) for row in all_entries],
                "search_history": [dict(row) for row in search_history]
            }
            
            with open(backup_file, 'w') as f:
                json.dump(backup_data, f, indent=2)
            
            return f"💾 Backup created: {backup_file} ({len(all_entries)} entries)"
            
        except Exception as e:
            return f"❌ Backup failed: {str(e)}"
    
    def semantic_search(self, query: str, threshold: float = 0.1, limit: int = 10) -> str:
        """Advanced semantic search with similarity threshold"""
        try:
            # Generate query embedding
            query_embedding = self.kb._generate_embedding(query)
            
            # Get all entries with embeddings
            results = self.kb.conn.execute("""
                SELECT id, title, content, source, category, embedding_vector, access_count
                FROM knowledge_entries
            """).fetchall()
            
            if not results:
                return "🔍 No knowledge entries found"
            
            # Calculate similarities
            scored_results = []
            for row in results:
                entry_embedding = np.array(json.loads(row["embedding_vector"]))
                similarity = self.kb._cosine_similarity(query_embedding, entry_embedding)
                
                if similarity >= threshold:
                    scored_results.append({
                        "id": row["id"],
                        "title": row["title"],
                        "content": row["content"][:150] + "..." if len(row["content"]) > 150 else row["content"],
                        "source": row["source"],
                        "category": row["category"],
                        "similarity": similarity,
                        "access_count": row["access_count"]
                    })
            
            # Sort by similarity
            scored_results.sort(key=lambda x: x["similarity"], reverse=True)
            scored_results = scored_results[:limit]
            
            if not scored_results:
                return f"🔍 No semantic matches found for '{query}' (threshold: {threshold})"
            
            response = f"🧠 Semantic Search: {query}\n"
            response += f"🎯 Threshold: {threshold} | Found: {len(scored_results)}\n\n"
            
            for i, entry in enumerate(scored_results, 1):
                response += f"{i}. **{entry['title']}** ({entry['similarity']:.3f})\n"
                response += f"   {entry['content']}\n"
                response += f"   📂 {entry['category']} | 👁️ {entry['access_count']} views\n\n"
            
            return response
            
        except Exception as e:
            return f"❌ Semantic search failed: {str(e)}"
    
    def analyze_knowledge_graph(self) -> str:
        """Analyze knowledge relationships and patterns"""
        try:
            # Get all entries
            entries = self.kb.conn.execute("""
                SELECT id, title, content, category, tags, access_count
                FROM knowledge_entries
            """).fetchall()
            
            if not entries:
                return "📊 No knowledge entries to analyze"
            
            # Category analysis
            categories = {}
            total_content_length = 0
            total_access = 0
            
            for entry in entries:
                cat = entry["category"]
                categories[cat] = categories.get(cat, 0) + 1
                total_content_length += len(entry["content"])
                total_access += entry["access_count"]
            
            # Find content similarities
            similar_pairs = []
            for i, entry1 in enumerate(entries):
                emb1 = np.array(json.loads(self.kb.conn.execute(
                    "SELECT embedding_vector FROM knowledge_entries WHERE id = ?", 
                    (entry1["id"],)
                ).fetchone()["embedding_vector"]))
                
                for j, entry2 in enumerate(entries[i+1:], i+1):
                    emb2 = np.array(json.loads(self.kb.conn.execute(
                        "SELECT embedding_vector FROM knowledge_entries WHERE id = ?", 
                        (entry2["id"],)
                    ).fetchone()["embedding_vector"]))
                    
                    similarity = self.kb._cosine_similarity(emb1, emb2)
                    if similarity > 0.3:  # Significant similarity
                        similar_pairs.append({
                            "entry1": entry1["title"],
                            "entry2": entry2["title"],
                            "similarity": similarity
                        })
            
            # Generate analysis report
            response = "📊 Knowledge Graph Analysis\n\n"
            response += f"📚 Total Entries: {len(entries)}\n"
            response += f"📂 Categories: {len(categories)}\n"
            response += f"📝 Avg Content Length: {total_content_length // len(entries)} chars\n"
            response += f"👁️ Total Views: {total_access}\n\n"
            
            # Category distribution
            response += "📂 Category Distribution:\n"
            for cat, count in sorted(categories.items(), key=lambda x: x[1], reverse=True):
                percentage = (count / len(entries)) * 100
                response += f"  • {cat}: {count} entries ({percentage:.1f}%)\n"
            
            # Similar content pairs
            if similar_pairs:
                response += f"\n🔗 Similar Content Pairs ({len(similar_pairs)}):\n"
                for pair in similar_pairs[:5]:  # Top 5
                    response += f"  • {pair['entry1']} ↔ {pair['entry2']} ({pair['similarity']:.3f})\n"
            
            # Most accessed
            top_accessed = sorted(entries, key=lambda x: x["access_count"], reverse=True)[:3]
            if any(e["access_count"] > 0 for e in top_accessed):
                response += "\n🔥 Most Accessed:\n"
                for entry in top_accessed:
                    if entry["access_count"] > 0:
                        response += f"  • {entry['title']} ({entry['access_count']} views)\n"
            
            return response
            
        except Exception as e:
            return f"❌ Analysis failed: {str(e)}"
    
    def find_related(self, entry_id: int, limit: int = 5) -> str:
        """Find entries related to a specific entry"""
        try:
            # Get target entry
            target = self.kb.conn.execute(
                "SELECT id, title, embedding_vector FROM knowledge_entries WHERE id = ?",
                (entry_id,)
            ).fetchone()
            
            if not target:
                return f"❌ Entry {entry_id} not found"
            
            target_embedding = np.array(json.loads(target["embedding_vector"]))
            
            # Get all other entries
            others = self.kb.conn.execute("""
                SELECT id, title, content, category, embedding_vector, access_count
                FROM knowledge_entries WHERE id != ?
            """, (entry_id,)).fetchall()
            
            if not others:
                return f"🔗 No other entries to compare with"
            
            # Calculate similarities
            related = []
            for entry in others:
                entry_embedding = np.array(json.loads(entry["embedding_vector"]))
                similarity = self.kb._cosine_similarity(target_embedding, entry_embedding)
                
                related.append({
                    "id": entry["id"],
                    "title": entry["title"],
                    "content": entry["content"][:100] + "..." if len(entry["content"]) > 100 else entry["content"],
                    "category": entry["category"],
                    "similarity": similarity,
                    "access_count": entry["access_count"]
                })
            
            # Sort by similarity
            related.sort(key=lambda x: x["similarity"], reverse=True)
            related = related[:limit]
            
            response = f"🔗 Related to: {target['title']}\n\n"
            
            for i, entry in enumerate(related, 1):
                response += f"{i}. **{entry['title']}** ({entry['similarity']:.3f})\n"
                response += f"   {entry['content']}\n"
                response += f"   📂 {entry['category']} | 👁️ {entry['access_count']} views\n\n"
            
            return response
            
        except Exception as e:
            return f"❌ Related search failed: {str(e)}"
    
    def knowledge_insights(self) -> str:
        """Generate knowledge base insights and recommendations"""
        try:
            # Get comprehensive stats
            stats = self.kb.get_stats()
            if not stats["success"]:
                return f"❌ {stats['error']}"
            
            # Get search patterns
            recent_searches = self.kb.conn.execute("""
                SELECT query, COUNT(*) as frequency
                FROM search_history
                WHERE timestamp > datetime('now', '-7 days')
                GROUP BY query
                ORDER BY frequency DESC
                LIMIT 5
            """).fetchall()
            
            # Get content gaps (categories with few entries)
            sparse_categories = [cat for cat in stats["categories"] if cat["count"] <= 2]
            
            # Generate insights
            response = "💡 Knowledge Insights\n\n"
            
            # Growth recommendations
            if stats["total_entries"] < 10:
                response += "📈 Growth: Consider adding more knowledge entries\n"
            elif stats["total_entries"] < 50:
                response += "📈 Growth: Good foundation, expand key categories\n"
            else:
                response += "📈 Growth: Mature knowledge base, focus on quality\n"
            
            # Search insights
            if recent_searches:
                response += "\n🔍 Popular Searches (7 days):\n"
                for search in recent_searches:
                    response += f"  • '{search['query']}' ({search['frequency']}x)\n"
            
            # Content gaps
            if sparse_categories:
                response += f"\n📝 Sparse Categories ({len(sparse_categories)}):\n"
                for cat in sparse_categories[:3]:
                    response += f"  • {cat['category']} ({cat['count']} entries)\n"
            
            # Usage patterns
            total_views = sum(entry["access_count"] for entry in stats["top_entries"])
            if total_views > 0:
                response += f"\n👁️ Total Views: {total_views}\n"
                if stats["top_entries"]:
                    top_entry = stats["top_entries"][0]
                    response += f"🏆 Most Popular: {top_entry['title']} ({top_entry['access_count']} views)\n"
            
            # Recommendations
            response += "\n💡 Recommendations:\n"
            if len(stats["categories"]) < 3:
                response += "  • Add more diverse categories\n"
            if stats["total_searches"] < stats["total_entries"]:
                response += "  • Encourage more knowledge exploration\n"
            if sparse_categories:
                response += "  • Expand content in sparse categories\n"
            
            return response
            
        except Exception as e:
            return f"❌ Insights failed: {str(e)}"
