# jarvishud.py
import tkinter as tk
import random
import math

class JarvisHUD:
    def __init__(self, root):
        self.root = root
        self.root.title("J.A.R.V.I.S. Core Matrix")
        self.root.geometry("400x450")
        self.root.configure(bg="#0d0701")

        self.status_label = tk.Label(root, text="INITIALIZING...", font=("Courier", 12, "bold"), fg="#ffaa00", bg="#0d0701")
        self.status_label.pack(pady=15)

        self.canvas = tk.Canvas(root, width=360, height=360, bg="#0d0701", highlightthickness=0)
        self.canvas.pack()

        self.is_speaking = False
        self.nodes = []
        for _ in range(25):
            self.nodes.append({
                "theta": random.uniform(0, 2 * math.pi),
                "phi": random.uniform(0, math.pi),
                "speed": random.uniform(0.01, 0.03),
                "radius": random.uniform(80, 110)
            })
            
        self.animate()

    def set_speaking(self, state):
        self.is_speaking = state
        self.set_status("CORE ACTIVE..." if state else "SYSTEM ONLINE")

    def set_status(self, text):
        self.status_label.config(text=text, fg="#ffaa00" if "ACTIVE" in text or "ONLINE" in text else "#aa6600")

    def animate(self):
        self.canvas.delete("hud_elements")
        cx, cy = 180, 180 
        projected_coords = []

        base_orange = "#ffaa00" if self.is_speaking else "#d47a00"
        bright_glow = "#ffd700" if self.is_speaking else "#ff9900"
        core_color  = "#ffffff" if self.is_speaking else "#ffd700"

        for node in self.nodes:
            node["theta"] += node["speed"]
            x = node["radius"] * math.sin(node["phi"]) * math.cos(node["theta"])
            y = node["radius"] * math.sin(node["phi"]) * math.sin(node["theta"])
            z = node["radius"] * math.cos(node["phi"])
            
            if self.is_speaking:
                x += random.uniform(-1.5, 1.5)
                y += random.uniform(-1.5, 1.5)

            scale = (z + 150) / 300 + 0.5
            px = cx + x * scale
            py = cy + y * scale
            projected_coords.append((px, py, scale))

        for i in range(len(projected_coords)):
            x1, y1, s1 = projected_coords[i]
            for j in range(i + 1, len(projected_coords)):
                x2, y2, s2 = projected_coords[j]
                dist = math.hypot(x1 - x2, y1 - y2)
                if dist < 65:
                    self.canvas.create_line(x1, y1, x2, y2, fill=base_orange, width=1, tags="hud_elements")

        for px, py, scale in projected_coords:
            r = 2.5 * scale
            self.canvas.create_oval(px-r, py-r, px+r, py+r, fill=bright_glow, outline="", tags="hud_elements")

        core_r = 14 + (random.uniform(-1, 1) if self.is_speaking else 0)
        self.canvas.create_oval(cx-core_r, cy-core_r, cx+core_r, cy+core_r, fill=core_color, outline=bright_glow, width=2, tags="hud_elements")

        self.root.after(33, self.animate)