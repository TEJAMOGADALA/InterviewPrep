"""Curated Problem Bank.

Internal catalog of coding problems mapped by pattern. Each problem has a
LeetCode URL (linked externally — we do NOT scrape). Mission Engine V2 picks
from this catalog based on topic/pattern and user history.
"""

# Pattern → domain mapping helps drill-down knowledge tree
PATTERN_TO_DOMAIN = {
    "arrays":             ("dsa", "Arrays"),
    "hashing":            ("dsa", "Hashing"),
    "sliding_window":     ("dsa", "Sliding Window"),
    "two_pointers":       ("dsa", "Two Pointers"),
    "binary_search":      ("dsa", "Binary Search"),
    "stack":              ("dsa", "Stack"),
    "linked_list":        ("dsa", "Linked List"),
    "trees":              ("dsa", "Trees & Recursion"),
    "graphs":             ("dsa", "Graphs"),
    "heap":               ("dsa", "Heaps & Priority Queues"),
    "dp":                 ("dsa", "Dynamic Programming"),
    "backtracking":       ("dsa", "Backtracking"),
    "greedy":             ("dsa", "Greedy"),
    "strings":            ("dsa", "Strings"),
    "bit_manipulation":   ("dsa", "Bit Manipulation"),
    "intervals":          ("dsa", "Intervals"),
}

# Prerequisite knowledge — used for root-cause analysis. When a user fails a
# pattern, we surface these prerequisites as revision blocks.
PATTERN_PREREQUISITES = {
    "heap":            [("java", "Comparator & Comparable"), ("dsa", "Trees & Recursion")],
    "sliding_window":  [("dsa", "Two Pointers"), ("dsa", "Hashing")],
    "graphs":          [("dsa", "BFS & DFS"), ("dsa", "Stack")],
    "dp":              [("dsa", "Recursion"), ("dsa", "Arrays")],
    "backtracking":    [("dsa", "Recursion")],
    "trees":           [("dsa", "Recursion")],
    "binary_search":   [("dsa", "Arrays")],
    "intervals":       [("dsa", "Sorting")],
    "linked_list":     [("dsa", "Two Pointers")],
    "strings":         [("dsa", "Hashing")],
}


