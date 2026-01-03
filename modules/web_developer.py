import os
import subprocess
import webbrowser
from pathlib import Path
import json
import time

class WebDeveloper:
    def __init__(self):
        self.project_templates = {
            'simple': self.create_simple_template,
            'portfolio': self.create_portfolio_template,
            'dashboard': self.create_dashboard_template,
            'landing': self.create_landing_template,
            'blog': self.create_blog_template
        }
        
        self.frameworks = {
            'vanilla': self.create_vanilla_project,
            'react': self.create_react_project,
            'vue': self.create_vue_project,
            'bootstrap': self.create_bootstrap_project
        }
    
    def create_web_project(self, project_name, template='simple', framework='vanilla', features=None):
        """Create a complete web project"""
        try:
            project_path = Path.cwd() / project_name
            project_path.mkdir(exist_ok=True)
            
            # Create project structure
            self.create_project_structure(project_path)
            
            # Generate content based on template and framework
            if framework in self.frameworks:
                success, msg = self.frameworks[framework](project_path, template, features or [])
            else:
                success, msg = self.create_vanilla_project(project_path, template, features or [])
            
            if success:
                # Create package.json for modern projects
                self.create_package_json(project_path, project_name)
                
                # Create README
                self.create_readme(project_path, project_name, template, framework)
                
                return True, f"Web project '{project_name}' created successfully at {project_path}"
            else:
                return False, msg
                
        except Exception as e:
            return False, f"Failed to create web project: {e}"
    
    def create_project_structure(self, project_path):
        """Create basic project structure"""
        directories = ['css', 'js', 'images', 'assets']
        for directory in directories:
            (project_path / directory).mkdir(exist_ok=True)
    
    def create_vanilla_project(self, project_path, template, features):
        """Create vanilla HTML/CSS/JS project"""
        try:
            # Generate HTML
            html_content = self.project_templates[template](project_path.name, features)
            (project_path / 'index.html').write_text(html_content)
            
            # Generate CSS
            css_content = self.generate_css(template, features)
            (project_path / 'css' / 'style.css').write_text(css_content)
            
            # Generate JavaScript
            js_content = self.generate_javascript(template, features)
            (project_path / 'js' / 'script.js').write_text(js_content)
            
            return True, "Vanilla project created"
        except Exception as e:
            return False, f"Vanilla project creation failed: {e}"
    
    def create_react_project(self, project_path, template, features):
        """Create React project (requires Node.js)"""
        try:
            # Check if npx is available
            result = subprocess.run(['which', 'npx'], capture_output=True)
            if result.returncode != 0:
                return False, "Node.js/npx not found - install Node.js for React projects"
            
            # Create React app
            subprocess.run(['npx', 'create-react-app', str(project_path)], 
                         capture_output=True, check=True)
            
            return True, "React project created"
        except subprocess.CalledProcessError:
            return False, "Failed to create React project"
        except Exception as e:
            return False, f"React project error: {e}"
    
    def create_bootstrap_project(self, project_path, template, features):
        """Create Bootstrap-based project"""
        try:
            # Create vanilla project first
            success, msg = self.create_vanilla_project(project_path, template, features)
            if not success:
                return success, msg
            
            # Add Bootstrap CDN to HTML
            html_file = project_path / 'index.html'
            html_content = html_file.read_text()
            
            # Add Bootstrap CSS and JS
            bootstrap_css = '<link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/css/bootstrap.min.css" rel="stylesheet">'
            bootstrap_js = '<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.0/dist/js/bootstrap.bundle.min.js"></script>'
            
            html_content = html_content.replace('</head>', f'    {bootstrap_css}\n</head>')
            html_content = html_content.replace('</body>', f'    {bootstrap_js}\n</body>')
            
            html_file.write_text(html_content)
            
            return True, "Bootstrap project created"
        except Exception as e:
            return False, f"Bootstrap project error: {e}"
    
    def create_simple_template(self, project_name, features):
        """Create simple HTML template"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name.title()}</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="container">
        <header>
            <h1>Welcome to {project_name.title()}</h1>
        </header>
        <main>
            <p>This is your new web project created by JARVIS!</p>
            <button id="actionBtn" class="btn">Click Me</button>
        </main>
        <footer>
            <p>&copy; 2026 {project_name.title()} - Created by JARVIS</p>
        </footer>
    </div>
    <script src="js/script.js"></script>
</body>
</html>"""
    
    def create_portfolio_template(self, project_name, features):
        """Create portfolio template"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name.title()} - Portfolio</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <nav class="navbar">
        <div class="nav-container">
            <h1 class="nav-logo">{project_name.title()}</h1>
            <ul class="nav-menu">
                <li><a href="#home">Home</a></li>
                <li><a href="#about">About</a></li>
                <li><a href="#projects">Projects</a></li>
                <li><a href="#contact">Contact</a></li>
            </ul>
        </div>
    </nav>
    
    <section id="home" class="hero">
        <div class="hero-content">
            <h1>Hello, I'm {project_name.title()}</h1>
            <p>Welcome to my portfolio</p>
            <button class="cta-btn">View My Work</button>
        </div>
    </section>
    
    <section id="about" class="about">
        <div class="container">
            <h2>About Me</h2>
            <p>This portfolio was created by JARVIS AI Assistant.</p>
        </div>
    </section>
    
    <section id="projects" class="projects">
        <div class="container">
            <h2>My Projects</h2>
            <div class="project-grid">
                <div class="project-card">
                    <h3>Project 1</h3>
                    <p>Description of project 1</p>
                </div>
                <div class="project-card">
                    <h3>Project 2</h3>
                    <p>Description of project 2</p>
                </div>
            </div>
        </div>
    </section>
    
    <section id="contact" class="contact">
        <div class="container">
            <h2>Contact Me</h2>
            <form class="contact-form">
                <input type="text" placeholder="Your Name" required>
                <input type="email" placeholder="Your Email" required>
                <textarea placeholder="Your Message" required></textarea>
                <button type="submit">Send Message</button>
            </form>
        </div>
    </section>
    
    <script src="js/script.js"></script>
</body>
</html>"""
    
    def create_dashboard_template(self, project_name, features):
        """Create dashboard template"""
        return f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{project_name.title()} Dashboard</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <div class="dashboard">
        <aside class="sidebar">
            <h2>Dashboard</h2>
            <nav class="sidebar-nav">
                <a href="#overview" class="nav-item active">Overview</a>
                <a href="#analytics" class="nav-item">Analytics</a>
                <a href="#settings" class="nav-item">Settings</a>
            </nav>
        </aside>
        
        <main class="main-content">
            <header class="dashboard-header">
                <h1>Welcome to {project_name.title()}</h1>
                <div class="user-info">
                    <span>JARVIS User</span>
                </div>
            </header>
            
            <div class="dashboard-grid">
                <div class="card">
                    <h3>Total Users</h3>
                    <div class="metric">1,234</div>
                </div>
                <div class="card">
                    <h3>Revenue</h3>
                    <div class="metric">$12,345</div>
                </div>
                <div class="card">
                    <h3>Orders</h3>
                    <div class="metric">567</div>
                </div>
                <div class="card">
                    <h3>Growth</h3>
                    <div class="metric">+23%</div>
                </div>
            </div>
            
            <div class="chart-container">
                <h3>Analytics Chart</h3>
                <div class="chart-placeholder">Chart will be rendered here</div>
            </div>
        </main>
    </div>
    
    <script src="js/script.js"></script>
