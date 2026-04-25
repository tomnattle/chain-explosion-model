#!/usr/bin/env python3
"""
GHZ Isometric Interference Visualizer — v3
------------------------------------------
Advanced 3D visualization of the "Chain Explosion" ripple model.
Features:
- Isometric projection of 6 spherical wavefronts.
- Iso-surface rendering of "Interference Burst Zones" (Energy Envelopes).
- Phase vectors showing loop closure.
"""

import numpy as np
import matplotlib.pyplot as plt
from matplotlib import cm
from mpl_toolkits.mplot3d import Axes3D
from pathlib import Path

def generate_isometric_frames():
    # 3D Grid setup for the "Burst Zone"
    grid_size = 40
    limit = 6.0
    x = np.linspace(-limit, limit, grid_size)
    y = np.linspace(-limit, limit, grid_size)
    z = np.linspace(-limit, limit, grid_size)
    X, Y, Z = np.meshgrid(x, y, z)
    
    # 3 Sources (The 3 Stones) - 3D Positions
    d = 2.0
    sources = [
        (d * np.cos(0),           d * np.sin(0),           0.0),
        (d * np.cos(2*np.pi/3),   d * np.sin(2*np.pi/3),   0.0),
        (d * np.cos(4*np.pi/3),   d * np.sin(4*np.pi/3),   0.0)
    ]
    
    # 3 Observers (Alice, Bob, Charlie)
    r_det = 5.0
    detectors = [
        (r_det * np.cos(np.pi/3),     r_det * np.sin(np.pi/3),     0.0),
        (r_det * np.cos(np.pi),        r_det * np.sin(np.pi),        0.0),
        (r_det * np.cos(5*np.pi/3),   r_det * np.sin(5*np.pi/3),   0.0)
    ]
    
    out_dir = Path("visualizations/ghz_isometric_interference")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    k = 3.0
    threshold = 0.8 # Only show intense interference zones
    
    print(f"Generating Isometric Burst frames in {out_dir}...")
    
    times = np.linspace(2, 8, 10)
    
    for i, t in enumerate(times):
        # Calculate full 3D amplitude field
        Total_Amp = np.zeros_like(X)
        for sx, sy, sz in sources:
            dist = np.sqrt((X - sx)**2 + (Y - sy)**2 + (Z - sz)**2)
            # Each emitter sends 2 waves (simplification: one phase, but interferes with neighbors)
            Total_Amp += (1.0 / (dist + 0.5)) * np.cos(k * dist - 2.0 * t)
            
        fig = plt.figure(figsize=(12, 10))
        ax = fig.add_subplot(111, projection='3d')
        
        # 1. Plot the "Energy Envelope" (Burst Zones)
        # We only show points where |Amplitude| > threshold
        mask = np.abs(Total_Amp) > threshold
        if np.any(mask):
            # Plot as scattering of small glow points (simulating plasma/burst)
            ax.scatter(X[mask], Y[mask], Z[mask], c=Total_Amp[mask], 
                       cmap='YlOrRd', s=2, alpha=0.1, edgecolors='none')
            
        # 2. Plot Wavefront Wireframes (6 spherical ripples)
        u = np.linspace(0, 2 * np.pi, 20)
        v = np.linspace(0, np.pi, 10)
        radius = t - 1.0 # Wavefront radius at time t
        if radius > 0:
            for sx, sy, sz in sources:
                wx = radius * np.outer(np.cos(u), np.sin(v)) + sx
                wy = radius * np.outer(np.sin(u), np.sin(v)) + sy
                wz = radius * np.outer(np.ones(np.size(u)), np.cos(v)) + sz
                ax.plot_wireframe(wx, wy, wz, color='cyan', alpha=0.05, linewidth=0.5)

        # 3. Plot Phase Lines & Markers
        for j, (dx, dy, dz) in enumerate(detectors):
            ax.scatter(dx, dy, dz, color='green', s=100, marker='X', edgecolors='k', zorder=10)
            # Lines to nearby sources to show loop
            for sx, sy, sz in sources:
                ax.plot([sx, dx], [sy, dy], [sz, dz], 'k--', alpha=0.2, lw=1)
                
        for sx, sy, sz in sources:
            ax.scatter(sx, sy, sz, color='yellow', s=150, marker='o', edgecolors='k', zorder=10)

        # Set Isometric-like View
        ax.view_init(elev=30, azim=45)
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        ax.set_zlim(-limit, limit)
        ax.set_title(f"GHZ Isometric Interference - 'Burst Zones' - Time: {t:.2f}")
        ax.axis('off')
        
        frame_path = out_dir / f"isometric_frame_{i:02d}.png"
        plt.savefig(frame_path, dpi=120, bbox_inches='tight', facecolor='black')
        plt.close()
        print(f"  Isometric Frame {i} saved.")

if __name__ == "__main__":
    generate_isometric_frames()
