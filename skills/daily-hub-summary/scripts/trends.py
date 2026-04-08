#!/usr/bin/env python3
"""
每日信息汇总脚本 - 趋势分析版
重点：概率变化、成交量暴增、新上榜事件
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 配置
CONFIG = {
    "sources": {
        "polymarket": {
            "enabled": True,
            "count": 10,
            "api_base": "https://gamma-api.polymarket.com"
        }
    },
    "cache_file": Path(__file__).parent.parent / "data" / "cache.json",
    "output_file": Path(__file__).parent.parent / "data" / f"summary_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
}


def load_cache():
    """加载缓存"""
    try:
        if CONFIG["cache_file"].exists():
            with open(CONFIG["cache_file"], 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        pass
    return {}


def save_cache(data):
    """保存缓存"""
    try:
        CONFIG["cache_file"].parent.mkdir(parents=True, exist_ok=True)
        
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "polymarket": data.get("polymarket", []),
            "trend_analysis": data.get("trend_analysis", {})
        }
        
        with open(CONFIG["cache_file"], 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 缓存已保存")
    except Exception as e:
        print(f"❌ 保存缓存失败: {e}")


def fetch_and_analyze_polymarket():
    """获取并分析 Polymarket Top 10 趋势"""
    print("🔥 抓取 Polymarket Top 10 并分析趋势...")
    
    # 加载上次缓存
    prev_cache = load_cache()
    prev_events = prev_cache.get('polymarket', [])
    
    try:
        # 获取当前事件
        result = subprocess.run(
            ['curl', '-s', 'https://gamma-api.polymarket.com/events?active=true&closed=false&limit=100'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if result.returncode != 0:
            print("   ❌ API请求失败")
            return [], {}
        
        # 解析数据
        all_events = json.loads(result.stdout)
        
        # 按 volume24hr 排序
        sorted_events = sorted(
            all_events,
            key=lambda x: x.get('volume24hr', 0),
            reverse=True
        )
        
        top10 = sorted_events[:10]
        print(f"   ✅ 获取到 {len(top10)} 个事件")
        
        # 分析趋势
        trend_info = {
            'hot_new': [],      # 🔥 新上榜
            'surging': [],       # 📈 概率暴涨
            'plummeting': [],    # 📉 概率暴跌
            'volume_spike': [],  # 💥 成交量暴增
            'disappearing': []   # ❌ 消失
        }
        
        # 创建上次事件的映射
        prev_dict = {}
        for event in prev_events:
            slug = event.get('slug', '')
            title = event.get('title', '')
            if slug:
                prev_dict[slug] = event
            if title:
                prev_dict[title] = event
        
        # 分析当前事件
        for event in top10:
            curr_title = event.get('title', '')
            curr_slug = event.get('slug', '')
            curr_vol24h = event.get('volume24hr', 0)
            
            # 检查是否新上榜
            is_new = True
            prev_event = None
            
            if curr_slug in prev_dict:
                is_new = False
                prev_event = prev_dict[curr_slug]
            elif curr_title in prev_dict:
                is_new = False
                prev_event = prev_dict[curr_title]
            
            # 🔥 新上榜且成交量>1000
            if is_new and curr_vol24h > 1000:
                trend_info['hot_new'].append({
                    'title': curr_title,
                    'slug': curr_slug,
                    'url': f"https://polymarket.com/event/{curr_slug}",
                    'volume24h': curr_vol24h,
                    'reason': '🔥 新上榜且热门'
                })
            
            # 分析概率和成交量变化
            if prev_event and 'markets' in event:
                curr_markets = [m for m in event['markets'] if not m.get('closed', True)]
                prev_markets_data = prev_event.get('markets', [])
                prev_markets = [m for m in prev_markets_data if not m.get('closed', True)]
                
                if curr_markets and prev_markets:
                    curr_market = curr_markets[0]
                    prev_market = prev_markets[0]
                    
                    # 概率变化
                    curr_outcomes = curr_market.get('outcomePrices', '[]')
                    prev_outcomes = prev_market.get('outcomePrices', '[]')
                    
                    try:
                        curr_prices = json.loads(curr_outcomes) if curr_outcomes != '[]' else []
                        prev_prices = json.loads(prev_outcomes) if prev_outcomes != '[]' else []
                        
                        if len(curr_prices) >= 2 and len(prev_prices) >= 2:
                            curr_yes = float(curr_prices[0]) * 100
                            prev_yes = float(prev_prices[0]) * 100
                            
                            # 📈 概率暴涨（+20%以上）
                            if curr_yes - prev_yes >= 20:
                                trend_info['surging'].append({
                                    'title': curr_title,
                                    'slug': curr_slug,
                                    'from': f"{prev_yes:.0f}%",
                                    'to': f"{curr_yes:.0f}%",
                                    'change': f"+{curr_yes - prev_yes:+.0f}%",
                                    'volume24h': curr_vol24h,
                                    'reason': '📈 概率暴涨'
                                })
                            
                            # 📉 概率暴跌（-20%以下）
                            elif curr_yes - prev_yes <= -20:
                                trend_info['plummeting'].append({
                                    'title': curr_title,
                                    'slug': curr_slug,
                                    'from': f"{prev_yes:.0f}%",
                                    'to': f"{curr_yes:.0f}%",
                                    'change': f"{curr_yes - prev_yes:.0f}%",
                                    'volume24h': curr_vol24h,
                                    'reason': '📉 概率暴跌'
                                })
                    
                    except:
                        pass
                    
                    # 💥 成交量暴增（2倍以上）
                    prev_vol24h = prev_event.get('volume24hr', 0)
                    
                    if prev_vol24h > 0 and curr_vol24h > prev_vol24h * 2:
                        growth = (curr_vol24h - prev_vol24h) / prev_vol24h * 100
                        trend_info['volume_spike'].append({
                            'title': curr_title,
                            'slug': curr_slug,
                            'from': f"${prev_vol24h:.0f}",
                            'to': f"${curr_vol24h:.0f}",
                            'growth': f"+{growth:.0f}%",
                            'reason': '💥 成交量暴增'
                        })
        
        # ❌ 检查从榜单消失的事件（上次在Top 10，现在不在）
        for prev_event in prev_events[:10]:
            prev_slug = prev_event.get('slug', '')
            prev_title = prev_event.get('title', '')
            prev_vol24h = prev_event.get('volume24h', 0)
            
            # 检查是否还在当前Top 10
            still_in_top10 = False
            for curr_event in top10:
                if curr_event.get('slug', '') == prev_slug or curr_event.get('title', '') == prev_title:
                    still_in_top10 = True
                    break
            
            # 如果之前在榜单（有成交量），现在消失了
            if not still_in_top10 and prev_vol24h > 100:
                trend_info['disappearing'].append({
                    'title': prev_title,
                    'slug': prev_slug,
                    'last_volume24h': prev_vol24h,
                    'last_probability': prev_event.get('probability', 'N/A'),
                    'reason': '❌ 从Top 10消失'
                })
        
        # 格式化事件
        formatted_events = []
        for event in top10:
            formatted = {
                'title': event.get('title', 'N/A'),
                'slug': event.get('slug', ''),
                'url': f"https://polymarket.com/event/{event.get('slug', '')}",
                'source': 'Polymarket',
                'timestamp': datetime.now().isoformat()
            }
            
            # 提取概率
            if 'markets' in event and len(event['markets']) > 0:
                for market in event['markets'][:1]:
                    outcomes = market.get('outcomePrices', '[]')
                    if outcomes and outcomes != '[]':
                        try:
                            prices = json.loads(outcomes)
                            if len(prices) >= 2:
                                yes_prob = float(prices[0]) * 100
                                formatted['probability'] = f"{yes_prob:.1f}%"
                                formatted['yes_prob'] = yes_prob
                                
                                # 概率分类
                                if yes_prob >= 70:
                                    formatted['trend'] = '🔥 高概率'
                                elif yes_prob >= 40:
                                    formatted['trend'] = '📊 中等概率'
                                elif yes_prob >= 20:
                                    formatted['trend'] = '空 低概率'
                                else:
                                    formatted['trend'] = '❌ 很低'
                        except:
                            pass
                    
                    formatted['volume24hr'] = market.get('volume24hr', 0)
                    formatted['one_day_change'] = market.get('oneDayPriceChange', 0)
                    formatted['closed'] = market.get('closed', False)
                    
                    break
            
            formatted_events.append(formatted)
        
        # 显示趋势统计
        if any(trend_info.values()):
            print(f"\n📊 发现趋势:")
            if trend_info['hot_new']:
                print(f"   🔥 新上榜: {len(trend_info['hot_new'])}个")
            if trend_info['surging']:
                print(f"   📈 概率暴涨: {len(trend_info['surging'])}个")
            if trend_info['plummeting']:
                print(f"   📉 概率暴跌: {len(trend_info['plummeting'])}个")
            if trend_info['volume_spike']:
                print(f"   💥 成交量暴增: {len(trend_info['volume_spike'])}个")
            if trend_info['disappearing']:
                print(f"   ❌ 消失: {len(trend_info['disappearing'])}个")
        
        return formatted_events, trend_info
        
    except Exception as e:
        print(f"   ❌ 失败: {e}")
        import traceback
    return [], {}


def generate_report(polymarket_data, trend_analysis):
    """生成汇总报告"""
    report = []
    report.append("📊 每日信息汇总")
    report.append(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # 趋势分析部分
    if any(trend_analysis.values()):
        report.append("🚨 市场趋势警报")
        report.append("─" * 50)
        
        if trend_analysis['hot_new']:
            report.append(f"\n🔥 新上榜热门事件 ({len(trend_analysis['hot_new'])}个):")
            for item in trend_analysis['hot_new'][:3]:
                report.append(f"   • {item['title'][:60]}")
                report.append(f"     💹 {item['volume24h']:,.0f} | {item['reason']}")
        
        if trend_analysis['surging']:
            report.append(f"\n📈 概率暴涨事件 ({len(trend_analysis['surging'])}个):")
            for item in trend_analysis['surging'][:3]:
                report.append(f"   • {item['title'][:60]}")
                report.append(f"     {item['from']} → {item['to']} ({item['change']})")
        
        if trend_analysis['plummeting']:
            report.append(f"\n📉 概率暴跌事件 ({len(trend_analysis['plummeting'])}个):")
            for item in trend_analysis['plummeting'][:3]:
                report.append(f"   • {item['title'][:60]}")
                report.append(f"     {item['from']} → {item['to']} ({item['change']})")
        
        if trend_analysis['volume_spike']:
            report.append(f"\n💥 成交量暴增事件 ({len(trend_analysis['volume_spike'])}个):")
            for item in trend_analysis['volume_spike'][:3]:
                report.append(f"   • {item['title'][:60]}")
                report.append(f"     {item['from']} → {item['to']} ({item['growth']})")
        
        if trend_analysis['disappearing']:
            report.append(f"\n❌ 从Top 10消失 ({len(trend_analysis['disappearing'])}个):")
            for item in trend_analysis['disappearing'][:3]:
                report.append(f"   • {item['title'][:60]}")
                report.append(f"     最后24h成交量: ${item['last_volume24h']:,.0f}")
        
        report.append("\n" + "=" * 50)
        report.append("")
    
    # Polymarket Top 10 列表
    if polymarket_data:
        report.append("🔥 Polymarket Top 10（按24小时成交量排序）")
        report.append("─" * 50)
        for i, event in enumerate(polymarket_data, 1):
            prob_str = f" | {event.get('probability', 'N/A')}" if event.get('probability') else ""
            
            report.append(f"#{i}. {event['title']}{prob_str}")
            
            # 成交量
            if event.get('volume24hr') and event['volume24hr'] > 0:
                vol24h = event['volume24hr']
                if vol24h > 1000:
                    vol24h_str = f"${vol24h/1000:.1f}K"
                else:
                    vol24h_str = f"${vol24h:.0f}"
                report.append(f"   💹 {vol24h_str}")
            
            # 24h变化
            if event.get('one_day_change'):
                change = event['one_day_change']
                if change != 0:
                    if change > 0:
                        report.append(f"   📈 +{change*100:+.1f}% (24h)")
                    elif change < 0:
                        report.append(f"   📉 {change*100:+.1f}% (24h)")
            
            # 链接
            if event.get('url'):
                report.append(f"   🔗 {event['url']}")
            
            report.append("")
    
    report.append("─" * 50)
    report.append(f"📈 数据来源: Polymarket Gamma API")
    report.append(f"⚠️  注意: 首次运行无趋势数据，下次运行才会有变化分析")
    
    return "\n".join(report)


def fetch_v2ex_hot():
    """抓取 V2EX 热门"""
    print("💬 抓取 V2EX 热门...")
    
    try:
        response = subprocess.run(
            ['curl', '-s', 'https://www.v2ex.com/api/topics/hot.json'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if response.returncode == 0:
            data = json.loads(response.stdout)
            
            topics = []
            for item in data[:10]:
                topics.append({
                    "title": item.get("title", ""),
                    "author": item.get("member", {}).get("username", ""),
                    "replies": item.get("replies", 0),
                    "node": item.get("node", {}).get("title", ""),
                    "url": f"https://www.v2ex.com/t/{item.get('id')}",
                    "source": "V2EX",
                    "timestamp": datetime.now().isoformat()
                })
            
            print(f"   ✅ 成功获取 {len(topics)} 条")
            return topics
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return []


def fetch_hacker_news():
    """抓取 Hacker News"""
    print("📰 抓取 Hacker News...")
    
    try:
        # 获取热门故事ID列表
        response = subprocess.run(
            ['curl', '-s', 'https://hacker-news.firebaseio.com/v0/topstories.json'],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if response.returncode == 0:
            story_ids = json.loads(response.stdout)
            
            stories = []
            for story_id in story_ids[:10]:
                # 获取每个故事的详细信息
                detail_response = subprocess.run(
                    ['curl', '-s', f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"],
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                
                if detail_response.returncode == 0:
                    story = json.loads(detail_response.stdout)
                    stories.append({
                        "title": story.get("title", ""),
                        "url": story.get("url", ""),
                        "score": story.get("score", 0),
                        "descendants": story.get("descendants", 0),
                        "source": "Hacker News",
                        "timestamp": datetime.now().isoformat()
                    })
            
            print(f"   ✅ 成功获取 {len(stories)} 条")
            return stories
    except Exception as e:
        print(f"   ❌ 错误: {e}")
        return []


def generate_report(polymarket_data, trend_analysis, v2ex_data, hn_data):
    """生成完整汇总报告"""
    report = []
    report.append("📊 每日信息汇总")
    report.append(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # 趋势分析部分
    if any(trend_analysis.values()):
        report.append("🚨 市场趋势警报")
        report.append("─" * 50)
        
        if trend_analysis['hot_new']:
            report.append(f"\n🔥 新上榜热门事件 ({len(trend_analysis['hot_new'])}个):")
            for item in trend_analysis['hot_new'][:3]:
                report.append(f"   • {item['title'][:60]}")
                report.append(f"     💹 {item['volume24h']:,.0f} | {item['reason']}")
        
        if trend_analysis['surging']:
            report.append(f"\n📈 概率暴涨事件 ({len(trend_analysis['surging'])}个):")
            for item in trend_analysis['surging'][:3]:
                report.append(f"   • {item['title'][:60]}")
                report.append(f"     {item['from']} → {item['to']} ({item['change']})")
        
        if trend_analysis['plummeting']:
            report.append(f"\n📉 概率暴跌事件 ({len(trend_analysis['plummeting'])}个):")
            for item in trend_analysis['plummeting'][:3]:
                report.append(f"   • {item['title'][:60]}")
                report.append(f"     {item['from']} → {item['to']} ({item['change']})")
        
        if trend_analysis['volume_spike']:
            report.append(f"\n💥 成交量暴增事件 ({len(trend_analysis['volume_spike'])}个):")
            for item in trend_analysis['volume_spike'][:3]:
                report.append(f"   • {item['title'][:60]}")
                report.append(f"     {item['from']} → {item['to']} ({item['growth']})")
        
        if trend_analysis['disappearing']:
            report.append(f"\n❌ 从Top 10消失 ({len(trend_analysis['disappearing'])}个):")
            for item in trend_analysis['disappearing'][:3]:
                report.append(f"   • {item['title'][:60]}")
                report.append(f"     最后24h成交量: ${item['last_volume24h']:,.0f}")
        
        report.append("\n" + "=" * 50)
        report.append("")
    
    # Polymarket Top 10
    if polymarket_data:
        report.append("🔥 Polymarket Top 10（按24小时成交量排序）")
        report.append("─" * 50)
        for i, event in enumerate(polymarket_data, 1):
            prob_str = f" | {event.get('probability', 'N/A')}" if event.get('probability') else ""
            
            report.append(f"#{i}. {event['title']}{prob_str}")
            
            # 成交量
            if event.get('volume24hr') and event['volume24hr'] > 0:
                vol24h = event['volume24hr']
                if vol24h > 1000:
                    vol24h_str = f"${vol24h/1000:.1f}K"
                else:
                    vol24h_str = f"${vol24h:.0f}"
                report.append(f"   💹 {vol24h_str}")
            
            # 24h变化
            if event.get('one_day_change'):
                change = event['one_day_change']
                if change != 0:
                    if change > 0:
                        report.append(f"   📈 +{change*100:+.1f}% (24h)")
                    elif change < 0:
                        report.append(f"   📉 {change*100:+.1f}% (24h)")
            
            # 链接
            if event.get('url'):
                report.append(f"   🔗 {event['url']}")
            
            report.append("")
    
    # V2EX 热门
    if v2ex_data:
        report.append("💬 V2EX 热门 (Top 10)")
        report.append("─" * 50)
        for i, topic in enumerate(v2ex_data, 1):
            report.append(f"{i}. 【{topic['node']}】{topic['title']}")
            report.append(f"   👤 {topic['author']} | 💬 {topic['replies']} 回复")
        report.append("")
    
    # Hacker News
    if hn_data:
        report.append("📰 Hacker News (Top 10)")
        report.append("─" * 50)
        for i, story in enumerate(hn_data, 1):
            report.append(f"{i}. {story['title']}")
            report.append(f"   ⭐ {story['score']} | 💬 {story['descendants']}")
        report.append("")
    
    report.append("─" * 50)
    report.append(f"📈 数据来源: Polymarket Gamma API + V2EX + Hacker News")
    report.append(f"⚠️  注意: 首次运行无趋势数据，下次运行才会有变化分析")
    
    return "\n".join(report)


def main():
    """主函数"""
    print("=" * 60)
    print("📊 每日信息汇总 - 趋势分析版")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 获取所有数据
    polymarket_data, trend_analysis = fetch_and_analyze_polymarket()
    v2ex_data = fetch_v2ex_hot()
    hn_data = fetch_hacker_news()
    
    print()
    
    # 生成报告
    report = generate_report(polymarket_data, trend_analysis, v2ex_data, hn_data)
    
    # 显示
    print(report)
    print()
    
    # 保存
    data = {
        "polymarket": polymarket_data,
        "trend_analysis": trend_analysis,
        "v2ex": v2ex_data,
        "hackernews": hn_data,
        "report": report,
        "generated_at": datetime.now().isoformat()
    }
    
    save_cache(data)
    
    print("=" * 60)
    print("✅ 完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
