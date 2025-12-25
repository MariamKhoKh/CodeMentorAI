import subprocess
import json
import time
import tempfile
import os
from typing import Dict, Any, List
from app.config import settings
from app.utils.enums import TestCaseStatus


class CodeExecutionService:
    """Service for executing user code in isolated subprocess."""
    
    def __init__(self):
        self.timeout = settings.CODE_EXECUTION_TIMEOUT
    
    def execute_python(self, code: str, test_cases: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Execute Python code against test cases.
        
        Args:
            code: User's Python code
            test_cases: List of test cases with input and expected_output
            
        Returns:
            Dict with execution results for each test case
        """
        results = []
        total_runtime = 0
        total_memory = 0
        
        for idx, test_case in enumerate(test_cases):
            try:
                result = self._run_single_test(code, test_case, idx)
                results.append(result)
                
                if result["status"] == TestCaseStatus.PASSED:
                    total_runtime += result.get("runtime_ms", 0)
                    total_memory += result.get("memory_kb", 0)
                    
            except Exception as e:
                results.append({
                    "test_case_id": idx,
                    "status": TestCaseStatus.ERROR,
                    "error_message": str(e),
                    "input": test_case.get("input"),
                    "expected_output": test_case.get("expected_output"),
                    "actual_output": None,
                    "is_hidden": test_case.get("is_hidden", False)
                })
        
        passed_count = sum(1 for r in results if r["status"] == TestCaseStatus.PASSED)
        avg_runtime = total_runtime / passed_count if passed_count > 0 else 0
        avg_memory = total_memory / passed_count if passed_count > 0 else 0
        
        return {
            "test_results": results,
            "total_tests": len(test_cases),
            "passed_tests": passed_count,
            "all_tests_passed": passed_count == len(test_cases),
            "avg_runtime_ms": avg_runtime,
            "avg_memory_kb": avg_memory
        }
    
    def _run_single_test(self, code: str, test_case: Dict[str, Any], test_id: int) -> Dict[str, Any]:
        """Run code against a single test case."""
        
        test_input = test_case.get("input", {})
        expected_output = test_case.get("expected_output")
        
        # Create wrapper that runs the code and returns result as JSON
        wrapper_code = self._create_wrapper(code, test_input)
        
        # Execute in subprocess
        start_time = time.time()
        
        try:
            # Create temporary file with the code
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False) as f:
                f.write(wrapper_code)
                temp_file = f.name
            
            try:
                # Run the code in subprocess with timeout
                result = subprocess.run(
                    ['python', temp_file],
                    capture_output=True,
                    text=True,
                    timeout=self.timeout
                )
                
                runtime_ms = (time.time() - start_time) * 1000
                
                if result.returncode == 0:
                    # Parse output
                    actual_output = self._parse_output(result.stdout)
                    
                    # Compare outputs
                    if self._compare_outputs(actual_output, expected_output):
                        return {
                            "test_case_id": test_id,
                            "status": TestCaseStatus.PASSED,
                            "runtime_ms": runtime_ms,
                            "memory_kb": 0,
                            "input": test_input,
                            "expected_output": expected_output,
                            "actual_output": actual_output,
                            "is_hidden": test_case.get("is_hidden", False)
                        }
                    else:
                        return {
                            "test_case_id": test_id,
                            "status": TestCaseStatus.FAILED,
                            "runtime_ms": runtime_ms,
                            "input": test_input,
                            "expected_output": expected_output,
                            "actual_output": actual_output,
                            "error_message": f"Expected {expected_output}, got {actual_output}",
                            "is_hidden": test_case.get("is_hidden", False)
                        }
                else:
                    return {
                        "test_case_id": test_id,
                        "status": TestCaseStatus.ERROR,
                        "runtime_ms": runtime_ms,
                        "input": test_input,
                        "expected_output": expected_output,
                        "error_message": result.stderr or "Runtime error",
                        "is_hidden": test_case.get("is_hidden", False)
                    }
            finally:
                # Clean up temp file
                try:
                    os.unlink(temp_file)
                except:
                    pass
                    
        except subprocess.TimeoutExpired:
            return {
                "test_case_id": test_id,
                "status": TestCaseStatus.TIMEOUT,
                "input": test_input,
                "expected_output": expected_output,
                "error_message": f"Execution timed out after {self.timeout} seconds",
                "is_hidden": test_case.get("is_hidden", False)
            }
        except Exception as e:
            return {
                "test_case_id": test_id,
                "status": TestCaseStatus.ERROR,
                "input": test_input,
                "expected_output": expected_output,
                "error_message": str(e),
                "is_hidden": test_case.get("is_hidden", False)
            }
    
    def _create_wrapper(self, user_code: str, test_input: Dict[str, Any]) -> str:
        """Create wrapper code that executes user function with test input."""
        
        # Build function call
        params_str = ", ".join([f"{k}={repr(v)}" for k, v in test_input.items()])
        
        wrapper = f"""
import json
import sys
import re

# User code
{user_code}

# Find function name
code = '''{user_code}'''
match = re.search(r'def\\s+(\\w+)\\s*\\(', code)

if match:
    func_name = match.group(1)
    try:
        result = eval(f'{{func_name}}({params_str})')
        print(json.dumps(result))
    except Exception as e:
        print(json.dumps({{"error": str(e)}}), file=sys.stderr)
        sys.exit(1)
else:
    print(json.dumps({{"error": "No function found"}}), file=sys.stderr)
    sys.exit(1)
"""
        return wrapper
    
    def _parse_output(self, output: str) -> Any:
        """Parse output from execution."""
        try:
            return json.loads(output.strip())
        except:
            return output.strip()
    
    def _compare_outputs(self, actual: Any, expected: Any) -> bool:
        """Compare actual and expected outputs."""
        if isinstance(actual, list) and isinstance(expected, list):
            return actual == expected
        
        if isinstance(actual, (int, float)) and isinstance(expected, (int, float)):
            return abs(actual - expected) < 1e-9
        
        return actual == expected


# Global instance
execution_service = CodeExecutionService()