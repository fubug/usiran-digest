#!/usr/bin/env python3
import requests
import re
import json

def search_live_blogs():
    results = {}
    
    # Search for CBS News live blogs
    try:
        response = requests.get('https://www.bing.com/search?q=site:cbsnews.com+Iran+war+live', timeout=15)
        if response.status_code == 200:
            cbs_matches = re.findall(r'https://www\.cbsnews\.com/live-updates/iran-war-[^\\"\\s<>]+', response.text)
            results['cbs'] = cbs_matches[:2] if cbs_matches else []
        else:
            results['cbs'] = []
    except Exception as e:
        print('CBS search error:', e)
        results['cbs'] = []
    
    # Search for AP News live blogs
    try:
        response = requests.get('https://www.bing.com/search?q=site:apnews.com+Iran+war+live', timeout=15)
        if response.status_code == 200:
            ap_matches = re.findall(r'https://apnews\.com/live/iran-war-israel-[^\\"\\s<>]+', response.text)
            results['ap'] = ap_matches[:2] if ap_matches else []
        else:
            results['ap'] = []
    except Exception as e:
        print('AP search error:', e)
        results['ap'] = []
    
    # Search for NYT live blogs
    try:
        response = requests.get('https://www.bing.com/search?q=site:nytimes.com+Iran+war+live', timeout=15)
        if response.status_code == 200:
            nyt_matches = re.findall(r'https://www\.nytimes\.com/live/[^\\\"\\s<>]+/world/iran-war-[^\\"\\s<>]+', response.text)
            results['nyt'] = nyt_matches[:2] if nyt_matches else []
        else:
            results['nyt'] = []
    except Exception as e:
        print('NYT search error:', e)
        results['nyt'] = []
    
    # Search for Reuters
    try:
        response = requests.get('https://www.bing.com/search?q=site:reuters.com+Iran+war+live', timeout=15)
        if response.status_code == 200:
            reuters_matches = re.findall(r'https://www\.reuters\.com/article/us-[^\\"\\s<>]+', response.text)
            reuters_matches = [url for url in reuters_matches if 'iran' in url.lower()]
            results['reuters'] = reuters_matches[:2] if reuters_matches else []
        else:
            results['reuters'] = []
    except Exception as e:
        print('Reuters search error:', e)
        results['reuters'] = []
    
    return results

if __name__ == "__main__":
    results = search_live_blogs()
    print(json.dumps(results, indent=2))