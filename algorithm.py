from collections import deque
import heapq
from grid_elements import spawn_dynamic

def reconstruct_path(node):
    path = []
    while node:
        path.append(node)
        node = node.parent
    return path[::-1]

def bfs(start, target, grid, draw):
    queue = deque([start])
    visited = {start}
    while queue:
        curr = queue.popleft()
        if curr == target: return reconstruct_path(curr)
        for n in curr.get_neighbors(grid):
            if n not in visited:
                n.parent = curr
                visited.add(n)
                queue.append(n)
                draw(n, "FRONTIER", len(queue), len(visited))
        draw(curr, "EXPLORED", len(queue), len(visited))
        spawn_dynamic(grid)
    return None

def dfs(start, target, grid, draw):
    stack = [start]
    visited = {start}
    while stack:
        curr = stack.pop()
        if curr == target: return reconstruct_path(curr)
        for n in curr.get_neighbors(grid):
            if n not in visited:
                n.parent = curr
                visited.add(n)
                stack.append(n)
                draw(n, "FRONTIER", len(stack), len(visited))
        draw(curr, "EXPLORED", len(stack), len(visited))
        spawn_dynamic(grid)
    return None

def ucs(start, target, grid, draw):
    pq = [(0, start)]
    start.cost = 0
    visited = set()
    while pq:
        cost, curr = heapq.heappop(pq)
        if curr in visited: continue
        visited.add(curr)
        if curr == target: return reconstruct_path(curr)
        for n in curr.get_neighbors(grid):
            new_cost = cost + 1
            if new_cost < n.cost:
                n.cost = new_cost
                n.parent = curr
                heapq.heappush(pq, (new_cost, n))
                draw(n, "FRONTIER", len(pq), len(visited))
        draw(curr, "EXPLORED", len(pq), len(visited))
    return None

def dls(start, target, limit, grid, draw, depth=0, visited=None):
    if visited is None: visited = set()
    if start == target: return reconstruct_path(start)
    if depth >= limit: return None
    visited.add(start)
    draw(start, "EXPLORED", 0, len(visited))
    for n in start.get_neighbors(grid):
        n.parent = start
        res = dls(n, target, limit, grid, draw, depth + 1, visited)
        if res: return res
    return None

def iddfs(start, target, grid, draw):
    for limit in range(1, 50):
        for row in grid:
            for node in row: node.reset()
        res = dls(start, target, limit, grid, draw)
        if res: return res
    return None

def bidirectional(start, target, grid, draw):
    f_q, b_q = deque([start]), deque([target])
    f_vis, b_vis = {start: None}, {target: None}
    while f_q and b_q:
        c_f = f_q.popleft()
        for n in c_f.get_neighbors(grid):
            if n in b_vis:
                p1 = reconstruct_path(c_f)
                p2 = []
                curr = n
                while curr: p2.append(curr); curr = b_vis[curr]
                return p1 + p2
            if n not in f_vis:
                f_vis[n] = c_f; f_q.append(n); draw(n, "FRONTIER", len(f_q)+len(b_q), len(f_vis)+len(b_vis))
        c_b = b_q.popleft()
        for n in c_b.get_neighbors(grid):
            if n in f_vis:
                p1 = reconstruct_path(f_vis[n])
                p2 = []
                curr = c_b
                while curr: p2.append(curr); curr = b_vis[curr]
                return p1 + p2
            if n not in b_vis:
                b_vis[n] = c_b; b_q.append(n); draw(n, "FRONTIER", len(f_q)+len(b_q), len(f_vis)+len(b_vis))
    return None