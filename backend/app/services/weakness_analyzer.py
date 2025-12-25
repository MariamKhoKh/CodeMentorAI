from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from typing import Dict, List, Any
from app.models.submission import Submission
from app.models.analysis import AnalysisResult
from app.models.weakness_profile import WeaknessProfile
from app.models.problem import Problem
from collections import defaultdict, Counter
import logging

logger = logging.getLogger(__name__)


class WeaknessAnalyzer:
    """Analyzes user submissions to identify weaknesses and update profile."""
    
    async def update_weakness_profile(
        self, 
        user_id: int, 
        db: AsyncSession
    ) -> WeaknessProfile:
        """
        Analyze all user submissions and update their weakness profile.
        
        Args:
            user_id: The user's ID
            db: Database session
            
        Returns:
            Updated WeaknessProfile
        """
        
        # Fetch all user submissions with analysis
        result = await db.execute(
            select(Submission, AnalysisResult, Problem)
            .join(AnalysisResult, Submission.id == AnalysisResult.submission_id)
            .join(Problem, Submission.problem_id == Problem.id)
            .where(Submission.user_id == user_id)
            .order_by(Submission.created_at.desc())
            .limit(50)  # Analyze last 50 submissions
        )
        
        submissions_data = result.all()
        
        if not submissions_data:
            logger.info(f"No submissions found for user {user_id}")
            return await self._create_default_profile(user_id, db)
        
        # Analyze weaknesses
        weaknesses = self._identify_weaknesses(submissions_data)
        
        # Get or create weakness profile
        result = await db.execute(
            select(WeaknessProfile).where(WeaknessProfile.user_id == user_id)
        )
        profile = result.scalar_one_or_none()
        
        if not profile:
            profile = WeaknessProfile(user_id=user_id)
            db.add(profile)
        
        # Update profile
        profile.top_weaknesses = weaknesses["top_weaknesses"]
        profile.weak_tags = weaknesses["weak_tags"]
        profile.weak_patterns = weaknesses["weak_patterns"]
        profile.analysis_metadata = weaknesses["metadata"]
        
        await db.commit()
        await db.refresh(profile)
        
        logger.info(f"Updated weakness profile for user {user_id}: {weaknesses['top_weaknesses']}")
        return profile
    
    def _identify_weaknesses(
        self, 
        submissions_data: List[tuple]
    ) -> Dict[str, Any]:
        """
        Identify weaknesses from submission data.
        
        Args:
            submissions_data: List of (Submission, AnalysisResult, Problem) tuples
            
        Returns:
            Dictionary containing identified weaknesses
        """
        
        weaknesses = []
        weak_tags = []
        weak_patterns = []
        
        # Track failures and low complexity matches
        failed_problems = []
        low_complexity_problems = []
        slow_problems = []
        tag_performance = defaultdict(list)
        pattern_issues = defaultdict(int)
        
        for submission, analysis, problem in submissions_data:
            # Failed tests
            if not submission.all_tests_passed:
                failed_problems.append({
                    "problem": problem.title,
                    "tags": problem.tags or [],
                    "difficulty": problem.difficulty
                })
                
                # Track which tags are associated with failures
                if problem.tags:
                    for tag in problem.tags:
                        tag_performance[tag].append(0)  # 0 = failed
            
            # Low complexity match (inefficient solution)
            elif analysis.complexity_match is not None and analysis.complexity_match < 0.7:
                low_complexity_problems.append({
                    "problem": problem.title,
                    "complexity_match": analysis.complexity_match,
                    "estimated": analysis.estimated_time_complexity,
                    "optimal": analysis.optimal_time_complexity,
                    "tags": problem.tags or []
                })
                
                # Track tags with complexity issues
                if problem.tags:
                    for tag in problem.tags:
                        tag_performance[tag].append(0.5)  # 0.5 = suboptimal
            
            # Slow execution
            elif submission.runtime_ms and submission.runtime_ms > 1000:  # >1 second
                slow_problems.append({
                    "problem": problem.title,
                    "runtime": submission.runtime_ms,
                    "tags": problem.tags or []
                })
            
            # Successful submission
            else:
                if problem.tags:
                    for tag in problem.tags:
                        tag_performance[tag].append(1.0)  # 1.0 = success
            
            # Analyze patterns from AST features
            if analysis.ast_features:
                features = analysis.ast_features
                
                # Nested loops but low complexity match
                if features.get('nested_loops') and analysis.complexity_match and analysis.complexity_match < 0.8:
                    pattern_issues['inefficient_nested_loops'] += 1
                
                # No hash map usage when it could help
                if not features.get('uses_hashmap') and features.get('loops', 0) > 1:
                    if analysis.complexity_match and analysis.complexity_match < 0.8:
                        pattern_issues['missing_hashmap_optimization'] += 1
                
                # No guard clauses
                if not features.get('guards') and features.get('conditionals', 0) > 2:
                    pattern_issues['poor_code_structure'] += 1
        
        # Determine top weaknesses
        if failed_problems:
            # Most common tags in failed problems
            failed_tags = []
            for fp in failed_problems:
                failed_tags.extend(fp['tags'])
            
            if failed_tags:
                most_common_tags = Counter(failed_tags).most_common(3)
                for tag, count in most_common_tags:
                    weaknesses.append(f"struggles_with_{tag.lower().replace(' ', '_')}")
                    weak_tags.append(tag)
            else:
                weaknesses.append("test_case_failures")
        
        if low_complexity_problems:
            weaknesses.append("algorithm_optimization")
            
            # Identify specific complexity issues
            complexity_tags = []
            for lcp in low_complexity_problems:
                complexity_tags.extend(lcp['tags'])
            
            if complexity_tags:
                most_common = Counter(complexity_tags).most_common(2)
                for tag, _ in most_common:
                    weak_tags.append(tag)
        
        if slow_problems:
            weaknesses.append("time_efficiency")
        
        # Add pattern-based weaknesses
        for pattern, count in sorted(pattern_issues.items(), key=lambda x: x[1], reverse=True):
            if count >= 2:  # At least 2 occurrences
                weaknesses.append(pattern)
                weak_patterns.append(pattern)
        
        # Calculate tag performance scores
        tag_scores = {}
        for tag, scores in tag_performance.items():
            avg_score = sum(scores) / len(scores)
            tag_scores[tag] = avg_score
        
        # Identify weak tags (performance < 0.6)
        weak_performing_tags = [
            tag for tag, score in tag_scores.items() 
            if score < 0.6
        ]
        
        # If no specific weaknesses identified, add general ones
        if not weaknesses:
            weaknesses.append("general_practice_needed")
        
        # Ensure we have at least 1-3 top weaknesses
        weaknesses = weaknesses[:5]  # Limit to top 5
        weak_tags = list(set(weak_tags + weak_performing_tags))[:5]
        weak_patterns = weak_patterns[:3]
        
        return {
            "top_weaknesses": weaknesses,
            "weak_tags": weak_tags,
            "weak_patterns": weak_patterns,
            "metadata": {
                "total_analyzed": len(submissions_data),
                "failed_count": len(failed_problems),
                "low_complexity_count": len(low_complexity_problems),
                "slow_count": len(slow_problems),
                "tag_scores": tag_scores
            }
        }
    
    async def _create_default_profile(
        self, 
        user_id: int, 
        db: AsyncSession
    ) -> WeaknessProfile:
        """Create a default profile for users with no submissions."""
        
        profile = WeaknessProfile(
            user_id=user_id,
            top_weaknesses=["beginner_level"],
            weak_tags=["arrays", "strings"],
            weak_patterns=[],
            analysis_metadata={"total_analyzed": 0}
        )
        
        db.add(profile)
        await db.commit()
        await db.refresh(profile)
        
        return profile


# Global instance
weakness_analyzer = WeaknessAnalyzer()