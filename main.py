import subprocess

scripts = [
    "warmstart.py",
    "coldstart.py",
    "coldstartmem.py",
    "coldstartsize.py",
    "fly_size.py",
    "cputest2.py",
    "geodis.py",
    "inlinedata.py",
    "rampup.py",
]


for script in scripts:
    subprocess.run(["python", script])
