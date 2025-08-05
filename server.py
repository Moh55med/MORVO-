#!/usr/bin/env python3
"""
MORVO Phase 4 - Complete Scheduler
Automatically fetches data from SE Ranking, Brand24, and Ayrshare via Supabase Edge Functions
"""
from flask import Flask, jsonify, request
import os
import requests
import threading
import time
from datetime import datetime, timedelta
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration from environment variables
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY', '')
SCHEDULE_INTERVAL = int(os.environ.get('SCHEDULE_INTERVAL_HOURS', 6))  # Default 6 hours

# Supabase Edge Function URLs (update these with your actual project URLs)
EDGE_FUNCTIONS = {
    'seo': f'{SUPABASE_URL}/functions/v1/fetchSeoSignals',
    'mentions': f'{SUPABASE_URL}/functions/v1/fetchMentions', 
    'posts': f'{SUPABASE_URL}/functions/v1/fetchPosts'
}

# Global scheduler state
scheduler_running = False
next_run_time = None
last_run_time = None
run_count = 0

def call_supabase_function(function_name, url):
    """Call a Supabase Edge Function"""
    try:
        headers = {
            'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
            'Content-Type': 'application/json'
        }
        
        logger.info(f"🔄 Calling {function_name} function...")
        response = requests.get(url, headers=headers, timeout=30)
        
        if response.status_code == 200:
            logger.info(f"✅ {function_name} completed successfully")
            return {'status': 'success', 'data': response.json()}
        else:
            logger.error(f"❌ {function_name} failed: {response.status_code}")
            return {'status': 'error', 'code': response.status_code, 'message': response.text}
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ {function_name} exception: {str(e)}")
        return {'status': 'error', 'message': str(e)}

def fetch_all_data():
    """Fetch data from all MORVO sources"""
    global last_run_time, run_count
    
    start_time = datetime.now()
    logger.info(f"🚀 Starting MORVO data collection at {start_time.isoformat()}")
    
    results = {}
    
    # Call each Supabase Edge Function
    for source, url in EDGE_FUNCTIONS.items():
        if url.startswith('http'):  # Only call if URL is configured
            results[source] = call_supabase_function(source, url)
        else:
            results[source] = {'status': 'skipped', 'message': 'URL not configured'}
    
    # Update statistics
    last_run_time = start_time
    run_count += 1
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info(f"🎉 MORVO data collection completed in {duration:.2f} seconds")
    
    return {
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(), 
        'duration_seconds': duration,
        'results': results
    }

def schedule_worker():
    """Background thread that runs the scheduler"""
    global scheduler_running, next_run_time
    
    logger.info(f"📅 MORVO scheduler started - running every {SCHEDULE_INTERVAL} hours")
    
    while scheduler_running:
        # Calculate next run time
        next_run_time = datetime.now() + timedelta(hours=SCHEDULE_INTERVAL)
        
        # Run data collection
        try:
            fetch_all_data()
        except Exception as e:
            logger.error(f"❌ Scheduler error: {str(e)}")
        
        # Wait for next scheduled run
        logger.info(f"⏰ Next MORVO data collection at {next_run_time.isoformat()}")
        time.sleep(SCHEDULE_INTERVAL * 3600)  # Convert hours to seconds

def start_scheduler():
    """Start the background scheduler"""
    global scheduler_running
    
    if not scheduler_running:
        scheduler_running = True
        scheduler_thread = threading.Thread(target=schedule_worker, daemon=True)
        scheduler_thread.start()
        logger.info("✅ MORVO scheduler started")
        return True
    return False

# API Routes
@app.route('/')
def home():
    return jsonify({
        'project': 'MORVO Phase 4 - Scheduler',
        'description': 'Automated marketing data collection system',
        'status': 'active' if scheduler_running else 'stopped',
        'schedule': f'Every {SCHEDULE_INTERVAL} hours',
        'next_run': next_run_time.isoformat() if next_run_time else None,
        'last_run': last_run_time.isoformat() if last_run_time else None,
        'total_runs': run_count,
        'endpoints': {
            'status': '/api/status',
            'manual_trigger': '/api/trigger',
            'scheduler_control': '/api/scheduler/start | /api/scheduler/stop'
        }
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'scheduler_running': scheduler_running,
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status')
def api_status():
    return jsonify({
        'phase4_status': 'completed' if scheduler_running else 'ready',
        'scheduler': {
            'running': scheduler_running,
            'interval_hours': SCHEDULE_INTERVAL,
            'next_run': next_run_time.isoformat() if next_run_time else None,
            'last_run': last_run_time.isoformat() if last_run_time else None,
            'total_runs': run_count
        },
        'supabase_functions': {
            'seo_signals': EDGE_FUNCTIONS['seo'],
            'brand_mentions': EDGE_FUNCTIONS['mentions'],
            'social_posts': EDGE_FUNCTIONS['posts']
        },
        'configuration': {
            'supabase_url_configured': bool(SUPABASE_URL),
            'supabase_key_configured': bool(SUPABASE_ANON_KEY)
        }
    })

@app.route('/api/trigger', methods=['POST'])
def manual_trigger():
    """Manually trigger data collection"""
    logger.info("🔧 Manual data collection triggered")
    
    try:
        result = fetch_all_data()
        return jsonify({
            'message': 'Manual data collection completed',
            'result': result
        })
    except Exception as e:
        logger.error(f"❌ Manual trigger failed: {str(e)}")
        return jsonify({
            'error': 'Manual trigger failed',
            'message': str(e)
        }), 500

@app.route('/api/scheduler/start', methods=['POST'])
def start_scheduler_api():
    """Start the scheduler via API"""
    if start_scheduler():
        return jsonify({'message': 'Scheduler started successfully'})
    else:
        return jsonify({'message': 'Scheduler already running'})

@app.route('/api/scheduler/stop', methods=['POST'])
def stop_scheduler():
    """Stop the scheduler"""
    global scheduler_running
    scheduler_running = False
    logger.info("🛑 MORVO scheduler stopped")
    return jsonify({'message': 'Scheduler stopped'})

# Start scheduler when app starts
@app.before_first_request
def initialize():
    """Initialize the scheduler when the app starts"""
    logger.info("🏁 Initializing MORVO Phase 4 Scheduler...")
    
    # Check configuration
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        logger.warning("⚠️  Supabase configuration missing - add SUPABASE_URL and SUPABASE_ANON_KEY environment variables")
    
    # Start scheduler automatically
    start_scheduler()
    
    # Run initial data collection after 30 seconds
    def initial_run():
        time.sleep(30)
        logger.info("🎯 Running initial data collection...")
        fetch_all_data()
    
    threading.Thread(target=initial_run, daemon=True).start()

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=False)