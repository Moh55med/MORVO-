#!/usr/bin/env python3
"""
MORVO Phase 4 - Enhanced Scheduler with Supabase Python Client
Automatically fetches marketing data and stores in Supabase
"""
from flask import Flask, jsonify, request
import os
import requests
import threading
import time
from datetime import datetime, timedelta
import logging
from supabase import create_client, Client
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = Flask(__name__)

# Configuration
SUPABASE_URL = os.environ.get('SUPABASE_URL', '')
SUPABASE_ANON_KEY = os.environ.get('SUPABASE_ANON_KEY', '')
SCHEDULE_INTERVAL = int(os.environ.get('SCHEDULE_INTERVAL_HOURS', 6))

# Initialize Supabase client
supabase: Client = None
if SUPABASE_URL and SUPABASE_ANON_KEY:
    try:
        supabase = create_client(SUPABASE_URL, SUPABASE_ANON_KEY)
        logger.info("✅ Supabase client initialized")
    except Exception as e:
        logger.error(f"❌ Failed to initialize Supabase client: {e}")

# Edge Function URLs
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
last_results = {}

def call_edge_function(function_name, url):
    """Call a Supabase Edge Function"""
    try:
        headers = {
            'Authorization': f'Bearer {SUPABASE_ANON_KEY}',
            'Content-Type': 'application/json'
        }
        
        logger.info(f"🔄 Calling {function_name} Edge Function...")
        response = requests.post(url, headers=headers, timeout=60, json={})
        
        if response.status_code == 200:
            logger.info(f"✅ {function_name} completed successfully")
            return {
                'status': 'success', 
                'data': response.json(),
                'timestamp': datetime.now().isoformat()
            }
        else:
            logger.error(f"❌ {function_name} failed: HTTP {response.status_code}")
            return {
                'status': 'error', 
                'code': response.status_code, 
                'message': response.text[:200],
                'timestamp': datetime.now().isoformat()
            }
            
    except requests.exceptions.RequestException as e:
        logger.error(f"❌ {function_name} network error: {str(e)}")
        return {
            'status': 'error', 
            'message': f"Network error: {str(e)}",
            'timestamp': datetime.now().isoformat()
        }

def verify_data_in_tables():
    """Verify that data was stored in Supabase tables"""
    if not supabase:
        return {'status': 'error', 'message': 'Supabase client not initialized'}
    
    try:
        results = {}
        
        # Check seo_signals table
        seo_data = supabase.table('seo_signals').select('*').limit(1).execute()
        results['seo_signals'] = {
            'count': len(seo_data.data),
            'latest': seo_data.data[0] if seo_data.data else None
        }
        
        # Check mentions table  
        mentions_data = supabase.table('mentions').select('*').limit(1).execute()
        results['mentions'] = {
            'count': len(mentions_data.data),
            'latest': mentions_data.data[0] if mentions_data.data else None
        }
        
        # Check posts table
        posts_data = supabase.table('posts').select('*').limit(1).execute()
        results['posts'] = {
            'count': len(posts_data.data),
            'latest': posts_data.data[0] if posts_data.data else None
        }
        
        logger.info("✅ Database verification completed")
        return {'status': 'success', 'tables': results}
        
    except Exception as e:
        logger.error(f"❌ Database verification failed: {e}")
        return {'status': 'error', 'message': str(e)}

def fetch_all_morvo_data():
    """Execute complete MORVO data collection cycle"""
    global last_run_time, run_count, last_results
    
    start_time = datetime.now()
    logger.info(f"🚀 Starting MORVO Phase 4 data collection at {start_time.isoformat()}")
    
    results = {}
    
    # Call each Edge Function
    for source, url in EDGE_FUNCTIONS.items():
        if url and url.startswith('http'):
            results[source] = call_edge_function(source, url)
            time.sleep(2)  # Brief pause between calls
        else:
            results[source] = {
                'status': 'skipped', 
                'message': 'URL not configured',
                'timestamp': datetime.now().isoformat()
            }
    
    # Verify data was stored
    verification = verify_data_in_tables()
    results['database_verification'] = verification
    
    # Update global state
    last_run_time = start_time
    run_count += 1
    last_results = results
    
    end_time = datetime.now()
    duration = (end_time - start_time).total_seconds()
    
    logger.info(f"🎉 MORVO Phase 4 collection completed in {duration:.2f} seconds")
    
    return {
        'phase': 4,
        'start_time': start_time.isoformat(),
        'end_time': end_time.isoformat(),
        'duration_seconds': duration,
        'run_number': run_count,
        'results': results
    }

def scheduler_worker():
    """Background scheduler thread"""
    global scheduler_running, next_run_time
    
    logger.info(f"📅 MORVO Phase 4 scheduler started - interval: {SCHEDULE_INTERVAL} hours")
    
    while scheduler_running:
        # Calculate next run
        next_run_time = datetime.now() + timedelta(hours=SCHEDULE_INTERVAL)
        
        # Execute data collection
        try:
            fetch_all_morvo_data()
        except Exception as e:
            logger.error(f"❌ Scheduler execution error: {str(e)}")
        
        # Wait for next scheduled run
        logger.info(f"⏰ Next MORVO collection scheduled for {next_run_time.isoformat()}")
        time.sleep(SCHEDULE_INTERVAL * 3600)

