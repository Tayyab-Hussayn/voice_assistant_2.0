#!/usr/bin/env python3
"""
JARVIS Intelligence Testing Workflow
Systematic testing of all 20 tools with complex, real-world scenarios
"""

import json
import time
import subprocess
from datetime import datetime
from pathlib import Path

class JARVISIntelligenceTester:
    def __init__(self):
        self.test_results = {
            "session_id": f"test_{int(time.time())}",
            "start_time": datetime.now().isoformat(),
            "tools_tested": 0,
            "tools_passed": 0,
            "tools_failed": 0,
            "test_details": {}
        }
        
        # Define all 20 JARVIS tools with complex test scenarios
        self.tools_to_test = {
            1: {
                "name": "FileSystemManager",
                "description": "Advanced file operations with batch processing",
                "test_scenario": "Create a complex project structure with multiple nested directories, generate configuration files with specific content patterns, and perform batch operations across the entire structure",
                "complexity": "HIGH",
                "skills_tested": ["problem_solving", "pattern_recognition", "automation"]
            },
            2: {
                "name": "SearchSystem", 
                "description": "Regex pattern search across files",
                "test_scenario": "Search for complex patterns across a large codebase, find security vulnerabilities, extract specific data patterns, and generate a comprehensive report",
                "complexity": "HIGH",
                "skills_tested": ["pattern_recognition", "analysis", "reporting"]
            },
            3: {
                "name": "PatternMatcher",
                "description": "Advanced glob pattern matching for file discovery", 
                "test_scenario": "Find all files matching complex criteria across multiple directories, exclude specific patterns, and organize results by file type and modification date",
                "complexity": "MEDIUM",
                "skills_tested": ["pattern_recognition", "organization", "filtering"]
            },
            4: {
                "name": "CodeIntelligence",
                "description": "LSP integration with multi-language support",
                "test_scenario": "Analyze a multi-language codebase, identify function dependencies, suggest refactoring opportunities, and generate documentation for complex functions",
                "complexity": "VERY_HIGH", 
                "skills_tested": ["code_analysis", "reasoning", "documentation"]
            },
            5: {
                "name": "WindowManager",
                "description": "Window management (focus, move, resize)",
                "test_scenario": "Organize a complex development workspace with multiple applications, create an optimal window layout for productivity, and automate window switching workflows",
                "complexity": "MEDIUM",
                "skills_tested": ["automation", "optimization", "workflow_design"]
            },
            6: {
                "name": "ProcessManager", 
                "description": "Process management and system monitoring",
                "test_scenario": "Monitor system performance, identify resource-intensive processes, optimize system performance, and create automated monitoring alerts",
                "complexity": "HIGH",
                "skills_tested": ["system_analysis", "optimization", "automation"]
            },
            7: {
                "name": "WebSearch",
                "description": "Web search API with result processing",
                "test_scenario": "Research a complex technical topic, synthesize information from multiple sources, identify conflicting information, and create a comprehensive analysis report",
                "complexity": "HIGH", 
                "skills_tested": ["research", "synthesis", "critical_thinking"]
            },
            8: {
                "name": "ResearchAnalysis",
                "description": "Automated research workflows and synthesis",
                "test_scenario": "Conduct comprehensive research on emerging technology trends, analyze market implications, identify key players, and generate strategic recommendations",
                "complexity": "VERY_HIGH",
                "skills_tested": ["research", "analysis", "strategic_thinking"]
            },
            9: {
                "name": "KnowledgeManager",
                "description": "Persistent knowledge storage with vector database",
                "test_scenario": "Build a comprehensive knowledge base from multiple sources, create semantic relationships, implement intelligent search, and generate insights from stored knowledge",
                "complexity": "VERY_HIGH",
                "skills_tested": ["knowledge_organization", "semantic_understanding", "insight_generation"]
            },
            10: {
                "name": "SubagentManager",
                "description": "Subagent creation and parallel task execution", 
                "test_scenario": "Coordinate multiple specialized agents to complete a complex software development project, manage dependencies, handle failures, and ensure quality outcomes",
                "complexity": "VERY_HIGH",
                "skills_tested": ["coordination", "project_management", "quality_assurance"]
            },
            11: {
                "name": "TaskManagement",
                "description": "TODO list management and task tracking",
                "test_scenario": "Create and manage a complex project timeline with dependencies, priorities, and resource constraints. Optimize task scheduling and track progress automatically",
                "complexity": "HIGH",
                "skills_tested": ["project_planning", "optimization", "tracking"]
            },
            12: {
                "name": "WorkflowAutomation",
                "description": "Advanced workflow creation and automation",
                "test_scenario": "Design and implement an automated CI/CD pipeline with testing, deployment, and monitoring. Handle edge cases and failure scenarios intelligently",
                "complexity": "VERY_HIGH", 
                "skills_tested": ["automation_design", "error_handling", "system_integration"]
            },
            13: {
                "name": "AWSIntegration",
                "description": "AWS CLI command execution and resource management",
                "test_scenario": "Design and deploy a scalable cloud architecture, implement security best practices, optimize costs, and create monitoring and alerting systems",
                "complexity": "VERY_HIGH",
                "skills_tested": ["cloud_architecture", "security", "cost_optimization"]
            },
            14: {
                "name": "InfrastructureIntegration", 
                "description": "Infrastructure as Code and provisioning",
                "test_scenario": "Create Infrastructure as Code for a complex multi-tier application, implement blue-green deployment, and ensure high availability and disaster recovery",
                "complexity": "VERY_HIGH",
                "skills_tested": ["infrastructure_design", "reliability", "automation"]
            },
            15: {
                "name": "SecurityCompliance",
                "description": "Security scanning and compliance checking",
                "test_scenario": "Perform comprehensive security audit of a complex application, identify vulnerabilities, implement fixes, and ensure compliance with multiple frameworks",
                "complexity": "VERY_HIGH",
                "skills_tested": ["security_analysis", "compliance", "risk_assessment"]
            },
            16: {
                "name": "WebDeveloper",
                "description": "Intelligent web application builder",
                "test_scenario": "Build a full-stack web application with modern architecture, implement authentication, create responsive design, and optimize performance",
                "complexity": "VERY_HIGH",
                "skills_tested": ["full_stack_development", "architecture", "optimization"]
            },
            17: {
                "name": "MemorySystem",
                "description": "Long-term memory and context management", 
                "test_scenario": "Implement intelligent context switching across multiple complex projects, maintain conversation history, and provide contextual recommendations",
                "complexity": "HIGH",
                "skills_tested": ["context_management", "memory_optimization", "recommendation"]
            },
            18: {
                "name": "LearningSystem",
                "description": "Learning from interactions and adaptation",
                "test_scenario": "Analyze interaction patterns, identify improvement opportunities, adapt behavior based on feedback, and demonstrate measurable learning progress",
                "complexity": "VERY_HIGH",
                "skills_tested": ["pattern_analysis", "adaptation", "self_improvement"]
            },
            19: {
                "name": "IntentClassifier",
                "description": "Smart command/question detection",
                "test_scenario": "Process ambiguous and complex user inputs, correctly classify intent in edge cases, handle context switching, and provide intelligent routing",
                "complexity": "HIGH", 
                "skills_tested": ["natural_language_understanding", "context_awareness", "classification"]
            },
            20: {
                "name": "PerformanceMonitor",
                "description": "Performance tracking and optimization",
                "test_scenario": "Monitor system performance under complex workloads, identify bottlenecks, suggest optimizations, and implement automated performance tuning",
                "complexity": "HIGH",
                "skills_tested": ["performance_analysis", "optimization", "automation"]
            }
        }
    
    def run_comprehensive_test(self):
        """Run comprehensive intelligence testing workflow"""
        print("🧪 JARVIS Intelligence Testing Framework")
        print("=" * 50)
        print(f"📊 Testing {len(self.tools_to_test)} tools with complex scenarios")
        print(f"🎯 Objective: Achieve enterprise-level AI agent capabilities")
        print()
        
        # Start with the most critical tools first
        priority_order = [4, 8, 9, 10, 12, 13, 14, 15, 16, 7, 1, 2, 6, 11, 17, 18, 19, 20, 3, 5]
        
        for tool_id in priority_order:
            if tool_id in self.tools_to_test:
                self.test_tool(tool_id)
                print()
        
        self.generate_final_report()
    
    def test_tool(self, tool_id):
        """Test individual tool with complex scenario"""
        tool = self.tools_to_test[tool_id]
        print(f"🔧 Testing Tool {tool_id}: {tool['name']}")
        print(f"📝 Scenario: {tool['test_scenario']}")
        print(f"🎯 Complexity: {tool['complexity']}")
        print(f"🧠 Skills: {', '.join(tool['skills_tested'])}")
        print()
        
        # Create test command for JARVIS
        test_command = self.create_test_command(tool)
        
        print(f"🚀 Executing test...")
        print(f"💬 Command: {test_command}")
        print()
        
        # Execute test
        result = self.execute_jarvis_test(test_command)
        
        # Analyze results
        success = self.analyze_test_result(tool_id, result)
        
        # Record results
        self.record_test_result(tool_id, tool, result, success)
        
        if success:
            print(f"✅ Tool {tool_id} ({tool['name']}) - PASSED")
            self.test_results["tools_passed"] += 1
        else:
            print(f"❌ Tool {tool_id} ({tool['name']}) - FAILED")
            print(f"🔍 Analysis needed for improvement")
            self.test_results["tools_failed"] += 1
        
        self.test_results["tools_tested"] += 1
    
    def create_test_command(self, tool):
        """Create appropriate test command based on tool type"""
        scenario = tool['test_scenario']
        
        # Create natural language command without hints
        if "file" in tool['name'].lower():
            return f"I need you to {scenario.lower()}. Please complete this task autonomously."
        elif "search" in tool['name'].lower():
            return f"Please {scenario.lower()}. Use your search capabilities to complete this comprehensively."
        elif "web" in tool['name'].lower():
            return f"Research task: {scenario.lower()}. Provide detailed analysis."
        elif "code" in tool['name'].lower():
            return f"Code analysis task: {scenario.lower()}. Show your reasoning."
        elif "aws" in tool['name'].lower() or "infrastructure" in tool['name'].lower():
            return f"Cloud architecture task: {scenario.lower()}. Design and explain your approach."
        elif "security" in tool['name'].lower():
            return f"Security assessment: {scenario.lower()}. Provide comprehensive analysis."
        else:
            return f"Complex task: {scenario.lower()}. Complete this using your best capabilities."
    
    def execute_jarvis_test(self, command):
        """Execute test command with JARVIS"""
        try:
            # Run JARVIS with the test command
            cmd = [
                'python', 'jarvis_unified_cli.py'
            ]
            
            # Create input with command and exit
            test_input = f"{command}\nexit\n"
            
            result = subprocess.run(
                cmd,
                input=test_input,
                text=True,
                capture_output=True,
                timeout=120,  # 2 minute timeout
                cwd=Path.cwd()
            )
            
            return {
                "success": result.returncode == 0,
                "stdout": result.stdout,
                "stderr": result.stderr,
                "execution_time": time.time()
            }
            
        except subprocess.TimeoutExpired:
            return {
                "success": False,
                "stdout": "",
                "stderr": "Test timed out after 2 minutes",
                "execution_time": 120
            }
        except Exception as e:
            return {
                "success": False,
                "stdout": "",
                "stderr": f"Test execution error: {str(e)}",
                "execution_time": 0
            }
    
    def analyze_test_result(self, tool_id, result):
        """Analyze test result for intelligence and capability"""
        if not result["success"]:
            return False
        
        output = result["stdout"].lower()
        
        # Check for intelligence indicators
        intelligence_indicators = [
            "analyzing", "processing", "reasoning", "thinking",
            "completed", "generated", "created", "implemented",
            "optimized", "identified", "suggested", "recommended"
        ]
        
        # Check for problem-solving indicators
        problem_solving_indicators = [
            "solution", "approach", "strategy", "method",
            "workflow", "process", "steps", "plan"
        ]
        
        # Check for error handling
        error_indicators = ["error", "failed", "cannot", "unable"]
        
        intelligence_score = sum(1 for indicator in intelligence_indicators if indicator in output)
        problem_solving_score = sum(1 for indicator in problem_solving_indicators if indicator in output)
        error_count = sum(1 for indicator in error_indicators if indicator in output)
        
        # Success criteria: High intelligence + problem solving, low errors
        return (intelligence_score >= 2 and problem_solving_score >= 1 and error_count <= 1)
    
    def record_test_result(self, tool_id, tool, result, success):
        """Record detailed test results"""
        self.test_results["test_details"][tool_id] = {
            "tool_name": tool["name"],
            "test_scenario": tool["test_scenario"],
            "complexity": tool["complexity"],
            "skills_tested": tool["skills_tested"],
            "success": success,
            "execution_time": result.get("execution_time", 0),
            "output_length": len(result.get("stdout", "")),
            "has_errors": bool(result.get("stderr", "")),
            "timestamp": datetime.now().isoformat()
        }
    
    def generate_final_report(self):
        """Generate comprehensive test report"""
        self.test_results["end_time"] = datetime.now().isoformat()
        self.test_results["success_rate"] = (self.test_results["tools_passed"] / self.test_results["tools_tested"]) * 100
        
        print("📊 JARVIS Intelligence Testing - Final Report")
        print("=" * 60)
        print(f"🎯 Tools Tested: {self.test_results['tools_tested']}")
        print(f"✅ Tools Passed: {self.test_results['tools_passed']}")
        print(f"❌ Tools Failed: {self.test_results['tools_failed']}")
        print(f"📈 Success Rate: {self.test_results['success_rate']:.1f}%")
        print()
        
        # Save detailed results
        report_file = f"JARVIS_Intelligence_Test_Report_{self.test_results['session_id']}.json"
        with open(report_file, 'w') as f:
            json.dump(self.test_results, f, indent=2)
        
        print(f"📄 Detailed report saved: {report_file}")
        
        # Provide improvement recommendations
        if self.test_results["tools_failed"] > 0:
            print()
            print("🔧 Improvement Recommendations:")
            print("- Analyze failed tests for specific weaknesses")
            print("- Enhance reasoning capabilities in identified areas")
            print("- Improve error handling and recovery")
            print("- Re-test after improvements until 100% success rate")

def main():
    """Main testing workflow"""
    tester = JARVISIntelligenceTester()
    tester.run_comprehensive_test()

if __name__ == "__main__":
    main()
