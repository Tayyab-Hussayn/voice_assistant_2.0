import json
import time
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime
from enum import Enum
import threading

class WorkflowStatus(Enum):
    CREATED = "created"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    PAUSED = "paused"

class StepStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    SKIPPED = "skipped"

class WorkflowStep:
    """Individual step in a workflow"""
    
    def __init__(self, step_id: str, step_type: str, parameters: Dict[str, Any], 
                 condition: str = None, retry_count: int = 0):
        self.step_id = step_id
        self.step_type = step_type
        self.parameters = parameters
        self.condition = condition
        self.retry_count = retry_count
        self.status = StepStatus.PENDING
        self.result = None
        self.error = None
        self.started_at = None
        self.completed_at = None
        self.attempts = 0

class Workflow:
    """Workflow definition and execution"""
    
    def __init__(self, workflow_id: str, name: str, description: str = ""):
        self.workflow_id = workflow_id
        self.name = name
        self.description = description
        self.steps = []
        self.status = WorkflowStatus.CREATED
        self.created_at = datetime.now()
        self.started_at = None
        self.completed_at = None
        self.variables = {}
        self.results = {}
    
    def add_step(self, step: WorkflowStep):
        """Add step to workflow"""
        self.steps.append(step)
    
    def set_variable(self, key: str, value: Any):
        """Set workflow variable"""
        self.variables[key] = value
    
    def get_variable(self, key: str, default: Any = None) -> Any:
        """Get workflow variable"""
        return self.variables.get(key, default)

