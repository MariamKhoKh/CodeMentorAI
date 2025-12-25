"""
Seed script to populate database with curated coding problems.
Run with: python -m scripts.seed_problems
"""
import asyncio
import sys
from pathlib import Path

# Add backend to path
sys.path.append(str(Path(__file__).resolve().parent.parent))

from sqlalchemy.ext.asyncio import AsyncSession
from app.database import AsyncSessionLocal
from app.models.problem import Problem
from app.utils.enums import DifficultyLevel


PROBLEMS_DATA = [
    {
        "title": "Two Sum",
        "slug": "two-sum",
        "difficulty": DifficultyLevel.EASY,
        "description": """Given an array of integers `nums` and an integer `target`, return indices of the two numbers such that they add up to target.

You may assume that each input would have exactly one solution, and you may not use the same element twice.

You can return the answer in any order.

**Example 1:**
```
Input: nums = [2,7,11,15], target = 9
Output: [0,1]
Explanation: Because nums[0] + nums[1] == 9, we return [0, 1].
```

**Example 2:**
```
Input: nums = [3,2,4], target = 6
Output: [1,2]
```

**Example 3:**
```
Input: nums = [3,3], target = 6
Output: [0,1]
```""",
        "constraints": {
            "nums_length": "2 <= nums.length <= 10^4",
            "nums_values": "-10^9 <= nums[i] <= 10^9",
            "target_values": "-10^9 <= target <= 10^9",
            "guarantee": "Only one valid answer exists"
        },
        "tags": ["Array", "Hash Table"],
        "test_cases": [
            {
                "input": {"nums": [2, 7, 11, 15], "target": 9},
                "expected_output": [0, 1],
                "is_hidden": False,
                "explanation": "nums[0] + nums[1] = 2 + 7 = 9"
            },
            {
                "input": {"nums": [3, 2, 4], "target": 6},
                "expected_output": [1, 2],
                "is_hidden": False,
                "explanation": "nums[1] + nums[2] = 2 + 4 = 6"
            },
            {
                "input": {"nums": [3, 3], "target": 6},
                "expected_output": [0, 1],
                "is_hidden": False
            },
            {
                "input": {"nums": [-1, -2, -3, -4, -5], "target": -8},
                "expected_output": [2, 4],
                "is_hidden": True
            },
            {
                "input": {"nums": [1] * 10000 + [2], "target": 3},
                "expected_output": [0, 10000],
                "is_hidden": True,
                "explanation": "Large input test"
            }
        ],
        "optimal_patterns": {
            "time_complexity": "O(n)",
            "space_complexity": "O(n)",
            "key_patterns": ["Hash Table", "Single Pass"],
            "key_data_structures": ["HashMap/Dictionary"]
        },
        "starter_code": {
            "python": """def two_sum(nums: list[int], target: int) -> list[int]:
    # Write your solution here
    pass""",
            "javascript": """function twoSum(nums, target) {
    // Write your solution here
}"""
        },
        "reference_solution": {
            "python": """def two_sum(nums: list[int], target: int) -> list[int]:
    seen = {}
    for i, num in enumerate(nums):
        complement = target - num
        if complement in seen:
            return [seen[complement], i]
        seen[num] = i
    return []"""
        }
    },
    {
        "title": "Valid Parentheses",
        "slug": "valid-parentheses",
        "difficulty": DifficultyLevel.EASY,
        "description": """Given a string `s` containing just the characters '(', ')', '{', '}', '[' and ']', determine if the input string is valid.

An input string is valid if:
1. Open brackets must be closed by the same type of brackets.
2. Open brackets must be closed in the correct order.
3. Every close bracket has a corresponding open bracket of the same type.

**Example 1:**
```
Input: s = "()"
Output: true
```

**Example 2:**
```
Input: s = "()[]{}"
Output: true
```

**Example 3:**
```
Input: s = "(]"
Output: false
```

**Example 4:**
```
Input: s = "([)]"
Output: false
```""",
        "constraints": {
            "length": "1 <= s.length <= 10^4",
            "characters": "s consists of parentheses only '()[]{}'"
        },
        "tags": ["String", "Stack"],
        "test_cases": [
            {
                "input": {"s": "()"},
                "expected_output": True,
                "is_hidden": False
            },
            {
                "input": {"s": "()[]{}"},
                "expected_output": True,
                "is_hidden": False
            },
            {
                "input": {"s": "(]"},
                "expected_output": False,
                "is_hidden": False
            },
            {
                "input": {"s": "([)]"},
                "expected_output": False,
                "is_hidden": False
            },
            {
                "input": {"s": "{[]}"},
                "expected_output": True,
                "is_hidden": False
            },
            {
                "input": {"s": "(((((((((("},
                "expected_output": False,
                "is_hidden": True,
                "explanation": "Only opening brackets"
            },
            {
                "input": {"s": "())" * 1000},
                "expected_output": False,
                "is_hidden": True
            }
        ],
        "optimal_patterns": {
            "time_complexity": "O(n)",
            "space_complexity": "O(n)",
            "key_patterns": ["Stack", "Matching Pairs"],
            "key_data_structures": ["Stack"]
        },
        "starter_code": {
            "python": """def is_valid(s: str) -> bool:
    # Write your solution here
    pass"""
        },
        "reference_solution": {
            "python": """def is_valid(s: str) -> bool:
    stack = []
    mapping = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in mapping:
            top_element = stack.pop() if stack else '#'
            if mapping[char] != top_element:
                return False
        else:
            stack.append(char)
    
    return not stack"""
        }
    },
    {
        "title": "Merge Two Sorted Lists",
        "slug": "merge-two-sorted-lists",
        "difficulty": DifficultyLevel.EASY,
        "description": """You are given the heads of two sorted linked lists `list1` and `list2`.

Merge the two lists into one sorted list. The list should be made by splicing together the nodes of the first two lists.

Return the head of the merged linked list.

**Example 1:**
```
Input: list1 = [1,2,4], list2 = [1,3,4]
Output: [1,1,2,3,4,4]
```

**Example 2:**
```
Input: list1 = [], list2 = []
Output: []
```

**Example 3:**
```
Input: list1 = [], list2 = [0]
Output: [0]
```""",
        "constraints": {
            "length": "The number of nodes in both lists is in the range [0, 50]",
            "values": "-100 <= Node.val <= 100",
            "sorted": "Both list1 and list2 are sorted in non-decreasing order"
        },
        "tags": ["Linked List", "Recursion"],
        "test_cases": [
            {
                "input": {"list1": [1, 2, 4], "list2": [1, 3, 4]},
                "expected_output": [1, 1, 2, 3, 4, 4],
                "is_hidden": False
            },
            {
                "input": {"list1": [], "list2": []},
                "expected_output": [],
                "is_hidden": False
            },
            {
                "input": {"list1": [], "list2": [0]},
                "expected_output": [0],
                "is_hidden": False
            },
            {
                "input": {"list1": [1, 3, 5], "list2": [2, 4, 6]},
                "expected_output": [1, 2, 3, 4, 5, 6],
                "is_hidden": True
            }
        ],
        "optimal_patterns": {
            "time_complexity": "O(n + m)",
            "space_complexity": "O(1)",
            "key_patterns": ["Two Pointers", "Merge"],
            "key_data_structures": ["Linked List"]
        },
        "starter_code": {
            "python": """class ListNode:
    def __init__(self, val=0, next=None):
        self.val = val
        self.next = next

def merge_two_lists(list1: ListNode, list2: ListNode) -> ListNode:
    # Write your solution here
    pass"""
        },
        "reference_solution": {
            "python": """def merge_two_lists(list1: ListNode, list2: ListNode) -> ListNode:
    dummy = ListNode(0)
    current = dummy
    
    while list1 and list2:
        if list1.val <= list2.val:
            current.next = list1
            list1 = list1.next
        else:
            current.next = list2
            list2 = list2.next
        current = current.next
    
    current.next = list1 if list1 else list2
    return dummy.next"""
        }
    },
    {
        "title": "Best Time to Buy and Sell Stock",
        "slug": "best-time-to-buy-and-sell-stock",
        "difficulty": DifficultyLevel.EASY,
        "description": """You are given an array `prices` where `prices[i]` is the price of a given stock on the ith day.

You want to maximize your profit by choosing a single day to buy one stock and choosing a different day in the future to sell that stock.

Return the maximum profit you can achieve from this transaction. If you cannot achieve any profit, return 0.

**Example 1:**
```
Input: prices = [7,1,5,3,6,4]
Output: 5
Explanation: Buy on day 2 (price = 1) and sell on day 5 (price = 6), profit = 6-1 = 5.
```

**Example 2:**
```
Input: prices = [7,6,4,3,1]
Output: 0
Explanation: No profit can be made, so return 0.
```""",
        "constraints": {
            "length": "1 <= prices.length <= 10^5",
            "values": "0 <= prices[i] <= 10^4"
        },
        "tags": ["Array", "Dynamic Programming"],
        "test_cases": [
            {
                "input": {"prices": [7, 1, 5, 3, 6, 4]},
                "expected_output": 5,
                "is_hidden": False
            },
            {
                "input": {"prices": [7, 6, 4, 3, 1]},
                "expected_output": 0,
                "is_hidden": False
            },
            {
                "input": {"prices": [1, 2, 3, 4, 5]},
                "expected_output": 4,
                "is_hidden": True
            },
            {
                "input": {"prices": [3, 3, 3, 3, 3]},
                "expected_output": 0,
                "is_hidden": True
            }
        ],
        "optimal_patterns": {
            "time_complexity": "O(n)",
            "space_complexity": "O(1)",
            "key_patterns": ["Single Pass", "Track Minimum"],
            "key_data_structures": ["None - Variables Only"]
        },
        "starter_code": {
            "python": """def max_profit(prices: list[int]) -> int:
    # Write your solution here
    pass"""
        },
        "reference_solution": {
            "python": """def max_profit(prices: list[int]) -> int:
    min_price = float('inf')
    max_profit = 0
    
    for price in prices:
        if price < min_price:
            min_price = price
        elif price - min_price > max_profit:
            max_profit = price - min_price
    
    return max_profit"""
        }
    },
    {
        "title": "Maximum Subarray",
        "slug": "maximum-subarray",
        "difficulty": DifficultyLevel.MEDIUM,
        "description": """Given an integer array `nums`, find the subarray with the largest sum, and return its sum.

**Example 1:**
```
Input: nums = [-2,1,-3,4,-1,2,1,-5,4]
Output: 6
Explanation: The subarray [4,-1,2,1] has the largest sum 6.
```

**Example 2:**
```
Input: nums = [1]
Output: 1
```

**Example 3:**
```
Input: nums = [5,4,-1,7,8]
Output: 23
```""",
        "constraints": {
            "length": "1 <= nums.length <= 10^5",
            "values": "-10^4 <= nums[i] <= 10^4"
        },
        "tags": ["Array", "Dynamic Programming", "Divide and Conquer"],
        "test_cases": [
            {
                "input": {"nums": [-2, 1, -3, 4, -1, 2, 1, -5, 4]},
                "expected_output": 6,
                "is_hidden": False
            },
            {
                "input": {"nums": [1]},
                "expected_output": 1,
                "is_hidden": False
            },
            {
                "input": {"nums": [5, 4, -1, 7, 8]},
                "expected_output": 23,
                "is_hidden": False
            },
            {
                "input": {"nums": [-1, -2, -3, -4]},
                "expected_output": -1,
                "is_hidden": True
            },
            {
                "input": {"nums": [1] * 100000},
                "expected_output": 100000,
                "is_hidden": True
            }
        ],
        "optimal_patterns": {
            "time_complexity": "O(n)",
            "space_complexity": "O(1)",
            "key_patterns": ["Kadane's Algorithm", "Dynamic Programming"],
            "key_data_structures": ["None - Variables Only"]
        },
        "starter_code": {
            "python": """def max_subarray(nums: list[int]) -> int:
    # Write your solution here
    pass"""
        },
        "reference_solution": {
            "python": """def max_subarray(nums: list[int]) -> int:
    max_sum = current_sum = nums[0]
    
    for num in nums[1:]:
        current_sum = max(num, current_sum + num)
        max_sum = max(max_sum, current_sum)
    
    return max_sum"""
        }
    }
]


