import os
import tkinter as tk
from tkinter import ttk, messagebox
import numpy as np
import matplotlib.pyplot as plt
import matplotlib.animation as animation
from idm.simulation import run_simulation, save_simulation_csv

def run_simulation_and_animate(params):
    df = run_simulation(params)
    save_simulation_csv(df)
    print("\n\u2714\ufe0f Данные симуляции сохранены в: data/simulation_output.csv\n")

    pivot_x = df.pivot(index='time', columns='id', values='x')
    pivot_v = df.pivot(index='time', columns='id', values='v')
    times = sorted(pivot_x.index.tolist())

    fig, ax = plt.subplots(figsize=(12, 4))
    ax.set_xlim(0, params['road_length'])
    ax.set_ylim(-params['lane_width'], params['lane_width'])
    ax.set_yticks([])
    ax.set_xlabel('Позиция вдоль дороги (м)')
    ax.set_title('Симуляция движения по модели IDM')

    road = plt.Rectangle((0, -params['lane_width']/2), params['road_length'], params['lane_width'], color='gray', alpha=0.5)
    ax.add_patch(road)

    scat = ax.scatter([], [], s=params['marker_size'], color='red')
    annotations = [ax.text(0, -params['lane_width']/2 + 0.1, '', ha='center', va='bottom', fontsize=8, color='blue') for _ in range(params['num_vehicles'])]

    def update(frame):
        t = times[frame]
        xs = pivot_x.loc[t].values
        vs = pivot_v.loc[t].values
        coords = np.column_stack((xs, np.zeros_like(xs)))
        scat.set_offsets(coords)
        for i, txt in enumerate(annotations):
            txt.set_position((xs[i], -params['lane_width']/2 + 0.1))
            txt.set_text(f"{vs[i]:.1f} м/с")
        ax.set_title(f"t = {t:.2f} с")
        return scat, *annotations

    ani = animation.FuncAnimation(fig, update, frames=len(times), interval=50, blit=False)
    plt.tight_layout()
    plt.show()

class App(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title('IDM Симулятор (Функциональный подход)')
        self.entries = {}
        self._build_ui()

    def _build_ui(self):
        sim_fr = ttk.LabelFrame(self, text='Параметры симуляции')
        sim_fr.pack(fill='x', padx=10, pady=5)
        for name, lbl, default in [
            ('num_vehicles', 'Число машин', '30'),
            ('sim_time', 'Время симуляции (с)', '60'),
            ('dt', 'Шаг времени dt (с)', '0.05'),
            ('road_length', 'Длина дороги (м)', '1000'),
            ('speed_min', 'Мин. скорость (м/с)', '5'),
            ('speed_max', 'Макс. скорость (м/с)', '25'),
            ('first_speed', 'Скорость первой машины (опц.)', '')
        ]:
            ttk.Label(sim_fr, text=lbl).pack(side='left')
            var = tk.StringVar(value=default)
            ttk.Entry(sim_fr, textvariable=var, width=8).pack(side='left')
            self.entries[name] = var

        ttk.Label(sim_fr, text='Распределение позиций').pack(side='left')
        dist_var = tk.StringVar(value='uniform')
        ttk.OptionMenu(sim_fr, dist_var, 'uniform', 'uniform', 'random', 'normal', 'exponential', 'triangular').pack(side='left')
        self.entries['distribution'] = dist_var

        idm_fr = ttk.LabelFrame(self, text='Параметры модели IDM')
        idm_fr.pack(fill='x', padx=10, pady=5)
        for name, lbl, default in [
            ('a_max', 'Макс. ускорение a_max', '1.0'),
            ('b', 'Комфортное торможение b', '1.5'),
            ('delta', 'Экспонента delta', '4.0'),
            ('s0', 'Мин. дистанция s0', '2.0'),
            ('T', 'Время реакции T', '1.5'),
            ('v0', 'Желаемая скорость v0 (м/с)', '30.0')
        ]:
            ttk.Label(idm_fr, text=lbl).pack(side='left')
            var = tk.StringVar(value=default)
            ttk.Entry(idm_fr, textvariable=var, width=8).pack(side='left')
            self.entries[name] = var

        vis_fr = ttk.LabelFrame(self, text='Визуализация')
        vis_fr.pack(fill='x', padx=10, pady=5)
        for name, lbl, default in [
            ('marker_size', 'Размер маркеров (px)', '200'),
            ('lane_width', 'Ширина полосы (м)', '3.5')
        ]:
            ttk.Label(vis_fr, text=lbl).pack(side='left')
            var = tk.StringVar(value=default)
            ttk.Entry(vis_fr, textvariable=var, width=8).pack(side='left')
            self.entries[name] = var

        ttk.Button(self, text='Запустить симуляцию', command=self._on_run).pack(pady=10)

    def _on_run(self):
        try:
            params = {}
            for k, v in self.entries.items():
                if k == 'distribution':
                    params[k] = v.get()
                elif k == 'first_speed' and v.get().strip() == '':
                    params[k] = None
                elif '.' in v.get():
                    params[k] = float(v.get())
                else:
                    params[k] = int(v.get())

            idm_keys = ['a_max', 'b', 'delta', 's0', 'T', 'v0']
            params['idm'] = {k: params.pop(k) for k in idm_keys}
            params['speed_range'] = (params.pop('speed_min'), params.pop('speed_max'))
        except Exception as e:
            messagebox.showerror('Ошибка', str(e))
            return

        self.destroy()
        run_simulation_and_animate(params)

if __name__ == '__main__':
    App().mainloop()
