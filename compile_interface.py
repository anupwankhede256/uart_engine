# compile_interface.py

import subprocess  # allows execution of external programs from python
import os          # provides filesystem utilities such as os.path.exists()

# specifies the external compiler to invoke.
COMPILER_PATH = r"C:\Program Files\National Instruments\Digital Pattern Compiler\DigitalPatternCompiler.exe"

# Compilation logic
def compile_pattern(src_path, out_path, pinmap_path):

    # checks whether source file exists.
    if not os.path.exists(src_path):
        raise FileNotFoundError(f"Source .digipatsrc not found: {src_path}")
    # check pinmap file existence.
    if not os.path.exists(pinmap_path):
        raise FileNotFoundError(f"Pinmap file not found: {pinmap_path}")

    cmd = [
        COMPILER_PATH,
        "-i", src_path,  # adds input flag and input file.
        "-o", out_path,  # specifies output file
        "-pinmap", pinmap_path  # specifies pinmap file.
    ]

    result = subprocess.run(
        cmd,
        capture_output=True,
        text=True
    )

    if result.returncode != 0:
        raise RuntimeError(
            f"\nDigital Pattern Compilation Failed:\n"
            f"STDOUT:\n{result.stdout}\n"
            f"STDERR:\n{result.stderr}"
        )

    return True
