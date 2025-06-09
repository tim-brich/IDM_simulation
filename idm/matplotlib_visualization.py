# idm/matplotlib_visualization.py

import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
import pandas as pd
from matplotlib.patches import FancyBboxPatch
from idm.simulation import TrafficSimulation


def _parse_rgb(line: str) -> tuple[float, float, float]:
    """
    Преобразует строку "r,g,b" (каждое число 0.0–1.0) в кортеж (r, g, b).

    Args:
        line (str): Строка вида "0.7,0.7,0.7".

    Returns:
        tuple[float, float, float]: Тройка чисел float.

    Raises:
        ValueError: Если не три компонента или не удается сконвертировать в float.
    """
    parts = [x.strip() for x in line.split(',')]
    if len(parts) != 3:
        raise ValueError(f"Ожидаются три компонента R,G,B, получено: '{line}'")
    try:
        return float(parts[0]), float(parts[1]), float(parts[2])
    except Exception as e:
        raise ValueError(f"Ошибка при разборе RGB: {e}")


def run_matplotlib_visualization(
    *,
    # Параметры симуляции:
    num_vehicles: int,
    sim_time: float,
    dt: float,
    road_length: float,
    distribution: str,
    speed_min: float,
    speed_max: float,

    # Параметры визуализации:
    road_color: str,            # строка "r,g,b"
    car_color: str,             # строка "r,g,b"
    label_color: str,           # строка "r,g,b"
    car_length: float,
    car_width: float,
    lane_width: float,
    frame_skip: int,
    annotation_fontsize: int,
    annotation_box_alpha: float,
    annotation_box_facecolor: str  # строка "r,g,b"
) -> None:
    """
    Запускает анимацию движения автомобилей IDM-модели с помощью Matplotlib.

    Все параметры (симуляции и визуализации) передаются как аргументы,
    либо из командной строки, либо из config.ini (main.py).

    Args:
        num_vehicles          (int): Количество автомобилей.
        sim_time              (float): Время симуляции (сек).
        dt                    (float): Шаг времени (сек).
        road_length           (float): Длина дороги (м).
        distribution          (str): «uniform» или «normal».
        speed_min             (float): Нижняя граница начальной скорости (м/с).
        speed_max             (float): Верхняя граница начальной скорости (м/с).

        road_color            (str): Цвет дороги, строка "r,g,b".
        car_color             (str): Цвет машин, строка "r,g,b".
        label_color           (str): Цвет текста, строка "r,g,b".
        car_length            (float): Длина машины (м).
        car_width             (float): Ширина машины (м).
        lane_width            (float): Ширина полосы (м).
        frame_skip            (int): Пропуск кадров (>=1).
        annotation_fontsize   (int): Размер шрифта у подписи.
        annotation_box_alpha  (float): Прозрачность фона подписи (0.0–1.0).
        annotation_box_facecolor (str): Цвет фона подписи, "r,g,b".

    Returns:
        None: Открывает окно Matplotlib и показывает анимацию.
    """
    # ----------------------------------------
    # 1. Распарсим строки RGB → кортежи (float, float, float)
    # ----------------------------------------
    road_rgb_tuple = _parse_rgb(road_color)
    car_rgb_tuple = _parse_rgb(car_color)
    label_rgb_tuple = _parse_rgb(label_color)
    annotation_box_facecolor_tuple = _parse_rgb(annotation_box_facecolor)

    # ----------------------------------------
    # 2. Запускаем симуляцию IDM и собираем DataFrame
    # ----------------------------------------
    sim = TrafficSimulation(
        num_vehicles=num_vehicles,
        sim_time=sim_time,
        dt=dt,
        road_length=road_length,
        distribution=distribution,
        speed_range=(speed_min, speed_max)
    )
    sim.run()
    df = sim.get_data()  # колонки: ['time','id','x','y','v','a','mass']

    pivot_x = df.pivot(index="time", columns="id", values="x")
    pivot_v = df.pivot(index="time", columns="id", values="v")
    time_values_full = np.array(sorted(pivot_x.index.tolist()))

    # Пропускаем кадры, чтобы ускорить:
    time_values = time_values_full[::frame_skip]

    # ----------------------------------------
    # 3. Настройка Matplotlib-фигуры и осей
    # ----------------------------------------
    plt.style.use("default")
    fig, ax = plt.subplots(figsize=(12, 4))

    ax.set_xlim(0, road_length)
    ax.set_ylim(-lane_width, lane_width)
    ax.set_xlabel("Позиция вдоль дороги (м)")
    ax.set_yticks([])
    ax.set_title("IDM Traffic Simulation")

    # Широкий прямоугольник: дорога (толщина = lane_width)
    road_rect = plt.Rectangle(
        (0, -lane_width / 2),
        road_length,
        lane_width,
        color=road_rgb_tuple,
        alpha=0.8,
        zorder=0
    )
    ax.add_patch(road_rect)

    # ----------------------------------------
    # 4. Создаём “заготовки” для машин и подписей
    # ----------------------------------------
    car_patches = []
    annotations = []
    for _ in range(num_vehicles):
        patch = FancyBboxPatch(
            (0 - car_length / 2, -car_width / 2),
            car_length,
            car_width,
            boxstyle="round,pad=0.1,rounding_size=0.2",
            edgecolor="black",
            facecolor=car_rgb_tuple,
            linewidth=0.5,
            zorder=2,
        )
        ax.add_patch(patch)
        car_patches.append(patch)

        ann = ax.text(
            0,
            (car_width / 2) + 0.1,
            "",
            ha="center",
            va="bottom",
            fontsize=annotation_fontsize,
            color=label_rgb_tuple,
            bbox=dict(
                facecolor=annotation_box_facecolor_tuple,
                alpha=annotation_box_alpha,
                edgecolor="none",
            ),
            zorder=3,
        )
        annotations.append(ann)

    # ----------------------------------------
    # 5. Инициализация пустого кадра
    # ----------------------------------------
    def init():
        for patch in car_patches:
            patch.set_visible(False)
        for ann in annotations:
            ann.set_text("")
            ann.set_visible(False)
        return car_patches + annotations

    # ----------------------------------------
    # 6. Обновление каждого кадра анимации
    # ----------------------------------------
    def update(frame_idx: int):
        t = time_values[frame_idx]
        xs = pivot_x.loc[t].values    # реальные x позиции автомобилей
        vs = pivot_v.loc[t].values    # реальные скорости автомобилей

        for i, patch in enumerate(car_patches):
            x_i = xs[i]
            patch.set_visible(True)
            patch.set_x(x_i - car_length / 2)
            # Y-координата –car_width/2 не меняется

        for i, ann in enumerate(annotations):
            x_i = xs[i]
            v_i = vs[i]
            ann.set_visible(True)
            ann.set_position((x_i, (car_width / 2) + 0.1))
            ann.set_text(f"ID:{i}  v={v_i:.1f} m/s")

        ax.set_title(f"IDM Traffic Simulation — t = {t:.2f} c")
        return car_patches + annotations

    # ----------------------------------------
    # 7. Запуск анимации
    # ----------------------------------------
    interval_ms = int(dt * 1000 * frame_skip)
    ani = animation.FuncAnimation(
        fig,
        update,
        frames=len(time_values),
        init_func=init,
        blit=False,
        interval=interval_ms,
        repeat=False,
    )

    plt.tight_layout()
    plt.show()