class WorkflowEngine:
    """
    Workflow Automation Engine with advanced workflow creation and execution
    """
    
    def __init__(self, jarvis_instance=None):
        self.jarvis = jarvis_instance
        self.workflows = {}
        self.templates = {}
        self.running_workflows = {}
        self._init_templates()
    
    def _init_templates(self):
        """Initialize workflow templates"""
        self.templates = {
            "research_workflow": {
                "name": "Research Workflow",
                "description": "Comprehensive research and knowledge storage",
                "steps": [
                    {"type": "search", "params": {"query": "{topic}", "num_results": 5}},
                    {"type": "research", "params": {"topic": "{topic}", "depth": "medium"}},
                    {"type": "knowledge_add", "params": {"title": "Research: {topic}", "content": "{research_result}", "category": "research"}}
                ]
            },
            "task_workflow": {
                "name": "Task Creation Workflow",
                "description": "Create and organize tasks",
                "steps": [
                    {"type": "task_add", "params": {"title": "{task_title}", "description": "{task_description}", "priority": "{priority}"}},
                    {"type": "knowledge_add", "params": {"title": "Task Created: {task_title}", "content": "Task {task_id} created", "category": "tasks"}}
                ]
            },
            "analysis_workflow": {
                "name": "Content Analysis Workflow", 
                "description": "Analyze content and store insights",
                "steps": [
                    {"type": "analyze", "params": {"content": "{content}", "analysis_type": "summary"}},
                    {"type": "analyze", "params": {"content": "{content}", "analysis_type": "keywords"}},
                    {"type": "knowledge_add", "params": {"title": "Analysis: {content_title}", "content": "{analysis_result}", "category": "analysis"}}
                ]
            }
        }
    
    def create_workflow(self, name: str, description: str = "", template: str = None) -> str:
        """Create new workflow"""
        workflow_id = f"wf_{int(time.time())}"
        
        if template and template in self.templates:
            # Create from template
            template_def = self.templates[template]
            workflow = Workflow(workflow_id, template_def["name"], template_def["description"])
            
            for i, step_def in enumerate(template_def["steps"]):
                step = WorkflowStep(
                    f"step_{i+1}",
                    step_def["type"],
                    step_def["params"]
                )
                workflow.add_step(step)
        else:
            # Create empty workflow
            workflow = Workflow(workflow_id, name, description)
        
        self.workflows[workflow_id] = workflow
        return workflow_id
    
    def add_step(self, workflow_id: str, step_type: str, parameters: Dict[str, Any], 
                 condition: str = None, retry_count: int = 0) -> bool:
        """Add step to workflow"""
        if workflow_id not in self.workflows:
            return False
        
        workflow = self.workflows[workflow_id]
        if workflow.status != WorkflowStatus.CREATED:
            return False
        
        step_id = f"step_{len(workflow.steps) + 1}"
        step = WorkflowStep(step_id, step_type, parameters, condition, retry_count)
        workflow.add_step(step)
        return True
    
    def execute_workflow(self, workflow_id: str, variables: Dict[str, Any] = None) -> bool:
        """Execute workflow"""
        if workflow_id not in self.workflows:
            return False
        
        workflow = self.workflows[workflow_id]
        if workflow.status == WorkflowStatus.RUNNING:
            return False
        
        # Set variables
        if variables:
            for key, value in variables.items():
                workflow.set_variable(key, value)
        
        # Start execution in separate thread
        thread = threading.Thread(target=self._execute_workflow_thread, args=(workflow,), daemon=True)
        thread.start()
        
        self.running_workflows[workflow_id] = thread
        return True
    
    def _execute_workflow_thread(self, workflow: Workflow):
        """Execute workflow in separate thread"""
        try:
            workflow.status = WorkflowStatus.RUNNING
            workflow.started_at = datetime.now()
            
            for step in workflow.steps:
                # Check condition if specified
                if step.condition and not self._evaluate_condition(step.condition, workflow):
                    step.status = StepStatus.SKIPPED
                    continue
                
                # Execute step with retries
                success = False
                step.attempts = 0
                
                while step.attempts <= step.retry_count and not success:
                    step.attempts += 1
                    step.status = StepStatus.RUNNING
                    step.started_at = datetime.now()
                    
                    try:
                        result = self._execute_step(step, workflow)
                        step.result = result
                        step.status = StepStatus.COMPLETED
                        step.completed_at = datetime.now()
                        success = True
                        
                        # Store result in workflow
                        workflow.results[step.step_id] = result
                        
                    except Exception as e:
                        step.error = str(e)
                        if step.attempts > step.retry_count:
                            step.status = StepStatus.FAILED
                            step.completed_at = datetime.now()
                        else:
                            time.sleep(1)  # Wait before retry
                
                # If step failed and no more retries, fail workflow
                if not success:
                    workflow.status = WorkflowStatus.FAILED
                    workflow.completed_at = datetime.now()
                    return
            
            # All steps completed successfully
            workflow.status = WorkflowStatus.COMPLETED
            workflow.completed_at = datetime.now()
            
        except Exception as e:
            workflow.status = WorkflowStatus.FAILED
            workflow.completed_at = datetime.now()
        
        finally:
            # Remove from running workflows
            if workflow.workflow_id in self.running_workflows:
                del self.running_workflows[workflow.workflow_id]
    
    def _execute_step(self, step: WorkflowStep, workflow: Workflow) -> Any:
        """Execute individual workflow step"""
        # Replace variables in parameters
        params = self._replace_variables(step.parameters, workflow)
        
        if step.step_type == "search" and self.jarvis and hasattr(self.jarvis, 'web_search'):
            result = self.jarvis.web_search.search(params.get("query", ""), params.get("num_results", 5))
            return {"type": "search", "data": result}
        
        elif step.step_type == "research" and self.jarvis and hasattr(self.jarvis, 'research'):
            result = self.jarvis.research.research(params.get("topic", ""), params.get("depth", "medium"))
            return {"type": "research", "data": result}
        
        elif step.step_type == "knowledge_add" and self.jarvis and hasattr(self.jarvis, 'knowledge'):
            result = self.jarvis.knowledge.add(
                params.get("title", ""),
                params.get("content", ""),
                params.get("source", ""),
                params.get("category", "general")
            )
            return {"type": "knowledge_add", "data": result}
        
        elif step.step_type == "task_add" and self.jarvis and hasattr(self.jarvis, 'tasks'):
            result = self.jarvis.tasks.add(
                params.get("title", ""),
                params.get("description", ""),
                params.get("priority", "medium"),
                params.get("category", "general"),
                params.get("due_date", None)
            )
            return {"type": "task_add", "data": result}
        
        elif step.step_type == "analyze" and self.jarvis and hasattr(self.jarvis, 'research'):
            result = self.jarvis.research.analyze(
                params.get("content", ""),
                params.get("analysis_type", "summary")
            )
            return {"type": "analyze", "data": result}
        
        elif step.step_type == "wait":
            time.sleep(params.get("seconds", 1))
            return {"type": "wait", "data": f"Waited {params.get('seconds', 1)} seconds"}
        
        elif step.step_type == "set_variable":
            key = params.get("key", "")
            value = params.get("value", "")
            workflow.set_variable(key, value)
            return {"type": "set_variable", "data": f"Set {key} = {value}"}
        
        else:
            raise ValueError(f"Unknown step type: {step.step_type}")
    
    def _replace_variables(self, params: Dict[str, Any], workflow: Workflow) -> Dict[str, Any]:
        """Replace variables in parameters"""
        result = {}
        
        for key, value in params.items():
            if isinstance(value, str):
                # Replace {variable} patterns
                for var_key, var_value in workflow.variables.items():
                    value = value.replace(f"{{{var_key}}}", str(var_value))
                
                # Replace {result.step_id} patterns
                for result_key, result_value in workflow.results.items():
                    if isinstance(result_value, dict) and "data" in result_value:
                        value = value.replace(f"{{result.{result_key}}}", str(result_value["data"]))
            
            result[key] = value
        
        return result
    
    def _evaluate_condition(self, condition: str, workflow: Workflow) -> bool:
        """Evaluate step condition"""
        # Simple condition evaluation
        # Format: "variable == value" or "step_result == success"
        try:
            if "==" in condition:
                left, right = condition.split("==", 1)
                left = left.strip()
                right = right.strip().strip('"\'')
                
                if left in workflow.variables:
                    return str(workflow.variables[left]) == right
                elif left.startswith("step_") and left in workflow.results:
                    result = workflow.results[left]
                    return str(result.get("data", "")) == right
            
            return True
        except:
            return True
    
    def get_workflow_status(self, workflow_id: str) -> Dict[str, Any]:
        """Get workflow status"""
        if workflow_id not in self.workflows:
            return {"success": False, "error": "Workflow not found"}
        
        workflow = self.workflows[workflow_id]
        
        step_statuses = []
        for step in workflow.steps:
            step_statuses.append({
                "step_id": step.step_id,
                "type": step.step_type,
                "status": step.status.value,
                "attempts": step.attempts,
                "error": step.error
            })
        
        return {
            "success": True,
            "workflow_id": workflow_id,
            "name": workflow.name,
            "status": workflow.status.value,
            "created_at": workflow.created_at.isoformat(),
            "started_at": workflow.started_at.isoformat() if workflow.started_at else None,
            "completed_at": workflow.completed_at.isoformat() if workflow.completed_at else None,
            "steps": step_statuses,
            "variables": workflow.variables,
            "results": workflow.results
        }
    
    def list_workflows(self) -> Dict[str, Any]:
        """List all workflows"""
        workflows = []
        
        for workflow_id, workflow in self.workflows.items():
            workflows.append({
                "workflow_id": workflow_id,
                "name": workflow.name,
                "status": workflow.status.value,
                "steps": len(workflow.steps),
                "created_at": workflow.created_at.isoformat()
            })
        
        return {"success": True, "workflows": workflows}
    
    def get_templates(self) -> Dict[str, Any]:
        """Get available workflow templates"""
        return {"success": True, "templates": self.templates}

