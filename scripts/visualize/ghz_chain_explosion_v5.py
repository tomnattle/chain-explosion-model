#!/usr/bin/env python3
"""
GHZ Chain Explosion Visualizer — v5
------------------------------------
NON-LINEAR MODEL: Simulates wave-front collisions as explosive secondary emitters.
Features:
- Asymmetric source energy (unequal 'force' levels).
- Collision-triggered secondary ripples (The Chain Explosion).
- Momentum-based intensity (strong waves 'pushing' the pattern).
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def generate_chain_explosion_frames():
    res = 300
    limit = 12.0
    x = np.linspace(-limit, limit, res)
    y = np.linspace(-limit, limit, res)
    X, Y = np.meshgrid(x, y)
    
    # 3 Sources with ASYMMETRIC ENERGY (The user's 'force' levels)
    rng = np.random.default_rng(77)
    d_src = 3.0
    sources = [
        {"pos": (d_src * np.cos(0),           d_src * np.sin(0)),         "force": 1.5},
        {"pos": (d_src * np.cos(2*np.pi/3),   d_src * np.sin(2*np.pi/3)), "force": 0.8},
        {"pos": (d_src * np.cos(4*np.pi/3),   d_src * np.sin(4*np.pi/3)), "force": 1.2}
    ]
    
    out_dir = Path("visualizations/ghz_chain_explosion_v5")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    k = 5.0
    omega = 3.0
    v = omega / k
    
    print(f"Generating Chain Explosion frames in {out_dir}...")
    
    times = np.linspace(0, 10, 10)
    
    # We will track "Explosion Points" where wavefronts meet
    for i, t in enumerate(times):
        Z_main = np.zeros_like(X)
        Z_explosions = np.zeros_like(X)
        
        # 1. Main Ripples with Asymmetric Force
        wavefront_radii = []
        for s in sources:
            dist = np.sqrt((X - s["pos"][0])**2 + (Y - s["pos"][1])**2)
            mask = dist <= (v * t)
            amplitude = s["force"] / np.sqrt(dist + 0.5)
            Z_main += mask * amplitude * np.cos(k * dist - omega * t)
            wavefront_radii.append(v * t)

        # 2. Collision Detection (Simple proximity of wavefronts)
        # If two wavefronts from different sources are close, they "explode"
        for idx1 in range(len(sources)):
            for idx2 in range(idx1 + 1, len(sources)):
                s1, s2 = sources[idx1], sources[idx2]
                d1 = np.sqrt((X - s1["pos"][0])**2 + (Y - s1["pos"][1])**2)
                d2 = np.sqrt((X - s2["pos"][0])**2 + (Y - s2["pos"][1])**2)
                
                # Where wavefronts meet
                collision_mask = (np.abs(d1 - wavefront_radii[idx1]) < 0.2) & \
                                 (np.abs(d2 - wavefront_radii[idx2]) < 0.2)
                
                if np.any(collision_mask):
                    # Explosive secondary energy (Bright spots)
                    Z_explosions[collision_mask] += (s1["force"] + s2["force"])
        
        # Plotting
        plt.figure(figsize=(10, 10), facecolor='black')
        # Background interference field
        plt.imshow(Z_main, extent=[-limit, limit, -limit, limit], cmap='twilight', alpha=0.7)
        
        # Overlay the "Explosions" (Secondary emitters)
        plt.imshow(Z_explosions, extent=[-limit, limit, -limit, limit], cmap='YlOrRd', alpha=0.9)
        
        # Visualizing the "Force" as arrows or markers
        for s in sources:
            plt.plot(s["pos"][0], s["pos"][1], 'yo', markersize=s["force"]*10, alpha=0.8)
            plt.text(s["pos"][0], s["pos"][1]+0.5, f"Force: {s['force']}", color='white', ha='center')

        plt.title(f"GHZ Chain Explosion - Non-linear Collision - Time: {t:.2f}", color='white')
        plt.axis('off')
        
        frame_path = out_dir / f"explosion_frame_{i:02d}.png"
        plt.savefig(frame_path, dpi=120, bbox_inches='tight', facecolor='black')
        plt.close()
        print(f"  Explosion Frame {i} saved.")

if __name__ == "__main__":
    generate_chain_explosion_frames()
