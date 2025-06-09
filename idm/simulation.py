# idm/simulation.py

import numpy as np
import pandas as pd

from idm.model import Vehicle, IDM


class TrafficSimulation:
    """
    Класс, отвечающий за эмуляцию движения автопотока по модели IDM
    и за сбор данных для последующего анализа или визуализации.

    Параметры:
        num_vehicles (int): Число автомобилей.
        sim_time (float): Общее время симуляции (с).
        dt (float): Шаг времени (с).
        road_length (float): Длина «дороги» (м).
        distribution (str): Тип распределения позиций ('uniform' или 'normal').
        speed_range (tuple[float, float]): Диапазон начальных скоростей (min, max).
    """

    def __init__(
        self,
        num_vehicles: int = 10,
        sim_time: float = 60.0,
        dt: float = 0.1,
        road_length: float = 1000.0,
        distribution: str = 'uniform',
        speed_range: tuple[float, float] = (15.0, 25.0)
    ):
        self.num_vehicles = num_vehicles
        self.sim_time = float(sim_time)
        self.dt = float(dt)
        self.road_length = float(road_length)
        self.distribution = distribution
        self.speed_range = speed_range

        self.vehicles: list[Vehicle] = []
        self.idm = IDM()
        self.data: list[dict] = []  # Список словарей с результатами

        self._initialize_vehicles()

    def _initialize_vehicles(self) -> None:
        """
        Инициализация автомобилей:

        - Вычисляем начальные позиции в зависимости от self.distribution.
        - Начальные скорости случайно из self.speed_range.
        """
        if self.num_vehicles <= 0:
            raise ValueError("num_vehicles должен быть ≥ 1")

        if self.distribution == 'uniform':
            spacing = self.road_length / self.num_vehicles
            positions = [i * spacing for i in range(self.num_vehicles)]
        elif self.distribution == 'normal':
            positions = np.random.normal(
                loc=self.road_length / 2,
                scale=self.road_length / 5,
                size=self.num_vehicles
            )
            positions = np.clip(positions, 0.0, self.road_length)
            positions.sort()
        else:
            raise ValueError(f"Unknown distribution type: {self.distribution}")

        for i, pos in enumerate(positions):
            vel = np.random.uniform(self.speed_range[0], self.speed_range[1])
            car = Vehicle(vehicle_id=i, position=pos, velocity=vel)
            self.vehicles.append(car)

    def run(self) -> None:
        """
        Запуск симуляции:

        Для каждого временного шага t = 0, dt, 2*dt, …, sim_time:
          1) Для каждой машины car из self.vehicles:
             - Находим lead_car: ближайшую впереди идущую машину (position > car.position),
               у которой дистанция минимальна.
             - Вычисляем ускорение a = IDM.calculate_acceleration(car, lead_car).
          2) После вычисления ускорений:
             - Для каждой машины рассчитываем новое положение и скорость:
               OLD_V = car.velocity
               NEW_V = max(0, OLD_V + a*dt)
               ΔX = OLD_V*dt + 0.5*a*dt^2
               gap = (lead_car.position - car.position - 5) если lead_car, иначе inf
               Если ΔX > gap, то ΔX = gap
               car.position += ΔX
               car.velocity = NEW_V
               car.acceleration = a
             - Сохраняем запись {time, id, x, y, v, a, mass} в self.data.
        """
        time_steps = int(self.sim_time / self.dt)
        for t in range(time_steps):
            current_time = t * self.dt

            # 1) Сначала вычисляем ускорения для всех машин
            accelerations: list[float] = []
            lead_cars: list[Vehicle | None] = []

            for car in self.vehicles:
                lead_car = None
                min_gap = np.inf
                for other in self.vehicles:
                    if other.position > car.position:
                        gap = other.position - car.position
                        if gap < min_gap:
                            min_gap = gap
                            lead_car = other
                lead_cars.append(lead_car)

                a = self.idm.calculate_acceleration(car, lead_car)
                accelerations.append(a)

            # 2) Теперь обновляем все машины с учётом gap
            for idx, car in enumerate(self.vehicles):
                a = accelerations[idx]
                lead_car = lead_cars[idx]

                # Рассчитываем текущий gap (до передней машины)
                if lead_car is None:
                    gap = np.inf
                else:
                    gap = lead_car.position - car.position - 5.0

                # Интегрируем скорость
                old_v = car.velocity
                new_v = old_v + a * self.dt
                if new_v < 0.0:
                    new_v = 0.0

                # Интегрируем положение
                dx = old_v * self.dt + 0.5 * a * (self.dt ** 2)
                if dx < 0.0:
                    dx = 0.0

                # Если приращение превышает gap, прижимаемся к lead_car
                if dx > gap:
                    dx = gap

                # Обновляем состояние машины
                car.position += dx
                car.velocity = new_v
                car.acceleration = a

                # Сохраняем данные в результирующий список
                self.data.append({
                    'time': current_time,
                    'id': car.vehicle_id,
                    'x': car.position,
                    'y': 0.0,
                    'v': car.velocity,
                    'a': car.acceleration,
                    'mass': car.mass
                })

    def get_data(self) -> pd.DataFrame:
        """
        Возвращает результаты симуляции в виде pandas.DataFrame.

        Колонки: time, id, x, y, v, a, mass

        Returns:
            pandas.DataFrame: Датафрейм со всеми записями self.data.
        """
        return pd.DataFrame(self.data)

    def save_csv(self, path: str = "data/simulation_output.csv") -> None:
        """
        Сохраняет результаты симуляции в CSV-файл по указанному пути.

        Args:
            path (str): Путь до CSV (по умолчанию 'data/simulation_output.csv').
        """
        df = self.get_data()
        df.to_csv(path, index=False)
