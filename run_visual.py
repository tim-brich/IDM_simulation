# run_visual.py

"""
Отдельный скрипт для запуска 3D-анимации через VPython.
"""

from idm.matplotlib_visualization import run_matplotlib_visualization

if __name__ == "__main__":
    # Жёстко задаём параметры (можете поменять числа, но начинать с этих удобно):
    N = 5           # число автомобилей
    SIM_TIME = 30   # время симуляции (сек)
    DT = 0.05       # шаг времени (сек)
    ROAD_LEN = 500  # длина дороги (м)

    run_matplotlib_visualization(
        num_vehicles=N,
        sim_time=SIM_TIME,
        dt=DT,
        road_length=ROAD_LEN
    )
