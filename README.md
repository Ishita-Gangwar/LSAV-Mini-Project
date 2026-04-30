# LSAV-Mini-Project
A lightweight log rotation utility for Linux with a terminal dashboard UI. logmini.sh handles automatic compression and cleanup of log files, while dashboard.py provides a real-time Textual-based interface to monitor and trigger rotations.

1. Rotates .log files that exceed a size threshold or age limit
2. Compresses rotated logs with gzip in a race-condition-safe way
3. Automatically cleans up archives older than the retention window
4. Terminal dashboard shows active vs archived file counts and sizes
5. Progress bar visualises the active/archive storage split
6. "Run Janitor Sweep" button triggers rotation without leaving the UI
7. Non-blocking async subprocess keeps the dashboard responsive during sweeps

REQUIREMENTS:
Ubuntu / Debian Linux
Python 3.8+
Textual (pip install textual)

SETUP:
1. Clone the repo:
   git clone https://github.com/your-username/logmini.git
   cd logmini
2. Create and activate a virtual environment:
   python3 -m venv venv
   source venv/bin/activate
3. Install Python dependencies:
   pip install textual
4. Make the shell script executable:
   chmod +x logmini.sh

CONFIGURATION:
export LOG_DIR=~/my/log/directory
