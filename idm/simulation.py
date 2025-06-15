# idm/simulation.py

"""
Полностью функциональная реализация модели IDM и симуляции движения,
с учётом параметра длины автомобиля (car_length).
"""

import numpy as np
import pandas as pd
import os

def calculate_acceleration(ego, lead, idm_params, car_length):
    """
    Расчёт ускорения автомобиля "ego" по формуле IDM.
    ego, lead: словари с полями 'x', 'v'
    idm_params: словарь с a_max, b, delta, s0, T, v0
    car_length: физическая длина автомобиля (м)

    Возвращает ускорение, ограниченное [-b, a_max].
    """
    v = ego['v']
    if lead is None:
        s = np.inf
        delta_v = 0.0
    else:
        # s — расстояние между бамперами: позиция лидера минус позиция ego минус длину авто
        s = lead['x'] - ego['x'] - car_length
        delta_v = v - lead['v']
        if s <= 0:
            # машины «накладываются» — экстренное торможение
            return -idm_params['b']

    # желаемая дистанция s*
    s_star = idm_params['s0'] + v * idm_params['T'] + (v * delta_v) / (2 * np.sqrt(idm_params['a_max'] * idm_params['b']))
    term1 = (v / idm_params['v0']) ** idm_params['delta'] if idm_params['v0'] > 0 else 0.0
    term2 = (s_star / s) ** 2 if np.isfinite(s) else 0.0

    accel = idm_params['a_max'] * (1.0 - term1 - term2)
    # ограничиваем accel в диапазоне [-b, a_max]
    return float(np.clip(accel, -idm_params['b'], idm_params['a_max']))


def update_vehicle(vehicle, a, dt):
    """
    Обновление состояния автомобиля за шаг dt по накопленной акселерации:
      - новая скорость = max(old_v + a*dt, 0)
      - смещение = max(old_v*dt + 0.5*a*dt^2, 0)
    vehicle: словарь с 'v', 'x', 'a'
    """
    old_v = vehicle['v']
    new_v = max(old_v + a * dt, 0.0)
    dx = max(old_v * dt + 0.5 * a * (dt ** 2), 0.0)

    vehicle['x'] += dx
    vehicle['v'] = new_v
    vehicle['a'] = a


def init_vehicles(N, road_len, distribution, speed_min, speed_max):
    """
    Генерация N автомобилей с начальными позициями и скоростями.
    distribution: один из 'uniform','random','normal','exponential','triangular'
    """
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
        raise ValueError(f"Unknown distribution: {distribution}")

    speeds = np.random.uniform(speed_min, speed_max, size=N)
    return [
        {'id': i, 'x': float(pos), 'v': float(speeds[i]), 'a': 0.0, 'mass': 1500.0}
        for i, pos in enumerate(positions)
    ]


def run_simulation(config):
    """
    Основной цикл моделирования.
    config: словарь с ключами
      - num_vehicles, sim_time, dt, road_length, distribution, speed_range,
      - first_speed (или None), idm (словарь),
      - car_length (физическая длина автомобиля в метрах)
    Возвращает pandas.DataFrame с колонками
      time, id, x, y, v, a, mass
    """
    N            = config['num_vehicles']
    sim_time     = config['sim_time']
    dt           = config['dt']
    road_length  = config['road_length']
    distribution = config['distribution']
    speed_min, speed_max = config['speed_range']
    first_speed  = config.get('first_speed')
    idm_params   = config['idm']
    car_length   = config.get('car_length', 5.0)

    vehicles = init_vehicles(N, road_length, distribution, speed_min, speed_max)
    data = []

    # Зафиксируем лидера, если указана first_speed
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

        # вычисляем ускорения для всех, кроме зафиксированного
        for car in vehicles:
            if car['id'] == fixed_id:
                continue
            # находим ближайшего впереди
            lead = None
            min_gap = np.inf
            for other in vehicles:
                if other['x'] > car['x'] and (other['x'] - car['x']) < min_gap:
                    min_gap = other['x'] - car['x']
                    lead = other

            a = calculate_acceleration(car, lead, idm_params, car_length)
            accelerations[car['id']] = a
            leads[car['id']] = lead

        # обновляем состояния
        for car in vehicles:
            if car['id'] == fixed_id:
                # фиксированный лидер движется на constant speed
                car['x'] += car['v'] * dt
                car['a'] = 0.0
            else:
                a = accelerations[car['id']]
                update_vehicle(car, a, dt)

                # предотвращаем пересечение бамперов
                lead = leads[car['id']]
                if lead is not None:
                    min_dist = idm_params['s0'] + car_length
                    if car['x'] > lead['x'] - min_dist:
                        car['x'] = lead['x'] - min_dist
                        car['v'] = min(car['v'], lead['v'])
                        car['a'] = 0.0

        # сохраняем срез
        for car in vehicles:
            data.append({
                'time': t,
                'id':    car['id'],
                'x':     car['x'],
                'y':     0.0,
                'v':     car['v'],
                'a':     car['a'],
                'mass':  car['mass']
            })

    return pd.DataFrame(data)


def save_simulation_csv(df, path='data/simulation_output.csv'):
    """
    Сохраняет DataFrame в CSV, создавая директорию при необходимости.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)
    df.to_csv(path, index=False)
