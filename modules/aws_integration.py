import subprocess
import json
import os
from typing import Dict, List, Any, Optional
from datetime import datetime

class AWSCLIManager:
    """
    AWS CLI Integration with command execution and resource management
    """
    
    def __init__(self):
        self.aws_cli_available = self._check_aws_cli()
        self.default_region = os.environ.get('AWS_DEFAULT_REGION', 'us-east-1')
        self.profile = os.environ.get('AWS_PROFILE', 'default')
    
    def _check_aws_cli(self) -> bool:
        """Check if AWS CLI is available"""
        try:
            result = subprocess.run(['aws', '--version'], capture_output=True, text=True, timeout=5)
            return result.returncode == 0
        except:
            return False
    
    def execute_command(self, service: str, operation: str, parameters: Dict[str, Any] = None, 
                       region: str = None, profile: str = None) -> Dict[str, Any]:
        """Execute AWS CLI command"""
        if not self.aws_cli_available:
            return {"success": False, "error": "AWS CLI not available"}
        
        try:
            # Build command
            cmd = ['aws', service, operation]
            
            # Add region
            if region or self.default_region:
                cmd.extend(['--region', region or self.default_region])
            
            # Add profile
            if profile or self.profile:
                cmd.extend(['--profile', profile or self.profile])
            
            # Add parameters
            if parameters:
                for key, value in parameters.items():
                    if isinstance(value, bool):
                        if value:
                            cmd.append(f'--{key}')
                    elif isinstance(value, list):
                        cmd.extend([f'--{key}'] + value)
                    else:
                        cmd.extend([f'--{key}', str(value)])
            
            # Add JSON output
            cmd.extend(['--output', 'json'])
            
            # Execute command
            result = subprocess.run(cmd, capture_output=True, text=True, timeout=30)
            
            if result.returncode == 0:
                try:
                    output = json.loads(result.stdout) if result.stdout.strip() else {}
                except json.JSONDecodeError:
                    output = {"raw_output": result.stdout}
                
                return {
                    "success": True,
                    "data": output,
                    "command": " ".join(cmd)
                }
            else:
                return {
                    "success": False,
                    "error": result.stderr.strip() or result.stdout.strip(),
                    "command": " ".join(cmd)
                }
        
        except subprocess.TimeoutExpired:
            return {"success": False, "error": "Command timed out"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def list_s3_buckets(self) -> Dict[str, Any]:
        """List S3 buckets"""
        return self.execute_command('s3api', 'list-buckets')
    
    def list_ec2_instances(self, region: str = None) -> Dict[str, Any]:
        """List EC2 instances"""
        return self.execute_command('ec2', 'describe-instances', region=region)
    
    def list_lambda_functions(self, region: str = None) -> Dict[str, Any]:
        """List Lambda functions"""
        return self.execute_command('lambda', 'list-functions', region=region)
    
    def get_caller_identity(self) -> Dict[str, Any]:
        """Get current AWS identity"""
        return self.execute_command('sts', 'get-caller-identity')
    
    def list_iam_users(self) -> Dict[str, Any]:
        """List IAM users"""
        return self.execute_command('iam', 'list-users')
    
    def describe_vpcs(self, region: str = None) -> Dict[str, Any]:
        """Describe VPCs"""
        return self.execute_command('ec2', 'describe-vpcs', region=region)
    
    def list_cloudformation_stacks(self, region: str = None) -> Dict[str, Any]:
        """List CloudFormation stacks"""
        return self.execute_command('cloudformation', 'list-stacks', region=region)
    
    def get_account_summary(self) -> Dict[str, Any]:
        """Get account summary"""
        return self.execute_command('iam', 'get-account-summary')
    
    def list_rds_instances(self, region: str = None) -> Dict[str, Any]:
        """List RDS instances"""
        return self.execute_command('rds', 'describe-db-instances', region=region)
    
    def get_cost_and_usage(self, start_date: str, end_date: str) -> Dict[str, Any]:
        """Get cost and usage data"""
        params = {
            'time-period': f'Start={start_date},End={end_date}',
            'granularity': 'MONTHLY',
            'metrics': ['BlendedCost']
        }
        return self.execute_command('ce', 'get-cost-and-usage', params)

# Integration class for JARVIS
class AWSIntegration:
    """AWS CLI integration for JARVIS"""
    
    def __init__(self):
        self.aws_manager = AWSCLIManager()
    
    def status(self) -> str:
        """Get AWS CLI status"""
        if not self.aws_manager.aws_cli_available:
            return "❌ AWS CLI not available. Install with: pip install awscli"
        
        # Get identity
        identity = self.aws_manager.get_caller_identity()
        
        if identity["success"]:
            data = identity["data"]
            response = "☁️ AWS CLI Status: Connected\n\n"
            response += f"👤 User: {data.get('Arn', 'Unknown')}\n"
            response += f"🆔 Account: {data.get('Account', 'Unknown')}\n"
            response += f"🌍 Region: {self.aws_manager.default_region}\n"
            response += f"👤 Profile: {self.aws_manager.profile}"
            return response
        else:
            return f"❌ AWS CLI available but not configured: {identity['error']}"
    
    def s3_buckets(self) -> str:
        """List S3 buckets"""
        result = self.aws_manager.list_s3_buckets()
        
        if not result["success"]:
            return f"❌ Failed to list S3 buckets: {result['error']}"
        
        buckets = result["data"].get("Buckets", [])
        
        if not buckets:
            return "🪣 No S3 buckets found"
        
        response = f"🪣 S3 Buckets ({len(buckets)}):\n\n"
        
        for bucket in buckets:
            name = bucket.get("Name", "Unknown")
            created = bucket.get("CreationDate", "Unknown")[:10]
            response += f"• **{name}**\n"
            response += f"  📅 Created: {created}\n\n"
        
        return response
    
    def ec2_instances(self, region: str = None) -> str:
        """List EC2 instances"""
        result = self.aws_manager.list_ec2_instances(region)
        
        if not result["success"]:
            return f"❌ Failed to list EC2 instances: {result['error']}"
        
        reservations = result["data"].get("Reservations", [])
        instances = []
        
        for reservation in reservations:
            instances.extend(reservation.get("Instances", []))
        
        if not instances:
            return f"🖥️ No EC2 instances found in {region or self.aws_manager.default_region}"
        
        response = f"🖥️ EC2 Instances ({len(instances)}):\n\n"
        
        for instance in instances:
            instance_id = instance.get("InstanceId", "Unknown")
            instance_type = instance.get("InstanceType", "Unknown")
            state = instance.get("State", {}).get("Name", "Unknown")
            
            # Get name tag
            name = "No Name"
            for tag in instance.get("Tags", []):
                if tag.get("Key") == "Name":
                    name = tag.get("Value", "No Name")
                    break
            
            state_icon = {"running": "🟢", "stopped": "🔴", "pending": "🟡", "stopping": "🟠"}.get(state, "⚪")
            
            response += f"{state_icon} **{name}** ({instance_id})\n"
            response += f"  🔧 Type: {instance_type} | 📊 State: {state}\n\n"
        
        return response
    
    def lambda_functions(self, region: str = None) -> str:
        """List Lambda functions"""
        result = self.aws_manager.list_lambda_functions(region)
        
        if not result["success"]:
            return f"❌ Failed to list Lambda functions: {result['error']}"
        
        functions = result["data"].get("Functions", [])
        
        if not functions:
            return f"⚡ No Lambda functions found in {region or self.aws_manager.default_region}"
        
        response = f"⚡ Lambda Functions ({len(functions)}):\n\n"
        
        for func in functions:
            name = func.get("FunctionName", "Unknown")
            runtime = func.get("Runtime", "Unknown")
            size = func.get("CodeSize", 0)
            modified = func.get("LastModified", "Unknown")[:10]
            
            response += f"⚡ **{name}**\n"
            response += f"  🔧 Runtime: {runtime} | 📦 Size: {size:,} bytes\n"
            response += f"  📅 Modified: {modified}\n\n"
        
        return response
    
    def iam_users(self) -> str:
        """List IAM users"""
        result = self.aws_manager.list_iam_users()
        
        if not result["success"]:
            return f"❌ Failed to list IAM users: {result['error']}"
        
        users = result["data"].get("Users", [])
        
        if not users:
            return "👤 No IAM users found"
        
        response = f"👤 IAM Users ({len(users)}):\n\n"
        
        for user in users:
            name = user.get("UserName", "Unknown")
            created = user.get("CreateDate", "Unknown")[:10]
            path = user.get("Path", "/")
            
            response += f"👤 **{name}**\n"
            response += f"  📁 Path: {path} | 📅 Created: {created}\n\n"
        
        return response
    
    def vpcs(self, region: str = None) -> str:
        """List VPCs"""
        result = self.aws_manager.describe_vpcs(region)
        
        if not result["success"]:
            return f"❌ Failed to list VPCs: {result['error']}"
        
        vpcs = result["data"].get("Vpcs", [])
        
        if not vpcs:
            return f"🌐 No VPCs found in {region or self.aws_manager.default_region}"
        
        response = f"🌐 VPCs ({len(vpcs)}):\n\n"
        
        for vpc in vpcs:
            vpc_id = vpc.get("VpcId", "Unknown")
            cidr = vpc.get("CidrBlock", "Unknown")
            state = vpc.get("State", "Unknown")
            is_default = vpc.get("IsDefault", False)
            
            # Get name tag
            name = "No Name"
            for tag in vpc.get("Tags", []):
                if tag.get("Key") == "Name":
                    name = tag.get("Value", "No Name")
                    break
            
            default_icon = "⭐" if is_default else "🌐"
            state_icon = {"available": "🟢", "pending": "🟡"}.get(state, "⚪")
            
            response += f"{default_icon} {state_icon} **{name}** ({vpc_id})\n"
            response += f"  📡 CIDR: {cidr} | 📊 State: {state}\n\n"
        
        return response
    
    def cloudformation_stacks(self, region: str = None) -> str:
        """List CloudFormation stacks"""
        result = self.aws_manager.list_cloudformation_stacks(region)
        
        if not result["success"]:
            return f"❌ Failed to list CloudFormation stacks: {result['error']}"
        
        stacks = result["data"].get("StackSummaries", [])
        
        if not stacks:
            return f"📚 No CloudFormation stacks found in {region or self.aws_manager.default_region}"
        
        response = f"📚 CloudFormation Stacks ({len(stacks)}):\n\n"
        
        for stack in stacks:
            name = stack.get("StackName", "Unknown")
            status = stack.get("StackStatus", "Unknown")
            created = stack.get("CreationTime", "Unknown")
            if isinstance(created, str):
                created = created[:10]
            
            status_icon = {
                "CREATE_COMPLETE": "✅",
                "UPDATE_COMPLETE": "🔄",
                "DELETE_COMPLETE": "🗑️",
                "ROLLBACK_COMPLETE": "↩️"
            }.get(status, "⚪")
            
            response += f"{status_icon} **{name}**\n"
            response += f"  📊 Status: {status} | 📅 Created: {created}\n\n"
        
        return response
    
    def rds_instances(self, region: str = None) -> str:
        """List RDS instances"""
        result = self.aws_manager.list_rds_instances(region)
        
        if not result["success"]:
            return f"❌ Failed to list RDS instances: {result['error']}"
        
        instances = result["data"].get("DBInstances", [])
        
        if not instances:
            return f"🗄️ No RDS instances found in {region or self.aws_manager.default_region}"
        
        response = f"🗄️ RDS Instances ({len(instances)}):\n\n"
        
        for instance in instances:
            name = instance.get("DBInstanceIdentifier", "Unknown")
            engine = instance.get("Engine", "Unknown")
            status = instance.get("DBInstanceStatus", "Unknown")
            instance_class = instance.get("DBInstanceClass", "Unknown")
            
            status_icon = {"available": "🟢", "stopped": "🔴", "starting": "🟡"}.get(status, "⚪")
            
            response += f"{status_icon} **{name}**\n"
            response += f"  🔧 Engine: {engine} | 💻 Class: {instance_class}\n"
            response += f"  📊 Status: {status}\n\n"
        
        return response
    
    def execute_custom(self, service: str, operation: str, **params) -> str:
        """Execute custom AWS CLI command"""
        result = self.aws_manager.execute_command(service, operation, params)
        
        if not result["success"]:
            return f"❌ AWS command failed: {result['error']}"
        
        response = f"☁️ AWS {service} {operation}\n\n"
        
        if isinstance(result["data"], dict) and result["data"]:
            # Format JSON output
            formatted = json.dumps(result["data"], indent=2)
            if len(formatted) > 1000:
                response += formatted[:1000] + "\n... (truncated)"
            else:
                response += formatted
        else:
            response += str(result["data"])
        
        return response
