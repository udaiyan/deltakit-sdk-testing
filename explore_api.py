"""Explore the Deltakit API surface.

Run this once to discover what's actually available in your installed
version, so we can write tests against the real API rather than guesses.

Usage:
    python explore_api.py
"""
import importlib
import traceback

print("=" * 70)
print("Deltakit API Exploration")
print("=" * 70)

# --- 1. Top-level package versions -----------------------------------------
print("\n[1] Installed Deltakit packages and versions\n")
for pkg in [
    "deltakit",
    "deltakit_circuit",
    "deltakit_core",
    "deltakit_decode",
    "deltakit_explorer",
    "deltakit_compile",
    "deltakit_visualise",
]:
    try:
        mod = importlib.import_module(pkg)
        version = getattr(mod, "__version__", "(no __version__)")
        print(f"    OK    {pkg:25s} {version}")
    except Exception as e:
        print(f"    FAIL  {pkg:25s} {type(e).__name__}: {e}")

# --- 2. Explore key modules -------------------------------------------------
print("\n[2] Public names in key modules\n")
modules_to_explore = [
    "deltakit",
    "deltakit.explorer",
    "deltakit.explorer.codes",
    "deltakit.explorer.qpu",
    "deltakit.explorer.simulation",
    "deltakit.circuit",
    "deltakit.circuit.gates",
]

for modname in modules_to_explore:
    print(f"\n  --- {modname} ---")
    try:
        mod = importlib.import_module(modname)
        public = [n for n in dir(mod) if not n.startswith("_")]
        if public:
            for name in public:
                print(f"      {name}")
        else:
            print("      (no public names)")
    except Exception as e:
        print(f"      IMPORT FAILED: {type(e).__name__}: {e}")

# --- 3. Confirm documented API entry points ---------------------------------
print("\n[3] Confirming documented API entry points\n")
checks = [
    ("deltakit.circuit.gates", "PauliBasis"),
    ("deltakit.explorer.codes", "RepetitionCode"),
    ("deltakit.explorer.codes", "RotatedPlanarCode"),
    ("deltakit.explorer.codes", "css_code_memory_circuit"),
    ("deltakit.explorer.qpu", "QPU"),
    ("deltakit.explorer.qpu", "SI1000Noise"),
    ("deltakit.explorer.simulation", "simulate_with_stim"),
]

for modname, attr in checks:
    try:
        mod = importlib.import_module(modname)
        obj = getattr(mod, attr, None)
        if obj is None:
            print(f"    MISSING  {modname}.{attr}")
        else:
            kind = type(obj).__name__
            print(f"    OK       {modname}.{attr}  ({kind})")
    except Exception as e:
        print(f"    FAIL     {modname}.{attr}  {type(e).__name__}: {e}")

# --- 4. Inspect key signatures ----------------------------------------------
print("\n[4] Signatures of key callables\n")
import inspect

signature_targets = [
    ("deltakit.explorer.codes", "css_code_memory_circuit"),
    ("deltakit.explorer.simulation", "simulate_with_stim"),
]

for modname, attr in signature_targets:
    try:
        mod = importlib.import_module(modname)
        obj = getattr(mod, attr, None)
        if obj is not None and callable(obj):
            print(f"    {modname}.{attr}{inspect.signature(obj)}")
        else:
            print(f"    {modname}.{attr} is not callable or missing")
    except Exception as e:
        print(f"    FAIL  {modname}.{attr}: {type(e).__name__}: {e}")

# --- 5. End-to-end smoke test ------------------------------------------------
print("\n[5] End-to-end pipeline smoke test\n")

try:
    from deltakit.circuit.gates import PauliBasis
    from deltakit.explorer.codes import (
        RepetitionCode,
        css_code_memory_circuit,
    )
    from deltakit.explorer.qpu import QPU, SI1000Noise
    from deltakit.explorer.simulation import simulate_with_stim

    print("    a. Building repetition code (distance=3, Z stabilisers)...")
    rep_code = RepetitionCode(distance=3, stabiliser_type=PauliBasis.Z)
    print(f"       -> {type(rep_code).__name__}")

    print("    b. Generating memory circuit (3 rounds)...")
    circuit = css_code_memory_circuit(
        css_code=rep_code, num_rounds=3, logical_basis=PauliBasis.Z
    )
    print(f"       -> {type(circuit).__name__}")
    print(f"       -> qubits: {getattr(circuit, 'qubits', '(no qubits attr)')}")

    print("    c. Adding SI1000 noise (p=0.01)...")
    noise = SI1000Noise(p=0.01)
    qpu = QPU(qubits=circuit.qubits, noise_model=noise)
    noisy_circuit = qpu.compile_and_add_noise_to_circuit(circuit)
    print(f"       -> {type(noisy_circuit).__name__}")

    print("    d. Converting to Stim circuit...")
    stim_circuit = noisy_circuit.as_stim_circuit()
    print(f"       -> {type(stim_circuit).__name__}")

    print("    e. Simulating 1000 shots with Stim...")
    result = simulate_with_stim(stim_circuit, shots=1000)
    print(f"       -> returns: {type(result).__name__}")
    if isinstance(result, tuple):
        print(f"       -> tuple of {len(result)} items: "
              f"{[type(x).__name__ for x in result]}")

    print("\n    Smoke test PASSED.")
except Exception:
    print("    Smoke test FAILED:\n")
    traceback.print_exc()

print("\n" + "=" * 70)
print("Done. Paste the full output back.")
print("=" * 70)