import os
import json
from pathlib import Path
import webbrowser
import subprocess
import time

class IntelligentWebBuilder:
    def __init__(self, ai_handler):
        self.ai_handler = ai_handler
        # Set up dedicated Web Projects directory
        self.web_projects_dir = Path.cwd() / "playground" / "Web Projects"
        self.web_projects_dir.mkdir(parents=True, exist_ok=True)
        
    def analyze_web_request(self, user_request):
        """Analyze user request and extract web page requirements"""
        if not self.ai_handler.client:
            return None
            
        analysis_prompt = f"""Analyze this web page request and extract the requirements:

User Request: "{user_request}"

Extract and return ONLY a JSON object with these fields:
{{
    "page_type": "landing/portfolio/dashboard/blog/ecommerce/other",
    "title": "page title",
    "description": "what the page should do/show",
    "sections": ["list", "of", "main", "sections"],
    "colors": {{"primary": "#color", "secondary": "#color"}},
    "features": ["interactive elements", "animations", "etc"],
    "content": {{"section_name": "content description"}}
}}

Examples:
- "build a landing page for my restaurant" → page_type: "landing", sections: ["hero", "menu", "contact"]
- "create a portfolio for a photographer" → page_type: "portfolio", sections: ["gallery", "about", "contact"]
- "make a dashboard for sales data" → page_type: "dashboard", sections: ["charts", "metrics", "tables"]

Return ONLY the JSON, no other text."""

        try:
            response = self.ai_handler.client.chat.completions.create(
                model=self.ai_handler.model,
                messages=[
                    {"role": "system", "content": "You are a web development analyst. Return only valid JSON."},
                    {"role": "user", "content": analysis_prompt}
                ],
                temperature=0.3,
                max_tokens=500
            )
            
            result = response.choices[0].message.content.strip()
            # Clean up the response to extract JSON
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            
            # Try to parse JSON, with fallback
            try:
                return json.loads(result)
            except json.JSONDecodeError:
                # Fallback: create basic requirements from user request
                return self.create_fallback_requirements(user_request)
                
        except Exception as e:
            print(f"Analysis error: {e}")
            return self.create_fallback_requirements(user_request)
    
    def generate_custom_html(self, requirements):
        """Generate custom HTML based on requirements"""
        if not self.ai_handler.client:
            return self.fallback_html(requirements)
            
        html_prompt = f"""Generate a complete HTML page based on these requirements:

Requirements: {json.dumps(requirements, indent=2)}

Create a modern, responsive HTML page with:
1. Proper HTML5 structure
2. Meta tags for responsiveness
3. Link to external CSS file: "style.css"
4. Link to external JS file: "script.js"
5. Semantic HTML elements
6. All sections from requirements
7. Placeholder content that matches the description
8. Modern class names for styling

Return ONLY the HTML code, no explanations."""

        try:
            response = self.ai_handler.client.chat.completions.create(
                model=self.ai_handler.model,
                messages=[
                    {"role": "system", "content": "You are an expert HTML developer. Generate clean, semantic HTML5 code."},
                    {"role": "user", "content": html_prompt}
                ],
                temperature=0.4,
                max_tokens=1500
            )
            
            html_content = response.choices[0].message.content.strip()
            # Clean up code blocks
            if "```html" in html_content:
                html_content = html_content.split("```html")[1].split("```")[0]
            elif "```" in html_content:
                html_content = html_content.split("```")[1].split("```")[0]
                
            return html_content.strip()
            
        except Exception as e:
            print(f"HTML generation error: {e}")
            return self.fallback_html(requirements)
    
    def generate_custom_css(self, requirements):
        """Generate custom CSS based on requirements"""
        if not self.ai_handler.client:
            return self.fallback_css(requirements)
            
        css_prompt = f"""Generate modern CSS for this web page:

Requirements: {json.dumps(requirements, indent=2)}

Create CSS with:
1. Modern reset/normalize
2. Responsive design (mobile-first)
3. Color scheme from requirements
4. Typography hierarchy
5. Layout for all sections
6. Hover effects and transitions
7. Modern design patterns (flexbox/grid)
8. Professional styling

Return ONLY the CSS code, no explanations."""

        try:
            response = self.ai_handler.client.chat.completions.create(
                model=self.ai_handler.model,
                messages=[
                    {"role": "system", "content": "You are an expert CSS developer. Generate modern, responsive CSS."},
                    {"role": "user", "content": css_prompt}
                ],
                temperature=0.4,
                max_tokens=2000
            )
            
            css_content = response.choices[0].message.content.strip()
            # Clean up code blocks
            if "```css" in css_content:
                css_content = css_content.split("```css")[1].split("```")[0]
            elif "```" in css_content:
                css_content = css_content.split("```")[1].split("```")[0]
                
            return css_content.strip()
            
        except Exception as e:
            print(f"CSS generation error: {e}")
            return self.fallback_css(requirements)
    
    def generate_custom_js(self, requirements):
        """Generate custom JavaScript based on requirements"""
        if not self.ai_handler.client:
            return self.fallback_js(requirements)
            
        js_prompt = f"""Generate JavaScript for this web page:

Requirements: {json.dumps(requirements, indent=2)}

Create JavaScript with:
1. DOM ready event listener
2. Interactive features from requirements
3. Form handling if needed
4. Smooth scrolling for navigation
5. Basic animations/effects
6. Mobile-friendly interactions
7. Error handling

Return ONLY the JavaScript code, no explanations."""

        try:
            response = self.ai_handler.client.chat.completions.create(
                model=self.ai_handler.model,
                messages=[
                    {"role": "system", "content": "You are an expert JavaScript developer. Generate clean, modern JavaScript."},
                    {"role": "user", "content": js_prompt}
                ],
                temperature=0.4,
                max_tokens=1000
            )
            
            js_content = response.choices[0].message.content.strip()
            # Clean up code blocks
            if "```javascript" in js_content:
                js_content = js_content.split("```javascript")[1].split("```")[0]
            elif "```js" in js_content:
                js_content = js_content.split("```js")[1].split("```")[0]
            elif "```" in js_content:
                js_content = js_content.split("```")[1].split("```")[0]
                
            return js_content.strip()
            
        except Exception as e:
            print(f"JavaScript generation error: {e}")
            return self.fallback_js(requirements)
    
    def build_intelligent_webpage(self, user_request, project_name=None):
        """Build a custom webpage based on user's natural language request"""
        try:
            # Step 1: Analyze the request
            print("🔍 Analyzing your web page requirements...")
            requirements = self.analyze_web_request(user_request)
            
            if not requirements:
                return False, "Could not understand web page requirements"
            
            print(f"📋 Building: {requirements.get('title', 'Custom Web Page')}")
            
            # Step 2: Create project directory in Web Projects folder
            if not project_name:
                project_name = requirements.get('title', 'custom_webpage').lower().replace(' ', '_')
            
            project_path = self.web_projects_dir / project_name
            project_path.mkdir(exist_ok=True)
            
            print(f"📁 Creating project in: {project_path}")
            
            # Create subdirectories
            (project_path / 'css').mkdir(exist_ok=True)
            (project_path / 'js').mkdir(exist_ok=True)
            (project_path / 'images').mkdir(exist_ok=True)
            
            # Step 3: Generate custom HTML
            print("🏗️ Generating HTML structure...")
            html_content = self.generate_custom_html(requirements)
            (project_path / 'index.html').write_text(html_content)
            
            # Step 4: Generate custom CSS
            print("🎨 Creating custom styles...")
            css_content = self.generate_custom_css(requirements)
            (project_path / 'css' / 'style.css').write_text(css_content)
            
            # Step 5: Generate custom JavaScript
            print("⚡ Adding interactivity...")
            js_content = self.generate_custom_js(requirements)
            (project_path / 'js' / 'script.js').write_text(js_content)
            
            # Step 6: Create README
            readme_content = f"""# {requirements.get('title', 'Custom Web Page')}

{requirements.get('description', 'Custom web page built by JARVIS AI')}

## Features
{chr(10).join('- ' + feature for feature in requirements.get('features', []))}

## Sections
{chr(10).join('- ' + section.title() for section in requirements.get('sections', []))}

## Built by JARVIS
This webpage was intelligently generated based on your requirements:
"{user_request}"

Generated on: {time.strftime('%Y-%m-%d %H:%M:%S')}
"""
            (project_path / 'README.md').write_text(readme_content)
            
            # Step 7: Open in browser
            index_file = project_path / 'index.html'
            webbrowser.open(f"file://{index_file.absolute()}")
            
            return True, f"Custom webpage '{project_name}' built in Web Projects folder and opened in browser!"
            
        except Exception as e:
            return False, f"Failed to build webpage: {e}"
    
    def fallback_html(self, requirements):
        """Fallback HTML when AI is not available"""
        title = requirements.get('title', 'Custom Page')
        sections = requirements.get('sections', ['header', 'main', 'footer'])
        
        html = f"""<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link rel="stylesheet" href="css/style.css">
</head>
<body>
    <header class="header">
        <h1>{title}</h1>
        <nav class="nav">
            {chr(10).join(f'            <a href="#{section}">{section.title()}</a>' for section in sections)}
        </nav>
    </header>
    
    <main class="main">
        {chr(10).join(f'        <section id="{section}" class="{section}"><h2>{section.title()}</h2><p>Content for {section} section.</p></section>' for section in sections if section not in ['header', 'footer'])}
    </main>
    
    <footer class="footer">
        <p>&copy; 2026 {title} - Built by JARVIS AI</p>
    </footer>
    
    <script src="js/script.js"></script>
</body>
</html>"""
        return html
    
    def fallback_css(self, requirements):
        """Fallback CSS when AI is not available"""
        primary_color = requirements.get('colors', {}).get('primary', '#007bff')
        secondary_color = requirements.get('colors', {}).get('secondary', '#6c757d')
        
        return f"""* {{
    margin: 0;
    padding: 0;
    box-sizing: border-box;
}}

body {{
    font-family: 'Arial', sans-serif;
    line-height: 1.6;
    color: #333;
}}

.header {{
    background: {primary_color};
    color: white;
    padding: 2rem 0;
    text-align: center;
}}

.nav a {{
    color: white;
    text-decoration: none;
    margin: 0 1rem;
    padding: 0.5rem 1rem;
    border-radius: 5px;
    transition: background 0.3s;
}}

.nav a:hover {{
    background: rgba(255,255,255,0.2);
}}

.main {{
    max-width: 1200px;
    margin: 0 auto;
    padding: 2rem;
}}

section {{
    margin: 3rem 0;
    padding: 2rem;
    background: #f8f9fa;
    border-radius: 10px;
}}

.footer {{
    background: {secondary_color};
    color: white;
    text-align: center;
    padding: 2rem 0;
    margin-top: 3rem;
}}

@media (max-width: 768px) {{
    .nav a {{
        display: block;
        margin: 0.5rem 0;
    }}
    
    .main {{
        padding: 1rem;
    }}
}}"""
    
    def fallback_js(self, requirements):
        """Fallback JavaScript when AI is not available"""
        return """document.addEventListener('DOMContentLoaded', function() {
    console.log('Custom webpage loaded by JARVIS AI');
    
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
    
    // Add some basic interactivity
    const sections = document.querySelectorAll('section');
    sections.forEach(section => {
        section.addEventListener('mouseenter', function() {
            this.style.transform = 'translateY(-5px)';
            this.style.transition = 'transform 0.3s ease';
        });
        
        section.addEventListener('mouseleave', function() {
            this.style.transform = 'translateY(0)';
        });
    });
});"""
    
    def create_fallback_requirements(self, user_request):
        """Create basic requirements when AI analysis fails"""
        request_lower = user_request.lower()
        
        # Determine page type
        if "restaurant" in request_lower or "food" in request_lower:
            page_type = "restaurant"
            sections = ["hero", "menu", "about", "contact"]
            colors = {"primary": "#d4a574", "secondary": "#8b4513"}
        elif "portfolio" in request_lower:
            page_type = "portfolio"
            sections = ["hero", "about", "projects", "contact"]
            colors = {"primary": "#007bff", "secondary": "#6c757d"}
        elif "business" in request_lower or "company" in request_lower:
            page_type = "business"
            sections = ["hero", "services", "about", "contact"]
            colors = {"primary": "#28a745", "secondary": "#17a2b8"}
        else:
            page_type = "landing"
            sections = ["hero", "features", "about", "contact"]
            colors = {"primary": "#007bff", "secondary": "#6c757d"}
        
        # Extract title/name
        words = user_request.split()
        title = "Custom Website"
        for i, word in enumerate(words):
            if word.lower() in ["called", "named"] and i + 1 < len(words):
                title = " ".join(words[i + 1:]).strip()
                break
        
        return {
            "page_type": page_type,
            "title": title,
            "description": f"A {page_type} website for {title}",
            "sections": sections,
            "colors": colors,
            "features": ["responsive design", "modern styling", "interactive elements"],
            "content": {section: f"Content for {section} section" for section in sections}
        }
