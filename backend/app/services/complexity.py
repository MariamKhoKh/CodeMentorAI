from typing import Dict, Any, Optional


class ComplexityAnalyzer:
    """Estimates time and space complexity based on AST features."""
    
    def estimate_complexity(
        self,
        ast_features: Dict[str, Any],
        optimal_patterns: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Estimate time and space complexity.
        
        Args:
            ast_features: Features from AST analysis
            optimal_patterns: Expected optimal complexity from problem
            
        Returns:
            Dict with estimated complexities and comparison
        """
        time_complexity = self._estimate_time_complexity(ast_features)
        space_complexity = self._estimate_space_complexity(ast_features)
        
        result = {
            "estimated_time_complexity": time_complexity,
            "estimated_space_complexity": space_complexity,
        }
        
        if optimal_patterns:
            result["optimal_time_complexity"] = optimal_patterns.get("time_complexity", "Unknown")
            result["optimal_space_complexity"] = optimal_patterns.get("space_complexity", "Unknown")
            result["complexity_match"] = self._calculate_match_score(
                time_complexity,
                optimal_patterns.get("time_complexity", "")
            )
        
        return result
    
    def _estimate_time_complexity(self, features: Dict[str, Any]) -> str:
        """Estimate time complexity based on code structure."""
        
        # Check for common patterns
        max_depth = features.get("max_loop_depth", 0)
        loops = features.get("loops", 0)
        recursion = features.get("recursion", False)
        sorting = features.get("sorting_used", False)
        
        # Nested loops
        if max_depth >= 3:
            return "O(n^3)"
        elif max_depth == 2:
            return "O(n^2)"
        elif max_depth == 1:
            # Single loop with sorting
            if sorting:
                return "O(n log n)"
            # Single loop with hashmap
            elif features.get("uses_hashmap"):
                return "O(n)"
            else:
                return "O(n)"
        
        # Recursion without loops
        if recursion:
            # Check if it's divide and conquer (sorting or binary search pattern)
            if sorting or "sorted" in features.get("function_calls", []):
                return "O(n log n)"
            else:
                return "O(2^n)"  # Assume exponential if not clear
        
        # Sorting without loops
        if sorting:
            return "O(n log n)"
        
        # No loops, no recursion
        if loops == 0 and not recursion:
            return "O(1)"
        
        return "O(n)"
    
    def _estimate_space_complexity(self, features: Dict[str, Any]) -> str:
        """Estimate space complexity."""
        
        uses_dict = features.get("uses_hashmap", False) or features.get("uses_dict", False)
        uses_set = features.get("uses_set", False)
        uses_list = features.get("uses_list", False)
        recursion = features.get("recursion", False)
        
        # Recursion adds call stack space
        if recursion:
            return "O(n)"
        
        # Using hash-based data structures
        if uses_dict or uses_set:
            return "O(n)"
        
        # Using lists
        if uses_list:
            return "O(n)"
        
        # No additional data structures
        return "O(1)"
    
    def _calculate_match_score(self, estimated: str, optimal: str) -> float:
        """
        Calculate how well estimated complexity matches optimal.
        Returns score between 0.0 and 1.0.
        """
        if not optimal or optimal == "Unknown":
            return 0.5
        
        # Normalize complexity strings
        estimated = estimated.strip().lower()
        optimal = optimal.strip().lower()
        
        # Exact match
        if estimated == optimal:
            return 1.0
        
        # Define complexity hierarchy (from best to worst)
        complexity_order = [
            "o(1)",
            "o(log n)",
            "o(n)",
            "o(n log n)",
            "o(n^2)",
            "o(n^3)",
            "o(2^n)",
            "o(n!)"
        ]
        
        try:
            est_idx = complexity_order.index(estimated)
            opt_idx = complexity_order.index(optimal)
            
            # Same complexity = 1.0
            if est_idx == opt_idx:
                return 1.0
            
            # One step worse = 0.7
            elif est_idx == opt_idx + 1:
                return 0.7
            
            # Two steps worse = 0.4
            elif est_idx == opt_idx + 2:
                return 0.4
            
            # Better than optimal = 0.9 (might be too optimistic estimation)
            elif est_idx < opt_idx:
                return 0.9
            
            # Much worse = 0.2
            else:
                return 0.2
                
        except ValueError:
            # Unknown complexity format
            return 0.5


# Global instance
complexity_analyzer = ComplexityAnalyzer()