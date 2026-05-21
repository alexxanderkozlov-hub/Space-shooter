import tkinter as tk
import random


class SpaceShooter:
    def __init__(self, root):
        self.root = root
        self.root.title("Космический шутер")
        self.root.resizable(False, False)

        self.width = 500
        self.height = 600

        # Параметры уровней сложности: (минимальная_скорость, максимальная_скорость, начальный_спавнрейт)
        self.difficulty_settings = {
            "easy": {"min_spd": 1.5, "max_spd": 3.0, "spawn": 1200},
            "medium": {"min_spd": 3.0, "max_spd": 5.0, "spawn": 800},
            "hard": {"min_spd": 5.0, "max_spd": 8.0, "spawn": 500}
        }

        self.current_difficulty = "medium"
        self.game_active = False

        # Списки для игровых объектов
        self.bullets = []
        self.asteroids = []

        # Запускаем главное меню
        self.create_menu()

    def create_menu(self):
        # Контейнер стартового меню
        self.menu_frame = tk.Frame(self.root, padx=50, pady=60)
        self.menu_frame.pack()

        title_label = tk.Label(
            self.menu_frame,
            text="КОСМИЧЕСКИЙ ШУТЕР",
            font=("Arial", 20, "bold"),
            pady=15
        )
        title_label.pack()

        desc_label = tk.Label(
            self.menu_frame,
            text="Выберите уровень сложности:",
            font=("Arial", 11),
            pady=10
        )
        desc_label.pack()

        # Кнопки меню
        easy_btn = tk.Button(
            self.menu_frame, text="Легкий (Релакс)", font=("Arial", 11),
            width=25, height=2, bg="#2ecc71", fg="white", activebackground="#27ae60",
            command=lambda: self.start_game("easy")
        )
        easy_btn.pack(pady=5)

        medium_btn = tk.Button(
            self.menu_frame, text="Средний (Канон)", font=("Arial", 11),
            width=25, height=2, bg="#f1c40f", fg="white", activebackground="#d35400",
            command=lambda: self.start_game("medium")
        )
        medium_btn.pack(pady=5)

        hard_btn = tk.Button(
            self.menu_frame, text="Хард (Армагеддон!)", font=("Arial", 11),
            width=25, height=2, bg="#e74c3c", fg="white", activebackground="#c0392b",
            command=lambda: self.start_game("hard")
        )
        hard_btn.pack(pady=5)

    def start_game(self, difficulty):
        self.current_difficulty = difficulty
        self.player_hp = 3
        self.score = 0
        self.bullets = []
        self.asteroids = []

        # Берем настройки из словаря
        self.spawn_rate = self.difficulty_settings[difficulty]["spawn"]

        # Прячем меню
        self.menu_frame.pack_forget()

        # Игровой холст
        self.canvas = tk.Canvas(self.root, width=self.width, height=self.height, bg="#0f172a")
        self.canvas.pack()

        self.create_player()
        self.create_ui()

        # Управление
        self.canvas.bind("<Motion>", self.move_player)
        self.root.bind("<space>", self.shoot)
        self.canvas.focus_set()

        # Активация игровых циклов
        self.game_active = True
        self.game_loop()
        self.spawn_asteroids_loop()

    def create_player(self):
        self.player_width = 40
        self.player = self.canvas.create_polygon(
            self.width // 2, self.height - 50,
            self.width // 2 - self.player_width // 2, self.height - 20,
            self.width // 2 + self.player_width // 2, self.height - 20,
            fill="#38bdf8", outline="#0284c7", width=2
        )

    def create_ui(self):
        self.score_text = self.canvas.create_text(
            60, 25, text=f"Очки: {self.score}",
            fill="white", font=("Arial", 14, "bold")
        )
        self.hp_text = self.canvas.create_text(
            self.width - 60, 25, text=f"Жизни: {self.player_hp}",
            fill="#ef4444", font=("Arial", 14, "bold")
        )

    def move_player(self, event):
        if not self.game_active:
            return
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
        player_pos = self.canvas.coords(self.player)
        if not player_pos: return

        nose_x = player_pos[0]
        nose_y = player_pos[1]

        bullet = self.canvas.create_rectangle(
            nose_x - 2, nose_y - 15,
            nose_x + 2, nose_y,
            fill="#facc15", outline=""
        )
        self.bullets.append(bullet)

    def spawn_asteroids_loop(self):
        if not self.game_active:
            return

        # Настройки скорости текущей сложности
        settings = self.difficulty_settings[self.current_difficulty]

        size = random.randint(20, 50)
        x1 = random.randint(0, self.width - size)
        y1 = -size

        asteroid = self.canvas.create_oval(
            x1, y1, x1 + size, y1 + size,
            fill="#64748b", outline="#475569", width=2
        )

        speed = random.uniform(settings["min_spd"], settings["max_spd"])
        self.asteroids.append({"id": asteroid, "speed": speed, "size": size})

        # Постепенное нарастание темпа (ограничение до 200мс)
        if self.spawn_rate > 200:
            self.spawn_rate -= 8

        self.root.after(self.spawn_rate, self.spawn_asteroids_loop)

    def game_loop(self):
        if not self.game_active:
            return

        # 1. Движение снарядов
        for bullet in self.bullets[:]:
            self.canvas.move(bullet, 0, -8)
            b_pos = self.canvas.coords(bullet)
            if b_pos and b_pos[1] < 0:
                self.canvas.delete(bullet)
                self.bullets.remove(bullet)

        # 2. Движение метеоритов
        p_pos = self.canvas.coords(self.player)

        for ast in self.asteroids[:]:
            self.canvas.move(ast["id"], 0, ast["speed"])
            a_pos = self.canvas.coords(ast["id"])

            if not a_pos:
                continue

            # Вылетел за нижний край
            if a_pos[1] > self.height:
                self.canvas.delete(ast["id"])
                self.asteroids.remove(ast)
                continue

            # Столкновение метеорита с игроком
            if p_pos and self.check_collision(a_pos, p_pos):
                self.player_hp -= 1
                self.canvas.itemconfig(self.hp_text, text=f"Жизни: {self.player_hp}")
                self.canvas.delete(ast["id"])
                self.asteroids.remove(ast)

                if self.player_hp <= 0:
                    self.end_game()
                    return
                continue

            # Столкновение снарядов с метеоритом
            for bullet in self.bullets[:]:
                b_pos = self.canvas.coords(bullet)
                if b_pos and self.check_collision(b_pos, a_pos):
                    self.canvas.delete(bullet)
                    if bullet in self.bullets: self.bullets.remove(bullet)

                    self.canvas.delete(ast["id"])
                    if ast in self.asteroids: self.asteroids.remove(ast)

                    self.score += 10 if ast["size"] > 35 else 20
                    self.canvas.itemconfig(self.score_text, text=f"Очки: {self.score}")
                    break

        self.root.after(16, self.game_loop)

    def check_collision(self, pos1, pos2):
        if len(pos1) < 4 or len(pos2) < 4: return False
        return not (pos1[2] < pos2[0] or pos1[0] > pos2[2] or
                    pos1[3] < pos2[1] or pos1[1] > pos2[3])

    def end_game(self):
        self.game_active = False

        # Вывод текста окончания
        self.canvas.create_text(
            self.width // 2, self.height // 2 - 30,
            text="КОРАБЛЬ УНИЧТОЖЕН",
            fill="#ef4444", font=("Arial", 24, "bold")
        )

        # Кнопка возврата в меню на холсте
        self.return_btn = tk.Button(
            self.root, text="В главное меню", font=("Arial", 12, "bold"),
            bg="#38bdf8", fg="white", activebackground="#0284c7",
            command=self.reset_to_menu
        )
        self.canvas.create_window(self.width // 2, self.height // 2 + 30, window=self.return_btn)

    def reset_to_menu(self):
        # Полностью очищаем холст и отвязываем события
        self.canvas.unbind("<Motion>")
        self.root.unbind("<space>")
        self.canvas.destroy()

        # Очищаем массивы
        self.bullets = []
        self.asteroids = []
        self.game_active = False

        # Отрисовываем заново меню выбора сложности
        self.create_menu()


if __name__ == "__main__":
    root = tk.Tk()
    app = SpaceShooter(root)
    root.mainloop()