import tkinter as tk
import random


class SpaceShooter:
    def __init__(self, root):
        self.root = root
        self.root.title("Космический шутер")
        self.root.resizable(False, False)

        self.width = 500
        self.height = 600

        self.canvas = tk.Canvas(root, width=self.width, height=self.height, bg="#0f172a")
        self.canvas.pack()

        # Игровые параметры
        self.player_hp = 3
        self.score = 0
        self.game_active = True

        # Списки для отслеживания объектов на экране
        self.bullets = []
        self.asteroids = []

        # Частота появления метеоритов (миллисекунды)
        self.spawn_rate = 1000

        self.create_player()
        self.create_ui()

        # Привязка управления
        self.canvas.bind("<Motion>", self.move_player)
        self.root.bind("<space>", self.shoot)
        self.canvas.focus_set()

        # Запуск игровых циклов
        self.game_loop()
        self.spawn_asteroids_loop()

    def create_player(self):
        # Рисуем космический корабль (полигон в форме треугольника/истребителя)
        self.player_width = 40
        self.player = self.canvas.create_polygon(
            self.width // 2, self.height - 50,
            self.width // 2 - self.player_width // 2, self.height - 20,
            self.width // 2 + self.player_width // 2, self.height - 20,
            fill="#38bdf8", outline="#0284c7", width=2
        )

    def create_ui(self):
        # Текст очков
        self.score_text = self.canvas.create_text(
            60, 25, text=f"Очки: {self.score}",
            fill="white", font=("Arial", 14, "bold")
        )
        # Текст здоровья
        self.hp_text = self.canvas.create_text(
            self.width - 60, 25, text=f"Жизни: {self.player_hp}",
            fill="#ef4444", font=("Arial", 14, "bold")
        )

    def move_player(self, event):
        if not self.game_active:
            return
        # Корабль плавно следует за мышкой только по горизонтали
        x = event.x
        if x < self.player_width // 2:
            x = self.player_width // 2
        elif x > self.width - self.player_width // 2:
            x = self.width - self.player_width // 2

        self.canvas.coords(
            self.player,
            x, self.height - 50,
               x - self.player_width // 2, self.height - 20,
               x + self.player_width // 2, self.height - 20
        )

    def shoot(self, event):
        if not self.game_active:
            return
        # Получаем координаты носа корабля
        player_pos = self.canvas.coords(self.player)
        nose_x = player_pos[0]
        nose_y = player_pos[1]

        # Создаем лазерный снаряд
        bullet = self.canvas.create_rectangle(
            nose_x - 2, nose_y - 15,
            nose_x + 2, nose_y,
            fill="#facc15", outline=""
        )
        self.bullets.append(bullet)

    def spawn_asteroids_loop(self):
        if not self.game_active:
            return

        # Случайный размер и положение метеорита
        size = random.randint(20, 50)
        x1 = random.randint(0, self.width - size)
        y1 = -size

        # Рисуем метеорит (овал)
        asteroid = self.canvas.create_oval(
            x1, y1, x1 + size, y1 + size,
            fill="#64748b", outline="#475569", width=2
        )

        # Задаем ему индивидуальную скорость
        speed = random.uniform(2.0, 5.0)

        # Сохраняем в список как словарь
        self.asteroids.append({"id": asteroid, "speed": speed, "size": size})

        # Постепенно ускоряем появление метеоритов по ходу игры
        if self.spawn_rate > 300:
            self.spawn_rate -= 10

        self.root.after(self.spawn_rate, self.spawn_asteroids_loop)

    def game_loop(self):
        if not self.game_active:
            return

        # 1. Двигаем снаряды вверх
        for bullet in self.bullets[:]:
            self.canvas.move(bullet, 0, -8)
            b_pos = self.canvas.coords(bullet)
            # Удаляем снаряд, если он улетел за экран
            if b_pos[1] < 0:
                self.canvas.delete(bullet)
                self.bullets.remove(bullet)

        # 2. Двигаем метеориты вниз
        for ast in self.asteroids[:]:
            self.canvas.move(ast["id"], 0, ast["speed"])
            a_pos = self.canvas.coords(ast["id"])

            # Если метеорит пролетел мимо игрока вниз
            if a_pos[1] > self.height:
                self.canvas.delete(ast["id"])
                self.asteroids.remove(ast)
                continue

            # 3. Проверка столкновения метеорита с кораблем
            p_pos = self.canvas.coords(self.player)
            if self.check_collision(a_pos, p_pos):
                self.player_hp -= 1
                self.canvas.itemconfig(self.hp_text, text=f"Жизни: {self.player_hp}")
                self.canvas.delete(ast["id"])
                self.asteroids.remove(ast)

                if self.player_hp <= 0:
                    self.end_game()
                    return
                continue

            # 4. Проверка столкновения снарядов с метеоритами (Многие ко многим)
            for bullet in self.bullets[:]:
                b_pos = self.canvas.coords(bullet)
                if self.check_collision(b_pos, a_pos):
                    # Удаляем оба объекта
                    self.canvas.delete(bullet)
                    if bullet in self.bullets: self.bullets.remove(bullet)

                    self.canvas.delete(ast["id"])
                    if ast in self.asteroids: self.asteroids.remove(ast)

                    # Начисляем очки в зависимости от размера (чем меньше, тем сложнее попасть)
                    self.score += 10 if ast["size"] > 35 else 20
                    self.canvas.itemconfig(self.score_text, text=f"Очки: {self.score}")
                    break

        self.root.after(16, self.game_loop)

    def check_collision(self, pos1, pos2):
        # Простая и надежная проверка пересечения двух bounding box-ов (AABB)
        if len(pos1) < 4 or len(pos2) < 4: return False
        return not (pos1[2] < pos2[0] or pos1[0] > pos2[2] or
                    pos1[3] < pos2[1] or pos1[1] > pos2[3])

    def end_game(self):
        self.game_active = False
        self.canvas.create_text(
            self.width // 2, self.height // 2 - 30,
            text="КОСМИЧЕСКИЙ КОРАБЛЬ\nУНИЧТОЖЕН",
            fill="#ef4444", font=("Arial", 24, "bold"), justify="center"
        )

        # Создаем красивую кнопку перезапуска
        self.restart_btn = tk.Button(
            self.root, text="Играть снова", font=("Arial", 12, "bold"),
            bg="#38bdf8", fg="white", activebackground="#0284c7",
            command=self.restart_game
        )
        self.canvas.create_window(self.width // 2, self.height // 2 + 40, window=self.restart_btn)

    def restart_game(self):
        # Очищаем всё
        self.canvas.destroy()
        if hasattr(self, 'restart_btn'):
            self.restart_btn.destroy()

        # Сброс параметров
        self.player_hp = 3
        self.score = 0
        self.spawn_rate = 1000
        self.bullets = []
        self.asteroids = []
        self.game_active = True

        # Перезапуск холста и циклов
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="#0f172a")
        self.canvas.pack()
        self.create_player()
        self.create_ui()
        self.canvas.bind("<Motion>", self.move_player)
        self.canvas.focus_set()

        self.game_loop()
        self.spawn_asteroids_loop()


if __name__ == "__main__":
    root = tk.Tk()
    app = SpaceShooter(root)
    root.mainloop()