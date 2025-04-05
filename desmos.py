import tkinter as tk
from tkinter import filedialog
from PIL import Image, ImageTk
import time
import numpy as np

class DrawApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Draw and Export to Desmos")

        self.canvas_width = 800
        self.canvas_height = 600

        self.canvas = tk.Canvas(root, bg='white', width=self.canvas_width, height=self.canvas_height)
        self.canvas.pack()

        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.sampling_interval = 0.01  # Adjustable sampling interval (in seconds)
        self.sampling = False
        self.start_time = None
        self.last_sample_time = 0

        self.strokes = []
        self.current_stroke = None
        self.final_time = 0
        self.output_lines = []

        self.terminate_button = tk.Button(root, text="Terminate", command=self.on_terminate)
        self.terminate_button.pack(pady=5)

        self.image_button = tk.Button(root, text="Upload Image", command=self.process_image)
        self.image_button.pack(pady=5)

    def on_press(self, event):
        if self.start_time is None:
            self.start_time = time.time()

        self.current_stroke = []
        self.last_sample_time = time.time()
        t = self.last_sample_time - self.start_time
        self.current_stroke.append((t, event.x, event.y))
        self.sampling = True
        self.sample()

    def sample(self):
        if not self.sampling:
            return
        now = time.time()
        if now - self.last_sample_time >= self.sampling_interval:
            x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
            y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
            t = now - self.start_time
            self.current_stroke.append((t, x, y))
            if len(self.current_stroke) >= 2:
                _, px, py = self.current_stroke[-2]
                self.canvas.create_line(px, py, x, y, fill="black", width=2)
            self.last_sample_time = now
        self.root.after(int(self.sampling_interval * 1000), self.sample)

    def on_release(self, event):
        self.sampling = False
        t = time.time() - self.start_time
        self.current_stroke.append((t, event.x, event.y))
        self.strokes.append(self.current_stroke)
        self.final_time = t
        self.current_stroke = None

    def on_terminate(self):
        for stroke in self.strokes:
            for i in range(len(stroke) - 1):
                t0, x0, y0 = stroke[i]
                tf, x1, y1 = stroke[i + 1]
                y0 = self.canvas_height - y0
                y1 = self.canvas_height - y1
                t0 /= self.final_time
                tf /= self.final_time
                dx = x1 - x0
                dy = y1 - y0
                f_str = f"f(t,{t0:.6f},{tf:.6f},{dx:.6f},{x0:.6f})"
                g_str = f"g(t,{t0:.6f},{tf:.6f},{dy:.6f},{y0:.6f})"
                self.output_lines.append(f"({f_str}, {g_str})"+" { 0 < t < 1 }")

        with open("output.txt", "w") as f:
            f.write("\n".join(self.output_lines))

        print("Output saved to output.txt")
        print("Final time recorded:", self.final_time)
        self.root.destroy()

    def process_image(self):
        file_path = filedialog.askopenfilename()
        if not file_path:
            return

        img = Image.open(file_path).convert('L')  # grayscale
        arr = np.array(img)

        binary = arr < 128  # black pixel = True
        h, w = binary.shape

        visited = np.zeros((h, w), dtype=bool)
        for y in range(0, h, 4):
            for x in range(w):
                if binary[y, x] and not visited[y, x]:
                    # try vertical line
                    length = 0
                    while y + length < h and binary[y + length, x]:
                        visited[y + length, x] = True
                        length += 1
                    if length > 1:
                        y0 = y
                        y1 = y + length - 1
                        x0 = x1 = x
                        dx = 0
                        dy = y1 - y0
                        x_real = (x0 / w) * self.canvas_width
                        y_real = self.canvas_height - (y0 / h) * self.canvas_height
                        dy_real = -dy * (self.canvas_height / h)
                        f_str = f"f(t,0,1,{0:.6f},{x_real:.6f})"
                        g_str = f"g(t,0,1,{dy_real:.6f},{y_real:.6f})"
                        self.output_lines.append(f"({f_str}, {g_str})")

        for x in range(0, w, 4):
            for y in range(h):
                if binary[y, x] and not visited[y, x]:
                    # try horizontal line
                    length = 0
                    while x + length < w and binary[y, x + length]:
                        visited[y, x + length] = True
                        length += 1
                    if length > 1:
                        x0 = x
                        x1 = x + length - 1
                        y0 = y1 = y
                        dy = 0
                        dx = x1 - x0
                        x_real = (x0 / w) * self.canvas_width
                        y_real = self.canvas_height - (y0 / h) * self.canvas_height
                        dx_real = dx * (self.canvas_width / w)
                        f_str = f"f(t,0,1,{dx_real:.6f},{x_real:.6f})"
                        g_str = f"g(t,0,1,{0:.6f},{y_real:.6f})"
                        self.output_lines.append(f"({f_str}, {g_str})")

        with open("output.txt", "w") as f:
            f.write("\n".join(self.output_lines))

        print("Image processed and output saved to output.txt")

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawApp(root)
    root.mainloop()
