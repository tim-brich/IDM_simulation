import os  # для работы с путями и файлами
import tkinter as tk  # основное GUI-окно
from tkinter import ttk, messagebox  # для красивых виджетов и окон ошибок
import numpy as np  # математика и массивы
import matplotlib.pyplot as plt  # графики
import matplotlib.animation as animation  # анимация графиков
from idm.simulation import run_simulation, save_simulation_csv  # запуск симуляции и сохранение


def run_simulation_and_animate(params):  # запускаем симуляцию и рисуем анимацию
    df = run_simulation(params)  # получаем данные по всем машинам
    save_simulation_csv(df)  # сохраняем в файл .csv
    print("\n✔️ Данные симуляции сохранены в: data/simulation_output.csv\n")

    pivot_x = df.pivot(index='time', columns='id', values='x')  # позиции по времени
    pivot_v = df.pivot(index='time', columns='id', values='v')  # скорости по времени
    times = sorted(pivot_x.index.tolist())  # список всех моментов времени

    fig, ax = plt.subplots(figsize=(12, 4))  # создаём фигуру для графика
    ax.set_xlim(0, params['road_length'])  # границы по Х = длина дороги
    ax.set_ylim(-params['lane_width'], params['lane_width'])  # по Y — ширина полосы
    ax.set_yticks([])  # убираем деления по Y
    ax.set_xlabel('Позиция вдоль дороги (м)')  # подпись X
    ax.set_title('Симуляция движения по модели IDM')  # заголовок

    road = plt.Rectangle(  # рисуем дорогу прямоугольником
        (0, -params['lane_width'] / 2),
        params['road_length'],
        params['lane_width'],
        color='gray',
        alpha=0.5
    )
    ax.add_patch(road)  # добавляем прямоугольник на график

    scat = ax.scatter([], [], s=params['marker_size'], color='red')  # маркеры машин

    annotations = [  # подписи со скоростью
        ax.text(
            0,
            -params['lane_width'] / 2 + 0.1,
            '',
            ha='center',
            va='bottom',
            fontsize=8,
            color='blue'
        )
        for _ in range(params['num_vehicles'])
    ]

    def update(frame):  # обновление каждого кадра
        t = times[frame]  # текущий момент времени
        xs = pivot_x.loc[t].values  # координаты X
        vs = pivot_v.loc[t].values  # скорости
        coords = np.column_stack((xs, np.zeros_like(xs)))  # координаты для маркеров
        scat.set_offsets(coords)  # ставим новые точки
        for i, txt in enumerate(annotations):  # обновляем подписи
            txt.set_position((xs[i], -params['lane_width'] / 2 + 0.1))
            txt.set_text(f"{vs[i]:.1f} м/с")
        ax.set_title(f"t = {t:.2f} с")  # время в заголовок
        return scat, *annotations  # вернуть всё для отрисовки

    ani = animation.FuncAnimation(  # создаём анимацию
        fig,
        update,
        frames=len(times),
        interval=params['interval'],
        blit=False
    )

    plt.tight_layout()  # компактно располагаем
    plt.show()  # показываем график


class App(tk.Tk):  # главное окно
    def __init__(self):
        super().__init__()  # инициализация окна
        self.title('IDM Симулятор')  # заголовок окна
        self.entries = {}  # словарь для хранения полей ввода
        self._build_ui()  # создаём интерфейс

    def _build_ui(self):
        sim_fr = ttk.LabelFrame(self, text='Параметры симуляции')  # рамка с вводами
        sim_fr.pack(fill='x', padx=10, pady=5)  # размещаем

        for name, lbl, default in [  # список всех параметров
            ('num_vehicles', 'Число машин', '30'),
            ('sim_time', 'Время симуляции (с)', '60'),
            ('dt', 'Шаг времени dt (с)', '0.05'),
            ('road_length', 'Длина дороги (м)', '1000'),
            ('speed_min', 'Мин. скорость (м/с)', '5'),
            ('speed_max', 'Макс. скорость (м/с)', '25'),
            ('first_speed', 'Скорость первой машины (опц.)', ''),
            ('car_length', 'Длина машины (м)', '5.0')
        ]:
            ttk.Label(sim_fr, text=lbl).pack(side='left')  # надпись
            var = tk.StringVar(value=default)  # переменная
            ttk.Entry(sim_fr, textvariable=var, width=8).pack(side='left', padx=(0, 5))
            self.entries[name] = var  # сохраняем

        dist_label = ttk.Label(sim_fr, text='Распределение позиций')  # подпись
        dist_label.pack(anchor='w', pady=(10, 0))
        dist_var = tk.StringVar(value='uniform')  # выпадающий список
        ttk.OptionMenu(
            sim_fr, dist_var, 'uniform',
            'uniform', 'random', 'normal', 'exponential', 'triangular'
        ).pack(anchor='w', padx=(0, 5), pady=(0, 5))
        self.entries['distribution'] = dist_var  # сохраняем выбор

        idm_fr = ttk.LabelFrame(self, text='Параметры модели IDM')  # рамка для IDM
        idm_fr.pack(fill='x', padx=10, pady=5)

        for name, lbl, default in [  # параметры IDM
            ('a_max', 'Макс. ускорение a_max', '1.0'),
            ('b', 'Комфортное торможение b', '1.5'),
            ('delta', 'Экспонента delta', '4.0'),
            ('s0', 'Мин. дистанция s0', '2.0'),
            ('T', 'Время реакции T', '1.5'),
            ('v0', 'Желаемая скорость v0 (м/с)', '30.0')
        ]:
            ttk.Label(idm_fr, text=lbl).pack(side='left')
            var = tk.StringVar(value=default)
            ttk.Entry(idm_fr, textvariable=var, width=8).pack(side='left', padx=(0, 5))
            self.entries[name] = var

        vis_fr = ttk.LabelFrame(self, text='Параметры визуализации')  # рамка для графика
        vis_fr.pack(fill='x', padx=10, pady=5)

        for name, lbl, default in [  # настройки отображения
            ('marker_size', 'Размер маркеров (px)', '200'),
            ('lane_width', 'Ширина полосы (м)', '3.5'),
            ('interval', 'Интервал кадров (мс)', '50')
        ]:
            ttk.Label(vis_fr, text=lbl).pack(side='left')
            var = tk.StringVar(value=default)
            ttk.Entry(vis_fr, textvariable=var, width=8).pack(side='left', padx=(0, 5))
            self.entries[name] = var

        ttk.Button(  # кнопка запуска
            self,
            text='Запустить симуляцию',
            command=self._on_run
        ).pack(pady=10)

    def _on_run(self):  # при нажатии кнопки
        try:
            params = {}
            for k, v in self.entries.items():  # проходим по всем полям
                if k == 'distribution':
                    params[k] = v.get()
                elif k == 'first_speed' and v.get().strip() == '':
                    params[k] = None
                elif '.' in v.get():
                    params[k] = float(v.get())
                else:
                    params[k] = int(v.get())

            idm_keys = ['a_max', 'b', 'delta', 's0', 'T', 'v0']  # выносим параметры IDM
            params['idm'] = {k: params.pop(k) for k in idm_keys}
            params['speed_range'] = (
                params.pop('speed_min'),
                params.pop('speed_max')
            )
            params['car_length'] = params.pop('car_length')
            params['interval'] = params.pop('interval')

        except Exception as e:
            messagebox.showerror('Ошибка', str(e))  # если ошибка — показать окно
            return

        self.destroy()  # закрыть окно
        run_simulation_and_animate(params)  # запускаем моделирование


if __name__ == '__main__':
    App().mainloop()  # запуск GUI
