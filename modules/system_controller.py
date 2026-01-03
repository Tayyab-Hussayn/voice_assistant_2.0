import subprocess
import os
import json
import webbrowser
from pathlib import Path

class SystemController:
    def __init__(self):
        self.current_dir = Path.cwd()
        
    def execute_command(self, command):
        """Execute a shell command safely"""
        try:
            os.chdir(self.current_dir)
            
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            self.current_dir = Path.cwd()
            
            if result.returncode == 0:
                return {"success": True, "output": result.stdout}
            else:
                return {"success": False, "error": result.stderr}
                
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timeout"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def create_web_project(self, project_name, content_type="simple"):
        """Create a web project with HTML, CSS, JS"""
        project_path = self.current_dir / project_name
        project_path.mkdir(exist_ok=True)
        
        # HTML content
        if content_type == "simple":
            html_content = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name.title()}</title>
    <link rel="stylesheet" href="style.css">
</head>
<body>
    <div class="container">
        <h1>Welcome to {project_name.title()}</h1>
        <p>This is your new web project created by JARVIS!</p>
        <button id="actionBtn">Click Me</button>
    </div>
    <script src="script.js"></script>
</body>
</html>"""
        
            css_content = """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    min-height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
}

.container {
    background: white;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 10px 30px rgba(0,0,0,0.3);
    text-align: center;
    max-width: 500px;
}

h1 {
    color: #333;
    margin-bottom: 1rem;
}

p {
    color: #666;
    margin-bottom: 2rem;
}

button {
    background: #667eea;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    transition: background 0.3s;
}

button:hover {
    background: #5a6fd8;
}"""
        
            js_content = """document.addEventListener('DOMContentLoaded', function() {
    const button = document.getElementById('actionBtn');
    
    button.addEventListener('click', function() {
        alert('Hello from JARVIS! 🤖');
        this.style.background = '#28a745';
        this.textContent = 'Activated!';
    });
    
    console.log('JARVIS web project loaded successfully!');
});"""
        
        # Write files
        (project_path / "index.html").write_text(html_content)
        (project_path / "style.css").write_text(css_content)
        (project_path / "script.js").write_text(js_content)
        
        return project_path
    
    def open_in_browser(self, file_path):
        """Open file in default browser"""
        try:
            webbrowser.open(f"file://{file_path.absolute()}")
            return True
        except Exception as e:
            print(f"Error opening browser: {e}")
            return False
    
    def launch_application(self, app_name):
        """Launch applications on Linux"""
        app_commands = {
            "chrome": "google-chrome",
            "firefox": "firefox", 
            "code": "code",
            "vscode": "code",
            "terminal": "gnome-terminal",
            "files": "nautilus",
            "calculator": "gnome-calculator",
            "text editor": "gedit",
            "music": "rhythmbox"
        }
        
        command = app_commands.get(app_name.lower())
        if command:
            try:
                subprocess.Popen([command], stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return True
            except Exception as e:
                print(f"Error launching {app_name}: {e}")
                return False
        return False
    
    def get_system_info(self):
        """Get basic system information"""
        info = {}
        try:
            # Get current directory
            info['current_dir'] = str(self.current_dir)
            
            # Get disk usage
            result = subprocess.run(['df', '-h', '.'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    info['disk_usage'] = f"Used: {parts[2]}, Available: {parts[3]}"
            
            # Get memory info
            result = subprocess.run(['free', '-h'], capture_output=True, text=True)
            if result.returncode == 0:
                lines = result.stdout.strip().split('\n')
                if len(lines) > 1:
                    parts = lines[1].split()
                    info['memory'] = f"Used: {parts[2]}, Available: {parts[6]}"
                    
        except Exception as e:
            info['error'] = str(e)
            
        return info
