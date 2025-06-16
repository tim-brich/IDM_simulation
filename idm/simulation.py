# idm/simulation.py

import numpy as np  # для чисел, массивов и формул
import pandas as pd  # для работы с таблицами (как Excel)
import os  # чтобы сохранять файлы и работать с путями


def calculate_acceleration(ego, lead, idm_params, car_length):
    """
    ускорение для конкретной машины (ego).
    Берём параметры IDM и смотрим, где машина впереди (lead).
    car_length чтобы правильно посчитать расстояние между машинами.
    """
    v = ego['v']  # текущая скорость этой машины

    if lead is None:  # если никто не едет спереди
        s = np.inf  # бесконечная дистанция — безопасно
        delta_v = 0.0  # нет разницы в скорости
    else:
        s = lead['x'] - ego['x'] - car_length  # расстояние между бамперами
        delta_v = v - lead['v']  # разница в скорости (догоняет или нет)

        if s <= 0:  # если машины пересеклись (авария!)
            return -idm_params['b']  # срочно тормозим

    # желаемая дистанция, чтоб было комфортно ехать
    s_star = idm_params['s0'] + v * idm_params['T'] + (
        v * delta_v) / (2 * np.sqrt(idm_params['a_max'] * idm_params['b']))

    # насколько далеко от желаемой скорости
    term1 = (v / idm_params['v0']) ** idm_params['delta'] if idm_params['v0'] > 0 else 0.0
    # насколько близко к другой машине
    term2 = (s_star / s) ** 2 if np.isfinite(s) else 0.0

    # итоговое ускорение по формуле IDM
    accel = idm_params['a_max'] * (1.0 - term1 - term2)

    # ограничиваем ускорение, чтобы не было слишком сильным
    return float(np.clip(accel, -idm_params['b'], idm_params['a_max']))


def update_vehicle(vehicle, a, dt):
    """
    Обновляем координаты и скорость машины за один шаг времени (dt).
    Учитываем ускорение (a), чтобы посчитать смещение.
    """
    old_v = vehicle['v']  # запоминаем старую скорость
    new_v = max(old_v + a * dt, 0.0)  # новая скорость, не меньше нуля
    dx = max(old_v * dt + 0.5 * a * (dt ** 2), 0.0)  # на сколько проехала

    vehicle['x'] += dx  # новая позиция
    vehicle['v'] = new_v  # новая скорость
    vehicle['a'] = a  # текущее ускорение


def init_vehicles(N, road_len, distribution, speed_min, speed_max):
    """
    Создаём список из N машин с начальными позициями и скоростями.
    Позиции распределяем разными способами (равномерно, случайно и т.д.).
    """
    if distribution == 'uniform':  # равномерно по всей дороге
        positions = np.linspace(0, road_len, N, endpoint=False)
    elif distribution == 'random':  # просто случайные значения
        positions = np.sort(np.random.uniform(0, road_len, size=N))
    elif distribution == 'normal':  # по нормальному закону (центр + разброс)
        positions = np.sort(np.clip(
            np.random.normal(loc=road_len / 2, scale=road_len / 5, size=N), 0, road_len))
    elif distribution == 'exponential':  # экспоненциально — ближе к началу
        positions = np.sort(np.clip(
            np.random.exponential(scale=road_len / N, size=N), 0, road_len))
    elif distribution == 'triangular':  # треугольное — пик в середине
        positions = np.sort(np.random.triangular(
            left=0, mode=road_len / 2, right=road_len, size=N))
    else:
        raise ValueError(f"Unknown distribution: {distribution}")

    # случайные скорости от минимальной до максимальной
    speeds = np.random.uniform(speed_min, speed_max, size=N)

    # создаём список машин (каждая — словарь)
    return [
        {
            'id': i,
            'x': float(pos),  # координата
            'v': float(speeds[i]),  # скорость
            'a': 0.0,  # начальное ускорение
            'mass': 1500.0  # пусть будет стандартная масса
        }
        for i, pos in enumerate(positions)
    ]


def run_simulation(config):
    """
    Главная функция: запускаем симуляцию движения.
    Все параметры берём из config (словарь).
    Возвращаем таблицу со всеми данными по времени.
    """
    # распаковываем всё из конфигурации
    N = config['num_vehicles']
    sim_time = config['sim_time']
    dt = config['dt']
    road_length = config['road_length']
    distribution = config['distribution']
    speed_min, speed_max = config['speed_range']
    first_speed = config.get('first_speed')
    idm_params = config['idm']
    car_length = config.get('car_length', 5.0)

    vehicles = init_vehicles(N, road_length, distribution, speed_min, speed_max)  # создаём машины
    data = []  # сюда будем сохранять все данные

    if first_speed is not None:  # если задана скорость лидера
        lead = max(vehicles, key=lambda v: v['x'])  # берём того, кто самый спереди
        fixed_id = lead['id']
        lead['v'] = first_speed  # задаём фиксированную скорость
        lead['a'] = 0.0
    else:
        fixed_id = None  # иначе все машины обычные

    steps = int(sim_time / dt)  # сколько шагов всего будет

    for step in range(steps):  # по всем моментам времени
        t = step * dt  # текущее время
        accelerations = {}  # сюда ускорения
        leads = {}  # а сюда — кто спереди

        for car in vehicles:
            if car['id'] == fixed_id:
                continue  # если лидер — пропускаем

            lead = None  # по умолчанию никто не спереди
            min_gap = np.inf

            for other in vehicles:  # ищем ближайшего спереди
                if other['x'] > car['x'] and (other['x'] - car['x']) < min_gap:
                    min_gap = other['x'] - car['x']
                    lead = other

            a = calculate_acceleration(car, lead, idm_params, car_length)  # считаем ускорение
            accelerations[car['id']] = a  # сохраняем
            leads[car['id']] = lead  # сохраняем кто спереди

        for car in vehicles:
            if car['id'] == fixed_id:
                car['x'] += car['v'] * dt  # лидер просто едет прямо
                car['a'] = 0.0
            else:
                a = accelerations[car['id']]
                update_vehicle(car, a, dt)  # обновляем машину

                lead = leads[car['id']]  # проверим — не врезались ли
                if lead is not None:
                    min_dist = idm_params['s0'] + car_length  # безопасная дистанция
                    if car['x'] > lead['x'] - min_dist:
                        car['x'] = lead['x'] - min_dist  # двигаем назад
                        car['v'] = min(car['v'], lead['v'])  # скорость не больше, чем у лидера
                        car['a'] = 0.0

        for car in vehicles:  # сохраняем всё в таблицу
            data.append({
                'time': t,
                'id': car['id'],
                'x': car['x'],
                'y': 0.0,  # у нас 1D дорога
                'v': car['v'],
                'a': car['a'],
                'mass': car['mass']
            })

    return pd.DataFrame(data)  # возвращаем всю таблицу


def save_simulation_csv(df, path='data/simulation_output.csv'):
    """
    Сохраняем таблицу с результатами в .csv файл.
    Если папки нет — создаём её.
    """
    os.makedirs(os.path.dirname(path), exist_ok=True)  # создаём папку, если нужно
    df.to_csv(path, index=False)  # сохраняем без индексов
