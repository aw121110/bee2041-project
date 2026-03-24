import subprocess
import sys
import time

PYTHON = "/opt/anaconda3/bin/python"

steps = [
    {
        "label": "Step 1 - Scrape PL + UCL data from Opta Analyst",
        "cmd": [PYTHON, "scripts/01_scrape.py"],
    },
    {
        "label": "Step 2 - Clean and standardise raw data",
        "cmd": [PYTHON, "scripts/02_clean.py"],
    },
    {
        "label": "Step 3 - Descriptive analysis and visualisations",
        "cmd": [PYTHON, "scripts/03_analysis.py"],
    },
    {
        "label": "Step 4 - Double ML causal inference model",
        "cmd": [PYTHON, "scripts/04_causal.py"],
    },
    {
        "label": "Step 5 - Render Quarto blog",
        "cmd": ["quarto", "render", "blog.qmd"],
    },
]

print("=" * 60)
print("  BEE2041 Empirical Project - Full Pipeline")
print("=" * 60)

for i, step in enumerate(steps, 1):
    print(f"\n  {step['label']}")
    print(f"   Command: {' '.join(step['cmd'])}")
    start = time.time()
    result = subprocess.run(step["cmd"])
    elapsed = time.time() - start
    if result.returncode != 0:
        print(f"\nPipeline failed at step {i}: {step['label']}")
        print(f"Fix the error above and re-run: python run_all.py")
        sys.exit(1)
    print(f"   Done in {elapsed:.1f}s")

print("\n" + "=" * 60)
print("  Full pipeline complete - blog.html is ready")
print("=" * 60)
