import random
import tkinter as tk


class SnakeGame:
    def __init__(self, root: tk.Tk) -> None:
        """Initialize the window, input bindings, and default game settings."""
        self.root = root
        self.root.title("Snake")
        self.width = 1500
        self.height = 1000
        self.cell_size = 30 
        self.base_speed_ms = 200
        self.min_speed_ms = 100

        self.canvas = tk.Canvas(
            root,
            width=self.width,
            height=self.height,
            bg="#111111",
            highlightthickness=0,
        )
        self.canvas.pack()

        self.root.bind("<Up>", lambda _: self.change_direction("Up"))
        self.root.bind("<Down>", lambda _: self.change_direction("Down"))
        self.root.bind("<Left>", lambda _: self.change_direction("Left"))
        self.root.bind("<Right>", lambda _: self.change_direction("Right"))
        self.root.bind("w", lambda _: self.change_direction("Up"))
        self.root.bind("s", lambda _: self.change_direction("Down"))
        self.root.bind("a", lambda _: self.change_direction("Left"))
        self.root.bind("d", lambda _: self.change_direction("Right"))
        self.root.bind("<space>", lambda _: self.restart_if_game_over())

        self.direction_vectors = {
            "Up": (0, -1),
            "Down": (0, 1),
            "Left": (-1, 0),
            "Right": (1, 0),
        }
        self.opposites = {
            "Up": "Down",
            "Down": "Up",
            "Left": "Right",
            "Right": "Left",
        }

        self.job_id = None
        self.reset_game()

    def reset_game(self) -> None:
        """Reset all game state to a new run and start the update loop."""
        cols = self.width // self.cell_size
        rows = self.height // self.cell_size
        center_x = cols // 2
        center_y = rows // 2

        self.snake = [
            (center_x, center_y),
            (center_x - 1, center_y),
            (center_x - 2, center_y),
        ]
        self.direction = "Right"
        self.next_direction = "Right"
        self.food = self.spawn_food()
        self.score = 0
        self.game_over = False
        self.speed_ms = self.base_speed_ms

        if self.job_id is not None:
            self.root.after_cancel(self.job_id)
            self.job_id = None

        self.draw()
        self.schedule_next_tick()

    def restart_if_game_over(self) -> None:
        """Restart the game only when the current run has ended."""
        if self.game_over:
            self.reset_game()

    def change_direction(self, new_direction: str) -> None:
        """Update movement direction unless it is invalid or the game is over."""
        if self.game_over:
            return
        if new_direction == self.opposites[self.direction]:
            return
        self.next_direction = new_direction

    def spawn_food(self) -> tuple[int, int]:
        """Return a random empty grid cell for the next food position."""
        cols = self.width // self.cell_size
        rows = self.height // self.cell_size
        available = [
            (x, y)
            for x in range(cols)
            for y in range(rows)
            if (x, y) not in self.snake
        ]
        return random.choice(available)

    def schedule_next_tick(self) -> None:
        """Schedule the next frame update based on the current speed."""
        self.job_id = self.root.after(self.speed_ms, self.tick)

    def tick(self) -> None:
        """Advance one game step: move, collide, eat, redraw, and reschedule."""
        if self.game_over:
            return

        self.direction = self.next_direction
        dx, dy = self.direction_vectors[self.direction]
        head_x, head_y = self.snake[0]
        new_head = (head_x + dx, head_y + dy)

        if self.hits_wall(new_head) or self.hits_self(new_head):
            self.game_over = True
            self.draw()
            return

        self.snake.insert(0, new_head)

        if new_head == self.food:
            self.score += 1
            self.food = self.spawn_food()
            self.speed_ms = max(self.min_speed_ms, self.base_speed_ms - self.score * 2)
        else:
            self.snake.pop()

        self.draw()
        self.schedule_next_tick()

    def hits_wall(self, pos: tuple[int, int]) -> bool:
        """Check whether a position is outside the playable board."""
        x, y = pos
        cols = self.width // self.cell_size
        rows = self.height // self.cell_size
        return x < 0 or y < 0 or x >= cols or y >= rows

    def hits_self(self, pos: tuple[int, int]) -> bool:
        """Check whether a position overlaps with the snake body."""
        return pos in self.snake

    def draw(self) -> None:
        """Render the current frame: snake, food, score, and game-over overlay."""
        self.canvas.delete("all")

        food_x, food_y = self.food
        self.draw_cell(food_x, food_y, "#ff5f57")

        for i, (x, y) in enumerate(self.snake):
            color = "#33d17a" if i == 0 else "#26a269"
            self.draw_cell(x, y, color)

        self.canvas.create_text(
            10,
            10,
            anchor="nw",
            fill="#f6f5f4",
            font=("Consolas", 14, "bold"),
            text=f"Score: {self.score}",
        )

        if self.game_over:
            self.canvas.create_rectangle(90, 140, 510, 260, fill="#1f1f1f", outline="#888888")
            self.canvas.create_text(
                self.width // 2,
                180,
                fill="#ffffff",
                font=("Consolas", 22, "bold"),
                text="Game Over",
            )
            self.canvas.create_text(
                self.width // 2,
                220,
                fill="#d0d0d0",
                font=("Consolas", 12),
                text="Press SPACE to restart",
            )

    def draw_cell(self, x: int, y: int, color: str) -> None:
        """Draw one grid cell at board coordinates with the given fill color."""
        x1 = x * self.cell_size
        y1 = y * self.cell_size
        x2 = x1 + self.cell_size
        y2 = y1 + self.cell_size
        self.canvas.create_rectangle(x1, y1, x2, y2, fill=color, outline="#1b1b1b")


def main() -> None:
    """Create the app window and start the Tkinter event loop."""
    root = tk.Tk()
    SnakeGame(root)
    root.resizable(False, False)
    root.mainloop()


if __name__ == "__main__":
    main()