def start_scheduler():
    """Start the Phase 4 scheduler"""
    global scheduler_running
    
    if not scheduler_running:
        scheduler_running = True
        scheduler_thread = threading.Thread(target=scheduler_worker, daemon=True)
        scheduler_thread.start()
        logger.info("✅ MORVO Phase 4 scheduler activated")
        return True
    return False

# Flask Routes

@app.route('/')
def home():
    return jsonify({
        'project': 'MORVO Platform',
        'phase': '4 - Scheduler (COMPLETE)',
        'description': 'Automated marketing data collection from SE Ranking, Brand24, and Ayrshare',
        'status': 'active' if scheduler_running else 'stopped',
        'configuration': {
            'schedule': f'Every {SCHEDULE_INTERVAL} hours',
            'next_run': next_run_time.isoformat() if next_run_time else None,
            'last_run': last_run_time.isoformat() if last_run_time else None,
            'total_runs': run_count
        },
        'api_endpoints': {
            'detailed_status': '/api/status',
            'manual_trigger': 'POST /api/trigger',
            'last_results': '/api/results',
            'scheduler_start': 'POST /api/scheduler/start',
            'scheduler_stop': 'POST /api/scheduler/stop'
        }
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'phase4_active': scheduler_running,
        'supabase_connected': bool(supabase),
        'timestamp': datetime.now().isoformat()
    })

@app.route('/api/status')
def detailed_status():
    return jsonify({
        'morvo_phase_4': {
            'status': 'completed' if scheduler_running else 'ready',
            'scheduler_active': scheduler_running,
            'interval_hours': SCHEDULE_INTERVAL,
            'next_run': next_run_time.isoformat() if next_run_time else None,
            'last_run': last_run_time.isoformat() if last_run_time else None,
            'total_runs': run_count
        },
        'edge_functions': {
            'seo_signals': EDGE_FUNCTIONS['seo'],
            'brand_mentions': EDGE_FUNCTIONS['mentions'],
            'social_posts': EDGE_FUNCTIONS['posts']
        },
        'configuration': {
            'supabase_url_set': bool(SUPABASE_URL),
            'supabase_key_set': bool(SUPABASE_ANON_KEY),
            'supabase_client_ready': bool(supabase)
        },
        'project_phases': {
            'phase_1': 'Data Schema ✅',
            'phase_2': 'Supabase Setup ✅', 
            'phase_3': 'Edge Functions ✅',
            'phase_4': 'Scheduler ✅ (THIS PHASE)',
            'phase_5': 'Backend Logic (Next - Rafa)',
            'phase_6': 'Frontend Dashboard (Next - Rafa)'
        }
    })

@app.route('/api/results')
def get_last_results():
    """Get results from the last data collection run"""
    return jsonify({
        'last_run': last_run_time.isoformat() if last_run_time else None,
        'run_count': run_count,
        'results': last_results
    })

@app.route('/api/trigger', methods=['POST'])
def manual_trigger():
    """Manually trigger Phase 4 data collection"""
    logger.info("🔧 Manual Phase 4 trigger requested")
    
    try:
        result = fetch_all_morvo_data()
        return jsonify({
            'message': 'MORVO Phase 4 manual collection completed',
            'result': result
        })
    except Exception as e:
        logger.error(f"❌ Manual trigger failed: {str(e)}")
        return jsonify({
            'error': 'Manual trigger failed',
            'message': str(e)
        }), 500

@app.route('/api/scheduler/start', methods=['POST'])
def start_scheduler_endpoint():
    """Start the Phase 4 scheduler"""
    if start_scheduler():
        return jsonify({'message': 'MORVO Phase 4 scheduler started successfully'})
    else:
        return jsonify({'message': 'MORVO Phase 4 scheduler already running'})

@app.route('/api/scheduler/stop', methods=['POST'])
def stop_scheduler():
    """Stop the Phase 4 scheduler"""
    global scheduler_running
    scheduler_running = False
    logger.info("🛑 MORVO Phase 4 scheduler stopped")
    return jsonify({'message': 'MORVO Phase 4 scheduler stopped'})

# Initialize when app starts
@app.before_first_request
def initialize_phase_4():
    """Initialize MORVO Phase 4"""
    logger.info("🏁 Initializing MORVO Phase 4 - Scheduler...")
    
    # Verify configuration
    if not SUPABASE_URL or not SUPABASE_ANON_KEY:
        logger.warning("⚠️  Phase 4 requires SUPABASE_URL and SUPABASE_ANON_KEY environment variables")
        return
    
    # Start scheduler
    start_scheduler()
    
    # Initial run after 30 seconds
    def delayed_initial_run():
        time.sleep(30)
        logger.info("🎯 Running initial MORVO Phase 4 data collection...")
        fetch_all_morvo_data()
    
    threading.Thread(target=delayed_initial_run, daemon=True).start()
    logger.info("✅ MORVO Phase 4 initialization complete")

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    logger.info(f"🚀 Starting MORVO Phase 4 on port {port}")
    app.run(host='0.0.0.0', port=port, debug=False)