P1, P2 = (1, 2)
DIRS = [(0, -1), (0, 1), (-1, 0), (1, 0)]
ROWS, COLS = (16, 24)
LEVELS = [{'walls': [], 'p1': (8, 3), 'p2': (8, 20), 'portals': {(3, 11): (12, 11), (12, 11): (3, 11)}, 'cores': [(8, 11)]}, {'walls': [(4, 6), (4, 7), (5, 6), (5, 7), (4, 16), (4, 17), (5, 16), (5, 17), (10, 6), (10, 7), (11, 6), (11, 7), (10, 16), (10, 17), (11, 16), (11, 17)], 'p1': (8, 2), 'p2': (8, 21), 'portals': {}, 'cores': [(8, 11), (2, 11), (14, 11)]}, {'walls': [(r, 11) for r in range(5, 12)] + [(8, c) for c in range(8, 15)], 'p1': (3, 3), 'p2': (13, 20), 'portals': {(1, 1): (14, 22), (14, 22): (1, 1)}, 'cores': [(3, 11), (13, 11)]}, {'walls': [(4, c) for c in range(0, 20)] + [(11, c) for c in range(4, 24)], 'p1': (2, 2), 'p2': (13, 21), 'portals': {(7, 0): (7, 23), (7, 23): (7, 0)}, 'cores': [(7, 11)]}, {'walls': [(r, c) for r in range(ROWS) for c in range(COLS) if r == c or (r + c == 23 and 3 < r < 12)], 'p1': (1, 11), 'p2': (14, 11), 'portals': {}, 'cores': [(4, 4), (11, 19)]}]

class TronState:

    def __init__(self, lvl=0):
        l = LEVELS[lvl]
        self.walls = set(l['walls'])
        self.static_walls = set(l['walls'])
        self.portals = l['portals']
        self.cores = set(l['cores'])
        self.p1, self.p2 = (l['p1'], l['p2'])
        self.d1, self.d2 = ((0, 1), (0, -1))
        self.s1, self.s2 = (0, 0)
        self.turn = P1
        self.walls.update([self.p1, self.p2])

    def get_moves(self, player):
        pos, d = (self.p1, self.d1) if player == P1 else (self.p2, self.d2)
        valid = []
        for dr, dc in DIRS:
            if dr == -d[0] and dc == -d[1]:
                continue
            nr, nc = ((pos[0] + dr) % ROWS, (pos[1] + dc) % COLS)
            if (nr, nc) in self.portals:
                pr, pc = self.portals[nr, nc]
                if (pr, pc) not in self.walls:
                    valid.append((dr, dc))
            elif (nr, nc) not in self.walls:
                valid.append((dr, dc))
        return valid

    def apply_move(self, m):
        ns = TronState()
        ns.walls = set(self.walls)
        ns.static_walls = self.static_walls
        ns.portals, ns.cores = (self.portals, set(self.cores))
        ns.p1, ns.p2 = (self.p1, self.p2)
        ns.d1, ns.d2 = (self.d1, self.d2)
        ns.s1, ns.s2, ns.turn = (self.s1, self.s2, self.turn)
        pos = ns.p1 if ns.turn == P1 else ns.p2
        nr, nc = ((pos[0] + m[0]) % ROWS, (pos[1] + m[1]) % COLS)
        if (nr, nc) in ns.portals:
            nr, nc = ns.portals[nr, nc]
        if (nr, nc) in ns.cores:
            ns.cores.remove((nr, nc))
            if ns.turn == P1:
                ns.s1 += 1
            else:
                ns.s2 += 1
        if ns.turn == P1:
            ns.p1, ns.d1, ns.turn = ((nr, nc), m, P2)
            ns.walls.add(ns.p1)
        else:
            ns.p2, ns.d2, ns.turn = ((nr, nc), m, P1)
            ns.walls.add(ns.p2)
        return ns

    def get_bfs_area(self, player):
        q = [self.p1 if player == P1 else self.p2]
        vis = set(self.walls)
        area = 0
        while q and area < 40:
            c = q.pop(0)
            area += 1
            for dr, dc in DIRS:
                n = ((c[0] + dr) % ROWS, (c[1] + dc) % COLS)
                if n in self.portals:
                    n = self.portals[n]
                if n not in vis:
                    vis.add(n)
                    q.append(n)
        return area

    def get_features(self):
        return [[abs(self.p1[0] - 8) + abs(self.p1[1] - 12), abs(self.p2[0] - 8) + abs(self.p2[1] - 12), abs(self.p1[0] - self.p2[0]) + abs(self.p1[1] - self.p2[1]), len(self.get_moves(P1)), len(self.get_moves(P2))]]
