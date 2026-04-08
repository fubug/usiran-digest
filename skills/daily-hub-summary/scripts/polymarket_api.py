#!/usr/bin/env python3
"""
Polymarket 数据获取模块 - 使用官方 Gamma API
"""

import requests
import json
from datetime import datetime
from typing import List, Dict, Any


class PolymarketAPI:
    """Polymarket Gamma API 客户端"""
    
    BASE_URL = "https://gamma-api.polymarket.com"
    
    def __init__(self):
        self.session = requests.Session()
        self.session.headers.update({
            'User-Agent': 'Mozilla/5.0 (compatible; OpenClaw/1.0)'
        })
    
    def search_events(self, query: str, limit: int = 10) -> List[Dict]:
        """搜索事件"""
        try:
            url = f"{self.BASE_URL}/public-search"
            params = {'q': query, 'limit': limit}
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # public-search 返回格式: {"events": [...], ...}
                if 'events' in data:
                    return data['events']
                elif isinstance(data, list):
                    return data
                else:
                    return []
            else:
                return []
                
        except Exception as e:
            print(f"   ❌ 搜索失败: {e}")
            return []
    
    def get_event_by_slug(self, slug: str) -> Dict:
        """通过 slug 获取事件"""
        try:
            url = f"{self.BASE_URL}/events"
            params = {'slug': slug}
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                data = response.json()
                
                # 返回格式可能是列表或单个事件
                if isinstance(data, list) and len(data) > 0:
                    return data[0]
                elif isinstance(data, dict):
                    return data
                else:
                    return {}
            else:
                return {}
                
        except Exception as e:
            print(f"   ❌ 获取事件失败: {e}")
            return {}
    
    def get_active_events(self, limit: int = 50, order: str = "volume_24hr") -> List[Dict]:
        """获取活跃事件"""
        try:
            url = f"{self.BASE_URL}/events"
            params = {
                'active': 'true',
                'closed': 'false',
                'limit': limit,
                'order': order,
                'ascending': 'false'
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
                
        except Exception as e:
            print(f"   ❌ 获取活跃事件失败: {e}")
            return []
    
    def get_top_volume_events(self, limit: int = 10, compare_cache=None) -> tuple[List[Dict], Dict]:
        """获取按24小时成交量排序的Top N事件，并分析趋势变化
        
        Args:
            limit: 获取事件数量
            compare_cache: 上次的缓存数据，用于对比趋势
        
        Returns:
            (事件列表, 趋势分析数据)
        """
        try:
            url = f"{self.BASE_URL}/events"
            params = {
                'active': 'true',
                'closed': 'false',
                'limit': 100  # 获取更多，然后排序
            }
            
            response = self.session.get(url, params=params, timeout=10)
            
            if response.status_code == 200:
                all_events = response.json()
                
                # 在Python中按 volume24hr 排序
                sorted_events = sorted(
                    all_events,
                    key=lambda x: x.get('volume24hr', 0),
                    reverse=True
                )
                
                top_events = sorted_events[:limit]
                
                # 分析趋势
                trend_analysis = self.analyze_trends(top_events, compare_cache)
                
                return top_events, trend_analysis
            else:
                return [], {}
                
        except Exception as e:
            print(f"   ❌ 获取Top成交量事件失败: {e}")
            return [], {}
    
    def analyze_trends(self, current_events: List[Dict], previous_cache: Dict = None) -> Dict:
        """分析事件趋势变化
        
        Args:
            current_events: 当前的事件列表
            previous_cache: 上次的缓存数据
        
        Returns:
            趋势分析数据
        """
        trend_info = {
            'hot_new': [],      # 🔥 新上榜且热度高
            'surging': [],       # 📈 概率大幅上升（+20%以上）
            'plummeting': [],    # 📉 概率大幅下降（-20%以上）
            'volume_spike': [],  # 💥 成交量暴增（2倍以上）
            'disappearing': []   # ❌ 从榜单消失
        }
        
        if not previous_cache:
            return trend_info
        
        # 创建上次事件的字典（用ID或标题）
        prev_events = previous_cache.get('polymarket', [])
        prev_dict = {}
        
        for event in prev_events:
            event_id = event.get('slug', event.get('id', ''))
            title = event.get('title', '')
            
            if event_id:
                prev_dict[event_id] = event
            if title and title not in prev_dict:
                prev_dict[title] = event
        
        # 分析当前事件
        for curr_event in current_events:
            curr_id = curr_event.get('slug', curr_event.get('id', ''))
            curr_title = curr_event.get('title', '')
            curr_vol24h = curr_event.get('volume24hr', 0)
            
            # 检查是否新上榜
            is_new = True
            prev_event = None
            
            if curr_id and curr_id in prev_dict:
                is_new = False
                prev_event = prev_dict[curr_id]
            elif curr_title and curr_title in prev_dict:
                is_new = False
                prev_event = prev_dict[curr_title]
            
            # 🔥 新上榜且成交量高
            if is_new and curr_vol24h > 1000:
                trend_info['hot_new'].append({
                    'title': curr_title,
                    'url': f"https://polymarket.com/event/{curr_event.get('slug', '')}",
                    'volume24h': curr_vol24h,
                    'probability': curr_event.get('probability', 'N/A'),
                    'reason': '新上榜'
                })
            
            # 分析概率变化
            if prev_event and 'markets' in curr_event and 'markets' in prev_event:
                curr_markets = [m for m in curr_event['markets'] if not m.get('closed', True)]
                prev_markets = [m for m in prev_event['markets'] if not m.get('closed', True)]
                
                if curr_markets and prev_markets:
                    curr_market = curr_markets[0]
                    prev_market = prev_markets[0]
                    
                    curr_outcomes = curr_market.get('outcomePrices', '[]')
                    prev_outcomes = prev_market.get('outcomePrices', '[]')
                    
                    try:
                        curr_prices = json.loads(curr_outcomes) if curr_outcomes != '[]' else []
                        prev_prices = json.loads(prev_outcomes) if prev_outcomes != '[]' else []
                        
                        if len(curr_prices) >= 2 and len(prev_prices) >= 2:
                            curr_yes = float(curr_prices[0]) * 100
                            prev_yes = float(prev_prices[0]) * 100
                            
                            # 计算变化
                            change = curr_yes - prev_yes
                            
                            # 📈 概率大幅上升
                            if change >= 20:
                                trend_info['surging'].append({
                                    'title': curr_title,
                                    'url': f"https://polymarket.com/event/{curr_event.get('slug', '')}",
                                    'from': f"{prev_yes:.1f}%",
                                    'to': f"{curr_yes:.1f}%",
                                    'change': f"+{change:.1f}%",
                                    'volume24h': curr_vol24h,
                                    'reason': '概率大幅上升'
                                })
                            
                            # 📉 概率大幅下降
                            elif change <= -20:
                                trend_info['plummeting'].append({
                                    'title': curr_title,
                                    'url': f"https://polymarket.com/event/{curr_event.get('slug', '')}",
                                    'from': f"{prev_yes:.1f}%",
                                    'to': f"{curr_yes:.1f}%",
                                    'change': f"{change:.1f}",
                                    'volume24h': curr_vol24h,
                                    'reason': '概率大幅下降'
                                })
                    
                    except:
                        pass
            
            # 💥 成交量暴增
            if prev_event:
                prev_vol24h = prev_event.get('volume24hr', 0)
                
                if prev_vol24h > 0 and curr_vol24h > 0:
                    growth = (curr_vol24h - prev_vol24h) / prev_vol24h
                    
                    if growth >= 2.0:  # 增长2倍以上
                        trend_info['volume_spike'].append({
                            'title': curr_title,
                            'url': f"https://polymarket.com/event/{curr_event.get('slug', '')}",
                            'from': f"${prev_vol24h:.0f}",
                            'to': f"${curr_vol24h:.0f}",
                            'growth': f"+{growth*100:.0f}%",
                            'probability': curr_event.get('probability', 'N/A'),
                            'reason': '成交量暴增'
                        })
        
        # ❌ 检查从榜单消失的事件
        for prev_event in prev_events:
            prev_id = prev_event.get('slug', prev_event.get('id', ''))
            prev_title = prev_event.get('title', '')
            prev_vol24h = prev_event.get('volume24hr', 0)
            
            # 检查是否还在榜单
            still_in_top = False
            for curr_event in current_events:
                curr_id = curr_event.get('slug', curr_event.get('id', ''))
                curr_title = curr_event.get('title', '')
                
                if curr_id == prev_id or curr_title == prev_title:
                    still_in_top = True
                    break
            
            # 如果之前在榜单（有成交量），现在消失了
            if not still_in_top and prev_vol24h > 100:
                trend_info['disappearing'].append({
                    'title': prev_title,
                    'url': f"https://polymarket.com/event/{prev_event.get('slug', '')}",
                    'last_volume24h': prev_vol24h,
                    'last_probability': prev_event.get('probability', 'N/A'),
                    'reason': '从榜单消失'
                })
        
        return trend_info
    
    def get_tags(self) -> List[Dict]:
        """获取所有标签"""
        try:
            url = f"{self.BASE_URL}/tags"
            response = self.session.get(url, timeout=10)
            
            if response.status_code == 200:
                return response.json()
            else:
                return []
                
        except Exception as e:
            print(f"   ❌ 获取标签失败: {e}")
            return []


def fetch_polymarket_breaking_with_api(limit=10):
    """使用 Gamma API 获取 Breaking 板块事件"""
    print("🔥 抓取 Polymarket Breaking（使用 Gamma API）...")
    
    api = PolymarketAPI()
    
    # 尝试搜索 breaking 相关事件
    keywords = ['breaking', 'hot', 'trending', 'news']
    events = []
    
    for keyword in keywords:
        results = api.search_events(keyword, limit=20)
        if results:
            events.extend(results)
            if len(events) >= limit:
                break
    
    # 去重
    seen = set()
    unique_events = []
    
    for event in events:
        event_id = event.get('id', '')
        if event_id and event_id not in seen:
            seen.add(event_id)
            unique_events.append(event)
    
    return unique_events[:limit]


def format_polymarket_event(event: Dict) -> Dict:
    """格式化事件数据"""
    formatted = {
        'title': event.get('title', 'N/A'),
        'slug': event.get('slug', ''),
        'url': f"https://polymarket.com/event/{event.get('slug', '')}",
        'source': 'Polymarket Breaking',
        'timestamp': datetime.now().isoformat()
    }
    
    # 提取概率信息（从第一个活跃市场）
    if 'markets' in event and len(event['markets']) > 0:
        for market in event['markets']:
            if not market.get('closed', True):
                outcomes = market.get('outcomePrices', '[]')
                if outcomes and outcomes != '[]':
                    try:
                        prices = json.loads(outcomes)
                        if isinstance(prices, list) and len(prices) >= 2:
                            formatted['probability'] = f"{float(prices[0]) * 100:.1f}%"
                    except:
                        pass
                
                formatted['volume'] = market.get('volume', 'N/A')
                formatted['liquidity'] = market.get('liquidity', 'N/A')
                formatted['end_date'] = market.get('endDate', 'N/A')
                formatted['last_trade'] = market.get('lastTradePrice', 'N/A')
                formatted['one_day_change'] = market.get('oneDayPriceChange', 'N/A')
                
                # 如果有多个市场，也记录其他市场
                other_markets = []
                for m in event['markets']:
                    if m['id'] != market['id']:
                        other_markets.append({
                            'question': m.get('question', ''),
                            'closed': m.get('closed', False),
                            'outcomes': m.get('outcomePrices', 'N/A')
                        })
                if other_markets:
                    formatted['other_markets'] = other_markets
                
                break
    
    return formatted


# 测试
if __name__ == "__main__":
    print("测试 Polymarket API...")
    
    api = PolymarketAPI()
    
    # 测试1：搜索 Baghdad
    print("\n🔍 测试1: 搜索 Baghdad 相关事件")
    print("-" * 50)
    results = api.search_events('baghdad', limit=3)
    for event in results:
        title = event.get('title', 'N/A')
        slug = event.get('slug', '')
        print(f"  • {title}")
        print(f"    🔗 https://polymarket.com/event/{slug}")
    
    # 测试2：通过 slug 获取事件
    print("\n🎯 测试2: 通过 slug 获取事件")
    print("-" * 50)
    event = api.get_event_by_slug('us-evacuates-baghdad-embassy-by')
    
    if event:
        print(f"  标题: {event.get('title', 'N/A')}")
        print(f"  链接: https://polymarket.com/event/{event.get('slug', '')}")
        print(f"  市场数: {len(event.get('markets', []))}")
    
    # 测试3：获取活跃事件
    print("\n🔥 测试3: 获取前5个活跃事件")
    print("-" * 50)
    events = api.get_active_events(limit=5, order='volume_24hr')
    
    if events:
        print(f"  ✅ 获取到 {len(events)} 个事件")
        
        for i, event in enumerate(events[:3], 1):
            title = event.get('title', 'N/A')
            print(f"  {i}. {title}")
            
            # 第一个活跃市场的概率
            if 'markets' in event:
                for market in event['markets'][:1]:
                    if not market.get('closed', True):
                        outcomes = market.get('outcomePrices', '[]')
                        if outcomes and outcomes != '[]':
                            try:
                                prices = json.loads(outcomes)
                                if isinstance(prices, list) and len(prices) >= 2:
                                    yes_prob = float(prices[0]) * 100
                                    print(f"     ✅ Yes: {yes_prob:.1f}%")
                            except:
                                pass
                        break
    
    print("\n✅ Gamma API 测试完成!")
