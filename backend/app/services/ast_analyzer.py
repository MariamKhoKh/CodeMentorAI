import ast
from typing import Dict, Any, List


class ASTAnalyzer:
    """Analyzes Python code structure using Abstract Syntax Tree."""
    
    def analyze(self, code: str) -> Dict[str, Any]:
        """
        Analyze code structure and return features.
        
        Returns:
            Dict with AST features like loops, recursion, data structures, etc.
        """
        try:
            tree = ast.parse(code)
            
            features = {
                "loops": 0,
                "nested_loops": False,
                "max_loop_depth": 0,
                "recursion": False,
                "uses_hashmap": False,
                "uses_set": False,
                "uses_list": False,
                "uses_dict": False,
                "conditionals": 0,
                "early_exits": 0,
                "function_calls": [],
                "data_structures": [],
                "sorting_used": False,
                "list_comprehension": False,
                "guards": False,
            }
            
            visitor = CodeVisitor(features)
            visitor.visit(tree)
            
            # Post-process
            features["data_structures"] = list(set(features["data_structures"]))
            features["function_calls"] = list(set(features["function_calls"]))
            
            return features
            
        except SyntaxError as e:
            return {"error": f"Syntax error: {str(e)}"}
        except Exception as e:
            return {"error": f"Analysis error: {str(e)}"}


class CodeVisitor(ast.NodeVisitor):
    """AST visitor that extracts code features."""
    
    def __init__(self, features: Dict[str, Any]):
        self.features = features
        self.loop_depth = 0
        self.function_names = set()
        self.current_function = None
    
    def visit_FunctionDef(self, node):
        """Track function definitions."""
        self.function_names.add(node.name)
        old_function = self.current_function
        self.current_function = node.name
        self.generic_visit(node)
        self.current_function = old_function
    
    def visit_For(self, node):
        """Track for loops."""
        self.features["loops"] += 1
        self.loop_depth += 1
        
        if self.loop_depth > self.features["max_loop_depth"]:
            self.features["max_loop_depth"] = self.loop_depth
        
        if self.loop_depth > 1:
            self.features["nested_loops"] = True
        
        self.generic_visit(node)
        self.loop_depth -= 1
    
    def visit_While(self, node):
        """Track while loops."""
        self.features["loops"] += 1
        self.loop_depth += 1
        
        if self.loop_depth > self.features["max_loop_depth"]:
            self.features["max_loop_depth"] = self.loop_depth
        
        if self.loop_depth > 1:
            self.features["nested_loops"] = True
        
        self.generic_visit(node)
        self.loop_depth -= 1
    
    def visit_ListComp(self, node):
        """Track list comprehensions."""
        self.features["list_comprehension"] = True
        self.generic_visit(node)
    
    def visit_If(self, node):
        """Track conditionals and guard clauses."""
        self.features["conditionals"] += 1
        
        # Check for guard clause (early return)
        if any(isinstance(stmt, ast.Return) for stmt in node.body):
            self.features["guards"] = True
        
        self.generic_visit(node)
    
    def visit_Return(self, node):
        """Track early exits."""
        self.features["early_exits"] += 1
        self.generic_visit(node)
    
    def visit_Call(self, node):
        """Track function calls and data structure usage."""
        # Get function name
        if isinstance(node.func, ast.Name):
            func_name = node.func.id
            self.features["function_calls"].append(func_name)
            
            # Check for recursion
            if func_name == self.current_function:
                self.features["recursion"] = True
            
            # Check for built-in data structures
            if func_name in ["dict", "set", "list"]:
                self.features["data_structures"].append(func_name)
                if func_name == "dict":
                    self.features["uses_dict"] = True
                    self.features["uses_hashmap"] = True
                elif func_name == "set":
                    self.features["uses_set"] = True
                elif func_name == "list":
                    self.features["uses_list"] = True
            
            # Check for sorting
            if func_name in ["sort", "sorted"]:
                self.features["sorting_used"] = True
        
        elif isinstance(node.func, ast.Attribute):
            # Handle method calls like list.sort()
            if node.func.attr == "sort":
                self.features["sorting_used"] = True
        
        self.generic_visit(node)
    
    def visit_Dict(self, node):
        """Track dictionary literals."""
        self.features["uses_dict"] = True
        self.features["uses_hashmap"] = True
        self.features["data_structures"].append("dict")
        self.generic_visit(node)
    
    def visit_Set(self, node):
        """Track set literals."""
        self.features["uses_set"] = True
        self.features["data_structures"].append("set")
        self.generic_visit(node)
    
    def visit_List(self, node):
        """Track list literals."""
        self.features["uses_list"] = True
        self.features["data_structures"].append("list")
        self.generic_visit(node)


# Global instance
ast_analyzer = ASTAnalyzer()