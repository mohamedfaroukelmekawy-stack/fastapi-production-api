const { createClient } = require('@supabase/supabase-js');
const path = require('path');
require('dotenv').config({ path: path.resolve(__dirname, '../.env') });
// __dirname = src/core
// ../.env = الملف في src

const supabaseUrl = process.env.REACT_APP_SUPABASE_URL;
const supabaseAnonKey = process.env.REACT_APP_SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseAnonKey) {
  throw new Error("Environment variables SUPABASE_URL or SUPABASE_ANON_KEY are missing!");
}

const supabase = createClient(supabaseUrl, supabaseAnonKey);

async function testConnection() {
  try {
    console.log("Supabase client created successfully!");
  } catch (err) {
    console.error("Connection failed:", err);
  }
}

testConnection();
