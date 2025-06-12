import numpy as np
import pandas as pd
from idm.model import Vehicle, IDM

class TrafficSimulation:
    """
    Класс для эмуляции движения автопотока по модели IDM с различными законами распределения начальных позиций
    и опциональной фиксированной скоростью лидера.
    """
    def __init__(self,
                 num_vehicles=10,
                 sim_time=60.0,
                 dt=0.1,
                 road_length=1000.0,
                 distribution='uniform',
                 speed_range=(15.0, 25.0),
                 fixed_first_speed=None):
        self.num_vehicles = num_vehicles
        self.sim_time = float(sim_time)
        self.dt = float(dt)
        self.road_length = float(road_length)
        self.distribution = distribution
        self.speed_range = speed_range
        self.fixed_first_speed = fixed_first_speed  # None или число

        self.vehicles = []
        self.idm = IDM()
        self.data = []
        self._initialize_vehicles()
        # Определяем лидера (максимальная позиция) при фиксированной скорости
        if self.fixed_first_speed is not None:
            lead_car = max(self.vehicles, key=lambda v: v.position)
            self.first_vehicle_id = lead_car.vehicle_id
        else:
            self.first_vehicle_id = None

    def _initialize_vehicles(self):
        """
        Инициализация начальных позиций по выбранному закону:
          'uniform', 'random', 'normal', 'exponential', 'triangular'
        Присваиваем начальные скорости из диапазона speed_range.
        """
        N = self.num_vehicles
        L = self.road_length
        if self.distribution == 'uniform':
            positions = np.linspace(0, L, N, endpoint=False)
        elif self.distribution == 'random':
            positions = np.random.uniform(0, L, size=N)
        elif self.distribution == 'normal':
            positions = np.random.normal(loc=L/2, scale=L/5, size=N)
        elif self.distribution == 'exponential':
            positions = np.random.exponential(scale=L/N, size=N)
        elif self.distribution == 'triangular':
            positions = np.random.triangular(left=0, mode=L/2, right=L, size=N)
        else:
            raise ValueError(f"Unknown distribution: {self.distribution}")
        positions = np.clip(positions, 0, L)
        positions.sort()

        speeds = np.random.uniform(self.speed_range[0], self.speed_range[1], size=N)
        for i, (pos, vel) in enumerate(zip(positions, speeds)):
            self.vehicles.append(Vehicle(vehicle_id=i, position=pos, velocity=vel))

    def run(self):
        """
        Запуск симуляции:
          - вычисляем ускорения IDM для всех, кроме лидера
          - обновляем состояния: leader с фиксированной скоростью, остальные через car.update
          - предотвращаем обгон, контролируя минимальную дистанцию
          - сохраняем данные
        """
        steps = int(self.sim_time / self.dt)
        for t in range(steps):
            current_time = t * self.dt
            # Вычисление ускорений для последователей
            accelerations = {}
            leads = {}
            for car in self.vehicles:
                if car.vehicle_id == self.first_vehicle_id:
                    # лидер не рассчитывает IDM
                    continue
                # поиск лидера
                lead = None
                min_gap = np.inf
                for other in self.vehicles:
                    if other.position > car.position:
                        gap = other.position - car.position
                        if gap < min_gap:
                            min_gap, lead = gap, other
                accelerations[car.vehicle_id] = self.idm.calculate_acceleration(car, lead)
                leads[car.vehicle_id] = lead

            # Обновление состояний
            for car in self.vehicles:
                if car.vehicle_id == self.first_vehicle_id and self.fixed_first_speed is not None:
                    # обновление лидера по фиксированной скорости
                    car.acceleration = 0.0
                    car.velocity = self.fixed_first_speed
                    car.position += car.velocity * self.dt
                else:
                    # применение IDM
                    a = accelerations.get(car.vehicle_id, 0.0)
                    car.update(a, self.dt)
                # предотвращение обгона
                lead = leads.get(car.vehicle_id)
                if lead is not None:
                    min_dist = self.idm.s0 + 5.0
                    max_pos = lead.position - min_dist
                    if car.position > max_pos:
                        car.position = max_pos
                        car.velocity = min(car.velocity, lead.velocity)
                        car.acceleration = 0.0
                # сохранение данных
                self.data.append({
                    'time': current_time,
                    'id': car.vehicle_id,
                    'x': car.position,
                    'y': 0.0,
                    'v': car.velocity,
                    'a': car.acceleration,
                    'mass': car.mass
                })

    def get_data(self):
        """
        Возвращает pandas.DataFrame с колонками time, id, x, y, v, a, mass.
        """
        return pd.DataFrame(self.data)

    def save_csv(self, path="data/simulation_output.csv"):
        """
        Сохраняет результаты в CSV-файл.
        """
        df = self.get_data()
        df.to_csv(path, index=False)