async def seed_problems():
    """Seed the database with problems."""
    async with AsyncSessionLocal() as db:
        try:
            # Check if problems already exist
            from sqlalchemy import select
            result = await db.execute(select(Problem))
            existing = result.scalars().all()
            
            if existing:
                print(f"⚠️  Database already has {len(existing)} problems.")
                response = input("Do you want to delete existing problems and reseed? (yes/no): ")
                if response.lower() != 'yes':
                    print("❌ Seeding cancelled.")
                    return
                
                # Delete existing problems
                for problem in existing:
                    await db.delete(problem)
                await db.commit()
                print("🗑️  Deleted existing problems.")
            
            # Insert new problems
            for problem_data in PROBLEMS_DATA:
                problem = Problem(**problem_data)
                db.add(problem)
            
            await db.commit()
            print(f"✅ Successfully seeded {len(PROBLEMS_DATA)} problems!")
            
            # Print summary
            print("\n📊 Problems Summary:")
            for p in PROBLEMS_DATA:
                print(f"  - {p['title']} ({p['difficulty'].value})")
            
        except Exception as e:
            print(f"❌ Error seeding problems: {e}")
            await db.rollback()
            raise


if __name__ == "__main__":
    print("🌱 Starting problem seeding...\n")
    asyncio.run(seed_problems())