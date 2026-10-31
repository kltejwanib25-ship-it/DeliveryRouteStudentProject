from math import hypot, isfinite
def distance(a, b):
    return hypot(a[1] - b[1], a[2] - b[2])
def route_distance(stops, order):
    if not order:
        return 0.0
    path = [0] + list(order) + [0]
    return sum(distance(stops[path[i]], stops[path[i+1]]) for i in range(len(path)-1))
def nearest_neighbor(stops):
    remaining = set(range(1, len(stops)))
    order = []
    current = 0
    while remaining:
        nxt = min(remaining, key=lambda i: (distance(stops[current], stops[i]), i))
        order.append(nxt)
        remaining.remove(nxt)
        current = nxt
    return order
def two_opt(stops, order):
    order = list(order)
    if len(order) < 3:
        return order
    best = route_distance(stops, order)
    improved = True
    while improved:
        improved = False
        for i in range(len(order)-1):
            for j in range(i+1, len(order)):
                candidate = order[:i] + order[i:j+1][::-1] + order[j+1:]
                score = route_distance(stops, candidate)
                if score < best - 1e-9:
                    order, best = candidate, score
                    improved = True
                    break
            if improved:
                break
    return order
def validate(stops):
    if not 1 <= len(stops) <= 16:
        raise ValueError('Add a depot and at most 15 delivery stops.')
    for name, x, y in stops:
        if not str(name).strip():
            raise ValueError('Every stop needs a name.')
        if not (isfinite(float(x)) and isfinite(float(y))):
            raise ValueError('Coordinates must be finite numbers.')
def optimize(stops):
    validate(stops)
    original = list(range(1, len(stops)))
    greedy = nearest_neighbor(stops)
    improved = two_opt(stops, greedy)
    if route_distance(stops, original) < route_distance(stops, improved):
        improved = list(original)
    return {
        'original_order': original,
        'original_km': route_distance(stops, original),
        'greedy_order': greedy,
        'greedy_km': route_distance(stops, greedy),
        'optimized_order': improved,
        'optimized_km': route_distance(stops, improved),
    }
