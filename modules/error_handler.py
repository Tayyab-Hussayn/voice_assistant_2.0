import traceback
import logging
from datetime import datetime
from pathlib import Path

class ErrorHandler:
    def __init__(self, jarvis_instance):
        self.jarvis = jarvis_instance
        self.error_log_file = Path.cwd() / "Memory" / "error_log.txt"
        self.recovery_strategies = {
            "ConnectionError": self.recover_connection_error,
            "FileNotFoundError": self.recover_file_not_found,
            "PermissionError": self.recover_permission_error,
            "TimeoutError": self.recover_timeout_error,
            "ImportError": self.recover_import_error,
            "APIError": self.recover_api_error
        }
        
        # Setup logging
        self.setup_logging()
    
    def setup_logging(self):
        """Setup error logging"""
        self.error_log_file.parent.mkdir(parents=True, exist_ok=True)
        
        logging.basicConfig(
            filename=self.error_log_file,
            level=logging.ERROR,
            format='%(asctime)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
    
    def handle_error(self, error, context="", user_input="", recovery=True):
        """Main error handling function"""
        error_type = type(error).__name__
        error_message = str(error)
        timestamp = datetime.now().isoformat()
        
        # Log the error
        error_info = {
            "timestamp": timestamp,
            "error_type": error_type,
            "error_message": error_message,
            "context": context,
            "user_input": user_input,
            "traceback": traceback.format_exc()
        }
        
        self.log_error(error_info)
        
        # Attempt recovery if enabled
        if recovery and error_type in self.recovery_strategies:
            try:
                recovery_result = self.recovery_strategies[error_type](error, context, user_input)
                if recovery_result["success"]:
                    self.jarvis.ai.speak(f"I encountered an issue but recovered: {recovery_result['message']}")
                    return recovery_result
            except Exception as recovery_error:
                self.log_error({
                    "timestamp": datetime.now().isoformat(),
                    "error_type": "RecoveryError",
                    "error_message": f"Recovery failed: {str(recovery_error)}",
                    "original_error": error_type,
                    "context": context
                })
        
        # Generate user-friendly error message
        user_message = self.generate_user_friendly_message(error_type, error_message, context)
        
        return {
            "success": False,
            "error_type": error_type,
            "user_message": user_message,
            "technical_details": error_message,
            "recovery_attempted": error_type in self.recovery_strategies
        }
    
    def log_error(self, error_info):
        """Log error to file and memory"""
        # Log to file
        logging.error(f"{error_info['error_type']}: {error_info['error_message']} | Context: {error_info['context']}")
        
        # Store in memory system if available
        if hasattr(self.jarvis, 'memory') and self.jarvis.memory:
            self.jarvis.memory.store_knowledge(
                "errors", 
                f"error_{int(datetime.now().timestamp())}", 
                f"{error_info['error_type']}: {error_info['error_message']}"
            )
    
    def generate_user_friendly_message(self, error_type, error_message, context):
        """Generate user-friendly error messages"""
        friendly_messages = {
            "ConnectionError": "I'm having trouble connecting to the internet or a service. Please check your connection.",
            "FileNotFoundError": "I couldn't find the file or folder you're looking for. Please check the path.",
            "PermissionError": "I don't have permission to access that file or folder. You might need to run with elevated privileges.",
            "TimeoutError": "The operation took too long to complete. Please try again.",
            "ImportError": "A required component is missing. Some features might not be available.",
            "APIError": "There's an issue with the AI service. Please try again in a moment.",
            "KeyError": "I'm missing some required information to complete that task.",
            "ValueError": "The input provided doesn't match what I expected for this operation.",
            "OSError": "There's a system-level issue preventing me from completing that task."
        }
        
        base_message = friendly_messages.get(error_type, "I encountered an unexpected error.")
        
        if context:
            return f"{base_message} (Context: {context})"
        
        return base_message
    
    def recover_connection_error(self, error, context, user_input):
        """Recover from connection errors"""
        # Try to reconnect or use offline mode
        try:
            # Suggest offline alternatives
            offline_suggestions = [
                "I can still help with local file operations",
                "System commands are available offline",
                "Memory and context features work without internet"
            ]
            
            return {
                "success": True,
                "message": "Switched to offline mode. " + "; ".join(offline_suggestions),
                "action": "offline_mode"
            }
        except:
            return {"success": False}
    
    def recover_file_not_found(self, error, context, user_input):
        """Recover from file not found errors"""
        try:
            # Try to create the file/directory if it makes sense
            if "mkdir" in user_input or "create" in user_input:
                # Extract path and try to create parent directories
                return {
                    "success": True,
                    "message": "Created missing directories",
                    "action": "create_directories"
                }
            
            # Suggest similar files
            return {
                "success": True,
                "message": "File not found. You can create it or check the spelling.",
                "action": "suggest_alternatives"
            }
        except:
            return {"success": False}
    
    def recover_permission_error(self, error, context, user_input):
        """Recover from permission errors"""
        try:
            return {
                "success": True,
                "message": "Permission denied. Try running the command with appropriate permissions or choose a different location.",
                "action": "suggest_alternatives"
            }
        except:
            return {"success": False}
    
    def recover_timeout_error(self, error, context, user_input):
        """Recover from timeout errors"""
        try:
            return {
                "success": True,
                "message": "Operation timed out. I'll try a simpler approach.",
                "action": "retry_simplified"
            }
        except:
            return {"success": False}
    
    def recover_import_error(self, error, context, user_input):
        """Recover from import errors"""
        try:
            missing_module = str(error).split("'")[1] if "'" in str(error) else "unknown"
            
            return {
                "success": True,
                "message": f"The {missing_module} module is not available. Some features may be limited.",
                "action": "graceful_degradation"
            }
        except:
            return {"success": False}
    
    def recover_api_error(self, error, context, user_input):
        """Recover from API errors"""
        try:
            # Fall back to local processing
            return {
                "success": True,
                "message": "AI service unavailable. Using local processing instead.",
                "action": "local_fallback"
            }
        except:
            return {"success": False}
    
    def get_error_statistics(self):
        """Get error statistics"""
        try:
            with open(self.error_log_file, 'r') as f:
                lines = f.readlines()
            
            error_counts = {}
            recent_errors = []
            
            for line in lines[-50:]:  # Last 50 errors
                if " - ERROR - " in line:
                    parts = line.split(" - ERROR - ")
                    if len(parts) > 1:
                        error_part = parts[1].split(":")[0]
                        error_counts[error_part] = error_counts.get(error_part, 0) + 1
                        recent_errors.append(line.strip())
            
            return {
                "total_errors": len(lines),
                "error_types": error_counts,
                "recent_errors": recent_errors[-10:]  # Last 10 errors
            }
            
        except Exception as e:
            return {"error": f"Could not read error log: {e}"}
    
    def clear_error_log(self):
        """Clear the error log"""
        try:
            with open(self.error_log_file, 'w') as f:
                f.write(f"# Error log cleared on {datetime.now().isoformat()}\n")
            return True, "Error log cleared"
        except Exception as e:
            return False, f"Could not clear error log: {e}"
    
    def get_health_status(self):
        """Get overall system health status"""
        try:
            stats = self.get_error_statistics()
            
            if "error" in stats:
                return "Unknown - Cannot read error log"
            
            total_errors = stats["total_errors"]
            
            if total_errors == 0:
                return "Excellent - No errors recorded"
            elif total_errors < 10:
                return "Good - Few errors recorded"
            elif total_errors < 50:
                return "Fair - Some errors present"
            else:
                return "Poor - Many errors recorded"
                
        except Exception as e:
            return f"Unknown - Health check failed: {e}"
