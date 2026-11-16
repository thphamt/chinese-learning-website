// Supabase Client Configuration & Query Helpers for VNCHINESECLUB
// Project: vnchineseclub (mzxbospldzbbndqkfalt)

const SUPABASE_URL = "https://mzxbospldzbbndqkfalt.supabase.co";
const SUPABASE_ANON_KEY = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJzdXBhYmFzZSIsInJlZiI6Im16eGJvc3BsZHpiYm5kcWtmYWx0Iiwicm9sZSI6ImFub24iLCJpYXQiOjE3OTQ3MzcyNjcsImV4cCI6MjExMDMxMzI2N30.DWvUkoPg4exdSaC1s-CbRYuex3BRJtk0hc3OL3rPr98";

let supabaseClient = null;

function getSupabase() {
  if (supabaseClient) return supabaseClient;
  if (typeof window !== "undefined" && window.supabase && window.supabase.createClient) {
    supabaseClient = window.supabase.createClient(SUPABASE_URL, SUPABASE_ANON_KEY);
    return supabaseClient;
  }
  console.warn("Supabase JS SDK not yet loaded. Include <script src=\"https://cdn.jsdelivr.net/npm/@supabase/supabase-js@2\"></script> before supabaseClient.js");
  return null;
}

// Convenient Query Helpers
const VNChineseDB = {
  // 1. Get 214 Radicals (or filter to the 60 core radicals)
  async getRadicals(only60 = false) {
    const sb = getSupabase();
    if (!sb) return [];
    let query = sb.from("radicals").select("*").order("number", { ascending: true });
    if (only60) query = query.eq("is_in_60", true);
    const { data, error } = await query;
    if (error) { console.error("Error fetching radicals:", error); return []; }
    return data;
  },

  // 2. Get Stroke Order Writing Rules
  async getWritingRules() {
    const sb = getSupabase();
    if (!sb) return [];
    const { data, error } = await sb.from("writing_rules").select("*").order("rule_number", { ascending: true });
    if (error) { console.error("Error fetching writing rules:", error); return []; }
    return data;
  },

  // 3. Get Characters by Step (e.g. 3, 4, 5, 6) or Lesson Slug
  async getCharacters({ step = null, lessonSlug = null, limit = 100, offset = 0 } = {}) {
    const sb = getSupabase();
    if (!sb) return [];
    let query = sb.from("characters").select("*").order("id", { ascending: true });
    if (step) query = query.eq("source_step", step);
    if (lessonSlug) query = query.eq("lesson_slug", lessonSlug);
    query = query.range(offset, offset + limit - 1);
    const { data, error } = await query;
    if (error) { console.error("Error fetching characters:", error); return []; }
    return data;
  },

  // 4. Search Characters by Hanzi or Pinyin
  async searchCharacters(term) {
    const sb = getSupabase();
    if (!sb) return [];
    const { data, error } = await sb.from("characters")
      .select("*")
      .or(`hanzi.eq.${term},pinyin.ilike.%${term}%`)
      .limit(20);
    if (error) { console.error("Error searching characters:", error); return []; }
    return data;
  },

  // 5. Get 150 Conversational Topics
  async getTopics({ limit = 150, offset = 0 } = {}) {
    const sb = getSupabase();
    if (!sb) return [];
    const { data, error } = await sb.from("topics")
      .select("*")
      .order("topic_number", { ascending: true })
      .range(offset, offset + limit - 1);
    if (error) { console.error("Error fetching topics:", error); return []; }
    return data;
  }
};

// Global exports
window.getSupabase = getSupabase;
window.VNChineseDB = VNChineseDB;
window.SUPABASE_CONFIG = {
  url: SUPABASE_URL,
  anonKey: SUPABASE_ANON_KEY
};
