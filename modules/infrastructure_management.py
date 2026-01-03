import json
import yaml
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import tempfile

class InfrastructureManager:
    """
    Infrastructure Management with Infrastructure as Code and resource provisioning
    """
    
    def __init__(self, aws_manager=None):
        self.aws_manager = aws_manager
        self.templates = {}
        self.deployments = {}
        self._init_templates()
    
    def _init_templates(self):
        """Initialize infrastructure templates"""
        self.templates = {
            "simple_s3": {
                "name": "Simple S3 Bucket",
                "description": "Basic S3 bucket with versioning",
                "template": {
                    "AWSTemplateFormatVersion": "2010-09-09",
                    "Description": "Simple S3 bucket with versioning",
                    "Parameters": {
                        "BucketName": {
                            "Type": "String",
                            "Description": "Name of the S3 bucket"
                        }
                    },
                    "Resources": {
                        "S3Bucket": {
                            "Type": "AWS::S3::Bucket",
                            "Properties": {
                                "BucketName": {"Ref": "BucketName"},
                                "VersioningConfiguration": {
                                    "Status": "Enabled"
                                },
                                "PublicAccessBlockConfiguration": {
                                    "BlockPublicAcls": True,
                                    "BlockPublicPolicy": True,
                                    "IgnorePublicAcls": True,
                                    "RestrictPublicBuckets": True
                                }
                            }
                        }
                    },
                    "Outputs": {
                        "BucketName": {
                            "Description": "Name of the created S3 bucket",
                            "Value": {"Ref": "S3Bucket"}
                        }
                    }
                }
            },
            "lambda_function": {
                "name": "Lambda Function",
                "description": "Basic Lambda function with IAM role",
                "template": {
                    "AWSTemplateFormatVersion": "2010-09-09",
                    "Description": "Lambda function with execution role",
                    "Parameters": {
                        "FunctionName": {
                            "Type": "String",
                            "Description": "Name of the Lambda function"
                        },
                        "Runtime": {
                            "Type": "String",
                            "Default": "python3.9",
                            "Description": "Lambda runtime"
                        }
                    },
                    "Resources": {
                        "LambdaExecutionRole": {
                            "Type": "AWS::IAM::Role",
                            "Properties": {
                                "AssumeRolePolicyDocument": {
                                    "Version": "2012-10-17",
                                    "Statement": [{
                                        "Effect": "Allow",
                                        "Principal": {"Service": "lambda.amazonaws.com"},
                                        "Action": "sts:AssumeRole"
                                    }]
                                },
                                "ManagedPolicyArns": [
                                    "arn:aws:iam::aws:policy/service-role/AWSLambdaBasicExecutionRole"
                                ]
                            }
                        },
                        "LambdaFunction": {
                            "Type": "AWS::Lambda::Function",
                            "Properties": {
                                "FunctionName": {"Ref": "FunctionName"},
                                "Runtime": {"Ref": "Runtime"},
                                "Role": {"Fn::GetAtt": ["LambdaExecutionRole", "Arn"]},
                                "Handler": "index.handler",
                                "Code": {
                                    "ZipFile": "def handler(event, context):\n    return {'statusCode': 200, 'body': 'Hello World'}"
                                }
                            }
                        }
                    },
                    "Outputs": {
                        "FunctionArn": {
                            "Description": "ARN of the Lambda function",
                            "Value": {"Fn::GetAtt": ["LambdaFunction", "Arn"]}
                        }
                    }
                }
            },
            "vpc_basic": {
                "name": "Basic VPC",
                "description": "VPC with public and private subnets",
                "template": {
                    "AWSTemplateFormatVersion": "2010-09-09",
                    "Description": "Basic VPC with public and private subnets",
                    "Parameters": {
                        "VpcCidr": {
                            "Type": "String",
                            "Default": "10.0.0.0/16",
                            "Description": "CIDR block for VPC"
                        }
                    },
                    "Resources": {
                        "VPC": {
                            "Type": "AWS::EC2::VPC",
                            "Properties": {
                                "CidrBlock": {"Ref": "VpcCidr"},
                                "EnableDnsHostnames": True,
                                "EnableDnsSupport": True
                            }
                        },
                        "PublicSubnet": {
                            "Type": "AWS::EC2::Subnet",
                            "Properties": {
                                "VpcId": {"Ref": "VPC"},
                                "CidrBlock": "10.0.1.0/24",
                                "MapPublicIpOnLaunch": True
                            }
                        },
                        "PrivateSubnet": {
                            "Type": "AWS::EC2::Subnet",
                            "Properties": {
                                "VpcId": {"Ref": "VPC"},
                                "CidrBlock": "10.0.2.0/24"
                            }
                        },
                        "InternetGateway": {
                            "Type": "AWS::EC2::InternetGateway"
                        },
                        "AttachGateway": {
                            "Type": "AWS::EC2::VPCGatewayAttachment",
                            "Properties": {
                                "VpcId": {"Ref": "VPC"},
                                "InternetGatewayId": {"Ref": "InternetGateway"}
                            }
                        }
                    },
                    "Outputs": {
                        "VpcId": {
                            "Description": "ID of the VPC",
                            "Value": {"Ref": "VPC"}
                        }
                    }
                }
            }
        }
    
    def list_templates(self) -> Dict[str, Any]:
        """List available infrastructure templates"""
        return {
            "success": True,
            "templates": {
                template_id: {
                    "name": template["name"],
                    "description": template["description"]
                }
                for template_id, template in self.templates.items()
            }
        }
    
    def get_template(self, template_id: str) -> Dict[str, Any]:
        """Get specific template"""
        if template_id not in self.templates:
            return {"success": False, "error": "Template not found"}
        
        return {
            "success": True,
            "template": self.templates[template_id]
        }
    
    def deploy_template(self, template_id: str, stack_name: str, 
                       parameters: Dict[str, str] = None, region: str = None) -> Dict[str, Any]:
        """Deploy CloudFormation template"""
        if not self.aws_manager:
            return {"success": False, "error": "AWS manager not available"}
        
        if template_id not in self.templates:
            return {"success": False, "error": "Template not found"}
        
        try:
            # Get template
            template = self.templates[template_id]["template"]
            
            # Create temporary file for template
            with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
                json.dump(template, f, indent=2)
                template_file = f.name
            
            # Prepare parameters
            cf_params = {}
            if parameters:
                param_list = []
                for key, value in parameters.items():
                    param_list.extend([f"ParameterKey={key},ParameterValue={value}"])
                if param_list:
                    cf_params["parameters"] = param_list
            
            # Deploy stack
            cf_params.update({
                "stack-name": stack_name,
                "template-body": f"file://{template_file}",
                "capabilities": ["CAPABILITY_IAM"]
            })
            
            result = self.aws_manager.execute_command(
                "cloudformation", "create-stack", cf_params, region
            )
            
            # Clean up temp file
            os.unlink(template_file)
            
            if result["success"]:
                deployment = {
                    "stack_name": stack_name,
                    "template_id": template_id,
                    "parameters": parameters or {},
                    "region": region or self.aws_manager.default_region,
                    "deployed_at": datetime.now().isoformat(),
                    "stack_id": result["data"].get("StackId")
                }
                self.deployments[stack_name] = deployment
                
                return {
                    "success": True,
                    "stack_id": result["data"].get("StackId"),
                    "message": f"Stack {stack_name} deployment initiated"
                }
            else:
                return result
        
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def get_stack_status(self, stack_name: str, region: str = None) -> Dict[str, Any]:
        """Get CloudFormation stack status"""
        if not self.aws_manager:
            return {"success": False, "error": "AWS manager not available"}
        
        result = self.aws_manager.execute_command(
            "cloudformation", "describe-stacks", 
            {"stack-name": stack_name}, region
        )
        
        if result["success"]:
            stacks = result["data"].get("Stacks", [])
            if stacks:
                stack = stacks[0]
                return {
                    "success": True,
                    "stack": {
                        "name": stack.get("StackName"),
                        "status": stack.get("StackStatus"),
                        "creation_time": stack.get("CreationTime"),
                        "description": stack.get("Description"),
                        "outputs": stack.get("Outputs", [])
                    }
                }
        
        return result
    
    def delete_stack(self, stack_name: str, region: str = None) -> Dict[str, Any]:
        """Delete CloudFormation stack"""
        if not self.aws_manager:
            return {"success": False, "error": "AWS manager not available"}
        
        result = self.aws_manager.execute_command(
            "cloudformation", "delete-stack",
            {"stack-name": stack_name}, region
        )
        
        if result["success"]:
            # Remove from deployments
            if stack_name in self.deployments:
                del self.deployments[stack_name]
            
            return {
                "success": True,
                "message": f"Stack {stack_name} deletion initiated"
            }
        
        return result
    
    def list_deployments(self) -> Dict[str, Any]:
        """List tracked deployments"""
        return {
            "success": True,
            "deployments": self.deployments
        }
    
    def generate_terraform(self, template_id: str, parameters: Dict[str, str] = None) -> Dict[str, Any]:
        """Generate Terraform configuration from template"""
        if template_id not in self.templates:
            return {"success": False, "error": "Template not found"}
        
        # Simple CloudFormation to Terraform conversion
        template = self.templates[template_id]["template"]
        
        terraform_config = {
            "terraform": {
                "required_providers": {
                    "aws": {
                        "source": "hashicorp/aws",
                        "version": "~> 5.0"
                    }
                }
            },
            "provider": {
                "aws": {
                    "region": "var.aws_region"
                }
            },
            "variable": {
                "aws_region": {
                    "description": "AWS region",
                    "type": "string",
                    "default": "us-east-1"
                }
            }
        }
        
        # Add parameter variables
        if "Parameters" in template:
            for param_name, param_def in template["Parameters"].items():
                terraform_config["variable"][param_name.lower()] = {
                    "description": param_def.get("Description", ""),
                    "type": "string"
                }
        
        # Convert resources (simplified)
        terraform_config["resource"] = {}
        
        if "Resources" in template:
            for resource_name, resource_def in template["Resources"].items():
                resource_type = resource_def["Type"]
                
                if resource_type == "AWS::S3::Bucket":
                    terraform_config["resource"]["aws_s3_bucket"] = {
                        resource_name.lower(): {
                            "bucket": f"var.{resource_def['Properties']['BucketName']['Ref'].lower()}"
                        }
                    }
                elif resource_type == "AWS::Lambda::Function":
                    terraform_config["resource"]["aws_lambda_function"] = {
                        resource_name.lower(): {
                            "function_name": f"var.{resource_def['Properties']['FunctionName']['Ref'].lower()}",
                            "runtime": f"var.{resource_def['Properties']['Runtime']['Ref'].lower()}",
                            "handler": resource_def['Properties']['Handler'],
                            "filename": "function.zip"
                        }
                    }
        
        return {
            "success": True,
            "terraform_config": terraform_config
        }

