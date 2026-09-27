"""
Beam Calculator
================
A mechanical/structural engineering tool that computes and plots the
shear force, bending moment, deflection, bending stress, and safety
factor for a beam under load.

Supports:
    - Support types: simply supported, cantilever
    - Load types: single point load, uniform distributed load (UDL)
    - Cross-sections: rectangular, circular, I-beam (auto-computes I)

Author: Mahrad Roshaninezhad
"""

import numpy as np
import matplotlib.pyplot as plt


# ---------------------------------------------------------------------
# Cross-section moment of inertia calculators
# ---------------------------------------------------------------------

def moment_of_inertia_rectangular(width, height):
    """I = b*h^3 / 12  (about centroidal axis, bending about horizontal axis)"""
    return (width * height ** 3) / 12


def moment_of_inertia_circular(diameter):
    """I = pi*d^4 / 64"""
    return (np.pi * diameter ** 4) / 64


def moment_of_inertia_ibeam(b_flange, t_flange, h_web, t_web):
    """
    Approximate I-beam moment of inertia using composite rectangles.
    b_flange: flange width, t_flange: flange thickness
    h_web: web height (between flanges), t_web: web thickness
    """
    # Web (centered)
    I_web = (t_web * h_web ** 3) / 12

    # Each flange, offset from centroid via parallel axis theorem
    d = (h_web + t_flange) / 2  # distance from centroid to flange centroid
    I_flange_self = (b_flange * t_flange ** 3) / 12
    A_flange = b_flange * t_flange
    I_flange = I_flange_self + A_flange * d ** 2

    return I_web + 2 * I_flange


# ---------------------------------------------------------------------
# Beam analysis: simply supported beam
# ---------------------------------------------------------------------

def simply_supported_point_load(L, P, a, E, I, n=200):
    """
    Simply supported beam, point load P at distance a from left support.
    Returns x, V(x), M(x), y(x) (deflection).
    """
    x = np.linspace(0, L, n)
    b = L - a
    R1 = P * b / L
    R2 = P * a / L

    V = np.where(x < a, R1, R1 - P)
    M = np.where(x < a, R1 * x, R1 * x - P * (x - a))

    # Deflection (standard formula, for x <= a and x > a)
    y = np.zeros_like(x)
    for i, xi in enumerate(x):
        if xi <= a:
            y[i] = (P * b * xi / (6 * L * E * I)) * (L ** 2 - b ** 2 - xi ** 2)
        else:
            y[i] = (P * a * (L - xi) / (6 * L * E * I)) * (2 * L * xi - a ** 2 - xi ** 2)

    return x, V, M, -y  # negative so downward deflection plots below axis


def simply_supported_udl(L, w, E, I, n=200):
    """
    Simply supported beam, uniform distributed load w (force/length).
    """
    x = np.linspace(0, L, n)
    R = w * L / 2

    V = R - w * x
    M = (w * x / 2) * (L - x)
    y = (w * x / (24 * E * I)) * (L ** 3 - 2 * L * x ** 2 + x ** 3)

    return x, V, M, -y


# ---------------------------------------------------------------------
# Beam analysis: cantilever beam (fixed at x=0, free at x=L)
# ---------------------------------------------------------------------

def cantilever_point_load(L, P, E, I, n=200):
    """Cantilever beam, point load P at free end."""
    x = np.linspace(0, L, n)
    V = -P * np.ones_like(x)
    M = -P * (L - x)
    y = -(P * x ** 2 / (6 * E * I)) * (3 * L - x)
    return x, V, M, y


def cantilever_udl(L, w, E, I, n=200):
    """Cantilever beam, uniform distributed load w over full length."""
    x = np.linspace(0, L, n)
    V = -w * (L - x)
    M = -(w * (L - x) ** 2) / 2
    y = -(w * x ** 2 / (24 * E * I)) * (x ** 2 - 4 * L * x + 6 * L ** 2)
    return x, V, M, y


# ---------------------------------------------------------------------
# Stress / safety factor
# ---------------------------------------------------------------------

def bending_stress(M, c, I):
    """sigma = M*c / I"""
    return M * c / I


def safety_factor(yield_strength, max_stress):
    if max_stress == 0:
        return float("inf")
    return yield_strength / abs(max_stress)


# ---------------------------------------------------------------------
# Plotting
# ---------------------------------------------------------------------