</body>
</html>"""
    
    def create_landing_template(self, project_name, features):
        """Create landing page template"""
        return self.create_simple_template(project_name, features)  # Simplified for now
    
    def create_blog_template(self, project_name, features):
        """Create blog template"""
        return self.create_simple_template(project_name, features)  # Simplified for now
    
    def generate_css(self, template, features):
        """Generate CSS based on template"""
        base_css = """* {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}

body {
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: #333;
}

.container {
    max-width: 1200px;
    margin: 0 auto;
    padding: 0 20px;
}

.btn {
    background: #007bff;
    color: white;
    border: none;
    padding: 12px 24px;
    border-radius: 5px;
    cursor: pointer;
    font-size: 16px;
    transition: background 0.3s;
}

.btn:hover {
    background: #0056b3;
}"""
        
        if template == 'portfolio':
            base_css += """
.navbar {
    background: #fff;
    box-shadow: 0 2px 5px rgba(0,0,0,0.1);
    position: fixed;
    width: 100%;
    top: 0;
    z-index: 1000;
}

.nav-container {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 1rem 2rem;
}

.nav-menu {
    display: flex;
    list-style: none;
    gap: 2rem;
}

.nav-menu a {
    text-decoration: none;
    color: #333;
    font-weight: 500;
}

.hero {
    height: 100vh;
    display: flex;
    align-items: center;
    justify-content: center;
    background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
    color: white;
    text-align: center;
}

