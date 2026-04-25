#!/usr/bin/env python3
"""
GHZ Ripple Visualizer — v1
--------------------------
Simulates the physical interference of 3 ripple sources on a 2D surface.
Outputs 10 frames showing the time evolution of the interference pattern.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path
import os

def generate_ripple_frames():
    # Grid setup
    res = 400
    x = np.linspace(-10, 10, res)
    y = np.linspace(-10, 10, res)
    X, Y = np.meshgrid(x, y)
    
    # 3 Sources (The 3 Stones) arranged in a triangle
    r_src = 2.0
    sources = [
        (r_src * np.cos(0),           r_src * np.sin(0)),
        (r_src * np.cos(2*np.pi/3),   r_src * np.sin(2*np.pi/3)),
        (r_src * np.cos(4*np.pi/3),   r_src * np.sin(4*np.pi/3))
    ]
    
    # 3 Detectors (The 3 Observers) further out
    r_det = 8.0
    detectors = [
        (r_det * np.cos(np.pi/3),     r_det * np.sin(np.pi/3)),
        (r_det * np.cos(np.pi),        r_det * np.sin(np.pi)),
        (r_det * np.cos(5*np.pi/3),   r_det * np.sin(5*np.pi/3))
    ]
    
    # Physics parameters
    k = 4.0      # Wave number (spatial frequency)
    omega = 2.0  # Angular frequency (time speed)
    v = omega / k # Velocity
    
    out_dir = Path("visualizations/ghz_ripple_interference")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating 10 ripple frames in {out_dir}...")
    
    # Time steps: from early expansion to full interference
    times = np.linspace(0, 15, 10)
    
    for i, t in enumerate(times):
        Z = np.zeros_like(X)
        for sx, sy in sources:
            dist = np.sqrt((X - sx)**2 + (Y - sy)**2)
            # Damping: 1/sqrt(r) for energy conservation in 2D
            amplitude = 1.0 / np.sqrt(dist + 0.5)
            # Ripple wavefront: only exists where wave has reached
            wavefront_mask = dist <= (v * t)
            # Signal: cos(k*r - omega*t)
            Z += wavefront_mask * amplitude * np.cos(k * dist - omega * t)
            
        # Plotting
        plt.figure(figsize=(8, 8))
        plt.imshow(Z, extent=[-10, 10, -10, 10], cmap='RdBu', origin='lower', vmin=-1.5, vmax=1.5)
        
        # Mark Sources
        for sx, sy in sources:
            plt.plot(sx, sy, 'yo', markersize=10, markeredgecolor='k', label='Emitter' if sx == sources[0][0] else "")
            
        # Mark Detectors
        for dx, dy in detectors:
            plt.plot(dx, dy, 'gX', markersize=12, markeredgecolor='k', label='Observer' if dx == detectors[0][0] else "")
            
        plt.title(f"GHZ Ripple Interference - Time: {t:.2f}")
        plt.axis('off')
        
        frame_path = out_dir / f"frame_{i:02d}.png"
        plt.savefig(frame_path, dpi=120, bbox_inches='tight')
        plt.close()
        print(f"  Frame {i} saved.")

if __name__ == "__main__":
    generate_ripple_frames()
