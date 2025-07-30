import { serve } from 'https://deno.land/std@0.168.0/http/server.ts'
import { createClient } from 'https://esm.sh/@supabase/supabase-js@2'

const corsHeaders = {
  'Access-Control-Allow-Origin': '*',
  'Access-Control-Allow-Headers': 'authorization, x-client-info, apikey, content-type',
}

serve(async (req) => {
  // Handle CORS preflight requests
  if (req.method === 'OPTIONS') {
    return new Response('ok', { headers: corsHeaders })
  }

  try {
    // Initialize Supabase client
    const supabaseClient = createClient(
      Deno.env.get('SUPABASE_URL') ?? '',
      Deno.env.get('SUPABASE_SERVICE_ROLE_KEY') ?? ''
    )

    // Get Ayrshare API key from environment
    const ayrshareApiKey = Deno.env.get('AYRSHARE_API_KEY')
    if (!ayrshareApiKey) {
      throw new Error('AYRSHARE_API_KEY is not configured')
    }

    console.log('Fetching posts from Ayrshare API...')

    // Ayrshare API endpoint
    const ayrshareUrl = 'https://app.ayrshare.com/api/history'
    
    // Fetch data from Ayrshare API
    const response = await fetch(ayrshareUrl, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${ayrshareApiKey}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error(`Ayrshare API error: ${response.status} ${response.statusText}`)
    }

    const ayrshareData = await response.json()
    const posts = ayrshareData.posts || ayrshareData.data || ayrshareData
    console.log(`Received ${posts.length || 0} posts from Ayrshare`)

    // Transform Ayrshare data to match our schema
    const transformedData = posts.map((item: any) => ({
      post_id: item.id || item.post_id || `ayr_${Date.now()}_${Math.random()}`,
      post_content: item.post || item.content || item.text || '',
      platform: item.platform || item.social_network || 'unknown',
      status: item.status || (item.errors && item.errors.length > 0 ? 'failed' : 'published'),
      timestamp: item.published_at || item.created_at || item.date || new Date().toISOString(),
      scheduled_time: item.scheduled_at || item.schedule_date || null,
      media_urls: item.media_urls || item.images || item.videos || [],
      hashtags: item.hashtags || [],
      mentions: item.mentions || item.user_mentions || [],
      engagement_metrics: {
        likes: parseInt(item.likes || item.reactions?.like || '0'),
        shares: parseInt(item.shares || item.retweets || '0'),
        comments: parseInt(item.comments || item.replies || '0'),
        saves: parseInt(item.saves || item.bookmarks || '0')
      },
      reach: parseInt(item.reach || item.impressions || '0'),
      impressions: parseInt(item.impressions || item.views || '0'),
      click_through_rate: parseFloat(item.ctr || item.click_through_rate || '0'),
      api_response: {
        status: item.status || 'success',
        id: item.id,
        url: item.url || item.permalink
      },
      error_message: item.errors && item.errors.length > 0 ? item.errors.join(', ') : null,
      project_id: item.project_id || 'default_project',
      source_platform: 'ayrshare',
      is_active: true,
      metadata: {
        api_version: 'v1',
        fetched_at: new Date().toISOString(),
        raw_data: item
      }
    }))

    // Insert data into Supabase
    const { data, error } = await supabaseClient
      .from('posts')
      .insert(transformedData)

    if (error) {
      console.error('Supabase insert error:', error)
      throw error
    }

    console.log(`Successfully inserted ${transformedData.length} posts`)

    return new Response(
      JSON.stringify({
        success: true,
        message: `Successfully processed ${transformedData.length} posts`,
        data: {
          inserted_count: transformedData.length,
          timestamp: new Date().toISOString()
        }
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 200,
      }
    )

  } catch (error) {
    console.error('Error in fetchPosts:', error)
    
    return new Response(
      JSON.stringify({
        success: false,
        error: error.message,
        timestamp: new Date().toISOString()
      }),
      {
        headers: { ...corsHeaders, 'Content-Type': 'application/json' },
        status: 500,
      }
    )
  }
}) 