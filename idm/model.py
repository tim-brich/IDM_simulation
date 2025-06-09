# idm/model.py

import numpy as np

class Vehicle:
    """
    Класс-описание автомобиля.
    Атрибуты:
        vehicle_id: уникальный идентификатор машины
        position: текущее положение по оси X (float, метры)
        velocity: текущая скорость (float, м/с)
        acceleration: текущее ускорение (float, м/с^2)
        mass: масса автомобиля (float, кг)
    """
    def __init__(self, vehicle_id, position, velocity, acceleration=0.0, mass=1500.0):
        self.vehicle_id = vehicle_id
        self.position = float(position)
        self.velocity = float(velocity)
        self.acceleration = float(acceleration)
        self.mass = float(mass)

    def update(self, acceleration, dt):
        """
        Обновление состояния автомобиля за шаг dt:
          - NEW_V = OLD_V + acceleration * dt, но не ниже 0
          - ΔX = OLD_V*dt + 0.5 * acceleration * dt^2, но не меньше 0
          - position += ΔX
        После чего сохраняем self.velocity = NEW_V, self.acceleration = acceleration.
        """
        # 1) Сохраняем старую скорость
        old_v = self.velocity

        # 2) Вычисляем новую скорость
        new_v = old_v + acceleration * dt
        if new_v < 0.0:
            new_v = 0.0

        # 3) Вычисляем приращение позиции через OLD скорость
        delta_x = old_v * dt + 0.5 * acceleration * (dt ** 2)
        if delta_x < 0.0:
            # Запрещаем машине уезжать назад
            delta_x = 0.0

        # 4) Обновляем координату и скорость, сохраняем ускорение
        self.position += delta_x
        self.velocity = new_v
        self.acceleration = acceleration


class IDM:
    """
    Класс IDM (Intelligent Driver Model) для расчёта ускорения "ego"-автомобиля
    относительно "lead"-автомобиля.
    Параметры:
        a_max: float, максимальное ускорение (м/с^2)
        b: float, комфортное замедление (м/с^2)
        delta: float, экспонента (обычно 4)
        s0: float, минимальная дистанция (м)
        T: float, желательное время реакции (с)
        v0: float, желаемая скорость (м/с)
    """
    def __init__(self, a_max=1.0, b=1.5, delta=4.0, s0=2.0, T=1.5, v0=30.0):
        self.a_max = float(a_max)
        self.b = float(b)
        self.delta = float(delta)
        self.s0 = float(s0)
        self.T = float(T)
        self.v0 = float(v0)

    def calculate_acceleration(self, ego: Vehicle, lead: Vehicle):
        """
        Расчёт ускорения автомобиля "ego" по формуле IDM.
        Если нет передней машины (lead is None), дистанция считается бесконечной.
        Если s <= 0 (слишком близко), возвращаем -b (экстренное торможение).
        Любые overflow или NaN приводят к ограничению значения ускорения.
        """
        if lead is None:
            s = np.inf
            delta_v = 0.0
        else:
            s = lead.position - ego.position - 5.0  # вычитаем длину машины ≈ 5 м
            delta_v = ego.velocity - lead.velocity
            if s <= 0:
                # Если машины уже пересеклись, экстренное торможение
                return -self.b

        try:
            s_star = self.s0 + ego.velocity * self.T + (ego.velocity * delta_v) / (2 * np.sqrt(self.a_max * self.b))
        except Exception:
            return -self.b

        try:
            term1 = (ego.velocity / self.v0) ** self.delta
        except FloatingPointError:
            term1 = np.inf

        if np.isfinite(s):
            try:
                term2 = (s_star / s) ** 2
            except FloatingPointError:
                term2 = np.inf
        else:
            term2 = 0.0

        accel = self.a_max * (1.0 - term1 - term2)
        if not np.isfinite(accel):
            return -self.b

        # Ограничиваем accel в диапазоне [-b, a_max]
        accel = max(-self.b, min(self.a_max, accel))
        return accel
