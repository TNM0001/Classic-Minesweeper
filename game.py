import tkinter as tk
from tkinter import messagebox
import random
import time

# Constants
COLOR_MAP = {
    1: "blue", 2: "green", 3: "red", 4: "darkblue",
    5: "brown", 6: "cyan", 7: "black", 8: "gray"
}

class MainMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Main Menu")
        self.root.configure(bg="black", padx=10, pady=10)

        self.frame = tk.Frame(self.root, bg="black", bd=5, relief=tk.RIDGE)
        self.frame.pack(pady=10)

        self.play_button = tk.Button(self.frame, text="Play", font=("Arial", 12, "bold"), command=self.play)
        self.play_button.pack(pady=10)

        self.about_button = tk.Button(self.frame, text="About", font=("Arial", 12, "bold"), command=self.about)
        self.about_button.pack(pady=10)

        self.exit_button = tk.Button(self.frame, text="Exit", font=("Arial", 12, "bold"), command=self.root.quit)
        self.exit_button.pack(pady=10)

    def play(self):
        self.frame.destroy()
        GameModeMenu(self.root)

    def about(self):
        messagebox.showinfo("Thanks for playing!", "Written in Python with Tkinter, by therealtnm on Discord, with love.")

class GameModeMenu:
    def __init__(self, root):
        self.root = root
        self.root.title("Select Difficulty")
        self.frame = tk.Frame(self.root, bg="black", bd=5, relief=tk.RIDGE)
        self.frame.pack(pady=10)

        self.easy_button = tk.Button(self.frame, text="Easy", font=("Arial", 12, "bold"), command=lambda: self.start_game(7, 7))
        self.easy_button.pack(pady=10)

        self.normal_button = tk.Button(self.frame, text="Normal", font=("Arial", 12, "bold"), command=lambda: self.start_game(10, 15))
        self.normal_button.pack(pady=10)

        self.hard_button = tk.Button(self.frame, text="Hard", font=("Arial", 12, "bold"), command=lambda: self.start_game(13, 25))
        self.hard_button.pack(pady=10)

    def start_game(self, grid_size, mine_count):
        self.frame.destroy()
        Minesweeper(self.root, grid_size, mine_count)

