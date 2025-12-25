from openai import AzureOpenAI
from app.config import settings
from typing import List, Dict, Any

class ProblemGenerator:
    """Generates coding problems using Azure OpenAI based on user weaknesses."""
    def __init__(self):
        self.client = AzureOpenAI(
            api_key=settings.AZURE_OPENAI_API_KEY,
            api_version=settings.AZURE_OPENAI_API_VERSION,
            azure_endpoint=settings.AZURE_OPENAI_ENDPOINT
        )
        self.deployment = settings.AZURE_OPENAI_DEPLOYMENT

    def generate_problem(self, weaknesses: List[str]) -> Dict[str, Any]:
        prompt = self._build_prompt(weaknesses)
        response = self.client.chat.completions.create(
            model=self.deployment,
            messages=[
                {"role": "system", "content": "You are an expert coding interview problem creator. Generate a new, original coding problem that helps a user practice the following weak concepts: " + ', '.join(weaknesses) + ". Return the problem as a JSON object with fields: title, description, difficulty, constraints, tags, test_cases (with input, expected_output, explanation)."},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,
            max_tokens=1200
        )
        # Parse the response as JSON (assume model returns valid JSON)
        import json
        raw_content = response.choices[0].message.content
        print("[AI RAW RESPONSE]", raw_content)  # For debugging
        # Remove code block markers if present
        if raw_content.strip().startswith("```json"):
            raw_content = raw_content.strip()[7:]
        if raw_content.strip().startswith("```"):
            raw_content = raw_content.strip()[3:]
        if raw_content.strip().endswith("```"):
            raw_content = raw_content.strip()[:-3]
        try:
            return json.loads(raw_content.strip())
        except Exception as e:
            return {"error": f"Failed to parse AI response: {str(e)}", "raw": raw_content}

    def _build_prompt(self, weaknesses: List[str]) -> str:
        return f"Generate a new coding problem that helps practice: {', '.join(weaknesses)}. The problem should be unique, non-trivial, and suitable for a technical interview."

# Global instance
problem_generator = ProblemGenerator()
