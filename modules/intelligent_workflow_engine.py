import json
import time
import threading
import keyboard
from datetime import datetime
from pathlib import Path

class IntelligentWorkflowEngine:
    def __init__(self, jarvis_instance):
        self.jarvis = jarvis_instance
        self.workflows = {}
        self.workflow_file = Path.cwd() / "Memory" / "intelligent_workflows.json"
        self.active_workflow = None
        self.workflow_paused = False
        self.modification_mode = False
        
        # Available JARVIS tools that can be called in workflows
        self.available_tools = {
            '/web_search': self.call_web_search,
            '/vision': self.call_vision,
            '/memory': self.call_memory,
            '/system': self.call_system,
            '/web_dev': self.call_web_dev,
            '/ai_think': self.call_ai_think,
            '/file_ops': self.call_file_ops,
            '/context': self.call_context
        }
        
        self.load_workflows()
        self.setup_hotkeys()
    
    def setup_hotkeys(self):
        """Setup keyboard shortcuts for workflow control"""
        try:
            keyboard.add_hotkey('ctrl+m', self.toggle_modification_mode)
            keyboard.add_hotkey('ctrl+p', self.pause_resume_workflow)
        except:
            print("⚠️ Keyboard shortcuts not available in this environment")
    
    def toggle_modification_mode(self):
        """Toggle workflow modification mode (Ctrl+M)"""
        if self.active_workflow:
            self.modification_mode = not self.modification_mode
            if self.modification_mode:
                print("\n🔧 WORKFLOW MODIFICATION MODE ACTIVATED")
                print("You can now modify the current workflow. Press Ctrl+M again to continue.")
                self.jarvis.ai.speak("Workflow modification mode activated")
            else:
                print("✅ Continuing workflow execution...")
                self.jarvis.ai.speak("Continuing workflow")
    
    def pause_resume_workflow(self):
        """Pause/resume workflow execution (Ctrl+P)"""
        if self.active_workflow:
            self.workflow_paused = not self.workflow_paused
            if self.workflow_paused:
                print("⏸️ Workflow paused")
                self.jarvis.ai.speak("Workflow paused")
            else:
                print("▶️ Workflow resumed")
                self.jarvis.ai.speak("Workflow resumed")
    
    def generate_research_workflow(self, research_topic, depth="comprehensive"):
        """AI generates intelligent research workflow"""
        if not self.jarvis.ai.client:
            return None
            
        prompt = f"""Create an intelligent research workflow for: "{research_topic}"

Generate a JSON workflow with these capabilities:
- Use /web_search for finding information
- Use /ai_think for analysis and synthesis
- Use /file_ops for saving research
- Use /web_dev for creating research reports
- Include decision points and adaptive steps

Depth: {depth}

Return ONLY a JSON object with this structure:
{{
  "name": "Research: [topic]",
  "description": "Comprehensive research workflow",
  "adaptive": true,
  "steps": [
    {{
      "type": "tool_call",
      "tool": "/web_search",
      "action": "search query here",
      "description": "Search for information",
      "adaptive_next": true
    }},
    {{
      "type": "ai_decision",
      "condition": "evaluate search results",
      "true_action": "continue research",
      "false_action": "refine search",
      "description": "Evaluate results quality"
    }}
  ]
}}"""

        try:
            response = self.jarvis.ai.client.chat.completions.create(
                model=self.jarvis.ai.model,
                messages=[
                    {"role": "system", "content": "You are an expert workflow designer. Return only valid JSON."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=1500
            )
            
            result = response.choices[0].message.content.strip()
            if "```json" in result:
                result = result.split("```json")[1].split("```")[0]
            elif "```" in result:
                result = result.split("```")[1].split("```")[0]
            
            workflow_data = json.loads(result)
            workflow_id = self.create_workflow_from_data(workflow_data)
            return workflow_id
            
        except Exception as e:
            print(f"Error generating workflow: {e}")
            return self.create_fallback_research_workflow(research_topic)
    
    def create_fallback_research_workflow(self, topic):
        """Create a basic research workflow if AI generation fails"""
        workflow_data = {
            "name": f"Research: {topic}",
            "description": f"Comprehensive research on {topic}",
            "adaptive": True,
            "steps": [
                {
                    "type": "speak",
                    "action": f"Starting comprehensive research on {topic}",
                    "description": "Announce research start"
                },
                {
                    "type": "tool_call",
                    "tool": "/web_search",
                    "action": f"{topic} overview definition",
                    "description": "Search for basic information"
                },
                {
                    "type": "tool_call",
                    "tool": "/ai_think",
                    "action": f"analyze and summarize findings about {topic}",
                    "description": "Analyze initial findings"
                },
                {
                    "type": "tool_call",
                    "tool": "/web_search",
                    "action": f"{topic} latest developments trends 2024",
                    "description": "Search for recent developments"
                },
                {
                    "type": "tool_call",
                    "tool": "/file_ops",
                    "action": f"create research report for {topic}",
                    "description": "Save research findings"
                },
                {
                    "type": "speak",
                    "action": f"Research on {topic} completed and saved",
                    "description": "Announce completion"
                }
            ]
        }
        
        return self.create_workflow_from_data(workflow_data)
    
    def create_workflow_from_data(self, workflow_data):
        """Create workflow from JSON data"""
        workflow_id = workflow_data["name"].lower().replace(' ', '_').replace(':', '')
        
        workflow = {
            "name": workflow_data["name"],
            "description": workflow_data["description"],
            "steps": workflow_data["steps"],
            "adaptive": workflow_data.get("adaptive", False),
            "created": datetime.now().isoformat(),
            "last_run": None,
            "run_count": 0,
            "active": True
        }
        
        self.workflows[workflow_id] = workflow
        self.save_workflows()
        return workflow_id
    
    def execute_intelligent_workflow(self, workflow_id):
        """Execute workflow with intelligent features"""
        if workflow_id not in self.workflows:
            return False, f"Workflow '{workflow_id}' not found"
        
        workflow = self.workflows[workflow_id]
        self.active_workflow = workflow_id
        self.workflow_paused = False
        self.modification_mode = False
        
        print(f"🧠 Executing intelligent workflow: {workflow['name']}")
        self.jarvis.ai.speak(f"Starting intelligent workflow {workflow['name']}")
        
        results = []
        context = {"research_data": [], "decisions": [], "adaptations": []}
        
        for i, step in enumerate(workflow["steps"], 1):
            # Check for pause/modification
            while self.workflow_paused or self.modification_mode:
                if self.modification_mode:
                    modified_step = self.handle_step_modification(step, i)
                    if modified_step:
                        step = modified_step
                        workflow["steps"][i-1] = step  # Update workflow
                        self.save_workflows()
                    self.modification_mode = False
                time.sleep(0.1)
            
            try:
                print(f"  Step {i}: {step['description']}")
                
                success = False
                step_result = None
                
                if step["type"] == "tool_call":
                    success, step_result = self.execute_tool_call(step, context)
                    
                elif step["type"] == "ai_decision":
                    success, step_result = self.execute_ai_decision(step, context)
                    
                elif step["type"] == "adaptive_step":
                    success, step_result = self.execute_adaptive_step(step, context)
                    
                elif step["type"] == "speak":
                    self.jarvis.ai.speak(step["action"])
                    success = True
                    step_result = "Spoken message"
                    
                elif step["type"] == "wait":
                    time.sleep(int(step["action"]))
                    success = True
                    step_result = f"Waited {step['action']} seconds"
                
                # Store result in context for future steps
                context["step_results"] = context.get("step_results", [])
                context["step_results"].append({
                    "step": i,
                    "result": step_result,
                    "success": success
                })
                
                results.append({
                    "step": i,
                    "description": step["description"],
                    "success": success,
                    "result": step_result
                })
                
                if success:
                    print(f"    ✅ Success: {step_result}")
                else:
                    print(f"    ❌ Failed: {step_result}")
                
                # Adaptive workflow logic
                if workflow.get("adaptive") and "adaptive_next" in step:
                    next_steps = self.generate_adaptive_next_steps(step, step_result, context)
                    if next_steps:
                        workflow["steps"].extend(next_steps)
                        print(f"    🔄 Added {len(next_steps)} adaptive steps")
                
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
        
        self.active_workflow = None
        success_count = len([r for r in results if r["success"]])
        success_rate = (success_count / len(results)) * 100
        
        message = f"Intelligent workflow completed: {success_count}/{len(results)} steps successful ({success_rate:.1f}%)"
        self.jarvis.ai.speak("Intelligent workflow completed")
        
        return True, {
            "message": message,
            "results": results,
            "context": context,
            "success_rate": success_rate
        }
    
    def execute_tool_call(self, step, context):
        """Execute a tool call step"""
        tool = step["tool"]
        action = step["action"]
        
        if tool in self.available_tools:
            try:
                result = self.available_tools[tool](action, context)
                return True, result
            except Exception as e:
                return False, str(e)
        else:
            return False, f"Tool {tool} not available"
    
    def execute_ai_decision(self, step, context):
        """Execute an AI decision step"""
        condition = step["condition"]
        
        # Use AI to evaluate condition based on context
        if self.jarvis.ai.client:
            try:
                prompt = f"""Based on the workflow context, evaluate this condition: "{condition}"

Context: {json.dumps(context, indent=2)}

Return only "true" or "false" based on whether the condition is met."""

                response = self.jarvis.ai.client.chat.completions.create(
                    model=self.jarvis.ai.model,
                    messages=[
                        {"role": "system", "content": "You are a workflow decision evaluator. Return only 'true' or 'false'."},
                        {"role": "user", "content": prompt}
                    ],
                    temperature=0.1,
                    max_tokens=10
                )
                
                decision = response.choices[0].message.content.strip().lower()
                
                if decision == "true":
                    action = step.get("true_action", "continue")
                else:
                    action = step.get("false_action", "skip")
                
                context["decisions"].append({
                    "condition": condition,
                    "decision": decision,
                    "action": action
                })
                
                return True, f"Decision: {decision} -> {action}"
                
            except Exception as e:
                return False, str(e)
        
        return False, "AI not available for decision making"
    
    def execute_adaptive_step(self, step, context):
        """Execute an adaptive step that changes based on context"""
        # This would implement adaptive logic based on previous results
        return True, "Adaptive step executed"
    
    def generate_adaptive_next_steps(self, current_step, result, context):
        """Generate next steps based on current results"""
        # This would use AI to generate next steps dynamically
        return []
    
    def handle_step_modification(self, step, step_number):
        """Handle step modification in real-time"""
        print(f"\n🔧 Modifying Step {step_number}: {step['description']}")
        print(f"Current action: {step.get('action', 'N/A')}")
        
        new_action = input("Enter new action (or press Enter to keep current): ").strip()
        if new_action:
            step["action"] = new_action
            print(f"✅ Step modified: {new_action}")
            return step
        
        return None
    
    # Tool call implementations
    def call_web_search(self, query, context):
        """Call web search tool"""
        # This would integrate with actual web search
        result = f"Web search results for: {query}"
        context["research_data"].append({"type": "web_search", "query": query, "result": result})
        return result
    
    def call_vision(self, action, context):
        """Call computer vision tool"""
        if hasattr(self.jarvis, 'computer_vision') and self.jarvis.computer_vision:
            if "screenshot" in action:
                success, message = self.jarvis.computer_vision.take_screenshot()
                return message
        return "Vision tool executed"
    
    def call_memory(self, action, context):
        """Call memory system"""
        if "store" in action:
            # Store workflow results in memory
            self.jarvis.memory.store_knowledge("workflow_results", "latest", str(context))
            return "Data stored in memory"
        return "Memory operation completed"
    
    def call_system(self, action, context):
        """Call system operations"""
        result = self.jarvis.system.execute_command(action)
        return result.get("output", "System command executed")
    
    def call_web_dev(self, action, context):
        """Call web development tools"""
        if "create" in action:
            success, message = self.jarvis.web_developer.build_intelligent_webpage(action)
            return message
        return "Web development task completed"
    
    def call_ai_think(self, action, context):
        """Call AI thinking/analysis"""
        if self.jarvis.ai.client:
            try:
                response = self.jarvis.ai.client.chat.completions.create(
                    model=self.jarvis.ai.model,
                    messages=[
                        {"role": "system", "content": "You are an analytical AI assistant."},
                        {"role": "user", "content": f"Analyze and think about: {action}\n\nContext: {json.dumps(context, indent=2)}"}
                    ],
                    temperature=0.7,
                    max_tokens=500
                )
                
                analysis = response.choices[0].message.content.strip()
                context["research_data"].append({"type": "ai_analysis", "topic": action, "analysis": analysis})
                return analysis
                
            except Exception as e:
                return f"AI analysis error: {e}"
        
        return "AI thinking completed"
    
    def call_file_ops(self, action, context):
        """Call file operations"""
        if "create" in action and "report" in action:
            # Create research report from context
            report_content = self.generate_research_report(context)
            filename = f"research_report_{int(time.time())}.md"
            filepath = Path.cwd() / "playground" / "Documents" / filename
            filepath.parent.mkdir(parents=True, exist_ok=True)
            filepath.write_text(report_content)
            return f"Research report saved to {filename}"
        
        return "File operation completed"
    
    def call_context(self, action, context):
        """Call context management"""
        if "switch" in action:
            # Extract context name and switch
            context_name = action.replace("switch to", "").strip()
            self.jarvis.context_manager.switch_context(context_name)
            return f"Switched to context: {context_name}"
        
        return "Context operation completed"
    
    def generate_research_report(self, context):
        """Generate research report from workflow context"""
        report = f"""# Research Report
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

## Research Data
"""
        
        for item in context.get("research_data", []):
            report += f"\n### {item['type'].title()}\n"
            if item['type'] == 'web_search':
                report += f"Query: {item['query']}\n"
                report += f"Results: {item['result']}\n"
            elif item['type'] == 'ai_analysis':
                report += f"Topic: {item['topic']}\n"
                report += f"Analysis: {item['analysis']}\n"
        
        report += "\n## Workflow Decisions\n"
        for decision in context.get("decisions", []):
            report += f"- {decision['condition']}: {decision['decision']} -> {decision['action']}\n"
        
        return report
    
    def create_interactive_workflow(self, workflow_name):
        """Create workflow interactively with text input"""
        print(f"\n📝 Creating Interactive Workflow: {workflow_name}")
        print("=" * 50)
        print("Available tools: /web_search, /vision, /memory, /system, /web_dev, /ai_think, /file_ops, /context")
        print("Step types: tool_call, speak, wait, ai_decision, adaptive_step")
        print("Type 'done' when finished, 'help' for more info")
        
        steps = []
        step_num = 1
        
        while True:
            print(f"\nStep {step_num}:")
            step_type = input("Step type (tool_call/speak/wait/ai_decision): ").strip()
            
            if step_type.lower() == 'done':
                break
            elif step_type.lower() == 'help':
                self.show_workflow_help()
                continue
            
            description = input("Description: ").strip()
            
            if step_type == "tool_call":
                tool = input("Tool (e.g., /web_search): ").strip()
                action = input("Action/Query: ").strip()
                
                step = {
                    "type": "tool_call",
                    "tool": tool,
                    "action": action,
                    "description": description
                }
                
            elif step_type == "speak":
                message = input("Message to speak: ").strip()
                step = {
                    "type": "speak",
                    "action": message,
                    "description": description
                }
                
            elif step_type == "wait":
                seconds = input("Seconds to wait: ").strip()
                step = {
                    "type": "wait",
                    "action": seconds,
                    "description": description
                }
                
            elif step_type == "ai_decision":
                condition = input("Condition to evaluate: ").strip()
                true_action = input("Action if true: ").strip()
                false_action = input("Action if false: ").strip()
                
                step = {
                    "type": "ai_decision",
                    "condition": condition,
                    "true_action": true_action,
                    "false_action": false_action,
                    "description": description
                }
            
            else:
                print("Invalid step type. Try again.")
                continue
            
            steps.append(step)
            step_num += 1
            print(f"✅ Step {step_num-1} added")
        
        if steps:
            workflow_data = {
                "name": workflow_name,
                "description": f"Interactive workflow: {workflow_name}",
                "adaptive": True,
                "steps": steps
            }
            
            workflow_id = self.create_workflow_from_data(workflow_data)
            print(f"\n✅ Workflow '{workflow_name}' created with {len(steps)} steps!")
            return workflow_id
        
        return None
    
    def show_workflow_help(self):
        """Show workflow creation help"""
        help_text = """
🔧 Workflow Creation Help:

Step Types:
- tool_call: Call JARVIS tools (/web_search, /vision, etc.)
- speak: Make JARVIS speak a message
- wait: Add delay between steps
- ai_decision: Let AI make decisions based on context

Available Tools:
- /web_search: Search the web for information
- /vision: Use computer vision (screenshots, analysis)
- /memory: Store/retrieve from memory system
- /system: Execute system commands
- /web_dev: Create websites and web projects
- /ai_think: AI analysis and reasoning
- /file_ops: File operations (create, save reports)
- /context: Context management (switch contexts)

Examples:
- Tool call: /web_search "latest AI developments"
- Speak: "Research completed successfully"
- Wait: 3 (seconds)
- AI Decision: "Are search results comprehensive enough?"
"""
        print(help_text)
    
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
