"""
Fallback solutions for common LeetCode problems.
Used when the official LeetCode API doesn't return a solution (e.g., premium problems or API issues).
"""

COMMON_SOLUTIONS = {
    "two-sum": {
        "title": "Two Sum",
        "approach": "Hash Map",
        "explanation": """
## Approach: Hash Map

The key insight is to use a hash map (dictionary) to store numbers we've seen and their indices. 
As we iterate through the array, for each number, we check if its complement (target - current number) 
exists in our hash map.

### Algorithm:
1. Create an empty hash map to store {number: index}
2. For each number in the array:
   - Calculate complement = target - current_number
   - If complement exists in hash map, we found our answer!
   - Otherwise, add current number and its index to hash map
3. Return the two indices

### Why This Works:
Instead of checking every pair (which takes O(n²) time), we do a single pass through the array. 
For each number, we instantly check if we've already seen its complement using the hash map's O(1) lookup.

### Time Complexity: O(n) - single pass through array
### Space Complexity: O(n) - hash map stores up to n elements
""",
        "code": """def twoSum(nums, target):
    # Hash map to store {number: index}
    seen = {}
    
    for i, num in enumerate(nums):
        # Calculate what number we need to reach target
        complement = target - num
        
        # Check if we've seen the complement before
        if complement in seen:
            return [seen[complement], i]
        
        # Store current number and its index
        seen[num] = i
    
    return []  # No solution found

# Example usage:
# nums = [2, 7, 11, 15], target = 9
# Step 1: i=0, num=2, complement=7, seen={2: 0}
# Step 2: i=1, num=7, complement=2, found! return [0, 1]
""",
        "example": """
Example: nums = [2, 7, 11, 15], target = 9

Iteration 1 (i=0, num=2):
  - complement = 9 - 2 = 7
  - 7 not in seen
  - seen = {2: 0}

Iteration 2 (i=1, num=7):
  - complement = 9 - 7 = 2
  - 2 IS in seen (at index 0)
  - Return [0, 1] ✓
"""
    },
    
    "reverse-linked-list": {
        "title": "Reverse Linked List",
        "approach": "Iterative with Three Pointers",
        "explanation": """
## Approach: Iterative Reversal

The key is to reverse the direction of each node's 'next' pointer as we traverse the list.
We use three pointers to keep track of the previous node, current node, and next node.

### Algorithm:
1. Initialize prev = None (this will become the new head)
2. Initialize current = head
3. While current is not None:
   - Save next node: next_node = current.next
   - Reverse the link: current.next = prev
   - Move pointers forward: prev = current, current = next_node
4. Return prev (new head of reversed list)

### Visualization:
Original: 1 -> 2 -> 3 -> None
After:    None <- 1 <- 2 <- 3

### Time Complexity: O(n) - visit each node once
### Space Complexity: O(1) - only use three pointers
""",
        "code": """def reverseList(head):
    prev = None
    current = head
    
    while current:
        # Save next node before we change the link
        next_node = current.next
        
        # Reverse the link
        current.next = prev
        
        # Move pointers forward
        prev = current
        current = next_node
    
    return prev  # New head

# Example: 1 -> 2 -> 3 -> None
# Step 1: prev=None, curr=1, next=2
#         1.next = None, prev=1, curr=2
# Step 2: prev=1, curr=2, next=3
#         2.next = 1, prev=2, curr=3
# Step 3: prev=2, curr=3, next=None
#         3.next = 2, prev=3, curr=None
# Result: None <- 1 <- 2 <- 3 (return 3)
""",
        "example": """
Example: 1 -> 2 -> 3 -> None

Initial: prev=None, current=1

Step 1:
  next_node = 2
  1.next = None
  prev = 1, current = 2
  Result so far: None <- 1    2 -> 3 -> None

Step 2:
  next_node = 3
  2.next = 1
  prev = 2, current = 3
  Result so far: None <- 1 <- 2    3 -> None

Step 3:
  next_node = None
  3.next = 2
  prev = 3, current = None
  Result: None <- 1 <- 2 <- 3

Return prev (which is 3, the new head)
"""
    },
    
    "valid-parentheses": {
        "title": "Valid Parentheses",
        "approach": "Stack",
        "explanation": """
## Approach: Stack for Matching Pairs

Use a stack to keep track of opening brackets. When we see a closing bracket, 
check if it matches the most recent opening bracket (top of stack).

### Algorithm:
1. Create an empty stack
2. Create a mapping of closing to opening brackets
3. For each character:
   - If it's an opening bracket: push to stack
   - If it's a closing bracket:
     * Check if stack is empty (no matching opening) -> invalid
     * Pop from stack and check if it matches -> if not, invalid
4. After processing all characters, stack should be empty

### Time Complexity: O(n) - process each character once
### Space Complexity: O(n) - stack can hold up to n/2 brackets
""",
        "code": """def isValid(s):
    stack = []
    # Map closing brackets to their opening counterparts
    closing_to_opening = {')': '(', '}': '{', ']': '['}
    
    for char in s:
        if char in closing_to_opening:
            # It's a closing bracket
            if not stack or stack[-1] != closing_to_opening[char]:
                return False
            stack.pop()
        else:
            # It's an opening bracket
            stack.append(char)
    
    # Valid only if all brackets were matched (stack is empty)
    return len(stack) == 0

# Example: "({[]})"
# Step 1: '(' -> stack = ['(']
# Step 2: '{' -> stack = ['(', '{']
# Step 3: '[' -> stack = ['(', '{', '[']
# Step 4: ']' -> matches '[', stack = ['(', '{']
# Step 5: '}' -> matches '{', stack = ['(']
# Step 6: ')' -> matches '(', stack = []
# Result: True ✓
""",
        "example": """
Example: s = "({[]})"

Step 1: char='(' (opening)
  stack = ['(']

Step 2: char='{' (opening)
  stack = ['(', '{']

Step 3: char='[' (opening)
  stack = ['(', '{', '[']

Step 4: char=']' (closing)
  Top of stack is '[' -> matches!
  stack = ['(', '{']

Step 5: char='}' (closing)
  Top of stack is '{' -> matches!
  stack = ['(']

Step 6: char=')' (closing)
  Top of stack is '(' -> matches!
  stack = []

Stack is empty -> Valid! ✓
"""
    },
    
    "best-time-to-buy-and-sell-stock": {
        "title": "Best Time to Buy and Sell Stock",
        "approach": "Single Pass with Min Tracking",
        "explanation": """
## Approach: Track Minimum Price and Maximum Profit

Keep track of the minimum price seen so far and the maximum profit we can make.
For each price, calculate profit if we sold today (current price - minimum price so far).

### Algorithm:
1. Initialize min_price = infinity, max_profit = 0
2. For each price:
   - Update min_price if current price is lower
   - Calculate profit = current price - min_price
   - Update max_profit if this profit is higher
3. Return max_profit

### Key Insight:
We want to buy at the lowest price and sell at the highest price AFTER that.
By tracking the minimum price so far, we ensure we're always buying before selling.

### Time Complexity: O(n) - single pass
### Space Complexity: O(1) - only two variables
""",
        "code": """def maxProfit(prices):
    if not prices:
        return 0
    
    min_price = float('inf')
    max_profit = 0
    
    for price in prices:
        # Update minimum price seen so far
        min_price = min(min_price, price)
        
        # Calculate profit if we sold today
        profit = price - min_price
        
        # Update maximum profit
        max_profit = max(max_profit, profit)
    
    return max_profit

# Example: [7, 1, 5, 3, 6, 4]
# Day 0: price=7, min=7, profit=0, max=0
# Day 1: price=1, min=1, profit=0, max=0
# Day 2: price=5, min=1, profit=4, max=4
# Day 3: price=3, min=1, profit=2, max=4
# Day 4: price=6, min=1, profit=5, max=5
# Day 5: price=4, min=1, profit=3, max=5
# Result: 5 (buy at 1, sell at 6)
""",
        "example": """
Example: prices = [7, 1, 5, 3, 6, 4]

Day 0: price=7
  min_price = min(inf, 7) = 7
  profit = 7 - 7 = 0
  max_profit = 0

Day 1: price=1
  min_price = min(7, 1) = 1
  profit = 1 - 1 = 0
  max_profit = 0

Day 2: price=5
  min_price = min(1, 5) = 1
  profit = 5 - 1 = 4
  max_profit = 4

Day 3: price=3
  min_price = min(1, 3) = 1
  profit = 3 - 1 = 2
  max_profit = 4

Day 4: price=6
  min_price = min(1, 6) = 1
  profit = 6 - 1 = 5
  max_profit = 5 ✓

Day 5: price=4
  min_price = min(1, 4) = 1
  profit = 4 - 1 = 3
  max_profit = 5

Best strategy: Buy at day 1 (price=1), sell at day 4 (price=6), profit=5
"""
    }
}


def get_fallback_solution(problem_slug: str) -> dict:
    """
    Get a fallback solution for common problems.
    
    Args:
        problem_slug: The problem's title slug (e.g., "two-sum")
    
    Returns:
        dict with 'title', 'content' keys, or None if not found
    """
    solution = COMMON_SOLUTIONS.get(problem_slug)
    
    if not solution:
        return None
    
    # Format the solution content
    content = f"""# {solution['title']} - Solution

{solution['explanation']}

## Python Implementation:

```python
{solution['code']}
```

## Example Walkthrough:

{solution['example']}

---

**Note:** This is a common solution pattern. The actual LeetCode editorial may have additional approaches or optimizations.
"""
    
    return {
        "title": solution["title"],
        "content": content,
        "approach": solution["approach"]
    }

