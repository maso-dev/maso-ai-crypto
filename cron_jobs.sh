#!/bin/bash
"""
Cron Jobs Configuration for Temporal Optimization
=================================================

This file contains the cron job configurations for running the temporal
optimization pipeline on a schedule.

For Replit deployment, these can be set up using Replit's Cron feature
or run manually on a schedule.
"""

# Set up environment
export PYTHONPATH="/home/runner/workspace:$PYTHONPATH"
cd /home/runner/workspace

# Activate virtual environment if it exists
if [ -d ".venv" ]; then
    source .venv/bin/activate
fi

# =============================================================================
# PRODUCTION SCHEDULE (Recommended)
# =============================================================================

# Full cycle every 6 hours (4 times per day)
# 0 */6 * * * /home/runner/workspace/cron_jobs.sh full

# Collection only every 2 hours (for breaking news)
# 0 */2 * * * /home/runner/workspace/cron_jobs.sh collect

# Analysis only every 3 hours (to process collected articles)
# 30 */3 * * * /home/runner/workspace/cron_jobs.sh analyze

# =============================================================================
# DEVELOPMENT SCHEDULE (More frequent for testing)
# =============================================================================

# Full cycle every hour
# 0 * * * * /home/runner/workspace/cron_jobs.sh full

# Collection every 30 minutes
# */30 * * * * /home/runner/workspace/cron_jobs.sh collect

# =============================================================================
# MANUAL EXECUTION
# =============================================================================

# Function to run the scheduler
run_scheduler() {
    local mode=$1
    local timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    echo "[$timestamp] Starting temporal optimization: $mode"
    
    # Run the scheduler
    python3 collectors/scheduler.py --mode "$mode" 2>&1 | tee -a "data/logs/cron_${mode}_$(date +%Y%m%d).log"
    
    local exit_code=$?
    timestamp=$(date '+%Y-%m-%d %H:%M:%S')
    
    if [ $exit_code -eq 0 ]; then
        echo "[$timestamp] ✅ Temporal optimization completed: $mode"
    else
        echo "[$timestamp] ❌ Temporal optimization failed: $mode (exit code: $exit_code)"
    fi
    
    return $exit_code
}

# =============================================================================
# MAIN EXECUTION
# =============================================================================

case "${1:-full}" in
    "collect")
        echo "🚀 Running news collection only..."
        run_scheduler "collect"
        ;;
    "analyze") 
        echo "🧠 Running analysis pipeline only..."
        run_scheduler "analyze"
        ;;
    "full")
        echo "🏗️ Running full temporal optimization cycle..."
        run_scheduler "full"
        ;;
    "status")
        echo "📊 Checking temporal optimization status..."
        python3 collectors/scheduler.py --mode "status"
        ;;
    *)
        echo "Usage: $0 {collect|analyze|full|status}"
        echo ""
        echo "Modes:"
        echo "  collect - Run news collection only"
        echo "  analyze - Run analysis pipeline only"  
        echo "  full    - Run complete cycle (default)"
        echo "  status  - Show system status"
        exit 1
        ;;
esac