# Integration class for JARVIS
class WorkflowAutomation:
    """Workflow Automation integration for JARVIS"""
    
    def __init__(self, jarvis_instance=None):
        self.engine = WorkflowEngine(jarvis_instance)
    
    def create(self, name: str, description: str = "", template: str = None) -> str:
        """Create workflow"""
        workflow_id = self.engine.create_workflow(name, description, template)
        return f"🔄 Created workflow: {name} (ID: {workflow_id})"
    
    def add_step(self, workflow_id: str, step_type: str, **params) -> str:
        """Add step to workflow"""
        success = self.engine.add_step(workflow_id, step_type, params)
        
        if success:
            return f"➕ Added {step_type} step to workflow {workflow_id}"
        else:
            return f"❌ Failed to add step to workflow {workflow_id}"
    
    def execute(self, workflow_id: str, **variables) -> str:
        """Execute workflow"""
        success = self.engine.execute_workflow(workflow_id, variables)
        
        if success:
            return f"▶️ Started workflow {workflow_id}"
        else:
            return f"❌ Failed to start workflow {workflow_id}"
    
    def status(self, workflow_id: str) -> str:
        """Get workflow status"""
        result = self.engine.get_workflow_status(workflow_id)
        
        if not result["success"]:
            return f"❌ {result['error']}"
        
        response = f"🔄 Workflow: {result['name']} ({result['workflow_id']})\n"
        response += f"📊 Status: {result['status'].upper()}\n"
        response += f"📅 Created: {result['created_at'][:19]}\n"
        
        if result["started_at"]:
            response += f"▶️ Started: {result['started_at'][:19]}\n"
        
        if result["completed_at"]:
            response += f"✅ Completed: {result['completed_at'][:19]}\n"
        
        response += f"\n📋 Steps ({len(result['steps'])}):\n"
        
        status_icons = {
            "pending": "⏳",
            "running": "⚡",
            "completed": "✅",
            "failed": "❌",
            "skipped": "⏭️"
        }
        
        for step in result["steps"]:
            icon = status_icons.get(step["status"], "❓")
            response += f"  {icon} {step['step_id']}: {step['type']}"
            if step["error"]:
                response += f" (Error: {step['error']})"
            response += "\n"
        
        return response
    
    def list_workflows(self) -> str:
        """List all workflows"""
        result = self.engine.list_workflows()
        
        if not result["workflows"]:
            return "🔄 No workflows found"
        
        response = f"🔄 Workflows ({len(result['workflows'])}):\n\n"
        
        status_icons = {
            "created": "📝",
            "running": "⚡",
            "completed": "✅",
            "failed": "❌",
            "paused": "⏸️"
        }
        
        for wf in result["workflows"]:
            icon = status_icons.get(wf["status"], "❓")
            response += f"{icon} **{wf['name']}** ({wf['workflow_id']})\n"
            response += f"   📋 {wf['steps']} steps | 📅 {wf['created_at'][:10]}\n\n"
        
        return response
    
    def templates(self) -> str:
        """List workflow templates"""
        result = self.engine.get_templates()
        
        response = "📋 Workflow Templates:\n\n"
        
        for template_id, template in result["templates"].items():
            response += f"🔧 **{template['name']}** ({template_id})\n"
            response += f"   📝 {template['description']}\n"
            response += f"   📋 {len(template['steps'])} steps\n\n"
        
        return response
