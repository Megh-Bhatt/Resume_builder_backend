"""
Script to install all required LaTeX packages for the resume template
Run this ONCE after installing TeX Live
"""

import subprocess
import sys
from pathlib import Path

# List of required packages for the resume template
REQUIRED_PACKAGES = [
    "latexsym",
    "fullpage",
    "titlesec",
    "marvosym",
    "color",
    "verbatim",
    "enumitem",
    "hyperref",
    "fancyhdr",
    "babel",
    "tabularx",
    "fontawesome5",
    "tools",  # for multicol
]

def find_tlmgr():
    """Find tlmgr executable on Windows"""
    possible_paths = [
        r"C:\texlive\2025\bin\windows\tlmgr.bat",
        r"C:\texlive\2025\bin\win32\tlmgr.bat",
        r"C:\texlive\2024\bin\windows\tlmgr.bat",
        r"C:\texlive\2024\bin\win32\tlmgr.bat",
    ]
    
    for path in possible_paths:
        if Path(path).exists():
            print(f"Found tlmgr at: {path}")
            return path
    
    # Try to find it in PATH
    try:
        result = subprocess.run(
            ["where", "tlmgr"],
            capture_output=True,
            text=True,
            check=True
        )
        path = result.stdout.strip().split('\n')[0]
        print(f"Found tlmgr in PATH: {path}")
        return path
    except:
        pass
    
    return None

def install_texlive_packages():
    """Install required packages using tlmgr (TeX Live package manager)"""
    
    print("Installing required LaTeX packages for resume template...")
    print("This may take a few minutes...\n")
    
    # Find tlmgr
    tlmgr_path = find_tlmgr()
    if not tlmgr_path:
        print("ERROR: Could not find tlmgr (TeX Live package manager)")
        print("\nPlease make sure TeX Live is installed correctly.")
        print("You can also try adding TeX Live to your PATH:")
        print("  1. Search 'Environment Variables' in Windows")
        print("  2. Edit 'Path' variable")
        print("  3. Add: C:\\texlive\\2025\\bin\\windows")
        print("\nOr install packages manually using TeX Live Manager GUI")
        return False
    
    # Update tlmgr itself first
    print("Updating tlmgr...")
    try:
        subprocess.run(
            [tlmgr_path, "update", "--self"],
            check=True,
            capture_output=True,
            text=True,
            shell=True  # Important for .bat files on Windows
        )
        print("✓ tlmgr updated\n")
    except subprocess.CalledProcessError as e:
        print(f"Warning: Could not update tlmgr: {e.stderr}")
        print("Continuing with package installation...\n")
    
    # Install each package
    print("Installing packages (this may take several minutes)...\n")
    failed_packages = []
    installed_count = 0
    
    for package in REQUIRED_PACKAGES:
        print(f"Installing {package}...", end=" ", flush=True)
        try:
            result = subprocess.run(
                [tlmgr_path, "install", package],
                check=True,
                capture_output=True,
                text=True,
                timeout=300,  # 5 minute timeout per package
                shell=True
            )
            print("✓")
            installed_count += 1
        except subprocess.CalledProcessError as e:
            stderr_lower = e.stderr.lower() if e.stderr else ""
            stdout_lower = e.stdout.lower() if e.stdout else ""
            
            if "already installed" in stdout_lower or "already installed" in stderr_lower:
                print("✓ (already installed)")
                installed_count += 1
            else:
                print(f"✗ FAILED")
                print(f"  Error: {e.stderr[:200] if e.stderr else e.stdout[:200]}")
                failed_packages.append(package)
        except subprocess.TimeoutExpired:
            print("✗ TIMEOUT")
            failed_packages.append(package)
        except Exception as e:
            print(f"✗ ERROR: {str(e)[:100]}")
            failed_packages.append(package)
    
    print("\n" + "="*60)
    print(f"Installation complete: {installed_count}/{len(REQUIRED_PACKAGES)} packages")
    
    if failed_packages:
        print(f"\n⚠ WARNING: {len(failed_packages)} packages failed to install:")
        for pkg in failed_packages:
            print(f"  - {pkg}")
        print("\nYou can try installing these manually:")
        print(f"  {tlmgr_path} install {' '.join(failed_packages)}")
    else:
        print("\n✓ All packages installed successfully!")
        print("\nYou can now run your resume generator!")
    print("="*60)
    
    return len(failed_packages) == 0

if __name__ == "__main__":
    try:
        success = install_texlive_packages()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\nInstallation cancelled by user")
        sys.exit(1)
    except Exception as e:
        print(f"\n\nUnexpected error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)