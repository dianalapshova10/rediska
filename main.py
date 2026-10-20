import math
import uvicorn
from fastapi import FastAPI

app = FastAPI(title="Robot API")

LIMIT = 10.0  # робот не может выйти за [-10, 10]


def normalize_angle(deg: float) -> float:
    """Приводит угол к диапазону (-180, 180]."""
    deg = deg % 360
    if deg > 180:
        deg -= 360
    return deg


class Robot:
    def __init__(self):
        self.x = 0.0
        self.y = 0.0
        self.grad_total = 0.0  # накопленный поворот относительно нормали (знаковый)

    # ---- вычисляемые свойства ----
    @property
    def grad(self) -> float:
        """Текущий угол относительно нормали, (-180, 180]."""
        return normalize_angle(self.grad_total)

    def state(self) -> dict:
        return {
            "x": round(self.x, 3),
            "y": round(self.y, 3),
            "grad": round(self.grad, 3),                    # относительно нормали, знаковый
            "grad_total": round(self.grad_total, 3),        # накопленный поворот
            "distance_from_start": round(math.hypot(self.x, self.y), 3),
        }


robot = Robot()


# ---------- Служебные ----------

@app.get("/")
def root():
    return {"status": "ok", "state": robot.state()}


@app.get("/position")
def position():
    """Текущее положение: x, y и угол относительно нормали (стартового положения)."""
    return robot.state()


@app.get("/state")
def state():
    """Алиас /position."""
    return robot.state()


@app.get("/reset")
def reset():
    """Вернуть робота в (0, 0) с углом 0° (как в начале работы программы)."""
    robot.x = 0.0
    robot.y = 0.0
    robot.grad_total = 0.0
    return robot.state()


# ---------- Движение ----------

@app.get("/turn")
def turn(deg: float):
    """
    Поворот на deg градусов.
    deg > 0 — вправо (по часовой), deg < 0 — влево (против часовой).
    """
    robot.grad_total += deg
    return {"action": "turn", "deg": deg, "state": robot.state()}


@app.get("/step")
def step(len_step: float):
    """
    Шаг на len_step вдоль текущего направления.
    len_step > 0 — вперёд, < 0 — назад.
    Координаты обрезаются по [-10, 10].
    """
    # используем накопленный угол для корректного направления
    rad = math.radians(robot.grad_total)
    dx = math.sin(rad) * len_step
    dy = math.cos(rad) * len_step

    new_x = robot.x + dx
    new_y = robot.y + dy

    robot.x = max(-LIMIT, min(LIMIT, new_x))
    robot.y = max(-LIMIT, min(LIMIT, new_y))

    hit_wall = (new_x != robot.x) or (new_y != robot.y)

    return {
        "action": "step",
        "len_step": len_step,
        "hit_wall": hit_wall,
        "state": robot.state(),
    }


# ---------- Удобные алиасы ----------

@app.get("/forward")
def forward(length: float = 1.0):
    return step(abs(length))


@app.get("/backward")
def backward(length: float = 1.0):
    return step(-abs(length))


@app.get("/right")
def right(deg: float = 90.0):
    return turn(abs(deg))


@app.get("/left")
def left(deg: float = 90.0):
    return turn(-abs(deg))


if __name__ == "__main__":
    uvicorn.run("main:app", host="127.0.0.1", port=10007, reload=True)