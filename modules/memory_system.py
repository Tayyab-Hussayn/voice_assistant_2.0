import json
import sqlite3
from datetime import datetime
from pathlib import Path
import hashlib

class MemorySystem:
    def __init__(self):
        self.memory_dir = Path.cwd() / "playground" / "Memory"
        self.memory_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize SQLite database for structured memory
        self.db_path = self.memory_dir / "jarvis_memory.db"
        self.init_database()
        
        # Current session context
        self.current_session = self.create_session()
        self.short_term_memory = []
        self.context_window = 10  # Remember last 10 interactions
        
    def init_database(self):
        """Initialize memory database"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        # Sessions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS sessions (
                id TEXT PRIMARY KEY,
                start_time TEXT,
                end_time TEXT,
                summary TEXT
            )
        ''')
        
        # Interactions table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS interactions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                session_id TEXT,
                timestamp TEXT,
                user_input TEXT,
                jarvis_response TEXT,
                action_type TEXT,
                success BOOLEAN,
                FOREIGN KEY (session_id) REFERENCES sessions (id)
            )
        ''')
        
        # Knowledge base table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS knowledge (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                category TEXT,
                key TEXT,
                value TEXT,
                timestamp TEXT,
                UNIQUE(category, key)
            )
        ''')
        
        # User preferences table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT,
                timestamp TEXT
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def create_session(self):
        """Create a new session"""
        session_id = hashlib.md5(str(datetime.now()).encode()).hexdigest()[:8]
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO sessions (id, start_time)
            VALUES (?, ?)
        ''', (session_id, datetime.now().isoformat()))
        conn.commit()
        conn.close()
        
        return session_id
    
    def remember_interaction(self, user_input, jarvis_response, action_type="conversation", success=True):
        """Store an interaction in memory"""
        # Add to short-term memory
        interaction = {
            'timestamp': datetime.now().isoformat(),
            'user_input': user_input,
            'jarvis_response': jarvis_response,
            'action_type': action_type,
            'success': success
        }
        
        self.short_term_memory.append(interaction)
        
        # Keep only recent interactions in short-term memory
        if len(self.short_term_memory) > self.context_window:
            self.short_term_memory.pop(0)
        
        # Store in database
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT INTO interactions (session_id, timestamp, user_input, jarvis_response, action_type, success)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (self.current_session, interaction['timestamp'], user_input, jarvis_response, action_type, success))
        conn.commit()
        conn.close()
    
    def store_knowledge(self, category, key, value):
        """Store knowledge in long-term memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO knowledge (category, key, value, timestamp)
            VALUES (?, ?, ?, ?)
        ''', (category, key, value, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def recall_knowledge(self, category, key=None):
        """Recall knowledge from long-term memory"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        
        if key:
            cursor.execute('SELECT value FROM knowledge WHERE category = ? AND key = ?', (category, key))
            result = cursor.fetchone()
            conn.close()
            return result[0] if result else None
        else:
            cursor.execute('SELECT key, value FROM knowledge WHERE category = ?', (category,))
            results = cursor.fetchall()
            conn.close()
            return dict(results)
    
    def get_context(self):
        """Get current conversation context"""
        if not self.short_term_memory:
            return "No recent conversation history."
        
        context = "Recent conversation:\n"
        for interaction in self.short_term_memory[-5:]:  # Last 5 interactions
            context += f"User: {interaction['user_input']}\n"
            context += f"JARVIS: {interaction['jarvis_response']}\n"
        
        return context
    
    def set_preference(self, key, value):
        """Set user preference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            INSERT OR REPLACE INTO preferences (key, value, timestamp)
            VALUES (?, ?, ?)
        ''', (key, value, datetime.now().isoformat()))
        conn.commit()
        conn.close()
    
    def get_preference(self, key):
        """Get user preference"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('SELECT value FROM preferences WHERE key = ?', (key,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None
    
    def search_interactions(self, query, limit=10):
        """Search past interactions"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT timestamp, user_input, jarvis_response, action_type
            FROM interactions
            WHERE user_input LIKE ? OR jarvis_response LIKE ?
            ORDER BY timestamp DESC
            LIMIT ?
        ''', (f'%{query}%', f'%{query}%', limit))
        results = cursor.fetchall()
        conn.close()
        return results
    
    def get_session_summary(self):
        """Get summary of current session"""
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT COUNT(*), 
                   SUM(CASE WHEN success = 1 THEN 1 ELSE 0 END) as successful,
                   GROUP_CONCAT(DISTINCT action_type) as action_types
            FROM interactions
            WHERE session_id = ?
        ''', (self.current_session,))
        result = cursor.fetchone()
        conn.close()
        
        if result and result[0] > 0:
            total, successful, action_types = result
            return {
                'total_interactions': total,
                'successful_interactions': successful,
                'action_types': action_types.split(',') if action_types else [],
                'success_rate': (successful / total) * 100 if total > 0 else 0
            }
        return None
    
    def end_session(self):
        """End current session with summary"""
        summary = self.get_session_summary()
        
        conn = sqlite3.connect(self.db_path)
        cursor = conn.cursor()
        cursor.execute('''
            UPDATE sessions 
            SET end_time = ?, summary = ?
            WHERE id = ?
        ''', (datetime.now().isoformat(), json.dumps(summary), self.current_session))
        conn.commit()
        conn.close()
        
        return summary
