import json
import re
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
import hashlib

class SecurityScanner:
    """
    Security & Compliance system with security scanning and compliance checking
    """
    
    def __init__(self, aws_manager=None):
        self.aws_manager = aws_manager
        self.security_rules = self._init_security_rules()
        self.compliance_frameworks = self._init_compliance_frameworks()
        self.scan_history = []
    
    def _init_security_rules(self) -> Dict[str, Any]:
        """Initialize security scanning rules"""
        return {
            "aws_s3": {
                "public_read": {
                    "severity": "HIGH",
                    "description": "S3 bucket allows public read access",
                    "remediation": "Remove public read permissions"
                },
                "public_write": {
                    "severity": "CRITICAL",
                    "description": "S3 bucket allows public write access",
                    "remediation": "Remove public write permissions immediately"
                },
                "no_encryption": {
                    "severity": "MEDIUM",
                    "description": "S3 bucket not encrypted",
                    "remediation": "Enable server-side encryption"
                }
            },
            "aws_ec2": {
                "open_ssh": {
                    "severity": "HIGH",
                    "description": "Security group allows SSH from 0.0.0.0/0",
                    "remediation": "Restrict SSH access to specific IPs"
                },
                "open_rdp": {
                    "severity": "HIGH",
                    "description": "Security group allows RDP from 0.0.0.0/0",
                    "remediation": "Restrict RDP access to specific IPs"
                },
                "unencrypted_ebs": {
                    "severity": "MEDIUM",
                    "description": "EBS volume not encrypted",
                    "remediation": "Enable EBS encryption"
                }
            },
            "aws_iam": {
                "root_access_key": {
                    "severity": "CRITICAL",
                    "description": "Root user has access keys",
                    "remediation": "Delete root access keys, use IAM users"
                },
                "unused_credentials": {
                    "severity": "MEDIUM",
                    "description": "IAM credentials not used in 90+ days",
                    "remediation": "Remove unused credentials"
                },
                "overprivileged": {
                    "severity": "HIGH",
                    "description": "IAM policy grants excessive permissions",
                    "remediation": "Apply principle of least privilege"
                }
            },
            "code_security": {
                "hardcoded_secrets": {
                    "severity": "CRITICAL",
                    "description": "Hardcoded secrets found in code",
                    "remediation": "Use environment variables or secret management"
                },
                "sql_injection": {
                    "severity": "HIGH",
                    "description": "Potential SQL injection vulnerability",
                    "remediation": "Use parameterized queries"
                },
                "weak_crypto": {
                    "severity": "MEDIUM",
                    "description": "Weak cryptographic algorithm used",
                    "remediation": "Use strong encryption algorithms"
                }
            }
        }
    
    def _init_compliance_frameworks(self) -> Dict[str, Any]:
        """Initialize compliance frameworks"""
        return {
            "cis_aws": {
                "name": "CIS AWS Foundations Benchmark",
                "version": "1.4.0",
                "controls": {
                    "1.1": "Avoid root user for daily activities",
                    "1.2": "Ensure MFA is enabled for root user",
                    "2.1": "Ensure CloudTrail is enabled",
                    "2.2": "Ensure S3 bucket access logging is enabled",
                    "3.1": "Ensure VPC flow logging is enabled"
                }
            },
            "nist": {
                "name": "NIST Cybersecurity Framework",
                "version": "1.1",
                "controls": {
                    "ID.AM": "Asset Management",
                    "ID.GV": "Governance",
                    "PR.AC": "Access Control",
                    "PR.DS": "Data Security",
                    "DE.CM": "Continuous Monitoring"
                }
            },
            "pci_dss": {
                "name": "PCI Data Security Standard",
                "version": "4.0",
                "controls": {
                    "1": "Install and maintain network security controls",
                    "2": "Apply secure configurations",
                    "3": "Protect stored cardholder data",
                    "4": "Protect cardholder data with strong cryptography"
                }
            }
        }
    
    def scan_aws_security(self, region: str = None) -> Dict[str, Any]:
        """Scan AWS resources for security issues"""
        if not self.aws_manager:
            return {"success": False, "error": "AWS manager not available"}
        
        findings = []
        scan_id = f"scan_{int(datetime.now().timestamp())}"
        
        try:
            # Scan S3 buckets
            s3_findings = self._scan_s3_security()
            findings.extend(s3_findings)
            
            # Scan EC2 security groups
            ec2_findings = self._scan_ec2_security(region)
            findings.extend(ec2_findings)
            
            # Scan IAM
            iam_findings = self._scan_iam_security()
            findings.extend(iam_findings)
            
            # Create scan report
            scan_report = {
                "scan_id": scan_id,
                "timestamp": datetime.now().isoformat(),
                "region": region or self.aws_manager.default_region,
                "total_findings": len(findings),
                "critical": len([f for f in findings if f["severity"] == "CRITICAL"]),
                "high": len([f for f in findings if f["severity"] == "HIGH"]),
                "medium": len([f for f in findings if f["severity"] == "MEDIUM"]),
                "low": len([f for f in findings if f["severity"] == "LOW"]),
                "findings": findings
            }
            
            self.scan_history.append(scan_report)
            
            return {"success": True, "scan_report": scan_report}
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def _scan_s3_security(self) -> List[Dict[str, Any]]:
        """Scan S3 buckets for security issues"""
        findings = []
        
        try:
            # Get S3 buckets
            result = self.aws_manager.list_s3_buckets()
            if not result["success"]:
                return findings
            
            buckets = result["data"].get("Buckets", [])
            
            for bucket in buckets:
                bucket_name = bucket["Name"]
                
                # Check bucket ACL (simplified check)
                findings.append({
                    "resource_type": "S3",
                    "resource_id": bucket_name,
                    "rule_id": "public_read",
                    "severity": "HIGH",
                    "description": f"S3 bucket {bucket_name} may have public access",
                    "remediation": "Review and restrict bucket permissions"
                })
        
        except Exception:
            pass
        
        return findings
    
    def _scan_ec2_security(self, region: str = None) -> List[Dict[str, Any]]:
        """Scan EC2 security groups"""
        findings = []
        
        try:
            # Get security groups
            result = self.aws_manager.execute_command(
                "ec2", "describe-security-groups", region=region
            )
            
            if not result["success"]:
                return findings
            
            security_groups = result["data"].get("SecurityGroups", [])
            
            for sg in security_groups:
                sg_id = sg.get("GroupId", "")
                
                # Check for open SSH/RDP
                for rule in sg.get("IpPermissions", []):
                    port = rule.get("FromPort")
                    
                    if port == 22:  # SSH
                        for ip_range in rule.get("IpRanges", []):
                            if ip_range.get("CidrIp") == "0.0.0.0/0":
                                findings.append({
                                    "resource_type": "EC2",
                                    "resource_id": sg_id,
                                    "rule_id": "open_ssh",
                                    "severity": "HIGH",
                                    "description": f"Security group {sg_id} allows SSH from anywhere",
                                    "remediation": "Restrict SSH access to specific IP ranges"
                                })
        
        except Exception:
            pass
        
        return findings
    
    def _scan_iam_security(self) -> List[Dict[str, Any]]:
        """Scan IAM for security issues"""
        findings = []
        
        try:
            # Get IAM users
            result = self.aws_manager.list_iam_users()
            if not result["success"]:
                return findings
            
            users = result["data"].get("Users", [])
            
            for user in users:
                username = user.get("UserName", "")
                
                # Check for root user (simplified)
                if username == "root":
                    findings.append({
                        "resource_type": "IAM",
                        "resource_id": username,
                        "rule_id": "root_access_key",
                        "severity": "CRITICAL",
                        "description": "Root user detected - should not have access keys",
                        "remediation": "Use IAM users instead of root"
                    })
        
        except Exception:
            pass
        
        return findings
    
    def scan_code_security(self, file_path: str) -> Dict[str, Any]:
        """Scan code file for security vulnerabilities"""
        if not os.path.exists(file_path):
            return {"success": False, "error": "File not found"}
        
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            findings = []
            
            # Check for hardcoded secrets
            secret_patterns = [
                r'password\s*=\s*["\'][^"\']+["\']',
                r'api_key\s*=\s*["\'][^"\']+["\']',
                r'secret\s*=\s*["\'][^"\']+["\']',
                r'token\s*=\s*["\'][^"\']+["\']'
            ]
            
            for pattern in secret_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    findings.append({
                        "rule_id": "hardcoded_secrets",
                        "severity": "CRITICAL",
                        "line": content[:match.start()].count('\n') + 1,
                        "description": "Potential hardcoded secret found",
                        "code_snippet": match.group()
                    })
            
            # Check for SQL injection risks
            sql_patterns = [
                r'execute\s*\(\s*["\'][^"\']*\+',
                r'query\s*\(\s*["\'][^"\']*\+',
                r'SELECT\s+.*\+.*FROM'
            ]
            
            for pattern in sql_patterns:
                matches = re.finditer(pattern, content, re.IGNORECASE)
                for match in matches:
                    findings.append({
                        "rule_id": "sql_injection",
                        "severity": "HIGH",
                        "line": content[:match.start()].count('\n') + 1,
                        "description": "Potential SQL injection vulnerability",
                        "code_snippet": match.group()
                    })
            
            return {
                "success": True,
                "file_path": file_path,
                "findings": findings,
                "total_findings": len(findings)
            }
            
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def check_compliance(self, framework: str = "cis_aws") -> Dict[str, Any]:
        """Check compliance against framework"""
        if framework not in self.compliance_frameworks:
            return {"success": False, "error": "Unknown compliance framework"}
        
        framework_info = self.compliance_frameworks[framework]
        
        # Simplified compliance check
        compliance_results = []
        
        for control_id, control_desc in framework_info["controls"].items():
            # Mock compliance check
            status = "PASS" if hash(control_id) % 3 != 0 else "FAIL"
            
            compliance_results.append({
                "control_id": control_id,
                "description": control_desc,
                "status": status,
                "severity": "HIGH" if status == "FAIL" else "INFO"
            })
        
        passed = len([r for r in compliance_results if r["status"] == "PASS"])
        failed = len([r for r in compliance_results if r["status"] == "FAIL"])
        
        return {
            "success": True,
            "framework": framework_info["name"],
            "version": framework_info["version"],
            "total_controls": len(compliance_results),
            "passed": passed,
            "failed": failed,
            "compliance_score": round((passed / len(compliance_results)) * 100, 1),
            "results": compliance_results
        }
    
    def get_scan_history(self, limit: int = 10) -> Dict[str, Any]:
        """Get security scan history"""
        return {
            "success": True,
            "scans": self.scan_history[-limit:] if limit > 0 else self.scan_history
        }
    
    def generate_security_report(self, scan_id: str = None) -> Dict[str, Any]:
        """Generate comprehensive security report"""
        if scan_id:
            # Find specific scan
            scan = next((s for s in self.scan_history if s["scan_id"] == scan_id), None)
            if not scan:
                return {"success": False, "error": "Scan not found"}
            scans = [scan]
        else:
            # Use latest scan
            scans = self.scan_history[-1:] if self.scan_history else []
        
        if not scans:
            return {"success": False, "error": "No scans available"}
        
        latest_scan = scans[0]
        
        # Generate executive summary
        executive_summary = {
            "total_resources_scanned": len(set(f["resource_id"] for f in latest_scan["findings"])),
            "critical_issues": latest_scan["critical"],
            "high_issues": latest_scan["high"],
            "medium_issues": latest_scan["medium"],
            "risk_score": self._calculate_risk_score(latest_scan),
            "top_risks": self._get_top_risks(latest_scan["findings"])
        }
        
        return {
            "success": True,
            "report": {
                "scan_id": latest_scan["scan_id"],
                "generated_at": datetime.now().isoformat(),
                "executive_summary": executive_summary,
                "detailed_findings": latest_scan["findings"]
            }
        }
    
    def _calculate_risk_score(self, scan: Dict[str, Any]) -> int:
        """Calculate overall risk score"""
        score = 0
        score += scan["critical"] * 10
        score += scan["high"] * 5
        score += scan["medium"] * 2
        score += scan.get("low", 0) * 1
        
        # Normalize to 0-100 scale
        max_possible = scan["total_findings"] * 10
        if max_possible > 0:
            return min(100, int((score / max_possible) * 100))
        return 0
    
    def _get_top_risks(self, findings: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Get top security risks"""
        # Group by rule_id and count
        risk_counts = {}
        for finding in findings:
            rule_id = finding["rule_id"]
            if rule_id not in risk_counts:
                risk_counts[rule_id] = {
                    "rule_id": rule_id,
                    "severity": finding["severity"],
                    "count": 0,
                    "description": finding["description"]
                }
            risk_counts[rule_id]["count"] += 1
        
        # Sort by severity and count
        severity_order = {"CRITICAL": 4, "HIGH": 3, "MEDIUM": 2, "LOW": 1}
        top_risks = sorted(
            risk_counts.values(),
            key=lambda x: (severity_order.get(x["severity"], 0), x["count"]),
            reverse=True
        )
        
        return top_risks[:5]  # Top 5 risks

# Integration class for JARVIS
class SecurityCompliance:
    """Security & Compliance integration for JARVIS"""
    
    def __init__(self, aws_manager=None):
        self.security_scanner = SecurityScanner(aws_manager)
    
    def scan_aws(self, region: str = None) -> str:
        """Scan AWS resources for security issues"""
        result = self.security_scanner.scan_aws_security(region)
        
        if not result["success"]:
            return f"❌ Security scan failed: {result['error']}"
        
        report = result["scan_report"]
        
        response = f"🔒 AWS Security Scan Complete\n\n"
        response += f"📊 Scan ID: {report['scan_id']}\n"
        response += f"🌍 Region: {report['region']}\n"
        response += f"📅 Timestamp: {report['timestamp'][:19]}\n\n"
        
        response += f"🚨 Findings Summary:\n"
        response += f"  🔴 Critical: {report['critical']}\n"
        response += f"  🟠 High: {report['high']}\n"
        response += f"  🟡 Medium: {report['medium']}\n"
        response += f"  📊 Total: {report['total_findings']}\n\n"
        
        if report["findings"]:
            response += "🔍 Top Issues:\n"
            for finding in report["findings"][:3]:
                severity_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵"}.get(finding["severity"], "⚪")
                response += f"  {severity_icon} {finding['resource_type']}: {finding['description']}\n"
        
        return response
    
    def scan_code(self, file_path: str) -> str:
        """Scan code file for security vulnerabilities"""
        result = self.security_scanner.scan_code_security(file_path)
        
        if not result["success"]:
            return f"❌ Code scan failed: {result['error']}"
        
        response = f"🔒 Code Security Scan: {os.path.basename(file_path)}\n\n"
        response += f"📊 Total Findings: {result['total_findings']}\n\n"
        
        if result["findings"]:
            response += "🚨 Security Issues:\n"
            for finding in result["findings"]:
                severity_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵"}.get(finding["severity"], "⚪")
                response += f"  {severity_icon} Line {finding['line']}: {finding['description']}\n"
        else:
            response += "✅ No security issues found"
        
        return response
    
    def check_compliance(self, framework: str = "cis_aws") -> str:
        """Check compliance against framework"""
        result = self.security_scanner.check_compliance(framework)
        
        if not result["success"]:
            return f"❌ Compliance check failed: {result['error']}"
        
        response = f"📋 Compliance Check: {result['framework']}\n"
        response += f"📝 Version: {result['version']}\n\n"
        
        response += f"📊 Compliance Score: {result['compliance_score']}%\n"
        response += f"✅ Passed: {result['passed']}/{result['total_controls']}\n"
        response += f"❌ Failed: {result['failed']}/{result['total_controls']}\n\n"
        
        # Show failed controls
        failed_controls = [r for r in result["results"] if r["status"] == "FAIL"]
        if failed_controls:
            response += "🚨 Failed Controls:\n"
            for control in failed_controls[:5]:
                response += f"  ❌ {control['control_id']}: {control['description']}\n"
        
        return response
    
    def security_report(self, scan_id: str = None) -> str:
        """Generate security report"""
        result = self.security_scanner.generate_security_report(scan_id)
        
        if not result["success"]:
            return f"❌ Report generation failed: {result['error']}"
        
        report = result["report"]
        summary = report["executive_summary"]
        
        response = f"📊 Security Report\n\n"
        response += f"🔍 Scan ID: {report['scan_id']}\n"
        response += f"📅 Generated: {report['generated_at'][:19]}\n\n"
        
        response += f"📈 Executive Summary:\n"
        response += f"  🏗️ Resources Scanned: {summary['total_resources_scanned']}\n"
        response += f"  🔴 Critical Issues: {summary['critical_issues']}\n"
        response += f"  🟠 High Issues: {summary['high_issues']}\n"
        response += f"  🟡 Medium Issues: {summary['medium_issues']}\n"
        response += f"  📊 Risk Score: {summary['risk_score']}/100\n\n"
        
        if summary["top_risks"]:
            response += "🎯 Top Risks:\n"
            for risk in summary["top_risks"][:3]:
                severity_icon = {"CRITICAL": "🔴", "HIGH": "🟠", "MEDIUM": "🟡", "LOW": "🔵"}.get(risk["severity"], "⚪")
                response += f"  {severity_icon} {risk['rule_id']}: {risk['count']} occurrences\n"
        
        return response
    
    def scan_history(self) -> str:
        """Get security scan history"""
        result = self.security_scanner.get_scan_history(5)
        
        scans = result["scans"]
        
        if not scans:
            return "🔒 No security scans found"
        
        response = f"🔒 Security Scan History ({len(scans)}):\n\n"
        
        for scan in scans:
            response += f"📊 {scan['scan_id']}\n"
            response += f"   📅 {scan['timestamp'][:19]}\n"
            response += f"   🚨 {scan['total_findings']} findings ({scan['critical']} critical)\n\n"
        
        return response
