# --- ADVANCED MULTI-RING J.A.R.V.I.S. HUD (IRON MAN ORANGE EDITION WITH TELEMETRY) ---
import tkinter as tk
import psutil

class JarvisHUD:
    def __init__(self, root):
        self.root = root
        self.root.title("J.A.R.V.I.S. Mainframe Core")
        self.root.geometry("400x450")
        self.root.configure(bg="#0d0400") 

        self.status_label = tk.Label(root, text="INITIALIZING...", font=("Courier", 12, "bold"), fg="#ff6a00", bg="#0d0400")
        self.status_label.pack(pady=15)

        self.canvas = tk.Canvas(root, width=360, height=360, bg="#0d0400", highlightthickness=0)
        self.canvas.pack()

        self.angle_fast = 0
        self.angle_slow = 0
        self.is_speaking = False
        self.pulse_scale = 1.0
        self.pulse_dir = 1
        
        self.animate()

    def set_speaking(self, state):
        self.is_speaking = state
        self.set_status("JARVIS TALKING..." if state else "SYSTEM ONLINE")

    def set_status(self, text):
        self.status_label.config(text=text, fg="#ffae00" if "TALKING" in text or "ONLINE" in text else "#b34e00")

    def animate(self):
        self.canvas.delete("hud_elements")
        cx, cy = 180, 180 
        
        if self.is_speaking:
            self.pulse_scale += 0.004 * self.pulse_dir
            if self.pulse_scale > 1.02 or self.pulse_scale < 0.98:
                self.pulse_dir *= -1
            bright_color = "#ff6a00"  
            dim_color = "#ffaa00"
            self.angle_fast = (self.angle_fast + 2) % 360
            self.angle_slow = (self.angle_slow - 0.5) % 360
        else:
            self.pulse_scale += 0.002 * self.pulse_dir
            if self.pulse_scale > 1.01 or self.pulse_scale < 0.99:
                self.pulse_dir *= -1
            bright_color = "#d95f02"  
            dim_color = "#662500"
            self.angle_fast = (self.angle_fast + 2) % 360
            self.angle_slow = (self.angle_slow - 0.5) % 360

        r1 = 130 * self.pulse_scale
        self.canvas.create_oval(cx-r1, cy-r1, cx+r1, cy+r1, outline=dim_color, width=1, dash=(5, 15), tags="hud_elements")
        self.canvas.create_arc(cx-r1, cy-r1, cx+r1, cy+r1, start=self.angle_slow, extent=120, style="arc", outline=bright_color, width=2, tags="hud_elements")
        self.canvas.create_arc(cx-r1, cy-r1, cx+r1, cy+r1, start=self.angle_slow+180, extent=60, style="arc", outline=bright_color, width=2, tags="hud_elements")

        r2 = 105 * self.pulse_scale
        self.canvas.create_arc(cx-r2, cy-r2, cx+r2, cy+r2, start=self.angle_fast, extent=220, style="arc", outline=bright_color, width=3, tags="hud_elements")
        self.canvas.create_arc(cx-r2, cy-r2, cx+r2, cy+r2, start=self.angle_fast+260, extent=40, style="arc", outline=dim_color, width=2, tags="hud_elements")

        r3 = 85 * self.pulse_scale
        self.canvas.create_oval(cx-r3, cy-r3, cx+r3, cy+r3, outline=bright_color, width=1, dash=(2, 4), tags="hud_elements")

        r4 = 65 * self.pulse_scale
        self.canvas.create_arc(cx-r4, cy-r4, cx+r4, cy+r4, start=-self.angle_fast, extent=90, style="arc", outline=bright_color, width=2, tags="hud_elements")
        self.canvas.create_arc(cx-r4, cy-r4, cx+r4, cy+r4, start=-self.angle_fast+180, extent=90, style="arc", outline=bright_color, width=2, tags="hud_elements")

        r5 = 50
        self.canvas.create_oval(cx-r5, cy-r5, cx+r5, cy+r5, outline=dim_color, width=1, tags="hud_elements")

        # Central Text Anchor
        text_color = "#ffffff" if self.is_speaking else "#ffae00"
        self.canvas.create_text(cx, cy, text="J.A.R.V.I.S.", fill=text_color, font=("Courier", 13, "bold"), tags="hud_elements")

        cpu_usage = psutil.cpu_percent()
        ram_usage = psutil.virtual_memory().percent
        battery = psutil.sensors_battery()
        bat_percent = battery.percent if battery else 100

        self.canvas.create_text(45, 40, text=f"CPU_SYS\n{cpu_usage}%", fill="#ffae00", font=("Courier", 9, "bold"), justify="left", tags="hud_elements")
        self.canvas.create_line(15, 55, 65, 55, fill="#662500", width=1, tags="hud_elements")
        
        self.canvas.create_text(315, 40, text=f"RAM_MEM\n{ram_usage}%", fill="#ffae00", font=("Courier", 9, "bold"), justify="right", tags="hud_elements")
        self.canvas.create_line(295, 55, 345, 55, fill="#662500", width=1, tags="hud_elements")

        self.canvas.create_text(cx, 335, text=f"PWR_GRID: {bat_percent}%", fill="#ff6a00", font=("Courier", 9, "bold"), tags="hud_elements")

        self.root.after(33, self.animate)