class Minesweeper:
    def __init__(self, root, grid_size, mine_count):
        self.root = root
        self.root.title("Classic Minesweeper")
        self.root.configure(bg="black", padx=10, pady=10)
        
        self.frame = tk.Frame(self.root, bg="black", bd=5, relief=tk.RIDGE)
        self.frame.pack(pady=10)
        
        self.grid_size = grid_size
        self.mine_count = mine_count
        self.flags = 0
        self.start_time = None
        self.game_over = False
        
        # HUD
        self.hud_frame = tk.Frame(self.root, bg="black", bd=5, relief=tk.RIDGE)
        self.hud_frame.pack(pady=10)
        
        self.mine_label = tk.Label(self.hud_frame, text=f"Mines: {self.mine_count}", font=("Arial", 12, "bold"), bg="black", fg="white")
        self.mine_label.pack(side=tk.LEFT, padx=40)
        
        self.timer_label = tk.Label(self.hud_frame, text="Time: 0", font=("Arial", 12, "bold"), bg="black", fg="white")
        self.timer_label.pack(side=tk.LEFT, padx=40)
        
        self.reset_button = tk.Button(self.hud_frame, text="Reset", font=("Arial", 12, "bold"), command=self.reset_game)
        self.reset_button.pack(side=tk.RIGHT, padx=40)
        
        self.board = [[None for _ in range(self.grid_size)] for _ in range(self.grid_size)]
        self.mines = set()
        self.generate_board()
        
        self.update_timer()
    
    def generate_board(self):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                btn = tk.Button(self.frame, width=2, height=1, font=("Arial", 12, "bold"), command=lambda r=row, c=col: self.reveal_cell(r, c))
                btn.bind("<Button-3>", lambda event, r=row, c=col: self.flag_cell(r, c))
                btn.grid(row=row, column=col)
                self.board[row][col] = {"button": btn, "is_mine": False, "is_revealed": False, "is_flagged": False, "count": 0}
        
        self.mines = set()
        while len(self.mines) < self.mine_count:
            r, c = random.randint(0, self.grid_size-1), random.randint(0, self.grid_size-1)
            if not self.board[r][c]["is_mine"]:
                self.board[r][c]["is_mine"] = True
                self.mines.add((r, c))
        
        for r in range(self.grid_size):
            for c in range(self.grid_size):
                if not self.board[r][c]["is_mine"]:
                    self.board[r][c]["count"] = self.count_adjacent_mines(r, c)
    
    def count_adjacent_mines(self, row, col):
        count = 0
        for dr in [-1, 0, 1]:
            for dc in [-1, 0, 1]:
                if (dr == 0 and dc == 0) or not (0 <= row+dr < self.grid_size) or not (0 <= col+dc < self.grid_size):
                    continue
                if self.board[row+dr][col+dc]["is_mine"]:
                    count += 1
        return count
    
    def reveal_cell(self, row, col):
        if self.game_over or self.board[row][col]["is_revealed"] or self.board[row][col]["is_flagged"]:
            return
        
        if self.start_time is None:
            self.start_time = time.time()
        
        cell = self.board[row][col]
        cell["is_revealed"] = True
        cell["button"].config(relief=tk.SUNKEN, state=tk.DISABLED)
        
        if cell["is_mine"]:
            cell["button"].config(text="💣", bg="red")
            self.end_game(False)
        else:
            if cell["count"] > 0:
                color = COLOR_MAP.get(cell["count"], "black")
                cell["button"].config(text=str(cell["count"]), fg=color)
            else:
                cell["button"].config(bg="lightgrey")
                for dr in [-1, 0, 1]:
                    for dc in [-1, 0, 1]:
                        nr, nc = row + dr, col + dc
                        if 0 <= nr < self.grid_size and 0 <= nc < self.grid_size:
                            self.reveal_cell(nr, nc)
        
        self.check_win()
    
    def flag_cell(self, row, col):
        if self.game_over or self.board[row][col]["is_revealed"]:
            return
        
        cell = self.board[row][col]
        if cell["is_flagged"]:
            cell["is_flagged"] = False
            cell["button"].config(text="")
            self.flags -= 1
        else:
            if self.flags < self.mine_count:
                cell["is_flagged"] = True
                cell["button"].config(text="🚩", fg="red")
                self.flags += 1
        
        self.mine_label.config(text=f"Mines: {self.mine_count - self.flags}")
    
    def check_win(self):
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                if not self.board[row][col]["is_mine"] and not self.board[row][col]["is_revealed"]:
                    return
        self.end_game(True)
    
    def end_game(self, won):
        self.game_over = True
        for row in range(self.grid_size):
            for col in range(self.grid_size):
                cell = self.board[row][col]
                if not cell["is_revealed"] and not cell["is_mine"]:
                    color = COLOR_MAP.get(cell["count"], "black")
                    cell["button"].config(text=str(cell["count"]) if cell["count"] > 0 else "", fg=color)
        
        if won:
            self.root.title("Congrats, you've won!")
        else:
            for r, c in self.mines:
                self.board[r][c]["button"].config(text="💣", bg="red")
            self.root.title("Game over, try again!")
    
    def update_timer(self):
        if self.start_time and not self.game_over:
            elapsed = int(time.time() - self.start_time)
            self.timer_label.config(text=f"Time: {elapsed}")
        self.root.after(1000, self.update_timer)
    
    def reset_game(self):
        self.frame.destroy()
        self.frame = tk.Frame(self.root)
        self.frame.pack()
        self.mine_count = self.mine_count
        self.flags = 0
        self.start_time = None
        self.game_over = False
        self.mine_label.config(text=f"Mines: {self.mine_count}")
        self.timer_label.config(text="Time: 0")
        self.generate_board()
        self.root.title("Classic Minesweeper")

if __name__ == "__main__":
    root = tk.Tk()
    main_menu = MainMenu(root)
    root.mainloop()