.hero h1 {
    font-size: 3rem;
    margin-bottom: 1rem;
}

.cta-btn {
    background: white;
    color: #667eea;
    padding: 15px 30px;
    border: none;
    border-radius: 50px;
    font-size: 18px;
    cursor: pointer;
    margin-top: 2rem;
}

.about, .projects, .contact {
    padding: 5rem 0;
}

.project-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
    gap: 2rem;
    margin-top: 2rem;
}

.project-card {
    background: white;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 5px 15px rgba(0,0,0,0.1);
}

.contact-form {
    max-width: 600px;
    margin: 2rem auto;
}

.contact-form input,
.contact-form textarea {
    width: 100%;
    padding: 1rem;
    margin-bottom: 1rem;
    border: 1px solid #ddd;
    border-radius: 5px;
}"""
        
        elif template == 'dashboard':
            base_css += """
.dashboard {
    display: flex;
    height: 100vh;
}

.sidebar {
    width: 250px;
    background: #2c3e50;
    color: white;
    padding: 2rem 1rem;
}

.sidebar h2 {
    margin-bottom: 2rem;
    text-align: center;
}

.sidebar-nav {
    display: flex;
    flex-direction: column;
    gap: 1rem;
}

.nav-item {
    padding: 1rem;
    color: white;
    text-decoration: none;
    border-radius: 5px;
    transition: background 0.3s;
}

.nav-item:hover,
.nav-item.active {
    background: #34495e;
}

.main-content {
    flex: 1;
    padding: 2rem;
    background: #f8f9fa;
}

.dashboard-header {
    display: flex;
    justify-content: space-between;
    align-items: center;
    margin-bottom: 2rem;
}

.dashboard-grid {
    display: grid;
    grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
    gap: 2rem;
    margin-bottom: 2rem;
}

.card {
    background: white;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
    text-align: center;
}

.metric {
    font-size: 2.5rem;
    font-weight: bold;
    color: #007bff;
    margin-top: 1rem;
}

.chart-container {
    background: white;
    padding: 2rem;
    border-radius: 10px;
    box-shadow: 0 2px 10px rgba(0,0,0,0.1);
}

.chart-placeholder {
    height: 300px;
    background: #f8f9fa;
    display: flex;
    align-items: center;
    justify-content: center;
    border-radius: 5px;
    margin-top: 1rem;
}"""
        
        return base_css
    
    def generate_javascript(self, template, features):
        """Generate JavaScript based on template"""
        base_js = """document.addEventListener('DOMContentLoaded', function() {
    console.log('JARVIS web project loaded successfully!');
    
    // Add click handlers
    const buttons = document.querySelectorAll('.btn, .cta-btn');
    buttons.forEach(button => {
        button.addEventListener('click', function() {
            console.log('Button clicked:', this.textContent);
        });
    });
});"""
        
        if template == 'portfolio':
            base_js += """

