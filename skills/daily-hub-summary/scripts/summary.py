#!/usr/bin/env python3
"""
每日信息汇总脚本 - 简化版
使用 Polymarket Gamma API 按成交量排序获取Top 10事件
"""

import json
import subprocess
import sys
from datetime import datetime
from pathlib import Path

# 导入 Polymarket API
try:
    from polymarket_api import PolymarketAPI
except ImportError:
    PolymarketAPI = None

# 配置
CONFIG = {
    "sources": {
        "polymarket": {
            "enabled": True,
            "count": 10,
            "api_base": "https://gamma-api.polymarket.com"
        },
        "v2ex": {
            "enabled": True,
            "count": 10,
            "url": "https://www.v2ex.com/api/topics/hot.json"
        },
        "hackernews": {
            "enabled": True,
            "count": 10,
            "url": "https://hacker-news.firebaseio.com/v0/topstories.json"
        }
    },
    "cache_file": Path(__file__).parent.parent / "data" / "cache.json",
    "output_file": Path(__file__).parent.parent / "data" / f"summary_{datetime.now().strftime('%Y%m%d_%H%M')}.json"
}


def fetch_polymarket_top10():
    """使用 Gamma API 按成交量排序获取 Top 10"""
    print("🔥 抓取 Polymarket Top 10（按24小时成交量排序）...")
    
    if not PolymarketAPI:
        print("   ❌ PolymarketAPI 模块未加载")
        return []
    
    try:
        api = PolymarketAPI()
        
        # 方法1: 使用 get_top_volume_events
        print(f"   尝试方法1: get_top_volume_events")
        events = api.get_top_volume_events(limit=10)
        
        # 失败则使用方法2
        if not events:
            print(f"   方法1失败，尝试方法2: get_active_events")
            events = api.get_active_events(limit=10, order='volume_24hr')
        
        if not events:
            print("   ❌ 两种方法都失败")
            return []
        
        print(f"   ✅ 获取到 {len(events)} 个事件")
        
        # 格式化事件
        formatted_events = []
        for event in events[:10]:
            formatted = {
                'title': event.get('title', 'N/A'),
                'slug': event.get('slug', ''),
                'url': f"https://polymarket.com/event/{event.get('slug', '')}",
                'source': 'Polymarket',
                'timestamp': datetime.now().isoformat()
            }
            
            # 提取概率和市场数据
            if 'markets' in event and len(event['markets']) > 0:
                # 优先选择活跃市场
                active_markets = [m for m in event['markets'] if not m.get('closed', True)]
                markets_to_check = active_markets if active_markets else event['markets']
                
                for market in markets_to_check[:1]:
                    outcomes = market.get('outcomePrices', '[]')
                    if outcomes and outcomes != '[]':
                        try:
                            prices = json.loads(outcomes)
                            if isinstance(prices, list) and len(prices) >= 2:
                                yes_prob = float(prices[0]) * 100
                                no_prob = float(prices[1]) * 100
                                
                                formatted['probability'] = f"{yes_prob:.1f}%"
                                formatted['yes_prob'] = yes_prob
                                formatted['no_prob'] = no_prob
                                
                                # 概率分类
                                if yes_prob >= 70:
                                    formatted['trend'] = '🔥 高概率'
                                elif yes_prob >= 40:
                                    formatted['trend'] = '📊 中等概率'
                                elif yes_prob >= 20:
                                    formatted['trend'] = '📉 低概率'
                                else:
                                    formatted['trend'] = '❌ 很低'
                        except:
                            pass
                    
                    formatted['volume'] = market.get('volume', 0)
                    formatted['liquidity'] = market.get('liquidity', 0)
                    formatted['volume24hr'] = market.get('volume24hr', 0)
                    formatted['end_date'] = market.get('endDate', 'N/A')
                    formatted['last_trade'] = market.get('lastTradePrice', 0)
                    formatted['one_day_change'] = market.get('oneDayPriceChange', 0)
                    
                    # 市场状态
                    formatted['closed'] = market.get('closed', False)
                    
                    break
            
            formatted_events.append(formatted)
        
        print(f"   ✅ 成功格式化 {len(formatted_events)} 个事件")
        return formatted_events
        
    except Exception as e:
        print(f"   ❌ 获取失败: {e}")
        import traceback
        traceback.print_exc()
        return []


def fetch_v2ex_hot():
    """抓取 V2EX 热门"""
    print("💬 抓取 V2EX 热门...")
    
    try:
        response = subprocess.run(
            ['curl', '-s', CONFIG["sources"]["v2ex"]["url"]],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if response.returncode == 0:
            data = json.loads(response.stdout)
            
            topics = []
            for item in data[:CONFIG["sources"]["v2ex"]["count"]]:
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
            ['curl', '-s', CONFIG["sources"]["hackernews"]["url"]],
            capture_output=True,
            text=True,
            timeout=10
        )
        
        if response.returncode == 0:
            story_ids = json.loads(response.stdout)
            
            stories = []
            for story_id in story_ids[:CONFIG["sources"]["hackernews"]["count"]]:
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


def load_cache():
    """加载缓存"""
    try:
        if CONFIG["cache_file"].exists():
            with open(CONFIG["cache_file"], 'r', encoding='utf-8') as f:
                return json.load(f)
    except Exception as e:
        print(f"⚠️  无法加载缓存: {e}")
    return {}


