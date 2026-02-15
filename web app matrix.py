import pygame
import random
import sys
import tkinter as tk
from tkinter import ttk
import json
import os


# --- Configuration & Shared State ---
class Settings:
    base_font_size = 20
    target_zoom = 1.0
    current_zoom = 1.0
    zoom_smoothness = 0.05
    pan_x = 0
    pan_y = 0
    hue = 120
    # Higher number (e.g., 60) = SHORTER trails. Lower (e.g., 10) = LONGER trails.
    layer_fades = [40, 40, 40]
    layer_speeds = [1.0, 1.0, 1.0]
    densities = [300, 150, 40]
    running = True


settings = Settings()

# --- Preset Logic ---
PRESET_FILE = "matrix_presets.json"


def save_presets(all_presets):
    with open(PRESET_FILE, "w") as f: json.dump(all_presets, f)


def load_presets():
    if os.path.exists(PRESET_FILE):
        try:
            with open(PRESET_FILE, "r") as f:
                return json.load(f)
        except:
            return {}
    return {}


# --- Setup Control Window ---
def setup_controls():
    root = tk.Tk()
    root.title("Matrix Studio - Operator Console")
    root.geometry("500x750")
    root.attributes('-topmost', True)

    notebook = ttk.Notebook(root)
    notebook.pack(expand=True, fill='both', padx=10, pady=10)

    tab_optics = ttk.Frame(notebook);
    tab_physics = ttk.Frame(notebook)
    tab_density = ttk.Frame(notebook);
    tab_presets = ttk.Frame(notebook)
    notebook.add(tab_optics, text=" OPTICS ");
    notebook.add(tab_physics, text=" PHYSICS ")
    notebook.add(tab_density, text=" DENSITY ");
    notebook.add(tab_presets, text=" PRESETS ")

    def create_slider(parent, label, min_v, max_v, default, res=1):
        frame = ttk.Frame(parent);
        frame.pack(fill='x', padx=20, pady=5)
        ttk.Label(frame, text=label, font=("Consolas", 10, "bold")).pack(side='left')
        s = tk.Scale(frame, from_=min_v, to=max_v, resolution=res, orient='horizontal', length=220)
        s.set(default);
        s.pack(side='right')
        return s

    s_zoom = create_slider(tab_optics, "ZOOM", 0.1, 10.0, 1.0, 0.1)
    s_hue = create_slider(tab_optics, "HUE", 0, 360, 120)
    s_fbg = create_slider(tab_optics, "BG GHOST", 1, 100, 40)
    s_fmid = create_slider(tab_optics, "MID GHOST", 1, 100, 40)
    s_ffg = create_slider(tab_optics, "FG GHOST", 1, 100, 40)
    s_pan_x = create_slider(tab_optics, "PAN X", -2000, 2000, 0);
    s_pan_y = create_slider(tab_optics, "PAN Y", -2000, 2000, 0)
    s_vbg = create_slider(tab_physics, "BG SPD", 0.1, 5.0, 1.0, 0.1)
    s_vmid = create_slider(tab_physics, "MID SPD", 0.1, 5.0, 1.0, 0.1)
    s_vfg = create_slider(tab_physics, "FG SPD", 0.1, 5.0, 1.0, 0.1)
    s_dbg = create_slider(tab_density, "BG QTY", 0, 1000, 300)
    s_dmid = create_slider(tab_density, "MID QTY", 0, 500, 150)
    s_dfg = create_slider(tab_density, "FG QTY", 0, 200, 40)

    current_presets = load_presets()
    preset_entry = ttk.Entry(tab_presets, width=30);
    preset_entry.pack(pady=5)
    preset_listbox = tk.Listbox(tab_presets, height=10);
    preset_listbox.pack(padx=20, pady=10)
    for name in current_presets: preset_listbox.insert(tk.END, name)

    def save_current():
        name = preset_entry.get()
        if not name: return
        current_presets[name] = {"z": s_zoom.get(), "h": s_hue.get(), "f": [s_fbg.get(), s_fmid.get(), s_ffg.get()],
                                 "p": [s_pan_x.get(), s_pan_y.get()], "v": [s_vbg.get(), s_vmid.get(), s_vfg.get()],
                                 "d": [s_dbg.get(), s_dmid.get(), s_dfg.get()]}
        save_presets(current_presets)
        if name not in preset_listbox.get(0, tk.END): preset_listbox.insert(tk.END, name)

    def load_selected():
        sel = preset_listbox.curselection()
        if not sel: return
        p = current_presets[preset_listbox.get(sel[0])]
        s_zoom.set(p["z"]);
        s_hue.set(p["h"]);
        s_fbg.set(p["f"][0]);
        s_fmid.set(p["f"][1]);
        s_ffg.set(p["f"][2])
        s_pan_x.set(p["p"][0]);
        s_pan_y.set(p["p"][1]);
        s_vbg.set(p["v"][0]);
        s_vmid.set(p["v"][1]);
        s_vfg.set(p["v"][2])
        s_dbg.set(p["d"][0]);
        s_dmid.set(p["d"][1]);
        s_dfg.set(p["d"][2])

    ttk.Button(tab_presets, text="SAVE", command=save_current).pack();
    ttk.Button(tab_presets, text="LOAD", command=load_selected).pack()

    def on_close():
        settings.running = False; root.destroy()

    root.protocol("WM_DELETE_WINDOW", on_close)
    return root, s_zoom, s_vbg, s_vmid, s_vfg, s_fbg, s_fmid, s_ffg, s_pan_x, s_pan_y, s_dbg, s_dmid, s_dfg, s_hue