def plot_results(x, V, M, y, title="Beam Analysis"):
    fig, axes = plt.subplots(3, 1, figsize=(8, 9), sharex=True)

    axes[0].plot(x, V, color="tab:blue")
    axes[0].axhline(0, color="black", linewidth=0.8)
    axes[0].set_ylabel("Shear Force (N)")
    axes[0].set_title(f"{title} — Shear Force Diagram")
    axes[0].grid(True, alpha=0.3)

    axes[1].plot(x, M, color="tab:red")
    axes[1].axhline(0, color="black", linewidth=0.8)
    axes[1].set_ylabel("Bending Moment (N·m)")
    axes[1].set_title("Bending Moment Diagram")
    axes[1].grid(True, alpha=0.3)

    axes[2].plot(x, y, color="tab:green")
    axes[2].axhline(0, color="black", linewidth=0.8)
    axes[2].set_ylabel("Deflection (m)")
    axes[2].set_xlabel("Position along beam, x (m)")
    axes[2].set_title("Deflection Curve")
    axes[2].grid(True, alpha=0.3)

    fig.tight_layout()
    fig.savefig("beam_analysis.png", dpi=150)
    print("\nPlot saved as 'beam_analysis.png'")
    plt.show()


# ---------------------------------------------------------------------
# Interactive CLI
# ---------------------------------------------------------------------

def get_float(prompt):
    while True:
        try:
            return float(input(prompt))
        except ValueError:
            print("Please enter a valid number.")


def choose_cross_section():
    print("\nCross-section type:")
    print("  1. Rectangular")
    print("  2. Circular")
    print("  3. I-beam")
    choice = input("Choose (1-3): ").strip()

    if choice == "1":
        b = get_float("  Width b (m): ")
        h = get_float("  Height h (m): ")
        I = moment_of_inertia_rectangular(b, h)
        c = h / 2
    elif choice == "2":
        d = get_float("  Diameter d (m): ")
        I = moment_of_inertia_circular(d)
        c = d / 2
    elif choice == "3":
        b_f = get_float("  Flange width (m): ")
        t_f = get_float("  Flange thickness (m): ")
        h_w = get_float("  Web height (m): ")
        t_w = get_float("  Web thickness (m): ")
        I = moment_of_inertia_ibeam(b_f, t_f, h_w, t_w)
        c = (h_w + 2 * t_f) / 2
    else:
        print("Invalid choice, defaulting to rectangular 0.05m x 0.1m.")
        I = moment_of_inertia_rectangular(0.05, 0.1)
        c = 0.05

    return I, c


def main():
    print("=" * 60)
    print(" BEAM CALCULATOR — Shear, Moment, Deflection & Stress")
    print("=" * 60)

    print("\nSupport type:")
    print("  1. Simply supported")
    print("  2. Cantilever")
    support = input("Choose (1-2): ").strip()

    print("\nLoad type:")
    print("  1. Point load")
    print("  2. Uniform distributed load (UDL)")
    load_type = input("Choose (1-2): ").strip()

    L = get_float("\nBeam length L (m): ")
    E = get_float("Modulus of elasticity E (Pa) [steel ~ 200e9]: ")
    yield_strength = get_float("Material yield strength (Pa) [steel ~ 250e6]: ")

    I, c = choose_cross_section()

    if support == "1" and load_type == "1":
        P = get_float("\nPoint load P (N): ")
        a = get_float(f"Location of load from left support, a (0 to {L} m): ")
        x, V, M, y = simply_supported_point_load(L, P, a, E, I)
        title = "Simply Supported Beam — Point Load"

    elif support == "1" and load_type == "2":
        w = get_float("\nDistributed load w (N/m): ")
        x, V, M, y = simply_supported_udl(L, w, E, I)
        title = "Simply Supported Beam — UDL"

    elif support == "2" and load_type == "1":
        P = get_float("\nPoint load at free end P (N): ")
        x, V, M, y = cantilever_point_load(L, P, E, I)
        title = "Cantilever Beam — Point Load"

    elif support == "2" and load_type == "2":
        w = get_float("\nDistributed load w (N/m): ")
        x, V, M, y = cantilever_udl(L, w, E, I)
        title = "Cantilever Beam — UDL"

    else:
        print("Invalid selection. Exiting.")
        return

    max_moment = M[np.argmax(np.abs(M))]
    max_deflection = y[np.argmax(np.abs(y))]
    max_stress = bending_stress(max_moment, c, I)
    SF = safety_factor(yield_strength, max_stress)

    print("\n" + "-" * 60)
    print("RESULTS")
    print("-" * 60)
    print(f"Moment of Inertia (I):     {I:.6e} m^4")
    print(f"Distance to extreme fiber (c): {c:.6f} m")
    print(f"Max Bending Moment:        {max_moment:.3f} N·m")
    print(f"Max Bending Stress:        {max_stress/1e6:.3f} MPa")
    print(f"Max Deflection:            {max_deflection*1000:.3f} mm")
    print(f"Safety Factor:             {SF:.2f}")
    print("-" * 60)

    if SF < 1:
        print("WARNING: Safety factor < 1 — beam will yield under this load!")
    elif SF < 1.5:
        print("CAUTION: Low safety factor — consider a larger cross-section.")
    else:
        print("Beam design appears safe under these conditions.")

    plot_results(x, V, M, y, title=title)


if __name__ == "__main__":
    main()