from openai import AzureOpenAI
from typing import Dict, Any, List, Optional
from app.config import settings


class FeedbackGenerator:
    """Generates personalized feedback using Azure OpenAI."""
    
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
        )
        self.deployment = settings.AZURE_OPENAI_DEPLOYMENT
    
    def generate_feedback(
        self,
        problem_description: str,
        user_code: str,
        test_results: List[Dict[str, Any]],
        ast_features: Dict[str, Any],
        complexity_analysis: Dict[str, Any],
        all_tests_passed: bool
    ) -> Dict[str, Any]:
        """
        Generate personalized feedback for a code submission.
        
        Args:
            problem_description: The problem statement
            user_code: User's submitted code
            test_results: Results from test execution
            ast_features: AST analysis features
            complexity_analysis: Complexity estimation
            all_tests_passed: Whether all tests passed
            
        Returns:
            Dict with feedback text and improvement suggestions
        """
        
        # Build context for GPT
        prompt = self._build_prompt(
            problem_description,
            user_code,
            test_results,
            ast_features,
            complexity_analysis,
            all_tests_passed
        )
        
        try:
            response = self.client.chat.completions.create(
                model=self.deployment,
                messages=[
                    {
                        "role": "system",
                        "content": """You are an expert technical interview coach. Analyze code submissions and provide constructive, actionable feedback. Focus on:

1. What went wrong (if applicable)
2. Why it matters in technical interviews
3. How to improve the solution
4. Specific coding patterns or concepts to learn

Be encouraging but honest. Keep feedback concise (3-5 paragraphs max)."""
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=0.7,
                max_tokens=1000
            )
            
            feedback_text = response.choices[0].message.content
            
            # Generate structured suggestions
            suggestions = self._extract_suggestions(
                feedback_text,
                ast_features,
                complexity_analysis,
                all_tests_passed
            )
            
            return {
                "feedback_text": feedback_text,
                "improvement_suggestions": suggestions
            }
            
        except Exception as e:
            return {
                "feedback_text": f"Unable to generate feedback: {str(e)}",
                "improvement_suggestions": []
            }
    
    def _build_prompt(
        self,
        problem_description: str,
        user_code: str,
        test_results: List[Dict[str, Any]],
        ast_features: Dict[str, Any],
        complexity_analysis: Dict[str, Any],
        all_tests_passed: bool
    ) -> str:
        """Build the prompt for GPT."""
        
        # Test summary
        total_tests = len(test_results)
        passed_tests = sum(1 for t in test_results if t.get("status") == "passed")
        
        # Failed test cases (only non-hidden ones for privacy)
        failed_tests = [
            t for t in test_results 
            if t.get("status") != "passed" and not t.get("is_hidden", False)
        ]
        
        # Build prompt
        prompt = f"""## Problem
{problem_description}

## User's Code
```python
{user_code}
```

## Test Results
- Passed: {passed_tests}/{total_tests}
- All tests passed: {all_tests_passed}
"""
        
        if failed_tests:
            prompt += "\n### Failed Test Cases:\n"
            for test in failed_tests[:2]:  # Show max 2 failed tests
                prompt += f"- Input: {test.get('input')}\n"
                prompt += f"  Expected: {test.get('expected_output')}\n"
                prompt += f"  Got: {test.get('actual_output')}\n"
                if test.get('error_message'):
                    prompt += f"  Error: {test.get('error_message')}\n"
        
        # Complexity analysis
        prompt += f"""
## Code Analysis
- Time Complexity: {complexity_analysis.get('estimated_time_complexity')} (Optimal: {complexity_analysis.get('optimal_time_complexity', 'Unknown')})
- Space Complexity: {complexity_analysis.get('estimated_space_complexity')} (Optimal: {complexity_analysis.get('optimal_space_complexity', 'Unknown')})
- Complexity Match Score: {complexity_analysis.get('complexity_match', 0):.2f}/1.00

## Code Structure
- Loops: {ast_features.get('loops', 0)} (Nested: {ast_features.get('nested_loops', False)})
- Recursion: {ast_features.get('recursion', False)}
- Uses HashMap/Dict: {ast_features.get('uses_hashmap', False)}
- Data Structures: {', '.join(ast_features.get('data_structures', []))}
- Guard Clauses: {ast_features.get('guards', False)}

## Task
Provide feedback on this solution. Focus on:
1. Correctness issues (if any)
2. Algorithm efficiency
3. Code quality and best practices
4. What the candidate should learn or improve

Be specific and actionable."""
        
        return prompt
    
    def _extract_suggestions(
        self,
        feedback_text: str,
        ast_features: Dict[str, Any],
        complexity_analysis: Dict[str, Any],
        all_tests_passed: bool
    ) -> List[str]:
        """Extract structured improvement suggestions."""
        
        suggestions = []
        
        # Complexity suggestions
        complexity_match = complexity_analysis.get('complexity_match', 1.0)
        if complexity_match < 0.8:
            est = complexity_analysis.get('estimated_time_complexity', '')
            opt = complexity_analysis.get('optimal_time_complexity', '')
            suggestions.append(f"Optimize time complexity from {est} to {opt}")
        
        # Code structure suggestions
        if ast_features.get('nested_loops') and ast_features.get('loops', 0) > 1:
            if not ast_features.get('uses_hashmap'):
                suggestions.append("Consider using a hash map to avoid nested loops")
        
        if not ast_features.get('guards') and ast_features.get('conditionals', 0) > 0:
            suggestions.append("Use guard clauses for early returns to improve readability")
        
        # Test failure suggestions
        if not all_tests_passed:
            suggestions.append("Review edge cases and boundary conditions")
        
        # General suggestions based on patterns
        if ast_features.get('loops', 0) == 0 and not ast_features.get('recursion'):
            suggestions.append("Solution may be too simple - verify all test cases")
        
        return suggestions[:5]  # Max 5 suggestions


# Global instance
feedback_generator = FeedbackGenerator()