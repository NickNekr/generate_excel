import os
import time
from solve import solve
from config import Config


def tear_down_func():
    os.remove(Config.Const.output_png_file)
    os.remove(Config.Const.output_excel_file)


def measure_time(env, iterations):
    os.environ["FLASK_ENV"] = env
    total_execution_time = 0
    for i in range(iterations):
        start_time = time.time()

        solve.main()

        end_time = time.time()
        execution_time = end_time - start_time

        total_execution_time += execution_time

        tear_down_func()

    return total_execution_time / iterations


print(f"Среднее время выполнения для prod: {measure_time(Config.Const.prod, 5)} секунд")
print(f"Среднее время выполнения для dev: {measure_time(Config.Const.dev, 5)} секунд")
