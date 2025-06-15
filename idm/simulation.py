"""
Полностью функциональная реализация модели IDM и симуляции движения
без использования классов. Используются только функции и словари.
"""

import numpy as np
import pandas as pd

# === Модель IDM как функция ===
def calculate_acceleration(ego, lead, idm):
    v = ego['v']
    if lead is None:
        s = np.inf
        delta_v = 0.0
    else:
        s = lead['x'] - ego['x'] - 5.0  # длина машины
        delta_v = v - lead['v']
        if s <= 0:
            return -idm['b']

    s_star = idm['s0'] + v * idm['T'] + (v * delta_v) / (2 * np.sqrt(idm['a_max'] * idm['b']))
    term1 = (v / idm['v0']) ** idm['delta'] if idm['v0'] > 0 else 0.0
    term2 = (s_star / s) ** 2 if np.isfinite(s) else 0.0
    a = idm['a_max'] * (1.0 - term1 - term2)
    a = np.clip(a, -idm['b'], idm['a_max'])
    return a

# === Обновление позиции и скорости ===
def update_vehicle(vehicle, a, dt):
    old_v = vehicle['v']
    new_v = max(old_v + a * dt, 0.0)
    dx = max(old_v * dt + 0.5 * a * dt**2, 0.0)
    vehicle['x'] += dx
    vehicle['v'] = new_v
    vehicle['a'] = a

# === Инициализация машин ===
def init_vehicles(N, road_len, distribution, speed_min, speed_max):
    if distribution == 'uniform':
        positions = np.linspace(0, road_len, N, endpoint=False)
    elif distribution == 'random':
        positions = np.sort(np.random.uniform(0, road_len, size=N))
    elif distribution == 'normal':
        positions = np.sort(np.clip(np.random.normal(loc=road_len/2, scale=road_len/5, size=N), 0, road_len))
    elif distribution == 'exponential':
        positions = np.sort(np.clip(np.random.exponential(scale=road_len/N, size=N), 0, road_len))
    elif distribution == 'triangular':
        positions = np.sort(np.random.triangular(left=0, mode=road_len/2, right=road_len, size=N))
    else:
        raise ValueError("Unknown distribution")

    speeds = np.random.uniform(speed_min, speed_max, size=N)
    return [
        {'id': i, 'x': float(pos), 'v': float(speeds[i]), 'a': 0.0, 'mass': 1500.0}
        for i, pos in enumerate(positions)
    ]

# === Основной цикл симуляции ===
def run_simulation(config):
    N = config['num_vehicles']
    sim_time = config['sim_time']
    dt = config['dt']
    road_length = config['road_length']
    distribution = config['distribution']
    speed_range = config['speed_range']
    first_speed = config.get('first_speed')
    idm_params = config['idm']

    vehicles = init_vehicles(N, road_length, distribution, speed_range[0], speed_range[1])
    data = []

    if first_speed is not None:
        lead = max(vehicles, key=lambda v: v['x'])
        fixed_id = lead['id']
        lead['v'] = first_speed
        lead['a'] = 0.0
    else:
        fixed_id = None

    steps = int(sim_time / dt)
    for step in range(steps):
        t = step * dt
        accelerations = {}
        leads = {}
        for car in vehicles:
            if car['id'] == fixed_id:
                continue
            lead = None
            min_gap = np.inf
            for other in vehicles:
                if other['x'] > car['x']:
                    gap = other['x'] - car['x']
                    if gap < min_gap:
                        lead = other
                        min_gap = gap
            a = calculate_acceleration(car, lead, idm_params)
            accelerations[car['id']] = a
            leads[car['id']] = lead

        for car in vehicles:
            if car['id'] == fixed_id:
                car['a'] = 0.0
                car['x'] += car['v'] * dt
            else:
                a = accelerations[car['id']]
                update_vehicle(car, a, dt)
                lead = leads[car['id']]
                if lead is not None:
                    min_dist = idm_params['s0'] + 5.0
                    if car['x'] > lead['x'] - min_dist:
                        car['x'] = lead['x'] - min_dist
                        car['v'] = min(car['v'], lead['v'])
                        car['a'] = 0.0

        for car in vehicles:
            data.append({
                'time': t,
                'id': car['id'],
                'x': car['x'],
                'y': 0.0,
                'v': car['v'],
                'a': car['a'],
                'mass': car['mass']
            })

    return pd.DataFrame(data)

# === Сохранение результата ===
def save_simulation_csv(df, path='data/simulation_output.csv'):
    import os
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
