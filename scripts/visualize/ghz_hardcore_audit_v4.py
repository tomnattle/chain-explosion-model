#!/usr/bin/env python3
"""
GHZ Hardcore Audit Visualizer — v4
----------------------------------
DESTRUCTIVE AUDIT: Replaces simplified spheres with high-frequency interference fields.
Features:
- Dynamic 3D wavefront slices with phase curvature.
- Volumetric energy burst zones (psi^2) showing non-linear "Chain Resonance".
- Phase-loop coherence beams connecting sources and observers.
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def generate_hardcore_audit_frames():
    # Finer grid for high-frequency interference texture
    res = 60
    limit = 10.0
    x = np.linspace(-limit, limit, res)
    y = np.linspace(-limit, limit, res)
    z = np.linspace(-limit, limit, res)
    X, Y, Z = np.meshgrid(x, y, z)
    
    # 3 Sources (The 3 Stones) - 3D Positions
    d_src = 2.5
    sources = [
        (d_src * np.cos(0),           d_src * np.sin(0),           0.0),
        (d_src * np.cos(2*np.pi/3),   d_src * np.sin(2*np.pi/3),   0.0),
        (d_src * np.cos(4*np.pi/3),   d_src * np.sin(4*np.pi/3),   0.0)
    ]
    
    # 3 Detectors (Alice, Bob, Charlie)
    r_det = 8.0
    detectors = [
        (r_det * np.cos(np.pi/3),     r_det * np.sin(np.pi/3),     0.0),
        (r_det * np.cos(np.pi),        r_det * np.sin(np.pi),        0.0),
        (r_det * np.cos(5*np.pi/3),   r_det * np.sin(5*np.pi/3),   0.0)
    ]
    
    out_dir = Path("visualizations/ghz_hardcore_audit_v4")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    k = 6.0      # Higher spatial frequency for detailed texture
    omega = 4.0
    
    print(f"Executing Hardcore Audit Visualization (v4) in {out_dir}...")
    
    times = np.linspace(0, 12, 10)
    
    for i, t in enumerate(times):
        # The Interference Field (Sum of 6 waves)
        # Each source i sends a wave to neighboring detectors. 
        # Total 3 sources * 2 directions = 6 wave fronts.
        Psi_Total = np.zeros_like(X)
        for sx, sy, sz in sources:
            dist = np.sqrt((X - sx)**2 + (Y - sy)**2 + (Z - sz)**2)
            # 3D Attenuation and Phase Wave
            amplitude = 1.0 / (dist + 0.1)
            # Phase Wavefront: only exists within light-cone
            mask = dist <= (t * 1.5)
            Psi_Total += mask * amplitude * np.cos(k * dist - omega * t)
            
        # Energy Density (The 'Burst' potential)
        Energy = Psi_Total**2
        
        fig = plt.figure(figsize=(12, 10), facecolor='black')
        ax = fig.add_subplot(111, projection='3d', facecolor='black')
        
        # 1. Visualize High-Energy Bursts (The "Chain Explosion" zones)
        # We use a threshold to show the core of the interference pattern
        threshold = np.percentile(Energy, 98) # Only the hottest 2%
        mask_burst = Energy > threshold
        ax.scatter(X[mask_burst], Y[mask_burst], Z[mask_burst], 
                   c=Energy[mask_burst], cmap='hot', s=5, alpha=0.3, edgecolors='none')

        # 2. Visualize Wavefront Ripples (Cross-sections of the field)
        # We show a translucent slice to see the phase curvature
        z_slice = 0.0
        slice_idx = res // 2
        ax.contourf(X[:,:,slice_idx], Y[:,:,slice_idx], Psi_Total[:,:,slice_idx], 
                    levels=20, cmap='RdBu', alpha=0.3, offset=-limit)

        # 3. Geometric Coherence Beams (The "Shared Secret" Paths)
        for dx, dy, dz in detectors:
            ax.scatter(dx, dy, dz, color='cyan', s=200, marker='X', edgecolors='white', label='Observer')
            for sx, sy, sz in sources:
                # Beams showing the path of the ripples
                ax.plot([sx, dx], [sy, dy], [sz, dz], color='white', alpha=0.1, lw=0.5)

        for sx, sy, sz in sources:
            ax.scatter(sx, sy, sz, color='yellow', s=100, marker='o', label='Emitter')

        ax.view_init(elev=35, azim=45)
        ax.set_xlim(-limit, limit)
        ax.set_ylim(-limit, limit)
        ax.set_zlim(-limit, limit)
        ax.set_title(f"GHZ Hardcore Audit v4 - Interference Stranglehold - Time: {t:.2f}", color='white')
        ax.axis('off')
        
        frame_path = out_dir / f"hardcore_frame_{i:02d}.png"
        plt.savefig(frame_path, dpi=120, bbox_inches='tight', facecolor='black')
        plt.close()
        print(f"  Hardcore Frame {i} saved.")

if __name__ == "__main__":
    generate_hardcore_audit_frames()
