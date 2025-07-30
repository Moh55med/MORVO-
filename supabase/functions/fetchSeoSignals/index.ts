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

    // Get SE Ranking API key from environment
    const seRankingApiKey = Deno.env.get('SE_RANKING_API_KEY')
    if (!seRankingApiKey) {
      throw new Error('SE_RANKING_API_KEY is not configured')
    }

    console.log('Fetching SEO signals from SE Ranking API...')

    // SE Ranking API endpoint (example - adjust based on actual API)
    const seRankingUrl = 'https://api4.seranking.com/sites/keywords'
    
    // Fetch data from SE Ranking API
    const response = await fetch(seRankingUrl, {
      method: 'GET',
      headers: {
        'Authorization': `Token ${seRankingApiKey}`,
        'Content-Type': 'application/json'
      }
    })

    if (!response.ok) {
      throw new Error(`SE Ranking API error: ${response.status} ${response.statusText}`)
    }

    const seRankingData = await response.json()
    console.log(`Received ${seRankingData.length || 0} SEO signals from SE Ranking`)

    // Transform SE Ranking data to match our schema
    const transformedData = seRankingData.map((item: any) => ({
      keyword: item.keyword || item.query,
      position: item.position || item.rank,
      url: item.url || item.landing_page,
      volume: item.volume || item.search_volume || 0,
      cpc: parseFloat(item.cpc || item.cost_per_click || '0'),
      competition: parseFloat(item.competition || item.difficulty || '0'),
      previous_position: item.previous_position || item.prev_rank,
      position_change: item.position_change || (item.previous_position ? item.position - item.previous_position : 0),
      search_engine: item.search_engine || 'google',
      location: item.location || item.region || 'United States',
      device: item.device || 'desktop',
      tracked_date: item.tracked_date || new Date().toISOString(),
      project_id: item.project_id || 'default_project',
      source_platform: 'se_ranking',
      is_active: true,
      metadata: {
        api_version: 'v4',
        fetched_at: new Date().toISOString(),
        raw_data: item
      }
    }))

    // Insert data into Supabase
    const { data, error } = await supabaseClient
      .from('seo_signals')
      .insert(transformedData)

    if (error) {
      console.error('Supabase insert error:', error)
      throw error
    }

    console.log(`Successfully inserted ${transformedData.length} SEO signals`)

    return new Response(
      JSON.stringify({
        success: true,
        message: `Successfully processed ${transformedData.length} SEO signals`,
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
    console.error('Error in fetchSeoSignals:', error)
    
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