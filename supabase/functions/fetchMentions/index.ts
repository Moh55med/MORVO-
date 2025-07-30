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

    // Get Brand24 API key from environment
    const brand24ApiKey = Deno.env.get('BRAND24_API_KEY')
    if (!brand24ApiKey) {
      throw new Error('BRAND24_API_KEY is not configured')
    }

    console.log('Fetching mentions from Brand24 API...')

    // Brand24 API endpoint
    const brand24Url = 'https://api.brand24.com/v2/mentions'
    
    // Fetch data from Brand24 API
    const response = await fetch(brand24Url, {
      method: 'GET',
      headers: {
        'Authorization': `Bearer ${brand24ApiKey}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error(`Brand24 API error: ${response.status} ${response.statusText}`)
    }

    const brand24Data = await response.json()
    const mentions = brand24Data.results || brand24Data.mentions || brand24Data
    console.log(`Received ${mentions.length || 0} mentions from Brand24`)

    // Transform Brand24 data to match our schema
    const transformedData = mentions.map((item: any) => ({
      mention_id: item.id || item.mention_id || `brand24_${Date.now()}_${Math.random()}`,
      mention_text: item.summary || item.content || item.text || '',
      sentiment: item.sentiment_polarity || item.sentiment || 'neutral',
      sentiment_score: parseFloat(item.sentiment_score || item.polarity || '0'),
      platform: item.source_type || item.platform || item.source || 'unknown',
      author: item.author_name || item.author || item.username || 'unknown',
      author_followers: parseInt(item.author_followers || item.followers_count || '0'),
      author_verified: Boolean(item.author_verified || item.verified),
      url: item.url || item.link || '',
      published_date: item.published_at || item.date || item.created_at || new Date().toISOString(),
      collected_date: item.collected_at || new Date().toISOString(),
      reach: parseInt(item.reach || item.potential_reach || '0'),
      engagement: parseInt(item.interactions_count || item.engagement || '0'),
      language: item.language || item.lang || 'en',
      country: item.country || item.location || null,
      project_id: item.project_id || 'default_project',
      source_platform: 'brand24',
      is_active: true,
      metadata: {
        api_version: 'v2',
        fetched_at: new Date().toISOString(),
        raw_data: item
      }
    }))

    // Insert data into Supabase
    const { data, error } = await supabaseClient
      .from('mentions')
      .insert(transformedData)

    if (error) {
      console.error('Supabase insert error:', error)
      throw error
    }

    console.log(`Successfully inserted ${transformedData.length} mentions`)

    return new Response(
      JSON.stringify({
        success: true,
        message: `Successfully processed ${transformedData.length} mentions`,
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
    console.error('Error in fetchMentions:', error)
    
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