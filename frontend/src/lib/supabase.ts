import { createClient } from "@supabase/supabase-js";

export const SUPABASE_URL =
  process.env.NEXT_PUBLIC_SUPABASE_URL ||
  "https://ecpomgnznlyksdycbupy.supabase.co";

export const SUPABASE_KEY =
  process.env.NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY ||
  process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY ||
  "sb_publishable_nJhVvxfQo5UdTiOX-uWN0g_LINPt75E";

export const supabase = createClient(SUPABASE_URL, SUPABASE_KEY);