def save_cache(data):
    """保存缓存"""
    try:
        CONFIG["cache_file"].parent.mkdir(parents=True, exist_ok=True)
        
        cache_data = {
            "timestamp": datetime.now().isoformat(),
            "polymarket": data.get("polymarket", []),
            "v2ex": data.get("v2ex", []),
            "hackernews": data.get("hackernews", [])
        }
        
        with open(CONFIG["cache_file"], 'w', encoding='utf-8') as f:
            json.dump(cache_data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 缓存已保存")
    except Exception as e:
        print(f"❌ 保存缓存失败: {e}")


def save_output(data):
    """保存输出"""
    try:
        CONFIG["output_file"].parent.mkdir(parents=True, exist_ok=True)
        
        with open(CONFIG["output_file"], 'w', encoding='utf-8') as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        
        print(f"✅ 输出已保存: {CONFIG['output_file']}")
    except Exception as e:
        print(f"❌ 保存输出失败: {e}")


def generate_report(polymarket_data, v2ex_data, hn_data):
    """生成汇总报告"""
    report = []
    report.append("📊 每日信息汇总")
    report.append(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    report.append("")
    
    # Polymarket Top 10
    if polymarket_data:
        report.append("🔥 Polymarket Top 10（按24小时成交量排序）")
        report.append("─" * 50)
        for i, event in enumerate(polymarket_data, 1):
            prob_str = f" | {event.get('probability', 'N/A')}" if event.get('probability') else ""
            status_emoji = '✅' if not event.get('closed', True) else '⚠️'
            
            report.append(f"{status_emoji} #{i}. {event['title']}{prob_str}")
            
            # 成交量信息（重点）
            if event.get('volume24hr') and isinstance(event['volume24hr'], (int, float)) and event['volume24hr'] > 0:
                vol24h = event['volume24hr']
                if vol24h > 1000000:
                    vol24h_str = f"${vol24h/1000000:.1f}M"
                elif vol24h > 1000:
                    vol24h_str = f"${vol24h/1000:.1f}K"
                else:
                    vol24h_str = f"${vol24h:.0f}"
                report.append(f"   💹 24h成交量: {vol24h_str}")
            
            # 总成交量
            if event.get('volume') and isinstance(event['volume'], (int, float)) and event['volume'] > 0:
                volume = event['volume']
                if volume > 1000000:
                    vol_str = f"${volume/1000000:.1f}M"
                elif volume > 1000:
                    vol_str = f"${volume/1000:.1f}K"
                else:
                    vol_str = f"${volume:.0f}"
                report.append(f"   💰 总成交量: {vol_str}")
            
            # 24小时价格变化
            if event.get('one_day_change'):
                change = event['one_day_change']
                if isinstance(change, (int, float)) and change != 0:
                    if change > 0:
                        report.append(f"   📈 +{change*100:+.1f}% (24h)")
                    elif change < 0:
                        report.append(f"   📉 {change*100:+.1f}% (24h)")
            
            # 趋势标注
            if 'trend' in event:
                report.append(f"   {event['trend']}")
            
            report.append("")
        
        # 简化的总结
        if len(polymarket_data) > 0:
            report.append("📊 成交量排行亮点")
            report.append("─" * 50)
            
            # 统计
            total_vol_24h = sum(e.get('volume24hr', 0) for e in polymarket_data if isinstance(e.get('volume24hr'), (int, float)))
            
            if total_vol_24h > 0:
                if total_vol_24h > 1000000:
                    total_str = f"${total_vol_24h/1000000:.1f}M"
                elif total_vol_24h > 1000:
                    total_str = f"${total_vol_24h/1000:.1f}K"
                else:
                    total_str = f"${total_vol24h:.0f}"
                report.append(f"💹 Top 10总24h成交量: {total_str}")
            
            # 高概率事件
            high_prob = [e for e in polymarket_data if e.get('yes_prob', 0) >= 70]
            if high_prob:
                report.append(f"\n🔥 高概率事件（≥70%）: {len(high_prob)}个")
                for event in high_prob[:3]:
                    prob = event.get('probability', 'N/A')
                    title = event['title'][:60]
                    report.append(f"   • {title}")
                    report.append(f"     {prob}")
            
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
    report.append(f"⏰ 更新时间: {datetime.now().strftime('%H:%M')}")
    report.append(f"📈 数据来源: V2EX + Hacker News")
    
    return "\n".join(report)


def main():
    """主函数"""
    print("=" * 60)
    print("📊 每日信息汇总")
    print("=" * 60)
    print(f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print()
    
    # 抓取数据
    polymarket_data = fetch_polymarket_top10()
    v2ex_data = fetch_v2ex_hot()
    hn_data = fetch_hacker_news()
    
    print()
    
    # 生成报告
    report = generate_report(polymarket_data, v2ex_data, hn_data)
    
    # 显示报告
    print(report)
    print()
    
    # 保存数据
    data = {
        "polymarket": polymarket_data,
        "v2ex": v2ex_data,
        "hackernews": hn_data,
        "report": report,
        "generated_at": datetime.now().isoformat()
    }
    
    save_cache(data)
    save_output(data)
    
    # 保存消息到 /tmp 并创建发送标记
    try:
        message_file = Path("/tmp/daily_hub_message.txt")
        ready_flag = Path("/tmp/daily_hub_ready.flag")
        
        message_file.parent.mkdir(parents=True, exist_ok=True)
        message_file.write_text(report, encoding='utf-8')
        ready_flag.write_text(str(datetime.now().timestamp()))
        
        print("📁 消息已保存到 /tmp/daily_hub_message.txt")
        print("🚩 发送标记已创建")
    except Exception as e:
        print(f"⚠️  无法创建发送标记: {e}")
    
    print("=" * 60)
    print("✅ 完成!")
    print("=" * 60)


if __name__ == "__main__":
    main()