# --- Pygame App ---
pygame.init()
WIDTH, HEIGHT = 1280, 720
screen = pygame.display.set_mode((WIDTH, HEIGHT), pygame.RESIZABLE)
chars = [str(i) for i in range(10)] + [chr(i) for i in range(0xFF66, 0xFF9D)]

# 3 persistent canvases to hold the trails for each layer
layer_canvases = [pygame.Surface((WIDTH, HEIGHT)) for _ in range(3)]
for canvas in layer_canvases: canvas.fill((0, 0, 0))

layers_config = [{"depth": 0.4}, {"depth": 1.0}, {"depth": 1.8}]
MAX_POOL = 1000
layer_drops = [[[random.randint(-2000, 2000), random.uniform(2, 6), random.random()] for _ in range(MAX_POOL)] for _ in
               range(3)]

clock = pygame.time.Clock()
root, s_zoom, s_vbg, s_vmid, s_vfg, s_fbg, s_fmid, s_ffg, s_pan_x, s_pan_y, s_dbg, s_dmid, s_dfg, s_hue = setup_controls()

while settings.running:
    try:
        root.update()
        settings.target_zoom = s_zoom.get()
        settings.layer_fades = [s_fbg.get(), s_fmid.get(), s_ffg.get()]
        settings.pan_x, settings.pan_y, settings.hue = s_pan_x.get(), s_pan_y.get(), s_hue.get()
        settings.layer_speeds = [s_vbg.get(), s_vmid.get(), s_vfg.get()]
        settings.densities = [int(s_dbg.get()), int(s_dmid.get()), int(s_dfg.get())]
        settings.current_zoom += (settings.target_zoom - settings.current_zoom) * settings.zoom_smoothness
    except:
        break

    for event in pygame.event.get():
        if event.type == pygame.QUIT: settings.running = False
        if event.type == pygame.VIDEORESIZE:
            WIDTH, HEIGHT = event.w, event.h
            layer_canvases = [pygame.Surface((WIDTH, HEIGHT)) for _ in range(3)]

    # --- DRAWING SECTION ---
    screen.fill((0, 0, 0))
    color_obj = pygame.Color(0, 0, 0);
    color_obj.hsva = (settings.hue, 100, 100, 100)
    primary_color = (color_obj.r, color_obj.g, color_obj.b)

    for idx, config in enumerate(layers_config):
        depth = config["depth"]
        canvas = layer_canvases[idx]

        # --- THE FADE LOGIC FIX ---
        # Instead of clearing, we blit a semi-transparent surface to fade old frames
        fade_surface = pygame.Surface((WIDTH, HEIGHT))
        # 101 - fade because high slider = longer trails (lower alpha)
        fade_intensity = max(1, 101 - settings.layer_fades[idx])
        fade_surface.set_alpha(fade_intensity)
        fade_surface.fill((0, 0, 0))
        canvas.blit(fade_surface, (0, 0))

        cur_size = max(3, int(settings.base_font_size * settings.current_zoom * depth))
        font = pygame.font.SysFont("ms mincho", cur_size)
        dim = 0.3 if idx == 0 else 0.7 if idx == 1 else 1.0
        f_color = (int(primary_color[0] * dim), int(primary_color[1] * dim), int(primary_color[2] * dim))

        for i in range(min(settings.densities[idx], MAX_POOL)):
            # Horizontal wrap & Vertical wrap
            draw_x = ((layer_drops[idx][i][2] * WIDTH) + (settings.pan_x * depth)) % WIDTH
            draw_y = (layer_drops[idx][i][0] + (settings.pan_y * depth)) % (HEIGHT + cur_size * 2) - cur_size

            # Draw random characters
            char = random.choice(chars)
            color = (255, 255, 255) if random.random() > 0.98 else f_color
            canvas.blit(font.render(char, True, color), (draw_x, int(draw_y)))

            # Update physics
            layer_drops[idx][i][0] += layer_drops[idx][i][1] * settings.layer_speeds[
                idx] * settings.current_zoom * depth

        # Combine the layer canvas onto the main screen
        screen.blit(canvas, (0, 0), special_flags=pygame.BLEND_ADD)

    pygame.display.flip()
    clock.tick(60)

pygame.quit()
