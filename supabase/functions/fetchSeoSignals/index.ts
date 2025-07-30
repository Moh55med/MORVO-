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

    // SE Ranking API endpoint for keywords data
    const seRankingUrl = 'https://api4.seranking.com/research/keywords/'
    
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
    const keywords = seRankingData.results || seRankingData.data || seRankingData
    console.log(`Received ${keywords.length || 0} keywords from SE Ranking`)

    // Transform SE Ranking data to match our schema
    const transformedData = keywords.map((item: any) => ({
      keyword_id: item.id || `ser_${Date.now()}_${Math.random()}`,
      keyword: item.keyword || item.query || '',
      current_position: parseInt(item.position || item.rank || '0'),
      previous_position: parseInt(item.previous_position || item.prev_rank || '0'),
      position_change: parseInt(item.position_change || item.rank_change || '0'),
      search_volume: parseInt(item.search_volume || item.volume || '0'),
      keyword_difficulty: parseFloat(item.difficulty || item.kd || '0'),
      competition: item.competition || item.comp || 'unknown',
      cpc: parseFloat(item.cpc || item.cost_per_click || '0'),
      url: item.url || item.landing_page || '',
      search_engine: item.search_engine || item.engine || 'google',
      location: item.location || item.region || item.country || '',
      device: item.device || item.platform || 'desktop',
      language: item.language || item.lang || 'en',
      date_checked: item.date || item.checked_at || new Date().toISOString(),
      serp_features: item.serp_features || [],
      visibility: parseFloat(item.visibility || item.vis || '0'),
      traffic_potential: parseInt(item.traffic_potential || item.traffic || '0'),
      project_id: item.project_id || 'default_project',
      domain: item.domain || item.website || '',
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