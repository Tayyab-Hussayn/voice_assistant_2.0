import threading
import queue
import time
import json
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
import uuid

class SubagentStatus(Enum):
    IDLE = "idle"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class SubagentTask:
    """Individual task for subagent execution"""
    
    def __init__(self, task_id: str, task_type: str, parameters: Dict[str, Any], 
                 priority: int = 1, timeout: int = 300):
        self.task_id = task_id
        self.task_type = task_type
        self.parameters = parameters
        self.priority = priority
        self.timeout = timeout
        self.status = SubagentStatus.IDLE
        self.result = None
        self.error = None
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
    
    def __lt__(self, other):
        """Enable priority queue comparison"""
        return self.priority < other.priority

class Subagent:
    """Individual subagent worker"""
    
    def __init__(self, agent_id: str, capabilities: List[str], jarvis_instance=None):
        self.agent_id = agent_id
        self.capabilities = capabilities
        self.jarvis = jarvis_instance
        self.status = SubagentStatus.IDLE
        self.current_task = None
        self.task_queue = queue.PriorityQueue()
        self.results = {}
        self.thread = None
        self.running = False
        
    def can_handle(self, task_type: str) -> bool:
        """Check if subagent can handle task type"""
        return task_type in self.capabilities
    
    def add_task(self, task: SubagentTask):
        """Add task to subagent queue"""
        self.task_queue.put((task.priority, task))
    
    def start(self):
        """Start subagent worker thread"""
        if not self.running:
            self.running = True
            self.thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.thread.start()
    
    def stop(self):
        """Stop subagent worker"""
        self.running = False
        if self.thread:
            self.thread.join(timeout=5)
    
    def _worker_loop(self):
        """Main worker loop"""
        while self.running:
            try:
                # Get next task (blocks for 1 second)
                priority, task = self.task_queue.get(timeout=1)
                
                self.current_task = task
                self.status = SubagentStatus.RUNNING
                task.status = SubagentStatus.RUNNING
                task.started_at = datetime.now()
                
                # Execute task
                result = self._execute_task(task)
                
                # Store result
                task.result = result
                task.status = SubagentStatus.COMPLETED
                task.completed_at = datetime.now()
                self.results[task.task_id] = task
                
                self.current_task = None
                self.status = SubagentStatus.IDLE
                
            except queue.Empty:
                continue
            except Exception as e:
                if self.current_task:
                    self.current_task.error = str(e)
                    self.current_task.status = SubagentStatus.FAILED
                    self.current_task.completed_at = datetime.now()
                    self.results[self.current_task.task_id] = self.current_task
                
                self.current_task = None
                self.status = SubagentStatus.IDLE
    
    def _execute_task(self, task: SubagentTask) -> Dict[str, Any]:
        """Execute specific task based on type"""
        if task.task_type == "search":
            return self._handle_search(task.parameters)
        elif task.task_type == "research":
            return self._handle_research(task.parameters)
        elif task.task_type == "knowledge":
            return self._handle_knowledge(task.parameters)
        elif task.task_type == "analysis":
            return self._handle_analysis(task.parameters)
        elif task.task_type == "file_ops":
            return self._handle_file_ops(task.parameters)
        else:
            raise ValueError(f"Unknown task type: {task.task_type}")
    
    def _handle_search(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle search tasks"""
        if self.jarvis and hasattr(self.jarvis, 'web_search'):
            query = params.get("query", "")
            num_results = params.get("num_results", 5)
            
            result = self.jarvis.web_search.search(query, num_results)
            return {"success": True, "data": result, "task_type": "search"}
        
        return {"success": False, "error": "Search capability not available"}
    
    def _handle_research(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle research tasks"""
        if self.jarvis and hasattr(self.jarvis, 'research'):
            topic = params.get("topic", "")
            depth = params.get("depth", "medium")
            
            result = self.jarvis.research.research(topic, depth)
            return {"success": True, "data": result, "task_type": "research"}
        
        return {"success": False, "error": "Research capability not available"}
    
    def _handle_knowledge(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle knowledge operations"""
        if self.jarvis and hasattr(self.jarvis, 'knowledge'):
            operation = params.get("operation", "")
            
            if operation == "search":
                query = params.get("query", "")
                result = self.jarvis.knowledge.search(query)
            elif operation == "add":
                title = params.get("title", "")
                content = params.get("content", "")
                source = params.get("source", "")
                category = params.get("category", "general")
                result = self.jarvis.knowledge.add(title, content, source, category)
            else:
                return {"success": False, "error": f"Unknown knowledge operation: {operation}"}
            
            return {"success": True, "data": result, "task_type": "knowledge"}
        
        return {"success": False, "error": "Knowledge capability not available"}
    
    def _handle_analysis(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle analysis tasks"""
        if self.jarvis and hasattr(self.jarvis, 'research'):
            content = params.get("content", "")
            analysis_type = params.get("analysis_type", "summary")
            
            result = self.jarvis.research.analyze(content, analysis_type)
            return {"success": True, "data": result, "task_type": "analysis"}
        
        return {"success": False, "error": "Analysis capability not available"}
    
    def _handle_file_ops(self, params: Dict[str, Any]) -> Dict[str, Any]:
        """Handle file operations"""
        if self.jarvis and hasattr(self.jarvis, 'file_system'):
            operation = params.get("operation", "")
            
            if operation == "read":
                path = params.get("path", "")
                result = self.jarvis.file_system.read_file(path)
            elif operation == "write":
                path = params.get("path", "")
                content = params.get("content", "")
                result = self.jarvis.file_system.write_file(path, content)
            else:
                return {"success": False, "error": f"Unknown file operation: {operation}"}
            
            return {"success": True, "data": result, "task_type": "file_ops"}
        
        return {"success": False, "error": "File operations capability not available"}

class SubagentSystem:
    """Main subagent coordination system"""
    
    def __init__(self, jarvis_instance=None):
        self.jarvis = jarvis_instance
        self.subagents = {}
        self.task_history = {}
        self.active_workflows = {}
        
        # Initialize default subagents
        self._create_default_subagents()
    
    def _create_default_subagents(self):
        """Create default specialized subagents"""
        # Research Agent
        research_agent = Subagent(
            "research_agent",
            ["search", "research", "analysis"],
            self.jarvis
        )
        
        # Knowledge Agent
        knowledge_agent = Subagent(
            "knowledge_agent", 
            ["knowledge", "analysis"],
            self.jarvis
        )
        
        # File Agent
        file_agent = Subagent(
            "file_agent",
            ["file_ops", "analysis"],
            self.jarvis
        )
        
        self.subagents = {
            "research_agent": research_agent,
            "knowledge_agent": knowledge_agent,
            "file_agent": file_agent
        }
        
        # Start all subagents
        for agent in self.subagents.values():
            agent.start()
    
    def create_task(self, task_type: str, parameters: Dict[str, Any], 
                   priority: int = 1, timeout: int = 300) -> str:
        """Create new task and assign to appropriate subagent"""
        task_id = str(uuid.uuid4())[:8]
        task = SubagentTask(task_id, task_type, parameters, priority, timeout)
        
        # Find capable subagent
        assigned_agent = None
        for agent in self.subagents.values():
            if agent.can_handle(task_type):
                assigned_agent = agent
                break
        
        if not assigned_agent:
            task.status = SubagentStatus.FAILED
            task.error = f"No subagent available for task type: {task_type}"
            self.task_history[task_id] = task
            return task_id
        
        # Assign task
        assigned_agent.add_task(task)
        self.task_history[task_id] = task
        
        return task_id
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get status of specific task"""
        if task_id not in self.task_history:
            return {"success": False, "error": "Task not found"}
        
        task = self.task_history[task_id]
        
        return {
            "success": True,
            "task_id": task_id,
            "status": task.status.value,
            "task_type": task.task_type,
            "created_at": task.created_at.isoformat(),
            "started_at": task.started_at.isoformat() if task.started_at else None,
            "completed_at": task.completed_at.isoformat() if task.completed_at else None,
            "result": task.result,
            "error": task.error
        }
    
    def get_task_result(self, task_id: str) -> Dict[str, Any]:
        """Get result of completed task"""
        status = self.get_task_status(task_id)
        
        if not status["success"]:
            return status
        
        if status["status"] == "completed":
            return {
                "success": True,
                "task_id": task_id,
                "result": status["result"]
            }
        elif status["status"] == "failed":
            return {
                "success": False,
                "task_id": task_id,
                "error": status["error"]
            }
        else:
            return {
                "success": False,
                "task_id": task_id,
                "error": f"Task not completed (status: {status['status']})"
            }
    
    def create_parallel_workflow(self, tasks: List[Dict[str, Any]]) -> str:
        """Create workflow with parallel task execution"""
        workflow_id = str(uuid.uuid4())[:8]
        task_ids = []
        
        for task_def in tasks:
            task_id = self.create_task(
                task_def["task_type"],
                task_def["parameters"],
                task_def.get("priority", 1),
                task_def.get("timeout", 300)
            )
            task_ids.append(task_id)
        
        self.active_workflows[workflow_id] = {
            "task_ids": task_ids,
            "created_at": datetime.now(),
            "status": "running"
        }
        
        return workflow_id
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get status of parallel workflow"""
        if workflow_id not in self.active_workflows:
            return {"success": False, "error": "Workflow not found"}
        
        workflow = self.active_workflows[workflow_id]
        task_statuses = []
        
        completed_count = 0
        failed_count = 0
        
        for task_id in workflow["task_ids"]:
            status = self.get_task_status(task_id)
            task_statuses.append(status)
            
            if status["status"] == "completed":
                completed_count += 1
            elif status["status"] == "failed":
                failed_count += 1
        
        # Determine overall workflow status
        total_tasks = len(workflow["task_ids"])
        if completed_count == total_tasks:
            workflow_status = "completed"
        elif failed_count > 0:
            workflow_status = "partial_failure"
        else:
            workflow_status = "running"
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "status": workflow_status,
            "total_tasks": total_tasks,
            "completed": completed_count,
            "failed": failed_count,
            "running": total_tasks - completed_count - failed_count,
            "tasks": task_statuses
        }
    
    def get_system_status(self) -> Dict[str, Any]:
        """Get overall subagent system status"""
        agent_statuses = {}
        
        for agent_id, agent in self.subagents.items():
            agent_statuses[agent_id] = {
                "status": agent.status.value,
                "capabilities": agent.capabilities,
                "queue_size": agent.task_queue.qsize(),
                "completed_tasks": len(agent.results),
                "current_task": agent.current_task.task_id if agent.current_task else None
            }
        
        return {
            "success": True,
            "total_agents": len(self.subagents),
            "active_workflows": len(self.active_workflows),
            "total_tasks": len(self.task_history),
            "agents": agent_statuses
        }
    
    def shutdown(self):
        """Shutdown all subagents"""
        for agent in self.subagents.values():
            agent.stop()

# Integration class for JARVIS
class SubagentManager:
    """Subagent System integration for JARVIS"""
    
    def __init__(self, jarvis_instance=None):
        self.subagent_system = SubagentSystem(jarvis_instance)
    
    def create_task(self, task_type: str, **kwargs) -> str:
        """Create and execute task via subagent"""
        task_id = self.subagent_system.create_task(task_type, kwargs)
        return f"🤖 Created task {task_id} ({task_type})"
    
    def task_status(self, task_id: str) -> str:
        """Get task status"""
        status = self.subagent_system.get_task_status(task_id)
        
        if not status["success"]:
            return f"❌ {status['error']}"
        
        response = f"📋 Task {task_id}: {status['status'].upper()}\n"
        response += f"🔧 Type: {status['task_type']}\n"
        response += f"📅 Created: {status['created_at'][:19]}\n"
        
        if status["started_at"]:
            response += f"▶️ Started: {status['started_at'][:19]}\n"
        
        if status["completed_at"]:
            response += f"✅ Completed: {status['completed_at'][:19]}\n"
        
        if status["error"]:
            response += f"❌ Error: {status['error']}\n"
        
        return response
    
    def task_result(self, task_id: str) -> str:
        """Get task result"""
        result = self.subagent_system.get_task_result(task_id)
        
        if not result["success"]:
            return f"❌ {result['error']}"
        
        return f"📊 Task {task_id} Result:\n{result['result']['data']}"
    
    def parallel_workflow(self, *task_definitions) -> str:
        """Create parallel workflow"""
        tasks = []
        for task_def in task_definitions:
            if isinstance(task_def, str):
                # Simple format: "search:query=python"
                parts = task_def.split(":", 1)
                task_type = parts[0]
                params = {}
                if len(parts) > 1:
                    for param in parts[1].split(","):
                        key, value = param.split("=", 1)
                        params[key.strip()] = value.strip()
                tasks.append({"task_type": task_type, "parameters": params})
        
        workflow_id = self.subagent_system.create_parallel_workflow(tasks)
        return f"🔄 Created parallel workflow {workflow_id} with {len(tasks)} tasks"
    
    def workflow_status(self, workflow_id: str) -> str:
        """Get workflow status"""
        status = self.subagent_system.get_workflow_status(workflow_id)
        
        if not status["success"]:
            return f"❌ {status['error']}"
        
        response = f"🔄 Workflow {workflow_id}: {status['status'].upper()}\n"
        response += f"📊 Progress: {status['completed']}/{status['total_tasks']} completed\n"
        
        if status['failed'] > 0:
            response += f"❌ Failed: {status['failed']}\n"
        
        if status['running'] > 0:
            response += f"⏳ Running: {status['running']}\n"
        
        return response
    
    def system_status(self) -> str:
        """Get system status"""
        status = self.subagent_system.get_system_status()
        
        response = f"🤖 Subagent System Status\n\n"
        response += f"👥 Agents: {status['total_agents']}\n"
        response += f"🔄 Workflows: {status['active_workflows']}\n"
        response += f"📋 Total Tasks: {status['total_tasks']}\n\n"
        
        for agent_id, agent_status in status["agents"].items():
            response += f"🤖 {agent_id}: {agent_status['status'].upper()}\n"
            response += f"   📋 Queue: {agent_status['queue_size']}\n"
            response += f"   ✅ Completed: {agent_status['completed_tasks']}\n"
            if agent_status['current_task']:
                response += f"   ⏳ Current: {agent_status['current_task']}\n"
            response += "\n"
        
        return response
