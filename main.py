# main.py

import argparse
import configparser
import sys

from idm.simulation import TrafficSimulation


def read_simulation_config(config_path="config.ini"):
    """
    Считывает секцию [simulation] из config.ini.
    Возвращает словарь с ключами:
      num_vehicles, sim_time, dt, road_length, distribution, speed_min, speed_max.
    """
    parser = configparser.ConfigParser()
    try:
        with open(config_path, encoding="utf-8") as f:
            parser.read_file(f)
    except FileNotFoundError:
        sys.exit(f"Ошибка: файл '{config_path}' не найден.")
    except UnicodeDecodeError:
        sys.exit(f"Ошибка: неверная кодировка в '{config_path}'. Должно быть UTF-8.")

    if "simulation" not in parser:
        sys.exit("Ошибка: в config.ini отсутствует секция [simulation].")

    sim_conf = parser["simulation"]
    return {
        "num_vehicles": sim_conf.getint("num_vehicles", fallback=None),
        "sim_time": sim_conf.getfloat("sim_time", fallback=None),
        "dt": sim_conf.getfloat("dt", fallback=None),
        "road_length": sim_conf.getfloat("road_length", fallback=None),
        "distribution": sim_conf.get("distribution", fallback=None),
        "speed_min": sim_conf.getfloat("speed_min", fallback=None),
        "speed_max": sim_conf.getfloat("speed_max", fallback=None),
    }


def read_visual_config(config_path="config.ini"):
    """
    Считывает секцию [visual] из config.ini.
    Возвращает словарь с ключами:
      road_color, car_color, label_color,
      car_length, car_width, lane_width,
      frame_skip, annotation_fontsize,
      annotation_box_alpha, annotation_box_facecolor.
    """
    parser = configparser.ConfigParser()
    try:
        with open(config_path, encoding="utf-8") as f:
            parser.read_file(f)
    except FileNotFoundError:
        sys.exit(f"Ошибка: файл '{config_path}' не найден.")
    except UnicodeDecodeError:
        sys.exit(f"Ошибка: неверная кодировка в '{config_path}'. Должно быть UTF-8.")

    if "visual" not in parser:
        sys.exit("Ошибка: в config.ini отсутствует секция [visual].")

    vis_conf = parser["visual"]
    return {
        "road_color": vis_conf.get("road_color", fallback=None),
        "car_color": vis_conf.get("car_color", fallback=None),
        "label_color": vis_conf.get("label_color", fallback=None),
        "car_length": vis_conf.getfloat("car_length", fallback=None),
        "car_width": vis_conf.getfloat("car_width", fallback=None),
        "lane_width": vis_conf.getfloat("lane_width", fallback=None),
        "frame_skip": vis_conf.getint("frame_skip", fallback=None),
        "annotation_fontsize": vis_conf.getint("annotation_fontsize", fallback=None),
        "annotation_box_alpha": vis_conf.getfloat("annotation_box_alpha", fallback=None),
        "annotation_box_facecolor": vis_conf.get("annotation_box_facecolor", fallback=None),
    }


