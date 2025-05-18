'''
pip install pyinstaller opencv-python numpy PyQt5
python build.py
'''
import os
import sys
import platform
import subprocess

def uninstall_conflicts():
    """Uninstall packages that might conflict with PyInstaller"""
    conflicts = ['pathlib']
    for package in conflicts:
        try:
            subprocess.check_call([sys.executable, '-m', 'pip', 'uninstall', '-y', package])
            print(f"Uninstalled {package}")
        except:
            print(f"No {package} package found or could not uninstall it")

def install_requirements():
    """Install required packages for building"""
    requirements = [
        'pyinstaller',
        'opencv-python',
        'numpy',
        'PyQt5'
    ]
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', '--upgrade', 'pip'])
    subprocess.check_call([sys.executable, '-m', 'pip', 'install', *requirements])

def build_executable():
    """Build executable based on platform"""
    system = platform.system().lower()
    
    # Common PyInstaller options for single file
    options = [
        '--name=VideoProcessor',
        '--onefile',  # Create a single file
        '--noconsole',  # No console window
        '--clean',  # Clean PyInstaller cache
        '--add-data=README.md:.',  # Include README
        # Essential imports
        '--hidden-import=PyQt5',
        '--hidden-import=PyQt5.QtCore',
        '--hidden-import=PyQt5.QtGui',
        '--hidden-import=PyQt5.QtWidgets',
        '--hidden-import=cv2',
        '--hidden-import=numpy',
        # Exclude unnecessary modules
        '--exclude-module=matplotlib',
        '--exclude-module=scipy',
        '--exclude-module=PIL',
        '--exclude-module=tkinter',
        '--exclude-module=PyQt5.QtWebEngineWidgets',
        '--exclude-module=PyQt5.QtWebEngine',
        '--exclude-module=PyQt5.QtWebEngineCore',
        '--exclude-module=PyQt5.QtWebEngineQuick',
        '--exclude-module=PyQt5.QtWebSockets',
        '--exclude-module=PyQt5.QtNetwork',
        '--exclude-module=PyQt5.QtSql',
        '--exclude-module=PyQt5.QtTest',
        '--exclude-module=PyQt5.QtXml',
        '--exclude-module=PyQt5.QtXmlPatterns',
        '--exclude-module=PyQt5.QtDesigner',
        '--exclude-module=PyQt5.QtHelp',
        '--exclude-module=PyQt5.QtOpenGL',
        '--exclude-module=PyQt5.QtPrintSupport',
        '--exclude-module=PyQt5.QtQml',
        '--exclude-module=PyQt5.QtQuick',
        '--exclude-module=PyQt5.QtQuickWidgets',
        '--exclude-module=PyQt5.QtSvg',
        '--exclude-module=PyQt5.QtSvgWidgets',
        '--exclude-module=PyQt5.QtWebChannel',
        # Exclude unnecessary OpenCV modules
        '--exclude-module=cv2.cuda',
        '--exclude-module=cv2.gapi',
        '--exclude-module=cv2.ml',
        '--exclude-module=cv2.ocl',
        '--exclude-module=cv2.videoio_registry',
        '--exclude-module=cv2.utils',
        # Exclude unnecessary numpy modules
        '--exclude-module=numpy.random._examples',
        '--exclude-module=numpy.doc',
        '--exclude-module=numpy.f2py',
        '--exclude-module=numpy.distutils',
        '--exclude-module=numpy.testing',
        '--exclude-module=numpy.core.tests',
        '--exclude-module=numpy.lib.tests',
        '--exclude-module=numpy.linalg.tests',
        '--exclude-module=numpy.ma.tests',
        '--exclude-module=numpy.matrixlib.tests',
        '--exclude-module=numpy.polynomial.tests',
        '--exclude-module=numpy.random.tests',
        '--exclude-module=numpy.tests',
        'main.py'
    ]
    
    # Platform specific options
    if system == 'darwin':  # macOS
        options.extend([
            '--target-arch=universal2',
            '--codesign-identity=-',  # Skip code signing
            '--osx-bundle-identifier=com.videoprocessor.app'
        ])
    elif system == 'linux':
        options.extend([
            '--strip',  # Strip binary
            '--noupx'  # Don't use UPX compression
        ])
    elif system == 'windows':
        options.extend([
            '--uac-admin',  # Request admin privileges
            # '--win-private-assemblies',  # Bundle private assemblies
            # '--win-no-prefer-redirects'
        ])
    
    # Build command
    subprocess.check_call(['pyinstaller', *options])

def main():
    try:
        print("Uninstalling conflicting packages...")
        uninstall_conflicts()
        
        print("\nInstalling requirements...")
        install_requirements()
        
        print(f"\nBuilding for {platform.system()}...")
        build_executable()
        
        print("\nBuild completed!")
        print("The executable can be found in the 'dist' directory.")
        
    except subprocess.CalledProcessError as e:
        print(f"\nError during build process: {str(e)}")
        print("Please check the error message above and try again.")
        sys.exit(1)
    except Exception as e:
        print(f"\nUnexpected error: {str(e)}")
        sys.exit(1)

if __name__ == '__main__':
    main() 