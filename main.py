import time
import psutil
import tkinter as tk
from tkinter import ttk
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from collections import deque
from tkinter import filedialog

class Benchmark:
    def __init__(self, benchmark_window):
        self.benchmark_window = benchmark_window
        self.benchmark_window.title("BENCHMARK")

        self.benchmark_label = tk.Label(benchmark_window, text="BENCHMARK WINDOW")
        self.benchmark_label.pack(pady=10)

        self.start_button = tk.Button(benchmark_window, text="START BENCHMARK", command=self.start_benchmark)
        self.start_button.pack(pady=5)

        self.stop_button = tk.Button(benchmark_window, text="STOP BENCHMARK", command=self.stop_benchmark,
                                     state=tk.DISABLED)
        self.stop_button.pack(pady=5)

        self.save_button = tk.Button(benchmark_window, text="SAVE GRAPHS", command=self.save_graphs)
        self.save_button.pack(pady=5)

        self.timer_label = tk.Label(benchmark_window, text="Timer: 0 s")
        self.timer_label.pack(pady=10)

        self.cpu_usage_graph = RealTimeGraph(benchmark_window, "CPU USAGE", "Time (s)", "Usage (%)")
        self.cpu_usage_graph.pack(pady=10, expand=True, fill="both")

        self.mem_usage_graph = RealTimeGraph(benchmark_window, "RAM USAGE", "Time (s)", "Usage (%)")
        self.mem_usage_graph.pack(pady=10, expand=True, fill="both")

        self.running = False
        self.start_time = 0

    def start_benchmark(self):
        self.running = True
        self.start_time = time.time()
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        self.update_timer()
        self.update_graphs()

    def stop_benchmark(self):
        self.running = False
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)

    def save_graphs(self):
        self.cpu_usage_graph.save_graph()
        self.mem_usage_graph.save_graph()

    def update_timer(self):
        if self.running:
            elapsed_time = time.time() - self.start_time
            self.timer_label.config(text=f"Timer: {elapsed_time:.2f} s")
            self.benchmark_window.after(100, self.update_timer)

    def update_graphs(self):
        if self.running:
            cpu_usage = psutil.cpu_percent()
            mem_usage = psutil.virtual_memory().percent

            self.cpu_usage_graph.add_point(time.time() - self.start_time, cpu_usage)
            self.mem_usage_graph.add_point(time.time() - self.start_time, mem_usage)

            self.benchmark_window.after(1000, self.update_graphs)


class RealTimeGraph(tk.Frame):
    def __init__(self, parent, title, x_label, y_label):
        tk.Frame.__init__(self, parent)

        self.title = title
        self.x_label = x_label
        self.y_label = y_label
        self.x_data = deque()  # Store all data points
        self.y_data = deque()

        self.figure = Figure(figsize=(5, 3), dpi=100)
        self.subplot = self.figure.add_subplot(1, 1, 1)
        self.subplot.set_title(self.title)
        self.subplot.set_xlabel(self.x_label)
        self.subplot.set_ylabel(self.y_label)
        self.line, = self.subplot.plot(self.x_data, self.y_data)

        self.canvas = FigureCanvasTkAgg(self.figure, self)
        self.canvas.get_tk_widget().pack(expand=True, fill="both")

    def add_point(self, x, y):
        self.x_data.append(x)
        self.y_data.append(y)
        self.line.set_data(self.x_data, self.y_data)
        self.subplot.relim()
        self.subplot.autoscale_view()
        self.canvas.draw()

    def save_graph(self):
        file_path = filedialog.asksaveasfilename(defaultextension=".png", filetypes=[("PNG files", "*.png")])
        if file_path:
            self.figure.savefig(file_path)
            print(f"Graph saved as {file_path}")

def display_usage(cpu_usage, mem_usage):
    cpu_progressbar['value'] = cpu_usage
    cpu_label['text'] = f"CPU USAGE: {cpu_usage:.2f}%"

    mem_progressbar['value'] = mem_usage
    mem_label['text'] = f"RAM USAGE: {mem_usage:.2f}%"

def update_usage():
    cpu_usage = psutil.cpu_percent()
    mem_usage = psutil.virtual_memory().percent

    display_usage(cpu_usage, mem_usage)
    root.after(500, update_usage)

def open_benchmark_window():
    benchmark_window = tk.Toplevel(root)
    benchmark = Benchmark(benchmark_window)

root = tk.Tk()
root.title("HARDWARE USAGE")

window_width = 400
window_height = 250
screen_width = root.winfo_screenwidth()
screen_height = root.winfo_screenheight()
x = (screen_width // 2) - (window_width // 2)
y = (screen_height // 2) - (window_height // 2)
root.geometry(f"{window_width}x{window_height}+{x}+{y}")

cpu_label = tk.Label(root, text="CPU USAGE: 0.00%")
cpu_label.pack(pady=5)

cpu_progressbar = ttk.Progressbar(root, orient="horizontal", mode="determinate")
cpu_progressbar.pack(fill="both", expand=True, padx=50, pady=5)

mem_label = tk.Label(root, text="RAM USAGE: 0.00%")
mem_label.pack(pady=5)

mem_progressbar = ttk.Progressbar(root, orient="horizontal", mode="determinate")
mem_progressbar.pack(fill="both", expand=True, padx=50, pady=5)

benchmark_button = tk.Button(root, text="BENCHMARK", command=open_benchmark_window)
benchmark_button.pack(pady=10)

update_usage()

root.mainloop()