# Integration class for JARVIS
class InfrastructureIntegration:
    """Infrastructure Management integration for JARVIS"""
    
    def __init__(self, aws_manager=None):
        self.infra_manager = InfrastructureManager(aws_manager)
    
    def list_templates(self) -> str:
        """List infrastructure templates"""
        result = self.infra_manager.list_templates()
        
        if not result["success"]:
            return f"❌ {result['error']}"
        
        templates = result["templates"]
        
        if not templates:
            return "🏗️ No infrastructure templates available"
        
        response = f"🏗️ Infrastructure Templates ({len(templates)}):\n\n"
        
        for template_id, template in templates.items():
            response += f"🔧 **{template['name']}** ({template_id})\n"
            response += f"   📝 {template['description']}\n\n"
        
        return response
    
    def get_template(self, template_id: str) -> str:
        """Get template details"""
        result = self.infra_manager.get_template(template_id)
        
        if not result["success"]:
            return f"❌ {result['error']}"
        
        template = result["template"]
        cf_template = template["template"]
        
        response = f"🔧 Template: {template['name']}\n"
        response += f"📝 {template['description']}\n\n"
        
        # Show parameters
        if "Parameters" in cf_template:
            response += "📋 Parameters:\n"
            for param_name, param_def in cf_template["Parameters"].items():
                response += f"  • {param_name}: {param_def.get('Description', 'No description')}\n"
            response += "\n"
        
        # Show resources
        if "Resources" in cf_template:
            response += f"🏗️ Resources ({len(cf_template['Resources'])}):\n"
            for resource_name, resource_def in cf_template["Resources"].items():
                response += f"  • {resource_name}: {resource_def['Type']}\n"
        
        return response
    
    def deploy(self, template_id: str, stack_name: str, region: str = None, **parameters) -> str:
        """Deploy infrastructure template"""
        result = self.infra_manager.deploy_template(template_id, stack_name, parameters, region)
        
        if result["success"]:
            return f"🚀 {result['message']}\n📋 Stack ID: {result['stack_id']}"
        else:
            return f"❌ Deployment failed: {result['error']}"
    
    def stack_status(self, stack_name: str, region: str = None) -> str:
        """Get stack status"""
        result = self.infra_manager.get_stack_status(stack_name, region)
        
        if not result["success"]:
            return f"❌ {result['error']}"
        
        stack = result["stack"]
        
        response = f"📚 Stack: {stack['name']}\n"
        response += f"📊 Status: {stack['status']}\n"
        response += f"📅 Created: {str(stack['creation_time'])[:19]}\n"
        
        if stack.get("description"):
            response += f"📝 Description: {stack['description']}\n"
        
        if stack.get("outputs"):
            response += f"\n📤 Outputs ({len(stack['outputs'])}):\n"
            for output in stack["outputs"]:
                response += f"  • {output.get('OutputKey')}: {output.get('OutputValue')}\n"
        
        return response
    
    def delete_stack(self, stack_name: str, region: str = None) -> str:
        """Delete stack"""
        result = self.infra_manager.delete_stack(stack_name, region)
        
        if result["success"]:
            return f"🗑️ {result['message']}"
        else:
            return f"❌ Deletion failed: {result['error']}"
    
    def list_deployments(self) -> str:
        """List deployments"""
        result = self.infra_manager.list_deployments()
        
        deployments = result["deployments"]
        
        if not deployments:
            return "🏗️ No tracked deployments"
        
        response = f"🏗️ Tracked Deployments ({len(deployments)}):\n\n"
        
        for stack_name, deployment in deployments.items():
            response += f"📚 **{stack_name}**\n"
            response += f"   🔧 Template: {deployment['template_id']}\n"
            response += f"   🌍 Region: {deployment['region']}\n"
            response += f"   📅 Deployed: {deployment['deployed_at'][:19]}\n\n"
        
        return response
    
    def generate_terraform(self, template_id: str, **parameters) -> str:
        """Generate Terraform configuration"""
        result = self.infra_manager.generate_terraform(template_id, parameters)
        
        if not result["success"]:
            return f"❌ {result['error']}"
        
        terraform_config = result["terraform_config"]
        
        # Convert to HCL-like format (simplified)
        response = f"🔧 Terraform Configuration for {template_id}:\n\n"
        response += "```hcl\n"
        response += json.dumps(terraform_config, indent=2)
        response += "\n```"
        
        return response
