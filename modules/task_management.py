import json
import sqlite3
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from enum import Enum

class TaskPriority(Enum):
    LOW = 1
    MEDIUM = 2
    HIGH = 3
    URGENT = 4

class TaskStatus(Enum):
    TODO = "todo"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

class TaskManager:
    """
    Task Management System with TODO list and tracking capabilities
    """
    
    def __init__(self, db_path: str = "tasks.db"):
        self.db_path = db_path
        self.conn = None
        self._init_database()
    
    def _init_database(self):
        """Initialize SQLite database for task management"""
        self.conn = sqlite3.connect(self.db_path, check_same_thread=False)
        self.conn.row_factory = sqlite3.Row
        
        self.conn.executescript("""
            CREATE TABLE IF NOT EXISTS tasks (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                title TEXT NOT NULL,
                description TEXT,
                priority INTEGER DEFAULT 2,
                status TEXT DEFAULT 'todo',
                category TEXT DEFAULT 'general',
                due_date TEXT,
                created_at TEXT,
                updated_at TEXT,
                completed_at TEXT,
                estimated_hours REAL,
                actual_hours REAL,
                tags TEXT
            );
            
            CREATE TABLE IF NOT EXISTS task_notes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                task_id INTEGER,
                note TEXT,
                created_at TEXT,
                FOREIGN KEY (task_id) REFERENCES tasks (id)
            );
            
            CREATE INDEX IF NOT EXISTS idx_status ON tasks(status);
            CREATE INDEX IF NOT EXISTS idx_priority ON tasks(priority);
            CREATE INDEX IF NOT EXISTS idx_due_date ON tasks(due_date);
        """)
        self.conn.commit()
    
    def add_task(self, title: str, description: str = "", priority: int = 2, 
                 category: str = "general", due_date: str = None, 
                 estimated_hours: float = None, tags: List[str] = None) -> Dict[str, Any]:
        """Add new task"""
        try:
            timestamp = datetime.now().isoformat()
            tags_str = json.dumps(tags or [])
            
            cursor = self.conn.execute("""
                INSERT INTO tasks 
                (title, description, priority, category, due_date, created_at, updated_at, estimated_hours, tags)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (title, description, priority, category, due_date, timestamp, timestamp, estimated_hours, tags_str))
            
            self.conn.commit()
            
            return {
                "success": True,
                "task_id": cursor.lastrowid,
                "message": f"Task '{title}' added successfully"
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_tasks(self, status: str = None, category: str = None, 
                  priority: int = None, limit: int = 50) -> Dict[str, Any]:
        """Get tasks with optional filters"""
        try:
            sql = "SELECT * FROM tasks WHERE 1=1"
            params = []
            
            if status:
                sql += " AND status = ?"
                params.append(status)
            
            if category:
                sql += " AND category = ?"
                params.append(category)
            
            if priority:
                sql += " AND priority = ?"
                params.append(priority)
            
            sql += " ORDER BY priority DESC, created_at DESC LIMIT ?"
            params.append(limit)
            
            results = self.conn.execute(sql, params).fetchall()
            
            tasks = []
            for row in results:
                task = {
                    "id": row["id"],
                    "title": row["title"],
                    "description": row["description"],
                    "priority": row["priority"],
                    "status": row["status"],
                    "category": row["category"],
                    "due_date": row["due_date"],
                    "created_at": row["created_at"],
                    "updated_at": row["updated_at"],
                    "completed_at": row["completed_at"],
                    "estimated_hours": row["estimated_hours"],
                    "actual_hours": row["actual_hours"],
                    "tags": json.loads(row["tags"]) if row["tags"] else []
                }
                tasks.append(task)
            
            return {
                "success": True,
                "tasks": tasks,
                "count": len(tasks)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def update_task(self, task_id: int, **kwargs) -> Dict[str, Any]:
        """Update task fields"""
        try:
            # Check if task exists
            existing = self.conn.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()
            if not existing:
                return {"success": False, "error": "Task not found"}
            
            # Build update query
            update_fields = []
            params = []
            
            allowed_fields = ["title", "description", "priority", "status", "category", 
                            "due_date", "estimated_hours", "actual_hours"]
            
            for field in allowed_fields:
                if field in kwargs:
                    update_fields.append(f"{field} = ?")
                    params.append(kwargs[field])
            
            if "tags" in kwargs:
                update_fields.append("tags = ?")
                params.append(json.dumps(kwargs["tags"]))
            
            if not update_fields:
                return {"success": False, "error": "No fields to update"}
            
            # Add completion timestamp if status changed to completed
            if kwargs.get("status") == "completed":
                update_fields.append("completed_at = ?")
                params.append(datetime.now().isoformat())
            
            update_fields.append("updated_at = ?")
            params.append(datetime.now().isoformat())
            params.append(task_id)
            
            sql = f"UPDATE tasks SET {', '.join(update_fields)} WHERE id = ?"
            self.conn.execute(sql, params)
            self.conn.commit()
            
            return {"success": True, "message": f"Task {task_id} updated"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def delete_task(self, task_id: int) -> Dict[str, Any]:
        """Delete task and its notes"""
        try:
            # Check if task exists
            existing = self.conn.execute("SELECT title FROM tasks WHERE id = ?", (task_id,)).fetchone()
            if not existing:
                return {"success": False, "error": "Task not found"}
            
            # Delete notes first
            self.conn.execute("DELETE FROM task_notes WHERE task_id = ?", (task_id,))
            
            # Delete task
            self.conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
            self.conn.commit()
            
            return {"success": True, "message": f"Task '{existing['title']}' deleted"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def add_note(self, task_id: int, note: str) -> Dict[str, Any]:
        """Add note to task"""
        try:
            # Check if task exists
            existing = self.conn.execute("SELECT id FROM tasks WHERE id = ?", (task_id,)).fetchone()
            if not existing:
                return {"success": False, "error": "Task not found"}
            
            timestamp = datetime.now().isoformat()
            self.conn.execute("""
                INSERT INTO task_notes (task_id, note, created_at)
                VALUES (?, ?, ?)
            """, (task_id, note, timestamp))
            
            self.conn.commit()
            
            return {"success": True, "message": "Note added to task"}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_task_notes(self, task_id: int) -> Dict[str, Any]:
        """Get all notes for a task"""
        try:
            results = self.conn.execute("""
                SELECT note, created_at FROM task_notes 
                WHERE task_id = ? ORDER BY created_at DESC
            """, (task_id,)).fetchall()
            
            notes = [{"note": row["note"], "created_at": row["created_at"]} for row in results]
            
            return {"success": True, "notes": notes}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_dashboard(self) -> Dict[str, Any]:
        """Get task dashboard with statistics"""
        try:
            # Basic counts
            total = self.conn.execute("SELECT COUNT(*) as count FROM tasks").fetchone()["count"]
            todo = self.conn.execute("SELECT COUNT(*) as count FROM tasks WHERE status = 'todo'").fetchone()["count"]
            in_progress = self.conn.execute("SELECT COUNT(*) as count FROM tasks WHERE status = 'in_progress'").fetchone()["count"]
            completed = self.conn.execute("SELECT COUNT(*) as count FROM tasks WHERE status = 'completed'").fetchone()["count"]
            
            # Priority breakdown
            urgent = self.conn.execute("SELECT COUNT(*) as count FROM tasks WHERE priority = 4 AND status != 'completed'").fetchone()["count"]
            high = self.conn.execute("SELECT COUNT(*) as count FROM tasks WHERE priority = 3 AND status != 'completed'").fetchone()["count"]
            
            # Overdue tasks
            today = datetime.now().date().isoformat()
            overdue = self.conn.execute("""
                SELECT COUNT(*) as count FROM tasks 
                WHERE due_date < ? AND status != 'completed'
            """, (today,)).fetchone()["count"]
            
            # Categories
            categories = self.conn.execute("""
                SELECT category, COUNT(*) as count 
                FROM tasks WHERE status != 'completed'
                GROUP BY category ORDER BY count DESC LIMIT 5
            """).fetchall()
            
            # Recent completions
            recent_completed = self.conn.execute("""
                SELECT title, completed_at FROM tasks 
                WHERE status = 'completed' AND completed_at IS NOT NULL
                ORDER BY completed_at DESC LIMIT 5
            """).fetchall()
            
            return {
                "success": True,
                "total_tasks": total,
                "todo": todo,
                "in_progress": in_progress,
                "completed": completed,
                "urgent": urgent,
                "high_priority": high,
                "overdue": overdue,
                "categories": [{"category": row["category"], "count": row["count"]} for row in categories],
                "recent_completed": [{"title": row["title"], "completed_at": row["completed_at"]} for row in recent_completed]
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_due_soon(self, days: int = 7) -> Dict[str, Any]:
        """Get tasks due within specified days"""
        try:
            future_date = (datetime.now() + timedelta(days=days)).date().isoformat()
            
            results = self.conn.execute("""
                SELECT * FROM tasks 
                WHERE due_date <= ? AND status != 'completed'
                ORDER BY due_date ASC, priority DESC
            """, (future_date,)).fetchall()
            
            tasks = []
            for row in results:
                task = {
                    "id": row["id"],
                    "title": row["title"],
                    "priority": row["priority"],
                    "due_date": row["due_date"],
                    "category": row["category"]
                }
                tasks.append(task)
            
            return {"success": True, "tasks": tasks, "count": len(tasks)}
            
        except Exception as e:
            return {"success": False, "error": str(e)}

# Integration class for JARVIS
class TaskManagement:
    """Task Management integration for JARVIS"""
    
    def __init__(self, db_path: str = "jarvis_tasks.db"):
        self.task_manager = TaskManager(db_path)
    
    def add(self, title: str, description: str = "", priority: str = "medium", 
            category: str = "general", due_date: str = None) -> str:
        """Add new task"""
        priority_map = {"low": 1, "medium": 2, "high": 3, "urgent": 4}
        priority_num = priority_map.get(priority.lower(), 2)
        
        result = self.task_manager.add_task(title, description, priority_num, category, due_date)
        
        if result["success"]:
            return f"✅ Added task: {title} (ID: {result['task_id']})"
        else:
            return f"❌ Failed to add task: {result['error']}"
    
    def list_tasks(self, status: str = None, category: str = None) -> str:
        """List tasks with optional filters"""
        result = self.task_manager.get_tasks(status, category)
        
        if not result["success"]:
            return f"❌ {result['error']}"
        
        if not result["tasks"]:
            filter_text = f" ({status or 'all'} status)" if status else ""
            return f"📋 No tasks found{filter_text}"
        
        priority_icons = {1: "🔵", 2: "🟡", 3: "🟠", 4: "🔴"}
        status_icons = {"todo": "⏳", "in_progress": "⚡", "completed": "✅", "cancelled": "❌"}
        
        response = f"📋 Tasks ({result['count']}):\n\n"
        
        for task in result["tasks"]:
            priority_icon = priority_icons.get(task["priority"], "⚪")
            status_icon = status_icons.get(task["status"], "❓")
            
            response += f"{priority_icon} {status_icon} **{task['title']}** (ID: {task['id']})\n"
            if task["description"]:
                response += f"   📝 {task['description'][:50]}{'...' if len(task['description']) > 50 else ''}\n"
            response += f"   📂 {task['category']}"
            if task["due_date"]:
                response += f" | 📅 Due: {task['due_date']}"
            response += "\n\n"
        
        return response
    
    def complete(self, task_id: int) -> str:
        """Mark task as completed"""
        result = self.task_manager.update_task(task_id, status="completed")
        
        if result["success"]:
            return f"✅ Task {task_id} marked as completed"
        else:
            return f"❌ {result['error']}"
    
    def update(self, task_id: int, **kwargs) -> str:
        """Update task"""
        # Convert priority text to number
        if "priority" in kwargs:
            priority_map = {"low": 1, "medium": 2, "high": 3, "urgent": 4}
            if kwargs["priority"].lower() in priority_map:
                kwargs["priority"] = priority_map[kwargs["priority"].lower()]
        
        result = self.task_manager.update_task(task_id, **kwargs)
        
        if result["success"]:
            return f"✅ Task {task_id} updated"
        else:
            return f"❌ {result['error']}"
    
    def delete(self, task_id: int) -> str:
        """Delete task"""
        result = self.task_manager.delete_task(task_id)
        
        if result["success"]:
            return f"🗑️ {result['message']}"
        else:
            return f"❌ {result['error']}"
    
    def dashboard(self) -> str:
        """Get task dashboard"""
        result = self.task_manager.get_dashboard()
        
        if not result["success"]:
            return f"❌ {result['error']}"
        
        response = "📊 Task Dashboard\n\n"
        response += f"📋 Total Tasks: {result['total_tasks']}\n"
        response += f"⏳ TODO: {result['todo']}\n"
        response += f"⚡ In Progress: {result['in_progress']}\n"
        response += f"✅ Completed: {result['completed']}\n\n"
        
        if result['urgent'] > 0:
            response += f"🔴 Urgent: {result['urgent']}\n"
        if result['high_priority'] > 0:
            response += f"🟠 High Priority: {result['high_priority']}\n"
        if result['overdue'] > 0:
            response += f"⚠️ Overdue: {result['overdue']}\n"
        
        if result["categories"]:
            response += "\n📂 Active Categories:\n"
            for cat in result["categories"]:
                response += f"  • {cat['category']}: {cat['count']}\n"
        
        if result["recent_completed"]:
            response += "\n🎉 Recently Completed:\n"
            for task in result["recent_completed"][:3]:
                response += f"  • {task['title']}\n"
        
        return response
    
    def due_soon(self, days: int = 7) -> str:
        """Get tasks due soon"""
        result = self.task_manager.get_due_soon(days)
        
        if not result["success"]:
            return f"❌ {result['error']}"
        
        if not result["tasks"]:
            return f"📅 No tasks due in the next {days} days"
        
        priority_icons = {1: "🔵", 2: "🟡", 3: "🟠", 4: "🔴"}
        
        response = f"📅 Tasks Due Soon ({days} days):\n\n"
        
        for task in result["tasks"]:
            priority_icon = priority_icons.get(task["priority"], "⚪")
            response += f"{priority_icon} **{task['title']}** (ID: {task['id']})\n"
            response += f"   📅 Due: {task['due_date']} | 📂 {task['category']}\n\n"
        
        return response
