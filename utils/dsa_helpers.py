# DSA Helper Functions
# This file will contain implementations of DSA concepts used in the project

# Trie for keyword search
class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.data = []

class Trie:
    def __init__(self):
        self.root = TrieNode()
    
    def insert(self, word, data):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.data.append(data)
    
    def search(self, word):
        node = self.root
        for char in word.lower():
            if char not in node.children:
                return []
            node = node.children[char]
        return node.data if node.is_end else []
    
    def starts_with(self, prefix):
        results = []
        node = self.root
        for char in prefix.lower():
            if char not in node.children:
                return results
            node = node.children[char]
        
        def dfs(n, prefix):
            if n.is_end:
                results.extend(n.data)
            for char, child in n.children.items():
                dfs(child, prefix + char)
        
        dfs(node, prefix)
        return results

# Priority Queue for flashcard review scheduling
import heapq
from datetime import datetime

class PriorityQueue:
    def __init__(self):
        self.heap = []
        self.count = 0
    
    def push(self, item, priority):
        heapq.heappush(self.heap, (priority, self.count, item))
        self.count += 1
    
    def pop(self):
        if self.heap:
            return heapq.heappop(self.heap)[2]
        return None
    
    def peek(self):
        if self.heap:
            return self.heap[0][2]
        return None
    
    def is_empty(self):
        return len(self.heap) == 0
    
    
    def size(self):
        return len(self.heap)

# Dynamic Programming for Study Plan Optimization
# Distribute study topics across days to maximize coverage without burnout
def optimize_study_schedule(days_available, topics, max_hours_per_day=4):
    """
    DP Approach: knapsack-style distribution
    days_available: int (number of days until exam)
    topics: list of dicts {'name': str, 'weight': int(hours_needed)}
    max_hours_per_day: int
    """
    schedule = [[] for _ in range(days_available)]
    daily_hours = [0] * days_available
    
    # Sort topics by weight (heavier topics first) - Greedy approach for initial sort
    sorted_topics = sorted(topics, key=lambda x: x['weight'], reverse=True)
    
    for topic in sorted_topics:
        # Find the day with the most remaining capacity (Greedy fit)
        # This is a simplified bin packing heuristic which works well for this use case
        best_day = -1
        min_load = float('inf')
        
        for i in range(days_available):
            if daily_hours[i] + topic['weight'] <= max_hours_per_day:
                # If it fits, prefer the day with least current load to balance
                if daily_hours[i] < min_load:
                    min_load = daily_hours[i]
                    best_day = i
        
        if best_day != -1:
            schedule[best_day].append(topic)
            daily_hours[best_day] += topic['weight']
        else:
            # If it doesn't fit anywhere perfectly, split it (if allowed) or force add to least loaded day
            # Here we force add to least loaded day
            least_loaded_day = daily_hours.index(min(daily_hours))
            schedule[least_loaded_day].append(topic)
            daily_hours[least_loaded_day] += topic['weight']
            
    return schedule


