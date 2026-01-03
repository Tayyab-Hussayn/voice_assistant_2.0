import json
import threading
import time
from datetime import datetime, timedelta
from pathlib import Path
import schedule

class TaskScheduler:
    def __init__(self, jarvis_instance):
        self.jarvis = jarvis_instance
        self.tasks = {}
        self.running = False
        self.scheduler_thread = None
        self.tasks_file = Path.cwd() / "Memory" / "scheduled_tasks.json"
        
        # Load existing tasks
        self.load_tasks()
        
    def load_tasks(self):
        """Load scheduled tasks from file"""
        if self.tasks_file.exists():
            try:
                with open(self.tasks_file, 'r') as f:
                    self.tasks = json.load(f)
            except:
                self.tasks = {}
    
    def save_tasks(self):
        """Save scheduled tasks to file"""
        self.tasks_file.parent.mkdir(parents=True, exist_ok=True)
        with open(self.tasks_file, 'w') as f:
            json.dump(self.tasks, f, indent=2)
    
    def schedule_task(self, task_name, command, schedule_type, schedule_value, description=""):
        """Schedule a new task"""
        task_id = f"{task_name}_{int(time.time())}"
        
        task = {
            "name": task_name,
            "command": command,
            "schedule_type": schedule_type,  # "once", "daily", "weekly", "interval"
            "schedule_value": schedule_value,  # datetime string or interval seconds
            "description": description,
            "created": datetime.now().isoformat(),
            "last_run": None,
            "run_count": 0,
            "active": True
        }
        
        self.tasks[task_id] = task
        self.save_tasks()
        
        # Set up the actual schedule
        self.setup_schedule(task_id, task)
        
        return task_id
    
    def setup_schedule(self, task_id, task):
        """Set up actual scheduling for a task"""
        if task["schedule_type"] == "daily":
            schedule.every().day.at(task["schedule_value"]).do(self.execute_task, task_id)
        elif task["schedule_type"] == "weekly":
            day, time_str = task["schedule_value"].split(" ")
            getattr(schedule.every(), day.lower()).at(time_str).do(self.execute_task, task_id)
        elif task["schedule_type"] == "interval":
            schedule.every(int(task["schedule_value"])).seconds.do(self.execute_task, task_id)
        elif task["schedule_type"] == "once":
            # For one-time tasks, we'll check in the scheduler loop
            pass
    
    def execute_task(self, task_id):
        """Execute a scheduled task"""
        if task_id not in self.tasks or not self.tasks[task_id]["active"]:
            return
        
        task = self.tasks[task_id]
        
        try:
            print(f"🕒 Executing scheduled task: {task['name']}")
            
            # Execute the command through JARVIS
            command = task["command"]
            result = self.jarvis.system.execute_command(command)
            
            # Update task statistics
            task["last_run"] = datetime.now().isoformat()
            task["run_count"] += 1
            
            # Log the execution
            self.jarvis.memory.remember_interaction(
                f"Scheduled task: {task['name']}", 
                f"Executed: {command}",
                "scheduled_task",
                result["success"]
            )
            
            # Speak notification if JARVIS is active
            if hasattr(self.jarvis, 'ai') and self.jarvis.ai:
                self.jarvis.ai.speak(f"Scheduled task {task['name']} completed")
            
            # Deactivate one-time tasks
            if task["schedule_type"] == "once":
                task["active"] = False
            
            self.save_tasks()
            
        except Exception as e:
            print(f"❌ Error executing task {task['name']}: {e}")
            self.jarvis.memory.remember_interaction(
                f"Scheduled task: {task['name']}", 
                f"Error: {str(e)}",
                "scheduled_task",
                False
            )
    
    def start_scheduler(self):
        """Start the task scheduler"""
        if self.running:
            return False, "Scheduler already running"
        
        self.running = True
        self.scheduler_thread = threading.Thread(target=self.scheduler_loop)
        self.scheduler_thread.daemon = True
        self.scheduler_thread.start()
        
        return True, "Task scheduler started"
    
    def stop_scheduler(self):
        """Stop the task scheduler"""
        self.running = False
        if self.scheduler_thread:
            self.scheduler_thread.join(timeout=1)
        
        return True, "Task scheduler stopped"
    
    def scheduler_loop(self):
        """Main scheduler loop"""
        while self.running:
            # Run scheduled tasks
            schedule.run_pending()
            
            # Check one-time tasks
            current_time = datetime.now()
            for task_id, task in self.tasks.items():
                if (task["schedule_type"] == "once" and 
                    task["active"] and 
                    not task["last_run"]):
                    
                    try:
                        scheduled_time = datetime.fromisoformat(task["schedule_value"])
                        if current_time >= scheduled_time:
                            self.execute_task(task_id)
                    except:
                        continue
            
            time.sleep(1)  # Check every second
    
    def list_tasks(self):
        """List all scheduled tasks"""
        active_tasks = []
        inactive_tasks = []
        
        for task_id, task in self.tasks.items():
            task_info = {
                "id": task_id,
                "name": task["name"],
                "command": task["command"],
                "schedule": f"{task['schedule_type']}: {task['schedule_value']}",
                "last_run": task["last_run"],
                "run_count": task["run_count"],
                "description": task.get("description", "")
            }
            
            if task["active"]:
                active_tasks.append(task_info)
            else:
                inactive_tasks.append(task_info)
        
        return active_tasks, inactive_tasks
    
    def cancel_task(self, task_id):
        """Cancel a scheduled task"""
        if task_id in self.tasks:
            self.tasks[task_id]["active"] = False
            self.save_tasks()
            
            # Clear from schedule
            schedule.clear(task_id)
            
            return True, f"Task {self.tasks[task_id]['name']} cancelled"
        
        return False, "Task not found"
    
    def delete_task(self, task_id):
        """Delete a scheduled task"""
        if task_id in self.tasks:
            task_name = self.tasks[task_id]["name"]
            del self.tasks[task_id]
            self.save_tasks()
            
            # Clear from schedule
            schedule.clear(task_id)
            
            return True, f"Task {task_name} deleted"
        
        return False, "Task not found"
    
    def get_next_runs(self):
        """Get next scheduled runs"""
        next_runs = []
        
        for job in schedule.jobs:
            next_runs.append({
                "task": job.job_func.__name__ if hasattr(job.job_func, '__name__') else "Unknown",
                "next_run": job.next_run.isoformat() if job.next_run else "Unknown"
            })
        
        return sorted(next_runs, key=lambda x: x["next_run"])
    
    def create_reminder(self, message, when):
        """Create a simple reminder"""
        task_name = f"Reminder: {message[:30]}"
        command = f"echo 'Reminder: {message}'"
        
        return self.schedule_task(
            task_name,
            command,
            "once",
            when,
            f"Reminder: {message}"
        )
