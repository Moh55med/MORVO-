# Add content to index.js (this is a longer file)
@'
const cron = require('node-cron');
const axios = require('axios');
const express = require('express');

const app = express();
const PORT = process.env.PORT || 3000;

// Your Supabase Edge Function URLs
const FUNCTIONS = {
  fetchSeoSignals: 'https://ctcnutpnikiwvqbekdnp.supabase.co/functions/v1/fetchSeoSignals',
  fetchMentions: 'https://ctcnutpnikiwvqbekdnp.supabase.co/functions/v1/fetchMentions',
  fetchPosts: 'https://ctcnutpnikiwvqbekdnp.supabase.co/functions/v1/fetchPosts'
};

// Supabase configuration
const SUPABASE_CONFIG = {
  headers: {
    'Authorization': `Bearer ${process.env.SUPABASE_ANON_KEY}`,
    'Content-Type': 'application/json'
  }
};

// Function to call a Supabase Edge Function
async function callEdgeFunction(functionName, url) {
  try {
    console.log(`🚀 Calling ${functionName}...`);
    
    const response = await axios.post(url, {}, {
      ...SUPABASE_CONFIG,
      timeout: 30000 // 30 second timeout
    });
    
    console.log(`✅ ${functionName} completed successfully:`, response.data);
    return { success: true, data: response.data };
    
  } catch (error) {
    console.error(`❌ ${functionName} failed:`, error.response?.data || error.message);
    return { success: false, error: error.message };
  }
}

// Function to run all data collection tasks
async function runDataCollection() {
  console.log('🔄 Starting scheduled data collection...');
  const timestamp = new Date().toISOString();
  
  const results = await Promise.allSettled([
    callEdgeFunction('fetchSeoSignals', FUNCTIONS.fetchSeoSignals),
    callEdgeFunction('fetchMentions', FUNCTIONS.fetchMentions),
    callEdgeFunction('fetchPosts', FUNCTIONS.fetchPosts)
  ]);
  
  // Log results
  results.forEach((result, index) => {
    const functionNames = Object.keys(FUNCTIONS);
    const functionName = functionNames[index];
    
    if (result.status === 'fulfilled') {
      console.log(`📊 ${functionName}: ${result.value.success ? 'SUCCESS' : 'FAILED'}`);
    } else {
      console.log(`💥 ${functionName}: CRASHED - ${result.reason}`);
    }
  });
  
  console.log(`⏰ Data collection completed at ${timestamp}\n`);
}

// Schedule jobs
console.log('📅 Setting up scheduled jobs...');

// Run every 4 hours (0 */4 * * *)
cron.schedule('0 */4 * * *', () => {
  console.log('⏰ 4-hour scheduled run triggered');
  runDataCollection();
}, {
  scheduled: true,
  timezone: "UTC"
});

// Run every day at 6 AM UTC (0 6 * * *)
cron.schedule('0 6 * * *', () => {
  console.log('🌅 Daily morning run triggered');
  runDataCollection();
}, {
  scheduled: true,
  timezone: "UTC"
});

// Manual trigger endpoint for testing
app.get('/trigger', async (req, res) => {
  console.log('🔧 Manual trigger requested');
  await runDataCollection();
  res.json({ message: 'Data collection triggered successfully', timestamp: new Date().toISOString() });
});

// Health check endpoint
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy', 
    scheduler: 'running',
    timestamp: new Date().toISOString(),
    functions: Object.keys(FUNCTIONS)
  });
});

// Status endpoint
app.get('/', (req, res) => {
  res.json({
    name: 'MORVO Scheduler',
    status: 'running',
    description: 'Automated data collection from SE Ranking, Brand24, and Ayrshare',
    endpoints: {
      health: '/health',
      trigger: '/trigger (manual run)',
      status: '/ (this page)'
    },
    schedule: {
      'every_4_hours': '0 */4 * * * (every 4 hours)',
      'daily_morning': '0 6 * * * (6 AM UTC daily)'
    },
    functions: FUNCTIONS
  });
});

// Start the server
app.listen(PORT, () => {
  console.log(`🚀 MORVO Scheduler running on port ${PORT}`);
  console.log(`📋 Available endpoints:`);
  console.log(`   - Health: http://localhost:${PORT}/health`);
  console.log(`   - Manual trigger: http://localhost:${PORT}/trigger`);
  console.log(`   - Status: http://localhost:${PORT}/`);
  console.log(`⏰ Scheduled jobs are active!`);
  
  // Run once on startup for testing
  setTimeout(() => {
    console.log('🎯 Running initial data collection...');
    runDataCollection();
  }, 5000); // Wait 5 seconds after startup
});
'@ | Out-File "index.js" -Encoding UTF8