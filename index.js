// index.js - MORVO Platform Entry Point
const express = require('express');
const cors = require('cors');
const path = require('path');

const app = express();
const PORT = process.env.PORT || 3000;

// Middleware
app.use(cors());
app.use(express.json());
app.use(express.static('public'));

// Root endpoint
app.get('/', (req, res) => {
  res.json({
    name: 'MORVO Platform',
    description: 'Marketing Data Collection System',
    status: 'Active',
    version: '1.0.0',
    endpoints: {
      status: '/api/status',
      health: '/health'
    },
    timestamp: new Date().toISOString()
  });
});

// Health check
app.get('/health', (req, res) => {
  res.json({ 
    status: 'healthy',
    uptime: process.uptime(),
    timestamp: new Date().toISOString()
  });
});

// API status endpoint
app.get('/api/status', (req, res) => {
  res.json({
    project: 'MORVO',
    components: {
      'Data Schema': 'Completed ✅',
      'Database Setup': 'In Progress 🔄', 
      'Edge Functions': 'Planned 📋',
      'Scheduler': 'In Progress 🔄',
      'Backend Logic': 'Planned 📋',
      'Frontend Dashboard': 'Planned 📋'
    },
    integrations: ['SE Ranking', 'Brand24', 'Ayrshare'],
    database: 'Supabase'
  });
});

// Start server
app.listen(PORT, '0.0.0.0', () => {
  console.log(`🚀 MORVO Platform running on port ${PORT}`);
  console.log(`🌐 Environment: ${process.env.NODE_ENV || 'development'}`);
  console.log(`📊 Ready to serve MORVO API endpoints`);
});

// Handle graceful shutdown
process.on('SIGTERM', () => {
  console.log('🔄 SIGTERM received, shutting down gracefully');
  process.exit(0);
});

process.on('SIGINT', () => {
  console.log('🔄 SIGINT received, shutting down gracefully');
  process.exit(0);
});