def main():
    parser = argparse.ArgumentParser(
        description="IDM Traffic Simulation (Python)."
    )
    subparsers = parser.add_subparsers(dest="command")

    # ---- ПАРСЕР ДЛЯ "simulate" ----
    parser_sim = subparsers.add_parser(
        "simulate", help="Запустить симуляцию и сохранить CSV"
    )
    parser_sim.add_argument(
        "--num_vehicles", type=int, help="Число автомобилей (int)"
    )
    parser_sim.add_argument(
        "--sim_time", type=float, help="Общее время симуляции (сек) (float)"
    )
    parser_sim.add_argument(
        "--dt", type=float, help="Шаг времени (сек) (float)"
    )
    parser_sim.add_argument(
        "--road_length", type=float, help="Длина дороги (м) (float)"
    )
    parser_sim.add_argument(
        "--distribution", type=str, choices=["uniform", "normal"],
        help="Тип распределения машин"
    )
    parser_sim.add_argument(
        "--speed_min", type=float, help="Минимальная начальная скорость (м/с)"
    )
    parser_sim.add_argument(
        "--speed_max", type=float, help="Максимальная начальная скорость (м/с)"
    )

    # ---- ПАРСЕР ДЛЯ "visualize_matplotlib" ----
    parser_viz = subparsers.add_parser(
        "visualize_matplotlib", help="Запустить анимацию через Matplotlib"
    )
    # Параметры симуляции (те же, что у simulate) – чтобы переопределить
    parser_viz.add_argument("--num_vehicles", type=int, help="Число автомобилей (int)")
    parser_viz.add_argument("--sim_time", type=float, help="Время симуляции (сек) (float)")
    parser_viz.add_argument("--dt", type=float, help="Шаг времени (сек) (float)")
    parser_viz.add_argument("--road_length", type=float, help="Длина дороги (м) (float)")
    parser_viz.add_argument(
        "--distribution", type=str, choices=["uniform", "normal"],
        help="Тип распределения машин"
    )
    parser_viz.add_argument("--speed_min", type=float, help="Минимальная начальная скорость (м/с)")
    parser_viz.add_argument("--speed_max", type=float, help="Максимальная начальная скорость (м/с)")

    # Параметры визуализации
    parser_viz.add_argument(
        "--road_color", type=str,
        help="Цвет дороги, RGB строка 'r,g,b' (0.0–1.0)"
    )
    parser_viz.add_argument(
        "--car_color", type=str,
        help="Цвет машин, RGB строка 'r,g,b' (0.0–1.0)"
    )
    parser_viz.add_argument(
        "--label_color", type=str,
        help="Цвет текста, RGB строка 'r,g,b' (0.0–1.0)"
    )
    parser_viz.add_argument(
        "--car_length", type=float, help="Длина машины (м)"
    )
    parser_viz.add_argument(
        "--car_width", type=float, help="Ширина машины (м)"
    )
    parser_viz.add_argument(
        "--lane_width", type=float, help="Ширина полосы (м)"
    )
    parser_viz.add_argument(
        "--frame_skip", type=int,
        help="Пропуск кадров (целое >=1) для ускорения анимации"
    )
    parser_viz.add_argument(
        "--annotation_fontsize", type=int, help="Размер шрифта подписи (int)"
    )
    parser_viz.add_argument(
        "--annotation_box_alpha", type=float,
        help="Прозрачность фона подписи (0.0–1.0)"
    )
    parser_viz.add_argument(
        "--annotation_box_facecolor", type=str,
        help="Цвет фона подписи, RGB строка 'r,g,b' (0.0–1.0)"
    )

    args = parser.parse_args()

    # Если команда не указана, показываем help
    if args.command is None:
        parser.print_help()
        sys.exit(0)

    # Читаем конфиги из config.ini
    sim_conf = read_simulation_config("config.ini")
    vis_conf = read_visual_config("config.ini")

    # ------- ОБРАБОТКА "simulate" -------
    if args.command == "simulate":
        # Приоритет: CLI > config.ini > (если пусто, выходим с ошибкой)
        num_vehicles = (
            args.num_vehicles
            if args.num_vehicles is not None
            else sim_conf["num_vehicles"]
        )
        sim_time = (
            args.sim_time
            if args.sim_time is not None
            else sim_conf["sim_time"]
        )
        dt = args.dt if args.dt is not None else sim_conf["dt"]
        road_length = (
            args.road_length
            if args.road_length is not None
            else sim_conf["road_length"]
        )
        distribution = (
            args.distribution
            if args.distribution is not None
            else sim_conf["distribution"]
        )
        speed_min = (
            args.speed_min
            if args.speed_min is not None
            else sim_conf["speed_min"]
        )
        speed_max = (
            args.speed_max
            if args.speed_max is not None
            else sim_conf["speed_max"]
        )

        # Проверяем, что все обязательные параметры заданы
        missing = []
        for k, v in [
            ("num_vehicles", num_vehicles),
            ("sim_time", sim_time),
            ("dt", dt),
            ("road_length", road_length),
            ("distribution", distribution),
            ("speed_min", speed_min),
            ("speed_max", speed_max),
        ]:
            if v is None:
                missing.append(k)
        if missing:
            sys.exit(f"Ошибка: не заданы параметры {missing} для команды simulate.")

        sim = TrafficSimulation(
            num_vehicles=num_vehicles,
            sim_time=sim_time,
            dt=dt,
            road_length=road_length,
            distribution=distribution,
            speed_range=(speed_min, speed_max)
        )
        sim.run()
        sim.save_csv(path="data/simulation_output.csv")
        print(
            f"Симуляция завершена: {num_vehicles=}  {sim_time=}  {dt=}  "
            f"{road_length=}  dist={distribution}  speed_range=({speed_min},{speed_max})."
        )
        print("CSV сохранён в data/simulation_output.csv")

    # ------- ОБРАБОТКА "visualize_matplotlib" -------
    elif args.command == "visualize_matplotlib":
        # Будем переопределять все параметры: симуляции и визуализации
        num_vehicles = (
            args.num_vehicles
            if args.num_vehicles is not None
            else sim_conf["num_vehicles"]
        )
        sim_time = (
            args.sim_time
            if args.sim_time is not None
            else sim_conf["sim_time"]
        )
        dt = args.dt if args.dt is not None else sim_conf["dt"]
        road_length = (
            args.road_length
            if args.road_length is not None
            else sim_conf["road_length"]
        )
        distribution = (
            args.distribution
            if args.distribution is not None
            else sim_conf["distribution"]
        )
        speed_min = (
            args.speed_min
            if args.speed_min is not None
            else sim_conf["speed_min"]
        )
        speed_max = (
            args.speed_max
            if args.speed_max is not None
            else sim_conf["speed_max"]
        )

        # Визуальные параметры
        road_color = (
            args.road_color
            if args.road_color is not None
            else vis_conf["road_color"]
        )
        car_color = (
            args.car_color if args.car_color is not None else vis_conf["car_color"]
        )
        label_color = (
            args.label_color
            if args.label_color is not None
            else vis_conf["label_color"]
        )
        car_length = (
            args.car_length
            if args.car_length is not None
            else vis_conf["car_length"]
        )
        car_width = (
            args.car_width
            if args.car_width is not None
            else vis_conf["car_width"]
        )
        lane_width = (
            args.lane_width
            if args.lane_width is not None
            else vis_conf["lane_width"]
        )
        frame_skip = (
            args.frame_skip
            if args.frame_skip is not None
            else vis_conf["frame_skip"]
        )
        annotation_fontsize = (
            args.annotation_fontsize
            if args.annotation_fontsize is not None
            else vis_conf["annotation_fontsize"]
        )
        annotation_box_alpha = (
            args.annotation_box_alpha
            if args.annotation_box_alpha is not None
            else vis_conf["annotation_box_alpha"]
        )
        annotation_box_facecolor = (
            args.annotation_box_facecolor
            if args.annotation_box_facecolor is not None
            else vis_conf["annotation_box_facecolor"]
        )

        # Проверяем, что все параметры заданы (нет None)
        missing_sim = []
        for k, v in [
            ("num_vehicles", num_vehicles),
            ("sim_time", sim_time),
            ("dt", dt),
            ("road_length", road_length),
            ("distribution", distribution),
            ("speed_min", speed_min),
            ("speed_max", speed_max),
        ]:
            if v is None:
                missing_sim.append(k)
        if missing_sim:
            sys.exit(
                f"Ошибка: не заданы параметры симуляции {missing_sim} "
                f"для команды visualize_matplotlib."
            )

        missing_vis = []
        for k, v in [
            ("road_color", road_color),
            ("car_color", car_color),
            ("label_color", label_color),
            ("car_length", car_length),
            ("car_width", car_width),
            ("lane_width", lane_width),
            ("frame_skip", frame_skip),
            ("annotation_fontsize", annotation_fontsize),
            ("annotation_box_alpha", annotation_box_alpha),
            ("annotation_box_facecolor", annotation_box_facecolor),
        ]:
            if v is None:
                missing_vis.append(k)
        if missing_vis:
            sys.exit(
                f"Ошибка: не заданы параметры визуализации {missing_vis} "
                f"для команды visualize_matplotlib."
            )

        # Запуск функции анимации, передаём все параметры
        from idm.matplotlib_visualization import run_matplotlib_visualization

        run_matplotlib_visualization(
            num_vehicles=num_vehicles,
            sim_time=sim_time,
            dt=dt,
            road_length=road_length,
            distribution=distribution,
            speed_min=speed_min,
            speed_max=speed_max,
            road_color=road_color,
            car_color=car_color,
            label_color=label_color,
            car_length=car_length,
            car_width=car_width,
            lane_width=lane_width,
            frame_skip=frame_skip,
            annotation_fontsize=annotation_fontsize,
            annotation_box_alpha=annotation_box_alpha,
            annotation_box_facecolor=annotation_box_facecolor
        )
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
