import time
import psutil
from datetime import datetime, timedelta
from collections import defaultdict

class PerformanceMonitor:
    def __init__(self):
        self.metrics = {
            "response_times": [],
            "command_success_rates": defaultdict(list),
            "system_resources": [],
            "error_counts": defaultdict(int),
            "feature_usage": defaultdict(int)
        }
        self.start_time = time.time()
        
    def start_operation(self, operation_name):
        """Start timing an operation"""
        return {
            "operation": operation_name,
            "start_time": time.time(),
            "start_memory": psutil.Process().memory_info().rss
        }
    
    def end_operation(self, operation_data, success=True, error=None):
        """End timing an operation and record metrics"""
        end_time = time.time()
        end_memory = psutil.Process().memory_info().rss
        
        response_time = end_time - operation_data["start_time"]
        memory_delta = end_memory - operation_data["start_memory"]
        
        # Record response time
        self.metrics["response_times"].append({
            "operation": operation_data["operation"],
            "response_time": response_time,
            "timestamp": datetime.now().isoformat(),
            "success": success,
            "memory_delta": memory_delta
        })
        
        # Record success rate
        self.metrics["command_success_rates"][operation_data["operation"]].append(success)
        
        # Record feature usage
        self.metrics["feature_usage"][operation_data["operation"]] += 1
        
        # Record errors
        if not success and error:
            self.metrics["error_counts"][error] += 1
        
        # Keep only recent metrics (last 100 operations)
        if len(self.metrics["response_times"]) > 100:
            self.metrics["response_times"] = self.metrics["response_times"][-100:]
    
    def record_system_metrics(self):
        """Record current system metrics"""
        try:
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            
            self.metrics["system_resources"].append({
                "timestamp": datetime.now().isoformat(),
                "cpu_percent": cpu_percent,
                "memory_percent": memory.percent,
                "memory_used": memory.used,
                "memory_available": memory.available
            })
            
            # Keep only recent metrics (last 50 readings)
            if len(self.metrics["system_resources"]) > 50:
                self.metrics["system_resources"] = self.metrics["system_resources"][-50:]
                
        except Exception as e:
            print(f"Error recording system metrics: {e}")
    
    def get_performance_summary(self):
        """Get performance summary"""
        if not self.metrics["response_times"]:
            return "No performance data available yet."
        
        # Calculate average response time
        response_times = [m["response_time"] for m in self.metrics["response_times"]]
        avg_response_time = sum(response_times) / len(response_times)
        
        # Calculate overall success rate
        total_operations = len(self.metrics["response_times"])
        successful_operations = len([m for m in self.metrics["response_times"] if m["success"]])
        success_rate = (successful_operations / total_operations) * 100 if total_operations > 0 else 0
        
        # Get most used features
        top_features = sorted(self.metrics["feature_usage"].items(), 
                            key=lambda x: x[1], reverse=True)[:5]
        
        # Get recent system performance
        recent_system = self.metrics["system_resources"][-10:] if self.metrics["system_resources"] else []
        avg_cpu = sum(m["cpu_percent"] for m in recent_system) / len(recent_system) if recent_system else 0
        avg_memory = sum(m["memory_percent"] for m in recent_system) / len(recent_system) if recent_system else 0
        
        summary = f"""
🔧 JARVIS Performance Summary
============================
⏱️  Average Response Time: {avg_response_time:.2f}s
✅ Overall Success Rate: {success_rate:.1f}%
📊 Total Operations: {total_operations}
⚡ Uptime: {self.get_uptime()}

🎯 Most Used Features:
"""
        
        for feature, count in top_features:
            summary += f"   • {feature}: {count} times\n"
        
        summary += f"""
💻 System Performance:
   • Average CPU: {avg_cpu:.1f}%
   • Average Memory: {avg_memory:.1f}%
"""
        
        if self.metrics["error_counts"]:
            summary += "\n❌ Recent Errors:\n"
            for error, count in list(self.metrics["error_counts"].items())[:3]:
                summary += f"   • {error}: {count} times\n"
        
        return summary
    
    def get_uptime(self):
        """Get JARVIS uptime"""
        uptime_seconds = time.time() - self.start_time
        uptime_minutes = uptime_seconds / 60
        
        if uptime_minutes < 60:
            return f"{uptime_minutes:.1f} minutes"
        else:
            uptime_hours = uptime_minutes / 60
            return f"{uptime_hours:.1f} hours"
    
    def get_slow_operations(self, threshold=2.0):
        """Get operations that are slower than threshold"""
        slow_ops = []
        for metric in self.metrics["response_times"]:
            if metric["response_time"] > threshold:
                slow_ops.append({
                    "operation": metric["operation"],
                    "response_time": metric["response_time"],
                    "timestamp": metric["timestamp"]
                })
        
        return sorted(slow_ops, key=lambda x: x["response_time"], reverse=True)
    
    def get_feature_analytics(self):
        """Get detailed feature usage analytics"""
        analytics = {}
        
        for operation, success_list in self.metrics["command_success_rates"].items():
            total = len(success_list)
            successful = sum(success_list)
            success_rate = (successful / total) * 100 if total > 0 else 0
            
            # Get average response time for this operation
            op_times = [m["response_time"] for m in self.metrics["response_times"] 
                       if m["operation"] == operation]
            avg_time = sum(op_times) / len(op_times) if op_times else 0
            
            analytics[operation] = {
                "usage_count": self.metrics["feature_usage"][operation],
                "success_rate": success_rate,
                "average_response_time": avg_time,
                "total_attempts": total
            }
        
        return analytics
    
    def optimize_suggestions(self):
        """Get optimization suggestions based on performance data"""
        suggestions = []
        
        # Check for slow operations
        slow_ops = self.get_slow_operations(1.0)
        if slow_ops:
            suggestions.append(f"Consider optimizing these slow operations: {', '.join([op['operation'] for op in slow_ops[:3]])}")
        
        # Check for high error rates
        for operation, success_list in self.metrics["command_success_rates"].items():
            if len(success_list) > 5:  # Only check operations with enough data
                success_rate = (sum(success_list) / len(success_list)) * 100
                if success_rate < 80:
                    suggestions.append(f"Operation '{operation}' has low success rate ({success_rate:.1f}%) - needs improvement")
        
        # Check system resource usage
        if self.metrics["system_resources"]:
            recent_cpu = [m["cpu_percent"] for m in self.metrics["system_resources"][-10:]]
            recent_memory = [m["memory_percent"] for m in self.metrics["system_resources"][-10:]]
            
            avg_cpu = sum(recent_cpu) / len(recent_cpu)
            avg_memory = sum(recent_memory) / len(recent_memory)
            
            if avg_cpu > 80:
                suggestions.append("High CPU usage detected - consider reducing background processes")
            
            if avg_memory > 85:
                suggestions.append("High memory usage detected - consider restarting JARVIS periodically")
        
        return suggestions if suggestions else ["JARVIS is performing optimally!"]
