import os
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation

from idm.simulation import TrafficSimulation
from idm.model import IDM


def run_simulation_and_animate(params):
    """
    Запускает симуляцию IDM, автоматически сохраняет CSV в папку data
    и визуализирует результат через Matplotlib.
    Отображает скорость над каждым маркером, позволяет задать индивидуальную скорость первой машины.
    """
    # Распаковка параметров
    num_vehicles    = params['num_vehicles']
    sim_time        = params['sim_time']
    dt              = params['dt']
    road_length     = params['road_length']
    distribution    = params['distribution']
    speed_min       = params['speed_min']
    speed_max       = params['speed_max']
    first_speed     = params.get('first_speed')
    idm_p           = params['idm']
    frame_skip      = params['frame_skip']
    playback_speed  = params['playback_speed']
    marker_size     = params['marker_size']
    lane_width      = params['lane_width']

    # Папка data
    os.makedirs('data', exist_ok=True)
    csv_path = os.path.join('data', 'simulation_output.csv')

    # Инициализация симуляции
    sim = TrafficSimulation(
        num_vehicles=num_vehicles,
        sim_time=sim_time,
        dt=dt,
        road_length=road_length,
        distribution=distribution,
        speed_range=(speed_min, speed_max),
        fixed_first_speed=first_speed
    )
    # Если задана индивидуальная скорость первой машины
    if first_speed is not None:
        sim.vehicles[0].velocity = first_speed
        sim.vehicles[0].acceleration = 0.0
    # Настройка IDM-параметров
    sim.idm = IDM(
        a_max=idm_p['a_max'],
        b=idm_p['b'],
        delta=idm_p['delta'],
        s0=idm_p['s0'],
        T=idm_p['T'],
        v0=idm_p['v0']
    )
    sim.run()

    # Сохранение CSV
    sim.save_csv(csv_path)
    print(f"Данные симуляции сохранены в {csv_path}")

    # Подготовка данных для анимации
    df = sim.get_data()
    pivot_x = df.pivot(index='time', columns='id', values='x')
    pivot_v = df.pivot(index='time', columns='id', values='v')
    times_full = np.array(sorted(pivot_x.index.tolist()))
    times = times_full[::frame_skip]

    # Настройка фигуры
    fig, ax = plt.subplots(figsize=(12, 4))
    ax.set_xlim(0, road_length)
    ax.set_ylim(-lane_width/2, lane_width/2)
    ax.set_yticks([])
    ax.set_xlabel('Позиция вдоль дороги (м)')
    ax.set_title('t = 0.00 с')

    # Дорога
    road = plt.Rectangle((0, -lane_width/2), road_length, lane_width,
                         color='gray', alpha=0.5, zorder=0)
    ax.add_patch(road)

    # Scatter-маркеры и аннотации скорости чуть ниже
    scat = ax.scatter([], [], s=marker_size, c='red', edgecolors='black', zorder=2)
    y_offset = lane_width * 0.2  # опустили вниз
    annotations = []
    for _ in range(num_vehicles):
        txt = ax.text(0, y_offset, '', ha='center', va='top', fontsize=8, color='blue', zorder=3)
        annotations.append(txt)

    def update(frame_idx):
        t = times[frame_idx]
        xs = pivot_x.loc[t].values
        vs = pivot_v.loc[t].values
        coords = np.column_stack((xs, np.zeros_like(xs)))
        scat.set_offsets(coords)
        for txt, x, v in zip(annotations, xs, vs):
            txt.set_position((x, y_offset))
            txt.set_text(f'{v:.1f} м/с')
        ax.set_title(f't = {t:.2f} с')
        return [scat] + annotations

    interval_ms = dt * 1000 * frame_skip / playback_speed
    ani = animation.FuncAnimation(
        fig, update,
        frames=len(times),
        interval=interval_ms,
        blit=False,
        repeat=False
    )
    plt.tight_layout()
    plt.show()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('Симулятор IDM автопотока')
        self.entries = {}
        self._build_ui()

    def _build_ui(self):
        sim_fr = ttk.LabelFrame(self, text='Параметры симуляции')
        sim_fr.pack(fill='x', padx=10, pady=5)
        for name, lbl, default in [
            ('num_vehicles', 'Число машин', '50'),
            ('sim_time', 'Время симуляции (с)', '60'),
            ('dt', 'Шаг dt (с)', '0.05'),
            ('road_length', 'Длина дороги (м)', '10000'),
        ]:
            ttk.Label(sim_fr, text=lbl).pack(side='left')
            var = tk.StringVar(value=default)
            ttk.Entry(sim_fr, textvariable=var, width=8).pack(side='left', padx=5)
            self.entries[name] = var
        ttk.Label(sim_fr, text='Распределение позиций').pack(side='left')
        dist_var = tk.StringVar(value='uniform')
        ttk.OptionMenu(sim_fr, dist_var, 'uniform', 'uniform', 'random', 'normal', 'exponential', 'triangular').pack(side='left', padx=5)
        self.entries['distribution'] = dist_var
        for name, lbl, default in [
            ('speed_min', 'Минимальная скорость (м/с)', '0'),
            ('speed_max', 'Максимальная скорость (м/с)', '30'),
            ('first_speed', 'Скорость первой машины (м/с)', ''),
        ]:
            ttk.Label(sim_fr, text=lbl).pack(side='left')
            var = tk.StringVar(value=default)
            ttk.Entry(sim_fr, textvariable=var, width=8).pack(side='left', padx=5)
            self.entries[name] = var

        idm_fr = ttk.LabelFrame(self, text='Параметры IDM')
        idm_fr.pack(fill='x', padx=10, pady=5)
        for name, lbl, default in [
            ('a_max', 'Максимальное ускорение a_max (м/с²)', '1.0'),
            ('b', 'Комфортное замедление b (м/с²)', '1.5'),
            ('delta', 'Экспонента δ (безразмерная)', '4.0'),
            ('s0', 'Минимальная дистанция s₀ (м)', '2.0'),
            ('T', 'Желаемое время реакции T (с)', '1.5'),
            ('v0', 'Желаемая скорость v₀ (м/с)', '30.0'),
        ]:
            ttk.Label(idm_fr, text=lbl).pack(side='left')
            var = tk.StringVar(value=default)
            ttk.Entry(idm_fr, textvariable=var, width=8).pack(side='left', padx=5)
            self.entries[name] = var

        vis_fr = ttk.LabelFrame(self, text='Визуализация')
        vis_fr.pack(fill='x', padx=10, pady=5)
        for name, lbl, default in [
            ('frame_skip', 'Пропуск кадров', '1'),
            ('playback_speed', 'Скорость воспроизведения', '1.0'),
            ('marker_size', 'Размер маркера (px)', '200'),
            ('lane_width', 'Ширина полосы (м)', '3.5'),
        ]:
            ttk.Label(vis_fr, text=lbl).pack(side='left')
            var = tk.StringVar(value=default)
            ttk.Entry(vis_fr, textvariable=var, width=8).pack(side='left', padx=5)
            self.entries[name] = var

        ttk.Button(self, text='Запустить симуляцию', command=self._on_run).pack(pady=10)

    def _on_run(self):
        try:
            params = {}
            for k, var in self.entries.items():
                v = var.get()
                if k == 'distribution':
                    params[k] = v
                elif k == 'first_speed' and v.strip() == '':
                    params[k] = None
                else:
                    params[k] = float(v) if '.' in v or k.startswith('dt') else int(v)
        except Exception as e:
            messagebox.showerror('Ошибка ввода', str(e))
            return
        idm_keys = ['a_max', 'b', 'delta', 's0', 'T', 'v0']
        params['idm'] = {k: params.pop(k) for k in idm_keys}
        self.destroy()
        run_simulation_and_animate(params)

if __name__ == '__main__':
    App().mainloop()
