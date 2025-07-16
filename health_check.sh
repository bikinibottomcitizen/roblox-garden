#!/bin/bash

# Health check script for Docker container
# Checks if the application is running properly

set -e

# Function to check if Python process is running
check_python_process() {
    if pgrep -f "python -m roblox_garden" > /dev/null; then
        return 0
    else
        return 1
    fi
}

# Function to check if application can import modules
check_imports() {
    python -c "
import sys
sys.path.insert(0, '/app')
try:
    from roblox_garden.config.settings import Settings
    from roblox_garden.core.application import RobloxGardenApp
    print('✅ All imports successful')
    exit(0)
except Exception as e:
    print(f'❌ Import error: {e}')
    exit(1)
"
}

# Function to check if log file is being written
check_logs() {
    LOG_FILE="/app/logs/roblox_garden.log"
    if [ -f "$LOG_FILE" ]; then
        # Check if log file was modified in the last 10 minutes
        if [ $(find "$LOG_FILE" -mmin -10 | wc -l) -gt 0 ]; then
            return 0
        else
            echo "⚠️ Log file not updated recently"
            return 1
        fi
    else
        echo "⚠️ Log file not found"
        return 1
    fi
}

echo "🔍 Health check starting..."

# Check Python process
if check_python_process; then
    echo "✅ Python process running"
else
    echo "❌ Python process not found"
    exit 1
fi

# Check imports
if check_imports; then
    echo "✅ Module imports working"
else
    echo "❌ Module import failed"
    exit 1
fi

# Check logs (optional - don't fail if logs are missing)
if check_logs; then
    echo "✅ Log file active"
else
    echo "⚠️ Log file issues (non-critical)"
fi

echo "✅ Health check passed"
exit 0
