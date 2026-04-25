#!/usr/bin/env python3
"""
GHZ Spherical Interference Visualizer — v2
------------------------------------------
Simulates 3D spherical wave interference from 3 sources.
Renders the interference pattern on the surface of a distant sphere (r=R).
Uses 1/r amplitude attenuation (3D physics).
"""

import numpy as np
import matplotlib.pyplot as plt
from pathlib import Path

def generate_spherical_frames():
    # Spherical Grid setup (Longitude and Latitude)
    n_phi = 600
    n_theta = 300
    phi = np.linspace(0, 2*np.pi, n_phi)
    theta = np.linspace(0, np.pi, n_theta)
    PHI, THETA = np.meshgrid(phi, theta)
    
    # 3D Coordinate conversion for the sphere surface (Radius R)
    R = 10.0
    X_s = R * np.sin(THETA) * np.cos(PHI)
    Y_s = R * np.sin(THETA) * np.sin(PHI)
    Z_s = R * np.cos(THETA)
    
    # 3 Sources (The 3 Stones) in 3D space
    # Arranged in a small triangle in the XY plane (z=0)
    d = 1.0
    sources = [
        (d * np.cos(0),           d * np.sin(0),           0.0),
        (d * np.cos(2*np.pi/3),   d * np.sin(2*np.pi/3),   0.0),
        (d * np.cos(4*np.pi/3),   d * np.sin(4*np.pi/3),   0.0)
    ]
    
    # Physics parameters
    k = 8.0      # Higher wave number for more complexity
    omega = 2.0
    
    out_dir = Path("visualizations/ghz_spherical_interference")
    out_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"Generating 10 spherical interference frames in {out_dir}...")
    
    times = np.linspace(0, 10, 10)
    
    for i, t in enumerate(times):
        Z_field = np.zeros_like(X_s)
        for sx, sy, sz in sources:
            # 3D Euclidean distance
            dist = np.sqrt((X_s - sx)**2 + (Y_s - sy)**2 + (Z_s - sz)**2)
            # 3D Attenuation: 1/r
            amplitude = 1.0 / (dist + 0.1)
            # Wave: cos(k*r - omega*t)
            Z_field += amplitude * np.cos(k * dist - omega * t)
            
        # Plotting - Equirectangular Projection
        plt.figure(figsize=(12, 6))
        plt.imshow(Z_field, extent=[0, 360, -90, 90], cmap='magma', origin='lower')
        
        plt.colorbar(label='Amplitude')
        plt.xlabel('Longitude (Degrees)')
        plt.ylabel('Latitude (Degrees)')
        plt.title(f"GHZ Spherical Interference Surface (R={R}) - Time: {t:.2f}")
        
        # Mark detector positions (example)
        dets = [(0,0), (120, 0), (240, 0)]
        for dphi, dtheta in dets:
            plt.plot(dphi, dtheta, 'wx', markersize=10, label='Detector' if dphi==0 else "")

        frame_path = out_dir / f"spherical_frame_{i:02d}.png"
        plt.savefig(frame_path, dpi=120, bbox_inches='tight')
        plt.close()
        print(f"  Spherical Frame {i} saved.")

if __name__ == "__main__":
    generate_spherical_frames()
