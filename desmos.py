import tkinter as tk
import time

class DrawApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Draw and Export to Desmos")
        self.canvas = tk.Canvas(root, bg='white', width=800, height=600)
        self.canvas.pack()

        # Bind mouse events for drawing strokes
        self.canvas.bind("<ButtonPress-1>", self.on_press)
        self.canvas.bind("<ButtonRelease-1>", self.on_release)

        self.strokes = []  # Stores all strokes (each stroke is a list of (t, x, y))
        self.current_stroke = None

        # Sampling control
        self.sampling = False
        self.last_sample_time = 0
        self.sampling_interval = 0.02  # Adjustable sampling interval

        # Timing
        self.start_time = None
        self.final_time = 0  # Will be updated to the last recorded stroke time

        # Output storage
        self.output_lines = []

        # Terminate button
        self.terminate_button = tk.Button(root, text="Terminate", command=self.on_terminate)
        self.terminate_button.pack(pady=5)

    def on_press(self, event):
        """Start a new stroke on mouse press."""
        if self.start_time is None:
            self.start_time = time.time()  # Set t=0 on first press

        self.current_stroke = []
        t = time.time() - self.start_time
        self.last_sample_time = time.time()
        self.current_stroke.append((t, event.x, event.y))
        self.sampling = True
        self.sample()

    def sample(self):
        """Sample the current pointer position at set intervals."""
        if not self.sampling:
            return
        now = time.time()
        if now - self.last_sample_time >= self.sampling_interval:
            x = self.canvas.winfo_pointerx() - self.canvas.winfo_rootx()
            y = self.canvas.winfo_pointery() - self.canvas.winfo_rooty()
            t = now - self.start_time
            self.current_stroke.append((t, x, y))
            if len(self.current_stroke) >= 2:
                _, prev_x, prev_y = self.current_stroke[-2]
                self.canvas.create_line(prev_x, prev_y, x, y, fill="black", width=2)
            self.last_sample_time = now
        self.root.after(int(self.sampling_interval * 1000), self.sample)

    def on_release(self, event):
        """End the current stroke on mouse button release."""
        self.sampling = False
        t = time.time() - self.start_time
        self.current_stroke.append((t, event.x, event.y))
        self.strokes.append(self.current_stroke)
        self.final_time = t  # Update final recorded time
        self.current_stroke = None

    def on_terminate(self):
        """Terminate the program, output the function calls to files, and print the final time."""
        self.sampling = False

        for stroke in self.strokes:
            for i in range(len(stroke) - 1):
                t0, x0, y0 = stroke[i]
                y0=600-y0
                t0 = t0 / self.final_time
                tf, x1, y1 = stroke[i + 1]
                y1=600-y1
                tf = tf / self.final_time
                dx = x1 - x0
                dy = y1 - y0
                f_str = f"f(t,{t0:.6f},{tf:.6f},{dx:.6f},{x0:.6f})"
                g_str = f"g(t,{t0:.6f},{tf:.6f},{dy:.6f},{y0:.6f})"
                x= "(" + f_str + ", " + g_str + ")" + "\{ 0<t<a \}"
                self.output_lines.append(x)

        with open("output.txt", "w") as output_file:
            output_file.write("\n".join(self.output_lines))
        
        print("Output saved to output.txt")
        print("Final time recorded:", self.final_time)  # Print last recorded stroke time
        self.root.destroy()

if __name__ == "__main__":
    root = tk.Tk()
    app = DrawApp(root)
    root.mainloop()

