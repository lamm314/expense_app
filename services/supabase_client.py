from supabase import create_client
import os

url = os.environ.get("https://syqblzpshdoquyffmwwq.supabase.co")
key = os.environ.get("sb_publishable_bRMs8uZNdWXzlpcP0h21vw_vRUMF4RM")

supabase = create_client(url, key)