# --- Curated problem list ---
# Fields: id (stable slug), title, difficulty, pattern, estimated_minutes, leetcode_url, tags
PROBLEMS = [
    # ================= Sliding Window =================
    {"id": "lc-3",   "title": "Longest Substring Without Repeating Characters", "difficulty": "medium", "pattern": "sliding_window", "estimated_minutes": 25, "leetcode_url": "https://leetcode.com/problems/longest-substring-without-repeating-characters/", "tags": ["hashing", "string"]},
    {"id": "lc-76",  "title": "Minimum Window Substring", "difficulty": "hard", "pattern": "sliding_window", "estimated_minutes": 40, "leetcode_url": "https://leetcode.com/problems/minimum-window-substring/", "tags": ["hashing", "string"]},
    {"id": "lc-424", "title": "Longest Repeating Character Replacement", "difficulty": "medium", "pattern": "sliding_window", "estimated_minutes": 30, "leetcode_url": "https://leetcode.com/problems/longest-repeating-character-replacement/", "tags": ["hashing"]},
    {"id": "lc-567", "title": "Permutation in String", "difficulty": "medium", "pattern": "sliding_window", "estimated_minutes": 25, "leetcode_url": "https://leetcode.com/problems/permutation-in-string/", "tags": ["hashing"]},
    {"id": "lc-438", "title": "Find All Anagrams in a String", "difficulty": "medium", "pattern": "sliding_window", "estimated_minutes": 25, "leetcode_url": "https://leetcode.com/problems/find-all-anagrams-in-a-string/", "tags": ["hashing"]},
    {"id": "lc-209", "title": "Minimum Size Subarray Sum", "difficulty": "medium", "pattern": "sliding_window", "estimated_minutes": 20, "leetcode_url": "https://leetcode.com/problems/minimum-size-subarray-sum/", "tags": ["arrays"]},
    {"id": "lc-1004","title": "Max Consecutive Ones III", "difficulty": "medium", "pattern": "sliding_window", "estimated_minutes": 25, "leetcode_url": "https://leetcode.com/problems/max-consecutive-ones-iii/", "tags": ["arrays"]},
    {"id": "lc-239", "title": "Sliding Window Maximum", "difficulty": "hard", "pattern": "sliding_window", "estimated_minutes": 40, "leetcode_url": "https://leetcode.com/problems/sliding-window-maximum/", "tags": ["heap", "deque"]},
    {"id": "lc-643", "title": "Maximum Average Subarray I", "difficulty": "easy", "pattern": "sliding_window", "estimated_minutes": 15, "leetcode_url": "https://leetcode.com/problems/maximum-average-subarray-i/", "tags": []},

    # ================= Two Pointers =================
    {"id": "lc-1",   "title": "Two Sum", "difficulty": "easy", "pattern": "hashing", "estimated_minutes": 15, "leetcode_url": "https://leetcode.com/problems/two-sum/", "tags": []},
    {"id": "lc-167", "title": "Two Sum II - Sorted", "difficulty": "medium", "pattern": "two_pointers", "estimated_minutes": 15, "leetcode_url": "https://leetcode.com/problems/two-sum-ii-input-array-is-sorted/", "tags": []},
    {"id": "lc-15",  "title": "3Sum", "difficulty": "medium", "pattern": "two_pointers", "estimated_minutes": 30, "leetcode_url": "https://leetcode.com/problems/3sum/", "tags": ["sorting"]},
    {"id": "lc-11",  "title": "Container With Most Water", "difficulty": "medium", "pattern": "two_pointers", "estimated_minutes": 25, "leetcode_url": "https://leetcode.com/problems/container-with-most-water/", "tags": []},
    {"id": "lc-42",  "title": "Trapping Rain Water", "difficulty": "hard", "pattern": "two_pointers", "estimated_minutes": 40, "leetcode_url": "https://leetcode.com/problems/trapping-rain-water/", "tags": ["stack", "dp"]},
    {"id": "lc-125", "title": "Valid Palindrome", "difficulty": "easy", "pattern": "two_pointers", "estimated_minutes": 15, "leetcode_url": "https://leetcode.com/problems/valid-palindrome/", "tags": ["string"]},
    {"id": "lc-680", "title": "Valid Palindrome II", "difficulty": "easy", "pattern": "two_pointers", "estimated_minutes": 20, "leetcode_url": "https://leetcode.com/problems/valid-palindrome-ii/", "tags": []},

    # ================= Arrays =================
    {"id": "lc-53",  "title": "Maximum Subarray (Kadane)", "difficulty": "medium", "pattern": "arrays", "estimated_minutes": 20, "leetcode_url": "https://leetcode.com/problems/maximum-subarray/", "tags": ["dp"]},
    {"id": "lc-121", "title": "Best Time to Buy and Sell Stock", "difficulty": "easy", "pattern": "arrays", "estimated_minutes": 15, "leetcode_url": "https://leetcode.com/problems/best-time-to-buy-and-sell-stock/", "tags": []},
    {"id": "lc-238", "title": "Product of Array Except Self", "difficulty": "medium", "pattern": "arrays", "estimated_minutes": 25, "leetcode_url": "https://leetcode.com/problems/product-of-array-except-self/", "tags": []},
    {"id": "lc-152", "title": "Maximum Product Subarray", "difficulty": "medium", "pattern": "arrays", "estimated_minutes": 25, "leetcode_url": "https://leetcode.com/problems/maximum-product-subarray/", "tags": ["dp"]},
    {"id": "lc-189", "title": "Rotate Array", "difficulty": "medium", "pattern": "arrays", "estimated_minutes": 20, "leetcode_url": "https://leetcode.com/problems/rotate-array/", "tags": []},

    # ================= Hashing =================
    {"id": "lc-217", "title": "Contains Duplicate", "difficulty": "easy", "pattern": "hashing", "estimated_minutes": 10, "leetcode_url": "https://leetcode.com/problems/contains-duplicate/", "tags": []},
    {"id": "lc-49",  "title": "Group Anagrams", "difficulty": "medium", "pattern": "hashing", "estimated_minutes": 25, "leetcode_url": "https://leetcode.com/problems/group-anagrams/", "tags": ["string"]},
    {"id": "lc-347", "title": "Top K Frequent Elements", "difficulty": "medium", "pattern": "hashing", "estimated_minutes": 25, "leetcode_url": "https://leetcode.com/problems/top-k-frequent-elements/", "tags": ["heap"]},
    {"id": "lc-128", "title": "Longest Consecutive Sequence", "difficulty": "medium", "pattern": "hashing", "estimated_minutes": 30, "leetcode_url": "https://leetcode.com/problems/longest-consecutive-sequence/", "tags": []},

    # ================= Binary Search =================
    {"id": "lc-704", "title": "Binary Search", "difficulty": "easy", "pattern": "binary_search", "estimated_minutes": 15, "leetcode_url": "https://leetcode.com/problems/binary-search/", "tags": []},
    {"id": "lc-33",  "title": "Search in Rotated Sorted Array", "difficulty": "medium", "pattern": "binary_search", "estimated_minutes": 30, "leetcode_url": "https://leetcode.com/problems/search-in-rotated-sorted-array/", "tags": []},
    {"id": "lc-153", "title": "Find Minimum in Rotated Sorted Array", "difficulty": "medium", "pattern": "binary_search", "estimated_minutes": 25, "leetcode_url": "https://leetcode.com/problems/find-minimum-in-rotated-sorted-array/", "tags": []},
    {"id": "lc-410", "title": "Split Array Largest Sum", "difficulty": "hard", "pattern": "binary_search", "estimated_minutes": 40, "leetcode_url": "https://leetcode.com/problems/split-array-largest-sum/", "tags": ["dp"]},
    {"id": "lc-875", "title": "Koko Eating Bananas", "difficulty": "medium", "pattern": "binary_search", "estimated_minutes": 25, "leetcode_url": "https://leetcode.com/problems/koko-eating-bananas/", "tags": []},
    {"id": "lc-4",   "title": "Median of Two Sorted Arrays", "difficulty": "hard", "pattern": "binary_search", "estimated_minutes": 45, "leetcode_url": "https://leetcode.com/problems/median-of-two-sorted-arrays/", "tags": []},

    # ================= Stack =================
    {"id": "lc-20",  "title": "Valid Parentheses", "difficulty": "easy", "pattern": "stack", "estimated_minutes": 15, "leetcode_url": "https://leetcode.com/problems/valid-parentheses/", "tags": []},
    {"id": "lc-155", "title": "Min Stack", "difficulty": "medium", "pattern": "stack", "estimated_minutes": 25, "leetcode_url": "https://leetcode.com/problems/min-stack/", "tags": []},
    {"id": "lc-739", "title": "Daily Temperatures", "difficulty": "medium", "pattern": "stack", "estimated_minutes": 25, "leetcode_url": "https://leetcode.com/problems/daily-temperatures/", "tags": ["monotonic"]},
    {"id": "lc-853", "title": "Car Fleet", "difficulty": "medium", "pattern": "stack", "estimated_minutes": 30, "leetcode_url": "https://leetcode.com/problems/car-fleet/", "tags": []},
    {"id": "lc-84",  "title": "Largest Rectangle in Histogram", "difficulty": "hard", "pattern": "stack", "estimated_minutes": 40, "leetcode_url": "https://leetcode.com/problems/largest-rectangle-in-histogram/", "tags": ["monotonic"]},

    # ================= Linked List =================
    {"id": "lc-206", "title": "Reverse Linked List", "difficulty": "easy", "pattern": "linked_list", "estimated_minutes": 15, "leetcode_url": "https://leetcode.com/problems/reverse-linked-list/", "tags": []},
    {"id": "lc-21",  "title": "Merge Two Sorted Lists", "difficulty": "easy", "pattern": "linked_list", "estimated_minutes": 15, "leetcode_url": "https://leetcode.com/problems/merge-two-sorted-lists/", "tags": []},
    {"id": "lc-141", "title": "Linked List Cycle", "difficulty": "easy", "pattern": "linked_list", "estimated_minutes": 15, "leetcode_url": "https://leetcode.com/problems/linked-list-cycle/", "tags": ["two_pointers"]},
    {"id": "lc-143", "title": "Reorder List", "difficulty": "medium", "pattern": "linked_list", "estimated_minutes": 30, "leetcode_url": "https://leetcode.com/problems/reorder-list/", "tags": []},
    {"id": "lc-19",  "title": "Remove Nth Node From End", "difficulty": "medium", "pattern": "linked_list", "estimated_minutes": 20, "leetcode_url": "https://leetcode.com/problems/remove-nth-node-from-end-of-list/", "tags": ["two_pointers"]},
    {"id": "lc-146", "title": "LRU Cache", "difficulty": "medium", "pattern": "linked_list", "estimated_minutes": 40, "leetcode_url": "https://leetcode.com/problems/lru-cache/", "tags": ["hashing", "design"]},
    {"id": "lc-23",  "title": "Merge k Sorted Lists", "difficulty": "hard", "pattern": "linked_list", "estimated_minutes": 40, "leetcode_url": "https://leetcode.com/problems/merge-k-sorted-lists/", "tags": ["heap"]},

    # ================= Trees =================
    {"id": "lc-104", "title": "Maximum Depth of Binary Tree", "difficulty": "easy", "pattern": "trees", "estimated_minutes": 15, "leetcode_url": "https://leetcode.com/problems/maximum-depth-of-binary-tree/", "tags": ["recursion"]},
    {"id": "lc-100", "title": "Same Tree", "difficulty": "easy", "pattern": "trees", "estimated_minutes": 15, "leetcode_url": "https://leetcode.com/problems/same-tree/", "tags": []},
    {"id": "lc-226", "title": "Invert Binary Tree", "difficulty": "easy", "pattern": "trees", "estimated_minutes": 15, "leetcode_url": "https://leetcode.com/problems/invert-binary-tree/", "tags": []},
    {"id": "lc-102", "title": "Binary Tree Level Order Traversal", "difficulty": "medium", "pattern": "trees", "estimated_minutes": 25, "leetcode_url": "https://leetcode.com/problems/binary-tree-level-order-traversal/", "tags": ["bfs"]},
    {"id": "lc-98",  "title": "Validate Binary Search Tree", "difficulty": "medium", "pattern": "trees", "estimated_minutes": 30, "leetcode_url": "https://leetcode.com/problems/validate-binary-search-tree/", "tags": []},
    {"id": "lc-230", "title": "Kth Smallest Element in a BST", "difficulty": "medium", "pattern": "trees", "estimated_minutes": 25, "leetcode_url": "https://leetcode.com/problems/kth-smallest-element-in-a-bst/", "tags": []},
    {"id": "lc-105", "title": "Construct Tree from Preorder + Inorder", "difficulty": "medium", "pattern": "trees", "estimated_minutes": 35, "leetcode_url": "https://leetcode.com/problems/construct-binary-tree-from-preorder-and-inorder-traversal/", "tags": ["recursion"]},
    {"id": "lc-124", "title": "Binary Tree Maximum Path Sum", "difficulty": "hard", "pattern": "trees", "estimated_minutes": 45, "leetcode_url": "https://leetcode.com/problems/binary-tree-maximum-path-sum/", "tags": ["dp-on-tree"]},

    # ================= Graphs =================
    {"id": "lc-200", "title": "Number of Islands", "difficulty": "medium", "pattern": "graphs", "estimated_minutes": 25, "leetcode_url": "https://leetcode.com/problems/number-of-islands/", "tags": ["bfs", "dfs"]},
    {"id": "lc-133", "title": "Clone Graph", "difficulty": "medium", "pattern": "graphs", "estimated_minutes": 30, "leetcode_url": "https://leetcode.com/problems/clone-graph/", "tags": ["dfs", "bfs"]},
    {"id": "lc-207", "title": "Course Schedule", "difficulty": "medium", "pattern": "graphs", "estimated_minutes": 30, "leetcode_url": "https://leetcode.com/problems/course-schedule/", "tags": ["topological"]},
    {"id": "lc-417", "title": "Pacific Atlantic Water Flow", "difficulty": "medium", "pattern": "graphs", "estimated_minutes": 35, "leetcode_url": "https://leetcode.com/problems/pacific-atlantic-water-flow/", "tags": ["dfs"]},
    {"id": "lc-127", "title": "Word Ladder", "difficulty": "hard", "pattern": "graphs", "estimated_minutes": 45, "leetcode_url": "https://leetcode.com/problems/word-ladder/", "tags": ["bfs"]},
    {"id": "lc-994", "title": "Rotting Oranges", "difficulty": "medium", "pattern": "graphs", "estimated_minutes": 25, "leetcode_url": "https://leetcode.com/problems/rotting-oranges/", "tags": ["bfs"]},
    {"id": "lc-743", "title": "Network Delay Time", "difficulty": "medium", "pattern": "graphs", "estimated_minutes": 35, "leetcode_url": "https://leetcode.com/problems/network-delay-time/", "tags": ["dijkstra", "heap"]},

    # ================= Heap =================
    {"id": "lc-703", "title": "Kth Largest Element in a Stream", "difficulty": "easy", "pattern": "heap", "estimated_minutes": 20, "leetcode_url": "https://leetcode.com/problems/kth-largest-element-in-a-stream/", "tags": ["design"]},
    {"id": "lc-215", "title": "Kth Largest Element in an Array", "difficulty": "medium", "pattern": "heap", "estimated_minutes": 25, "leetcode_url": "https://leetcode.com/problems/kth-largest-element-in-an-array/", "tags": ["quickselect"]},
    {"id": "lc-1046","title": "Last Stone Weight", "difficulty": "easy", "pattern": "heap", "estimated_minutes": 15, "leetcode_url": "https://leetcode.com/problems/last-stone-weight/", "tags": []},
    {"id": "lc-973", "title": "K Closest Points to Origin", "difficulty": "medium", "pattern": "heap", "estimated_minutes": 25, "leetcode_url": "https://leetcode.com/problems/k-closest-points-to-origin/", "tags": []},
    {"id": "lc-621", "title": "Task Scheduler", "difficulty": "medium", "pattern": "heap", "estimated_minutes": 30, "leetcode_url": "https://leetcode.com/problems/task-scheduler/", "tags": ["greedy"]},
    {"id": "lc-295", "title": "Find Median from Data Stream", "difficulty": "hard", "pattern": "heap", "estimated_minutes": 40, "leetcode_url": "https://leetcode.com/problems/find-median-from-data-stream/", "tags": ["two_heaps", "design"]},
    {"id": "lc-355", "title": "Design Twitter", "difficulty": "medium", "pattern": "heap", "estimated_minutes": 45, "leetcode_url": "https://leetcode.com/problems/design-twitter/", "tags": ["design"]},

    # ================= Dynamic Programming =================
    {"id": "lc-70",  "title": "Climbing Stairs", "difficulty": "easy", "pattern": "dp", "estimated_minutes": 15, "leetcode_url": "https://leetcode.com/problems/climbing-stairs/", "tags": ["1d"]},
    {"id": "lc-198", "title": "House Robber", "difficulty": "medium", "pattern": "dp", "estimated_minutes": 20, "leetcode_url": "https://leetcode.com/problems/house-robber/", "tags": ["1d"]},
    {"id": "lc-213", "title": "House Robber II", "difficulty": "medium", "pattern": "dp", "estimated_minutes": 25, "leetcode_url": "https://leetcode.com/problems/house-robber-ii/", "tags": ["1d"]},
    {"id": "lc-322", "title": "Coin Change", "difficulty": "medium", "pattern": "dp", "estimated_minutes": 30, "leetcode_url": "https://leetcode.com/problems/coin-change/", "tags": ["unbounded"]},
    {"id": "lc-300", "title": "Longest Increasing Subsequence", "difficulty": "medium", "pattern": "dp", "estimated_minutes": 30, "leetcode_url": "https://leetcode.com/problems/longest-increasing-subsequence/", "tags": ["binary_search"]},
    {"id": "lc-1143","title": "Longest Common Subsequence", "difficulty": "medium", "pattern": "dp", "estimated_minutes": 30, "leetcode_url": "https://leetcode.com/problems/longest-common-subsequence/", "tags": ["2d"]},
    {"id": "lc-72",  "title": "Edit Distance", "difficulty": "hard", "pattern": "dp", "estimated_minutes": 40, "leetcode_url": "https://leetcode.com/problems/edit-distance/", "tags": ["2d"]},
    {"id": "lc-518", "title": "Coin Change II", "difficulty": "medium", "pattern": "dp", "estimated_minutes": 30, "leetcode_url": "https://leetcode.com/problems/coin-change-ii/", "tags": ["unbounded"]},

    # ================= Backtracking =================
    {"id": "lc-78",  "title": "Subsets", "difficulty": "medium", "pattern": "backtracking", "estimated_minutes": 25, "leetcode_url": "https://leetcode.com/problems/subsets/", "tags": []},
    {"id": "lc-46",  "title": "Permutations", "difficulty": "medium", "pattern": "backtracking", "estimated_minutes": 25, "leetcode_url": "https://leetcode.com/problems/permutations/", "tags": []},
    {"id": "lc-39",  "title": "Combination Sum", "difficulty": "medium", "pattern": "backtracking", "estimated_minutes": 30, "leetcode_url": "https://leetcode.com/problems/combination-sum/", "tags": []},
    {"id": "lc-51",  "title": "N-Queens", "difficulty": "hard", "pattern": "backtracking", "estimated_minutes": 45, "leetcode_url": "https://leetcode.com/problems/n-queens/", "tags": []},
    {"id": "lc-79",  "title": "Word Search", "difficulty": "medium", "pattern": "backtracking", "estimated_minutes": 30, "leetcode_url": "https://leetcode.com/problems/word-search/", "tags": ["dfs"]},

    # ================= Greedy =================
    {"id": "lc-55",  "title": "Jump Game", "difficulty": "medium", "pattern": "greedy", "estimated_minutes": 25, "leetcode_url": "https://leetcode.com/problems/jump-game/", "tags": []},
    {"id": "lc-45",  "title": "Jump Game II", "difficulty": "medium", "pattern": "greedy", "estimated_minutes": 30, "leetcode_url": "https://leetcode.com/problems/jump-game-ii/", "tags": []},
    {"id": "lc-134", "title": "Gas Station", "difficulty": "medium", "pattern": "greedy", "estimated_minutes": 30, "leetcode_url": "https://leetcode.com/problems/gas-station/", "tags": []},

    # ================= Intervals =================
    {"id": "lc-56",  "title": "Merge Intervals", "difficulty": "medium", "pattern": "intervals", "estimated_minutes": 25, "leetcode_url": "https://leetcode.com/problems/merge-intervals/", "tags": ["sorting"]},
    {"id": "lc-57",  "title": "Insert Interval", "difficulty": "medium", "pattern": "intervals", "estimated_minutes": 30, "leetcode_url": "https://leetcode.com/problems/insert-interval/", "tags": []},
    {"id": "lc-435", "title": "Non-Overlapping Intervals", "difficulty": "medium", "pattern": "intervals", "estimated_minutes": 30, "leetcode_url": "https://leetcode.com/problems/non-overlapping-intervals/", "tags": ["greedy"]},
    {"id": "lc-252", "title": "Meeting Rooms", "difficulty": "easy", "pattern": "intervals", "estimated_minutes": 15, "leetcode_url": "https://leetcode.com/problems/meeting-rooms/", "tags": []},
    {"id": "lc-253", "title": "Meeting Rooms II", "difficulty": "medium", "pattern": "intervals", "estimated_minutes": 30, "leetcode_url": "https://leetcode.com/problems/meeting-rooms-ii/", "tags": ["heap"]},

    # ================= Strings =================
    {"id": "lc-242", "title": "Valid Anagram", "difficulty": "easy", "pattern": "strings", "estimated_minutes": 15, "leetcode_url": "https://leetcode.com/problems/valid-anagram/", "tags": []},
    {"id": "lc-5",   "title": "Longest Palindromic Substring", "difficulty": "medium", "pattern": "strings", "estimated_minutes": 30, "leetcode_url": "https://leetcode.com/problems/longest-palindromic-substring/", "tags": ["dp"]},
    {"id": "lc-647", "title": "Palindromic Substrings", "difficulty": "medium", "pattern": "strings", "estimated_minutes": 30, "leetcode_url": "https://leetcode.com/problems/palindromic-substrings/", "tags": ["dp"]},
    {"id": "lc-14",  "title": "Longest Common Prefix", "difficulty": "easy", "pattern": "strings", "estimated_minutes": 15, "leetcode_url": "https://leetcode.com/problems/longest-common-prefix/", "tags": []},

    # ================= Bit Manipulation =================
    {"id": "lc-136", "title": "Single Number", "difficulty": "easy", "pattern": "bit_manipulation", "estimated_minutes": 15, "leetcode_url": "https://leetcode.com/problems/single-number/", "tags": ["xor"]},
    {"id": "lc-191", "title": "Number of 1 Bits", "difficulty": "easy", "pattern": "bit_manipulation", "estimated_minutes": 15, "leetcode_url": "https://leetcode.com/problems/number-of-1-bits/", "tags": []},
    {"id": "lc-338", "title": "Counting Bits", "difficulty": "easy", "pattern": "bit_manipulation", "estimated_minutes": 20, "leetcode_url": "https://leetcode.com/problems/counting-bits/", "tags": ["dp"]},
    {"id": "lc-190", "title": "Reverse Bits", "difficulty": "easy", "pattern": "bit_manipulation", "estimated_minutes": 15, "leetcode_url": "https://leetcode.com/problems/reverse-bits/", "tags": []},
]


def problem_by_id(pid: str):
    for p in PROBLEMS:
        if p["id"] == pid:
            return p
    return None


def problems_by_pattern(pattern: str):
    return [p for p in PROBLEMS if p["pattern"] == pattern]


def pattern_counts() -> dict:
    counts = {}
    for p in PROBLEMS:
        counts[p["pattern"]] = counts.get(p["pattern"], 0) + 1
    return counts


# Which pattern to pick from a subtopic string in mission engine.
SUBTOPIC_TO_PATTERN = {
    "Sliding Window":            "sliding_window",
    "Two Pointers":              "two_pointers",
    "Dynamic Programming":       "dp",
    "Trees & Recursion":         "trees",
    "Graphs · BFS & DFS":        "graphs",
    "Graphs":                    "graphs",
    "Heaps & Priority Queues":   "heap",
    "Backtracking":              "backtracking",
    "Binary Search":             "binary_search",
    "Arrays":                    "arrays",
    "Hashing":                   "hashing",
    "Stack":                     "stack",
    "Linked List":               "linked_list",
    "Intervals":                 "intervals",
    "Strings":                   "strings",
    "Bit Manipulation":          "bit_manipulation",
    "Greedy":                    "greedy",
}
