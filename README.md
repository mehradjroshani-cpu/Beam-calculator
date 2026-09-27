# Beam Calculator

A Python tool for structural beam analysis — computes and plots shear force, bending moment, deflection, and safety factor for simply supported and cantilever beams under point or distributed loads.

## Features
- Simply supported and cantilever beam support conditions
- Point load and uniform distributed load (UDL)
- Rectangular, circular, and I-beam cross-sections (auto-computed moment of inertia)
- Computes max bending stress and safety factor
- Generates shear force, bending moment, and deflection plots

## How to run
```bash
pip install -r requirements.txt
python beam_calculator.py
```

## Background
Based on standard mechanics of materials formulas (σ = Mc/I) for bending stress and Euler-Bernoulli beam theory for deflection.