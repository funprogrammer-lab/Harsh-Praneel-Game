# Cyberpunk Platformer

A Pygame-based platformer built in Python with neon cyberpunk visuals, moving platforms, hazards, and warp pipes.

## Requirements

- Python 3.11+ (or a compatible 3.10/3.12 environment)
- `pip` package manager
- `pygame` 2.6.1 or newer

## Installation

1. Clone the repository (Utilize your OS's terminal):

```bash
git clone <your-repo-url>
cd "Harsh & Praneel Game"
```

2. Install Python if needed:

- macOS: use Homebrew or the official Python installer
- Windows: use the official Python installer from python.org
- Linux: use your distribution package manager (for example, `sudo apt install python3 python3-venv python3-pip`)

3. Create and activate a virtual environment:

macOS / Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

Windows (PowerShell):

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

Windows (Command Prompt):

```cmd
python -m venv .venv
.\.venv\Scripts\activate
```

4. Install dependencies:

```bash
pip install pygame
```

5. Verify installation:

```bash
python -c "import pygame; print(pygame.version.ver)"
```

If this script prints a pygame version, the game is ready to run.

## Running the Game

Run the main game file:

```bash
python platformer.py
```

## Controls

- `A` / `D` : Move left / right
- `W` : Jump / double jump
- `S` : Use warp pipes
- `E` : Restart current level
- `N` : Advance to next level

## Files

- `platformer.py` - Main game logic and level data
- `ChatGPT Image Jun 28, 2026, 09_13_16 PM.png` - Background asset used by the game if present
- `Orbitron/` - Optional custom font files

## Notes

- The game window is resizable.
- The level designs include static platforms, moving platforms, hazards, and warp pipes.
- If the `Orbitron` font is unavailable, the game will use a system fallback font.
- The `Orbitron` font is a Google font available online to download.# Harsh-Praneel-Game
# Harsh-Praneel-Game