// Smooth scrolling for navigation links
document.querySelectorAll('a[href^="#"]').forEach(anchor => {
    anchor.addEventListener('click', function (e) {
        e.preventDefault();
        const target = document.querySelector(this.getAttribute('href'));
        if (target) {
            target.scrollIntoView({
                behavior: 'smooth',
                block: 'start'
            });
        }
    });
});

// Contact form handler
const contactForm = document.querySelector('.contact-form');
if (contactForm) {
    contactForm.addEventListener('submit', function(e) {
        e.preventDefault();
        alert('Thank you for your message! (This is a demo)');
    });
}"""
        
        elif template == 'dashboard':
            base_js += """

// Dashboard navigation
document.querySelectorAll('.nav-item').forEach(item => {
    item.addEventListener('click', function(e) {
        e.preventDefault();
        
        // Remove active class from all items
        document.querySelectorAll('.nav-item').forEach(nav => nav.classList.remove('active'));
        
        // Add active class to clicked item
        this.classList.add('active');
        
        console.log('Navigated to:', this.textContent);
    });
});

// Simulate real-time data updates
setInterval(() => {
    const metrics = document.querySelectorAll('.metric');
    metrics.forEach(metric => {
        if (metric.textContent.includes('$')) {
            const current = parseInt(metric.textContent.replace(/[^0-9]/g, ''));
            metric.textContent = '$' + (current + Math.floor(Math.random() * 100)).toLocaleString();
        }
    });
}, 5000);"""
        
        return base_js
    
    def create_package_json(self, project_path, project_name):
        """Create package.json for the project"""
        package_data = {
            "name": project_name.lower().replace(' ', '-'),
            "version": "1.0.0",
            "description": f"Web project created by JARVIS AI Assistant",
            "main": "index.html",
            "scripts": {
                "start": "python -m http.server 8000",
                "dev": "python -m http.server 8000"
            },
            "keywords": ["web", "jarvis", "ai-generated"],
            "author": "JARVIS AI Assistant",
            "license": "MIT"
        }
        
        (project_path / 'package.json').write_text(json.dumps(package_data, indent=2))
    
    def create_readme(self, project_path, project_name, template, framework):
        """Create README.md for the project"""
        readme_content = f"""# {project_name.title()}

A {template} web project created by JARVIS AI Assistant using {framework}.

## Features

- Responsive design
- Modern CSS styling
- Interactive JavaScript
- Clean project structure

## Getting Started

1. Open `index.html` in your browser
2. Or run a local server:
   ```bash
   python -m http.server 8000
   ```
3. Visit `http://localhost:8000`

## Project Structure

```
{project_name}/
├── index.html          # Main HTML file
├── css/
│   └── style.css      # Styles
├── js/
│   └── script.js      # JavaScript
├── images/            # Image assets
├── assets/            # Other assets
├── package.json       # Project configuration
└── README.md          # This file
```

## Created by JARVIS

This project was automatically generated by JARVIS AI Assistant.
Template: {template} | Framework: {framework}

---
*Generated on {time.strftime('%Y-%m-%d %H:%M:%S')}*
"""
        
        (project_path / 'README.md').write_text(readme_content)
    
    def open_project_in_browser(self, project_path):
        """Open project in default browser"""
        try:
            index_file = project_path / 'index.html'
            if index_file.exists():
                webbrowser.open(f"file://{index_file.absolute()}")
                return True, f"Opened {project_path.name} in browser"
            else:
                return False, "index.html not found"
        except Exception as e:
            return False, f"Failed to open in browser: {e}"
    
    def start_dev_server(self, project_path, port=8000):
        """Start a development server for the project"""
        try:
            os.chdir(project_path)
            subprocess.Popen(['python', '-m', 'http.server', str(port)],
                           stdout=subprocess.DEVNULL,
                           stderr=subprocess.DEVNULL)
            
            # Open in browser after a short delay
            time.sleep(1)
            webbrowser.open(f"http://localhost:{port}")
            
            return True, f"Development server started on http://localhost:{port}"
        except Exception as e:
            return False, f"Failed to start dev server: {e}"
