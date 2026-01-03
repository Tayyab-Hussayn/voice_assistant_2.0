import json
import time
from datetime import datetime
from pathlib import Path

class WorkflowEngine:
    def __init__(self, jarvis_instance):
        self.jarvis = jarvis_instance
        self.workflows = {}
        self.workflow_file = Path.cwd() / "Memory" / "workflows.json"
        self.load_workflows()
        
    def load_workflows(self):
        """Load saved workflows"""
        if self.workflow_file.exists():
            try:
                with open(self.workflow_file, 'r') as f:
                    self.workflows = json.load(f)
            except:
                self.workflows = {}
    
    def save_workflows(self):
        """Save workflows to file"""
        self.workflow_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.workflow_file, 'w') as f:
            json.dump(self.workflows, f, indent=2)
    
    def create_workflow(self, name, description, steps):
        """Create a new workflow"""
        workflow_id = name.lower().replace(' ', '_')
        
        workflow = {
            "name": name,
            "description": description,
            "steps": steps,
            "created": datetime.now().isoformat(),
            "last_run": None,
            "run_count": 0,
            "active": True
        }
        
        self.workflows[workflow_id] = workflow
        self.save_workflows()
        return workflow_id
    
    def execute_workflow(self, workflow_id):
        """Execute a workflow"""
        if workflow_id not in self.workflows:
            return False, f"Workflow '{workflow_id}' not found"
        
        workflow = self.workflows[workflow_id]
        if not workflow["active"]:
            return False, f"Workflow '{workflow['name']}' is inactive"
        
        results = []
        success_count = 0
        
        print(f"🔄 Executing workflow: {workflow['name']}")
        self.jarvis.ai.speak(f"Starting workflow {workflow['name']}")
        
        for i, step in enumerate(workflow["steps"], 1):
            try:
                print(f"  Step {i}: {step['description']}")
                
                if step["type"] == "command":
                    result = self.jarvis.system.execute_command(step["action"])
                    success = result["success"]
                    
                elif step["type"] == "web_project":
                    success, message = self.jarvis.web_developer.build_intelligent_webpage(
                        step["action"], step.get("project_name")
                    )
                    
                elif step["type"] == "application":
                    success = self.jarvis.system.launch_application(step["action"])
                    
                elif step["type"] == "wait":
                    time.sleep(int(step["action"]))
                    success = True
                    
                elif step["type"] == "speak":
                    self.jarvis.ai.speak(step["action"])
                    success = True
                    
                else:
                    success = False
                
                results.append({
                    "step": i,
                    "description": step["description"],
                    "success": success
                })
                
                if success:
                    success_count += 1
                    print(f"    ✅ Success")
                else:
                    print(f"    ❌ Failed")
                
                # Add delay between steps if specified
                if "delay" in step:
                    time.sleep(step["delay"])
                    
            except Exception as e:
                print(f"    ❌ Error: {e}")
                results.append({
                    "step": i,
                    "description": step["description"],
                    "success": False,
                    "error": str(e)
                })
        
        # Update workflow statistics
        workflow["last_run"] = datetime.now().isoformat()
        workflow["run_count"] += 1
        self.save_workflows()
        
        success_rate = (success_count / len(workflow["steps"])) * 100
        message = f"Workflow completed: {success_count}/{len(workflow['steps'])} steps successful ({success_rate:.1f}%)"
        
        self.jarvis.ai.speak(f"Workflow finished with {success_count} out of {len(workflow['steps'])} steps successful")
        
        return True, {
            "message": message,
            "results": results,
            "success_rate": success_rate
        }
    
    def create_development_workflow(self, project_name, project_type="website"):
        """Create a development workflow"""
        steps = [
            {
                "type": "speak",
                "action": f"Starting development workflow for {project_name}",
                "description": "Announce workflow start"
            },
            {
                "type": "command",
                "action": f"mkdir -p playground/Projects/{project_name}",
                "description": f"Create project directory for {project_name}"
            },
            {
                "type": "web_project",
                "action": f"create a {project_type} for {project_name}",
                "project_name": project_name,
                "description": f"Generate {project_type} files"
            },
            {
                "type": "application",
                "action": "code",
                "description": "Open VS Code",
                "delay": 2
            },
            {
                "type": "speak",
                "action": f"Development environment ready for {project_name}",
                "description": "Confirm completion"
            }
        ]
        
        return self.create_workflow(
            f"Dev Setup: {project_name}",
            f"Complete development setup for {project_name}",
            steps
        )
    
    def create_daily_startup_workflow(self):
        """Create a daily startup workflow"""
        steps = [
            {
                "type": "speak",
                "action": "Good morning! Starting your daily workflow",
                "description": "Morning greeting"
            },
            {
                "type": "application",
                "action": "chrome",
                "description": "Open Chrome browser",
                "delay": 2
            },
            {
                "type": "application", 
                "action": "code",
                "description": "Open VS Code",
                "delay": 2
            },
            {
                "type": "application",
                "action": "terminal",
                "description": "Open terminal",
                "delay": 1
            },
            {
                "type": "command",
                "action": "cd ~/code && ls -la",
                "description": "Navigate to code directory"
            },
            {
                "type": "speak",
                "action": "Your development environment is ready. Have a productive day!",
                "description": "Completion message"
            }
        ]
        
        return self.create_workflow(
            "Daily Startup",
            "Morning development environment setup",
            steps
        )
    
    def list_workflows(self):
        """List all workflows"""
        if not self.workflows:
            return []
        
        workflow_list = []
        for wf_id, workflow in self.workflows.items():
            workflow_list.append({
                "id": wf_id,
                "name": workflow["name"],
                "description": workflow["description"],
                "steps": len(workflow["steps"]),
                "last_run": workflow["last_run"],
                "run_count": workflow["run_count"],
                "active": workflow["active"]
            })
        
        return workflow_list
    
    def delete_workflow(self, workflow_id):
        """Delete a workflow"""
        if workflow_id in self.workflows:
            name = self.workflows[workflow_id]["name"]
            del self.workflows[workflow_id]
            self.save_workflows()
            return True, f"Workflow '{name}' deleted"
        
        return False, "Workflow not found"
    
    def toggle_workflow(self, workflow_id):
        """Toggle workflow active/inactive"""
        if workflow_id in self.workflows:
            workflow = self.workflows[workflow_id]
            workflow["active"] = not workflow["active"]
            self.save_workflows()
            status = "activated" if workflow["active"] else "deactivated"
            return True, f"Workflow '{workflow['name']}' {status}"
        
        return False, "Workflow not found"
