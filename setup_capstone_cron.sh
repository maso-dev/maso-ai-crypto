#!/bin/bash
# CAPSTONE CRON SETUP SCRIPT
# ==========================
# This script helps you set up the cron job for 4 times per day updates

echo "🎓 CAPSTONE CRON SETUP"
echo "======================="
echo ""

# Get the current project directory
PROJECT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
CRON_SCRIPT="$PROJECT_DIR/cron_jobs_capstone.sh"

echo "📍 Project Directory: $PROJECT_DIR"
echo "📜 Cron Script: $CRON_SCRIPT"
echo ""

# Check if cron script exists and is executable
if [ ! -f "$CRON_SCRIPT" ]; then
    echo "❌ Cron script not found: $CRON_SCRIPT"
    exit 1
fi

if [ ! -x "$CRON_SCRIPT" ]; then
    echo "🔧 Making cron script executable..."
    chmod +x "$CRON_SCRIPT"
fi

echo "✅ Cron script is ready: $CRON_SCRIPT"
echo ""

# Show current cron jobs
echo "📋 Current Cron Jobs:"
crontab -l 2>/dev/null || echo "   No cron jobs currently set"
echo ""

# Show the recommended cron configuration
echo "🚀 RECOMMENDED CRON CONFIGURATION:"
echo "=================================="
echo ""
echo "Add this line to your crontab:"
echo ""
echo "   # CAPSTONE: Run every 6 hours (4 times per day)"
echo "   0 */6 * * * $CRON_SCRIPT full"
echo ""
echo "Or for specific times (midnight, 6am, noon, 6pm):"
echo ""
echo "   # CAPSTONE: Run at specific times (4 times per day)"
echo "   0 0,6,12,18 * * * $CRON_SCRIPT full"
echo ""

# Ask user if they want to set up the cron job
read -p "🤔 Would you like me to set up the cron job now? (y/n): " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "🔧 Setting up cron job..."
    
    # Create temporary crontab file
    TEMP_CRON=$(mktemp)
    
    # Get existing cron jobs
    crontab -l 2>/dev/null > "$TEMP_CRON"
    
    # Add our capstone cron job
    echo "" >> "$TEMP_CRON"
    echo "# CAPSTONE: Run every 6 hours (4 times per day)" >> "$TEMP_CRON"
    echo "0 */6 * * * $CRON_SCRIPT full" >> "$TEMP_CRON"
    
    # Install the new crontab
    if crontab "$TEMP_CRON"; then
        echo "✅ Cron job installed successfully!"
        echo ""
        echo "📋 New cron configuration:"
        crontab -l
        echo ""
        echo "🎯 Your system will now update 4 times per day:"
        echo "   - Midnight (00:00)"
        echo "   - 6:00 AM"
        echo "   - Noon (12:00)"
        echo "   - 6:00 PM"
    else
        echo "❌ Failed to install cron job"
        exit 1
    fi
    
    # Clean up
    rm "$TEMP_CRON"
    
else
    echo "📝 Manual Setup Instructions:"
    echo "============================="
    echo ""
    echo "1. Edit your crontab:"
    echo "   crontab -e"
    echo ""
    echo "2. Add this line:"
    echo "   0 */6 * * * $CRON_SCRIPT full"
    echo ""
    echo "3. Save and exit"
    echo ""
    echo "4. Verify with: crontab -l"
fi

echo ""
echo "🧪 Test the setup:"
echo "   $CRON_SCRIPT status"
echo ""
echo "📚 For more information, see: CAPSTONE_UPDATE_SCHEDULE.md"
echo ""
echo "🎓 Your capstone is now configured for professional presentation!"
