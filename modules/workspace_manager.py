from pathlib import Path
import os

class WorkspaceManager:
    def __init__(self):
        self.base_dir = Path.cwd() / "playground"
        self.workspaces = {
            "web_projects": self.base_dir / "Web Projects",
            "documents": self.base_dir / "Documents", 
            "scripts": self.base_dir / "Scripts",
            "downloads": self.base_dir / "Downloads",
            "temp": self.base_dir / "Temp"
        }
        
        # Create all workspace directories
        for workspace_path in self.workspaces.values():
            workspace_path.mkdir(parents=True, exist_ok=True)
    
    def get_workspace(self, workspace_name):
        """Get path to a specific workspace"""
        return self.workspaces.get(workspace_name.lower(), self.base_dir)
    
    def create_project_folder(self, project_name, workspace="temp"):
        """Create a new project folder in specified workspace"""
        workspace_path = self.get_workspace(workspace)
        project_path = workspace_path / project_name
        project_path.mkdir(exist_ok=True)
        return project_path
    
    def list_workspaces(self):
        """List all available workspaces"""
        return list(self.workspaces.keys())
    
    def get_workspace_contents(self, workspace_name):
        """Get contents of a workspace"""
        workspace_path = self.get_workspace(workspace_name)
        if workspace_path.exists():
            return [item.name for item in workspace_path.iterdir()]
        return []
