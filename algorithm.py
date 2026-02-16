from collections import deque
import heapq
import time
from grid_elements import spawn_dynamic

# Set a global timeout for searches (in seconds)
SEARCH_TIMEOUT = 10 

def reconstruct_path(node):
    """Rebuilds the path from target to start by following parents."""
    path = []
    while node:
        path.append(node)
        node = node.parent
    return path[::-1]

def bfs(start, target, grid, draw):
    """Breadth-First Search: Explores layer by layer."""
    start_time = time.time()
    queue = deque([start])
    visited = {start}
    
    while queue:
        # Check for Timeout or Break signal
        if time.time() - start_time > SEARCH_TIMEOUT:
            print("BFS: Search timed out!")
            return None
            
        curr = queue.popleft()
        if curr == target: return reconstruct_path(curr)
        
        for n in curr.get_neighbors(grid):
            if n not in visited:
                n.parent = curr
                visited.add(n)
                queue.append(n)
                # Signal check: if draw returns "BREAK", terminate search
                if draw(n, "FRONTIER", len(queue), len(visited)) == "BREAK":
                    return None
        
        if draw(curr, "EXPLORED", len(queue), len(visited)) == "BREAK":
            return None
            
        spawn_dynamic(grid)
    return None

def dfs(start, target, grid, draw):
    """Depth-First Search: Explores as deep as possible first."""
    start_time = time.time()
    stack = [start]
    visited = {start}
    
    while stack:
        if time.time() - start_time > SEARCH_TIMEOUT:
            print("DFS: Search timed out!")
            return None
            
        curr = stack.pop()
        if curr == target: return reconstruct_path(curr)
        
        for n in curr.get_neighbors(grid):
            if n not in visited:
                n.parent = curr
                visited.add(n)
                stack.append(n)
                if draw(n, "FRONTIER", len(stack), len(visited)) == "BREAK":
                    return None
        
        if draw(curr, "EXPLORED", len(stack), len(visited)) == "BREAK":
            return None
            
        spawn_dynamic(grid)
    return None

def ucs(start, target, grid, draw):
    """Uniform-Cost Search: Priority queue based on cumulative cost."""
    start_time = time.time()
    count = 0 
    pq = [(0, count, start)]
    start.cost = 0
    visited = set()
    
    while pq:
        if time.time() - start_time > SEARCH_TIMEOUT:
            print("UCS: Search timed out!")
            return None
            
        cost, _, curr = heapq.heappop(pq)
        if curr in visited: continue
        visited.add(curr)
        
        if curr == target: return reconstruct_path(curr)
        
        for n in curr.get_neighbors(grid):
            new_cost = cost + 1 
            if new_cost < n.cost:
                n.cost = new_cost
                n.parent = curr
                count += 1
                heapq.heappush(pq, (new_cost, count, n))
                if draw(n, "FRONTIER", len(pq), len(visited)) == "BREAK":
                    return None
        
        if draw(curr, "EXPLORED", len(pq), len(visited)) == "BREAK":
            return None
            
        spawn_dynamic(grid)
    return None

def dls(curr, target, limit, grid, draw, depth=0, visited=None, start_time=None):
    """Depth-Limited Search: Helper for IDDFS."""
    if visited is None: visited = set()
    
    # Check for Timeout in recursion
    if start_time and time.time() - start_time > SEARCH_TIMEOUT:
        return "TIMEOUT"
    
    if curr == target: return reconstruct_path(curr)
    if depth >= limit: return None
    
    visited.add(curr)
    
    # Check for Break signal in recursion
    if draw(curr, "EXPLORED", depth, len(visited)) == "BREAK":
        return "BREAK"
    
    for n in curr.get_neighbors(grid):
        if n not in visited:
            n.parent = curr
            res = dls(n, target, limit, grid, draw, depth + 1, visited, start_time)
            if res: return res
    return None

def iddfs(start, target, grid, draw):
    """Iterative Deepening DFS: Gradually increases DLS depth."""
    start_time = time.time()
    MAX_IDDFS_DEPTH = 300 
    
    for limit in range(1, MAX_IDDFS_DEPTH):
        if time.time() - start_time > SEARCH_TIMEOUT:
            print("IDDFS: Search timed out!")
            return None
            
        for row in grid:
            for node in row: node.reset()
        
        res = dls(start, target, limit, grid, draw, 0, set(), start_time)
        
        if res == "TIMEOUT" or res == "BREAK":
            return None
        if res:
            return res
        
    print("IDDFS: Max depth reached.")
    return None

def bidirectional(start, target, grid, draw):
    """Bidirectional Search: Searches from both start and target simultaneously."""
    start_time = time.time()
    f_q, b_q = deque([start]), deque([target])
    f_vis, b_vis = {start: None}, {target: None}
    
    while f_q and b_q:
        if time.time() - start_time > SEARCH_TIMEOUT:
            print("Bidirectional: Search timed out!")
            return None
            
        # Forward Step
        c_f = f_q.popleft()
        for n in c_f.get_neighbors(grid):
            if n in b_vis:
                p1 = reconstruct_path(c_f)
                p2 = []
                curr = n
                while curr: 
                    p2.append(curr)
                    curr = b_vis[curr]
                return p1 + p2
            if n not in f_vis:
                f_vis[n] = c_f
                f_q.append(n)
                if draw(n, "FRONTIER", len(f_q), len(f_vis)) == "BREAK":
                    return None
        
        # Backward Step
        c_b = b_q.popleft()
        for n in c_b.get_neighbors(grid):
            if n in f_vis:
                p1 = reconstruct_path(f_vis[n])
                p2 = []
                curr = c_b
                while curr: 
                    p2.append(curr)
                    curr = b_vis[curr]
                return p1 + p2
            if n not in b_vis:
                b_vis[n] = c_b
                b_q.append(n)
                if draw(n, "FRONTIER", len(b_q), len(b_vis)) == "BREAK":
                    return None
                    
        spawn_dynamic(grid)
    return None