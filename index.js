

# Create new one - I'll give you a shorter version that works
@"
const cron = require('node-cron');
const axios = require('axios');
const express = require('express');

const app = express();
const PORT = process.env.PORT || 3000;

const FUNCTIONS = {
  fetchSeoSignals: 'https://ctcnutpnikiwvqbekdnp.supabase.co/functions/v1/fetchSeoSignals',
  fetchMentions: 'https://ctcnutpnikiwvqbekdnp.supabase.co/functions/v1/fetchMentions',
  fetchPosts: 'https://ctcnutpnikiwvqbekdnp.supabase.co/functions/v1/fetchPosts'
};

const SUPABASE_CONFIG = {
  headers: {
    'Authorization': `Bearer `+process.env.SUPABASE_ANON_KEY,
    'Content-Type': 'application/json'
  }
};

async function callEdgeFunction(functionName, url) {
  try {
    console.log(`Calling `+functionName+`...`);
    const response = await axios.post(url, {}, { ...SUPABASE_CONFIG, timeout: 30000 });
    console.log(`SUCCESS: `+functionName);
    return { success: true, data: response.data };
  } catch (error) {
    console.error(`FAILED: `+functionName+` - `+error.message);
    return { success: false, error: error.message };
  }
}

async function runDataCollection() {
  console.log('Starting data collection...');
  const results = await Promise.allSettled([
    callEdgeFunction('fetchSeoSignals', FUNCTIONS.fetchSeoSignals),
    callEdgeFunction('fetchMentions', FUNCTIONS.fetchMentions),
    callEdgeFunction('fetchPosts', FUNCTIONS.fetchPosts)
  ]);
  console.log('Data collection completed');
}

cron.schedule('0 */4 * * *', () => {
  console.log('4-hour scheduled run');
  runDataCollection();
});

cron.schedule('0 6 * * *', () => {
  console.log('Daily morning run');
  runDataCollection();
});

app.get('/trigger', async (req, res) => {
  await runDataCollection();
  res.json({ message: 'Triggered successfully', timestamp: new Date().toISOString() });
});

app.get('/health', (req, res) => {
  res.json({ status: 'healthy', timestamp: new Date().toISOString() });
});

app.get('/', (req, res) => {
  res.json({ name: 'MORVO Scheduler', status: 'running', functions: FUNCTIONS });
});

app.listen(PORT, () => {
  console.log(`MORVO Scheduler running on port `+PORT);
  setTimeout(runDataCollection, 5000);
});
"@ | Out-File "index.js" -Encoding UTF8