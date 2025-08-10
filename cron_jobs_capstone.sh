#!/bin/bash
# CAPSTONE CRON JOBS - 4 Times Per Day
# ======================================
# This script runs the temporal optimization pipeline 4 times per day
# instead of the frequent updates used during development.

# Set the project directory
PROJECT_DIR="/Users/maso/GitHub/maso-ai-crypto"
cd "$PROJECT_DIR"

# Activate virtual environment
source .venv/bin/activate

# Function to log execution
log_execution() {
    echo "$(date): $1" >> data/logs/cron_executions.log
}

# Function to run with error handling
run_with_logging() {
    local command="$1"
    local description="$2"
    
    log_execution "Starting: $description"
    
    if python3 collectors/scheduler.py --mode "$command"; then
        log_execution "Success: $description"
    else
        log_execution "Error: $description failed"
    fi
}

# Main execution based on argument
case "$1" in
    "full")
        # Full cycle - runs every 6 hours (4 times per day)
        run_with_logging "full" "Full temporal optimization cycle"
        ;;
    "collect")
        # News collection only
        run_with_logging "collect" "News collection cycle"
        ;;
    "analyze")
        # Analysis pipeline only
        run_with_logging "analyze" "Analysis pipeline cycle"
        ;;
    "status")
        # Show status
        python3 collectors/scheduler.py --mode status
        ;;
    *)
        echo "Usage: $0 {full|collect|analyze|status}"
        echo ""
        echo "CAPSTONE SCHEDULE (4 times per day):"
        echo "  0 */6 * * * $0 full     # Every 6 hours"
        echo "  0 0,6,12,18 * * * $0 full  # At midnight, 6am, noon, 6pm"
        echo ""
        echo "Manual execution:"
        echo "  $0 full     # Run full cycle now"
        echo "  $0 collect  # Collect news only"
        echo "  $0 analyze  # Analyze only"
        echo "  $0 status   # Show current status"
        exit 1
        ;;
esac
