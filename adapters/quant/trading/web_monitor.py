"""
A股量化交易系统 - Web监控界面

使用Streamlit创建Web界面监控交易系统
提供实时可视化、历史查询、绩效分析等功能

版本: 1.0.0
创建日期: 2026-03-09
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from pathlib import Path
from datetime import datetime, timedelta
import json

# 添加项目路径
import sys
project_root = Path(__file__).parent.parent.parent.parent
sys.path.insert(0, str(project_root))

from adapters.quant.trading.trade_journal import TradeJournal
from adapters.quant.data.china_stock_fetcher import ChinaStockDataFetcher


# ============================================
# 页面配置
# ============================================

st.set_page_config(
    page_title="A股量化交易系统",
    page_icon="📈",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 自定义CSS
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #1f77b4;
        text-align: center;
        margin-bottom: 1rem;
    }
    .metric-card {
        background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
        padding: 1rem;
        border-radius: 0.5rem;
        color: white;
        text-align: center;
    }
    .metric-value {
        font-size: 2rem;
        font-weight: bold;
    }
    .metric-label {
        font-size: 0.9rem;
        opacity: 0.9;
    }
</style>
""", unsafe_allow_html=True)


# ============================================
# 工具函数
# ============================================

@st.cache_data(ttl=60)  # 缓存60秒
def load_journal(data_dir: str = "trading_data"):
    """加载交易日志"""
    return TradeJournal(data_dir=data_dir)


@st.cache_data(ttl=30)
def get_realtime_quotes(symbols: list):
    """获取实时行情"""
    try:
        fetcher = ChinaStockDataFetcher(preferred_source="akshare")
        return fetcher.get_realtime_quotes(symbols)
    except Exception as e:
        st.error(f"获取实时行情失败: {e}")
        return {}


def format_currency(value: float) -> str:
    """格式化货币"""
    return f"¥{value:,.2f}"


def format_percent(value: float) -> str:
    """格式化百分比"""
    sign = "+" if value >= 0 else ""
    return f"{sign}{value:.2f}%"


# ============================================
# 侧边栏
# ============================================

def render_sidebar():
    """渲染侧边栏"""
    st.sidebar.title("🎛️ 控制面板")

    # 数据目录
    data_dir = st.sidebar.text_input("数据目录", value="trading_data")

    # 刷新按钮
    if st.sidebar.button("🔄 刷新数据"):
        st.cache_data.clear()
        st.rerun()

    st.sidebar.divider()

    # 系统状态
    st.sidebar.subheader("系统状态")

    try:
        journal = load_journal(data_dir)
        perf = journal.get_performance_summary()

        st.sidebar.metric("总交易数", perf['total_trades'])
        st.sidebar.metric("总收益率", f"{perf['total_return']:+.2f}%")
        st.sidebar.metric("胜率", f"{perf['win_rate']:.1f}%")
        st.sidebar.metric("最大回撤", f"{perf['max_drawdown']:.2f}%")

    except Exception as e:
        st.sidebar.error(f"加载数据失败: {e}")

    st.sidebar.divider()

    # 快速链接
    st.sidebar.subheader("快速导航")
    if st.sidebar.button("📊 概览"):
        st.session_state.page = "overview"
    if st.sidebar.button("📈 资金曲线"):
        st.session_state.page = "equity_curve"
    if st.sidebar.button("💼 持仓分析"):
        st.session_state.page = "positions"
    if st.sidebar.button("🔄 交易记录"):
        st.session_state.page = "trades"
    if st.sidebar.button("🎯 实时行情"):
        st.session_state.page="quotes"

    # 默认页面
    if 'page' not in st.session_state:
        st.session_state.page = "overview"

    return data_dir


# ============================================
# 概览页面
# ============================================

def render_overview(journal: TradeJournal):
    """渲染概览页面"""
    st.markdown('<p class="main-header">📊 系统概览</p>', unsafe_allow_html=True)

    # 获取绩效数据
    perf = journal.get_performance_summary()

    # 顶部指标卡片
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        st.markdown(f"""
        <div class="metric-card">
            <div class="metric-value">{format_currency(perf['latest_equity'])}</div>
            <div class="metric-label">最新净值</div>
        </div>
        """, unsafe_allow_html=True)

    with col2:
        color = "#4caf50" if perf['total_return'] >= 0 else "#f44336"
        st.markdown(f"""
        <div class="metric-card" style="background: {color};">
            <div class="metric-value">{format_percent(perf['total_return'])}</div>
            <div class="metric-label">总收益率</div>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #f093fb 0%, #f5576c 100%);">
            <div class="metric-value">{perf['win_rate']:.1f}%</div>
            <div class="metric-label">胜率</div>
        </div>
        """, unsafe_allow_html=True)

    with col4:
        st.markdown(f"""
        <div class="metric-card" style="background: linear-gradient(135deg, #fa709a 0%, #fee140 100%);">
            <div class="metric-value">{perf['max_drawdown']:.2f}%</div>
            <div class="metric-label">最大回撤</div>
        </div>
        """, unsafe_allow_html=True)

    st.divider()

    # 图表行
    col1, col2 = st.columns(2)

    with col1:
        st.subheader("💹 资金曲线")
        df_equity = journal.get_equity_curve()
        if not df_equity.empty:
            fig = px.line(df_equity, x='date', y='total_asset',
                         title='资金曲线',
                         labels={'total_asset': '总资产', 'date': '日期'})
            fig.update_layout(height=300)
            st.plotly_chart(fig, use_container_width=True)
        else:
            st.info("暂无数据")

    with col2:
        st.subheader("📊 收益分布")
        df_trades = journal.get_trades_dataframe()
        if not df_trades.empty and 'pnl' in df_trades.columns:
            pnl_data = df_trades[df_trades['pnl'] != 0]['pnl']
            if len(pnl_data) > 0:
                fig = px.histogram(pnl_data, nbins=30,
                                 title='盈亏分布',
                                 labels={'value': '盈亏金额', 'count': '次数'})
                fig.update_layout(height=300)
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("暂无盈亏数据")
        else:
            st.info("暂无数据")


# ============================================
# 资金曲线页面
# ============================================

def render_equity_curve(journal: TradeJournal):
    """渲染资金曲线页面"""
    st.markdown('<p class="main-header">📈 资金曲线分析</p>', unsafe_allow_html=True)

    df = journal.get_equity_curve()

    if df.empty:
        st.warning("暂无资金曲线数据")
        return

    # 主图表
    fig = go.Figure()

    # 添加总资产线
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['total_asset'],
        mode='lines',
        name='总资产',
        line=dict(color='#1f77b4', width=2)
    ))

    # 添加现金线
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['cash'],
        mode='lines',
        name='现金',
        line=dict(color='#2ca02c', width=1)
    ))

    # 添加持仓市值线
    fig.add_trace(go.Scatter(
        x=df['date'],
        y=df['market_value'],
        mode='lines',
        name='持仓市值',
        line=dict(color='#ff7f0e', width=1)
    ))

    fig.update_layout(
        title='资金曲线',
        xaxis_title='日期',
        yaxis_title='金额 (¥)',
        hovermode='x unified',
        height=500
    )

    st.plotly_chart(fig, use_container_width=True)

    # 详细数据表
    st.subheader("📋 详细数据")
    st.dataframe(
        df.sort_values('date', ascending=False).head(20),
        use_container_width=True,
        hide_index=True
    )


# ============================================
# 持仓分析页面
# ============================================

def render_positions(journal: TradeJournal):
    """渲染持仓分析页面"""
    st.markdown('<p class="main-header">💼 持仓分析</p>', unsafe_allow_html=True)

    # 从最新快照获取持仓数据
    if not journal.daily_snapshots:
        st.warning("暂无持仓数据")
        return

    latest_snapshot = journal.daily_snapshots[-1]

    if not latest_snapshot.positions:
        st.info("当前无持仓")
        return

    # 持仓数据表
    df_positions = pd.DataFrame(latest_snapshot.positions)

    st.subheader("📊 当前持仓")
    st.dataframe(
        df_positions,
        use_container_width=True,
        hide_index=True,
        column_config={
            'symbol': st.column_config.TextColumn('代码', width='small'),
            'quantity': st.column_config.NumberColumn('数量', format='%d'),
            'avg_price': st.column_config.NumberColumn('成本价', format='¥%.2f'),
            'current_price': st.column_config.NumberColumn('现价', format='¥%.2f'),
            'market_value': st.column_config.NumberColumn('市值', format='¥,.2f'),
            'unrealized_pnl': st.column_config.NumberColumn('浮动盈亏', format='¥+,.2f'),
            'unrealized_pnl_pct': st.column_config.NumberColumn('盈亏比例', format='%+.2f%%')
        }
    )

    # 持仓分布饼图
    st.subheader("🍰 持仓分布")
    fig = px.pie(
        df_positions,
        values='market_value',
        names='symbol',
        title='持仓市值分布'
    )
    st.plotly_chart(fig, use_container_width=True)

    # 盈亏分析
    st.subheader("📈 盈亏分析")
    col1, col2 = st.columns(2)

    with col1:
        profitable = [p for p in latest_snapshot.positions if p['unrealized_pnl'] > 0]
        losing = [p for p in latest_snapshot.positions if p['unrealized_pnl'] < 0]

        st.metric("盈利持仓", len(profitable))
        st.metric("亏损持仓", len(losing))

    with col2:
        total_pnl = sum(p['unrealized_pnl'] for p in latest_snapshot.positions)
        st.metric("总浮动盈亏", f"{total_pnl:+,.2f}")


# ============================================
# 交易记录页面
# ============================================

def render_trades(journal: TradeJournal):
    """渲染交易记录页面"""
    st.markdown('<p class="main-header">🔄 交易记录</p>', unsafe_allow_html=True)

    df = journal.get_trades_dataframe()

    if df.empty:
        st.warning("暂无交易记录")
        return

    # 统计信息
    col1, col2, col3, col4 = st.columns(4)

    total_trades = len(df)
    buy_trades = len(df[df['side'] == 'BUY'])
    sell_trades = len(df[df['side'] == 'SELL'])
    total_pnl = df[df['pnl'] != 0]['pnl'].sum()

    col1.metric("总交易次数", total_trades)
    col2.metric("买入次数", buy_trades)
    col3.metric("卖出次数", sell_trades)
    col4.metric("已实现盈亏", f"¥{total_pnl:+,.2f}")

    st.divider()

    # 交易记录表
    st.subheader("📋 交易明细")

    # 过滤器
    col1, col2, col3 = st.columns(3)
    with col1:
        symbol_filter = st.selectbox('股票代码', ['全部'] + sorted(df['symbol'].unique().tolist()))
    with col2:
        side_filter = st.selectbox('方向', ['全部', 'BUY', 'SELL'])
    with col3:
        limit = st.slider('显示条数', 10, 500, 100)

    # 应用过滤
    df_filtered = df.copy()
    if symbol_filter != '全部':
        df_filtered = df_filtered[df_filtered['symbol'] == symbol_filter]
    if side_filter != '全部':
        df_filtered = df_filtered[df_filtered['side'] == side_filter]

    # 显示数据
    st.dataframe(
        df_filtered.sort_values('trade_time', ascending=False).head(limit),
        use_container_width=True,
        hide_index=True
    )


# ============================================
# 实时行情页面
# ============================================

def render_quotes():
    """渲染实时行情页面"""
    st.markdown('<p class="main-header">🎯 实时行情</p>', unsafe_allow_html=True)

    # 热门股票列表
    default_symbols = [
        "600519.SH",  # 贵州茅台
        "000001.SZ",  # 平安银行
        "000002.SZ",  # 万科A
        "600030.SH",  # 中信证券
        "600036.SH",  # 招商银行
        "601318.SH",  # 中国平安
        "600276.SH",  # 恒瑞医药
        "300750.SZ",  # 宁德时代
        "002594.SZ",  # 比亚迪
        "600900.SH",  # 长江电力
    ]

    # 输入股票代码
    symbols_input = st.text_input(
        "输入股票代码（用逗号分隔）",
        value=",".join(default_symbols),
        help="格式: 600519.SH,000001.SZ"
    )

    symbols = [s.strip() for s in symbols_input.split(',') if s.strip()]

    # 获取行情按钮
    if st.button("获取实时行情"):
        with st.spinner("正在获取行情..."):
            quotes = get_realtime_quotes(symbols)

            if quotes:
                # 转换为DataFrame
                data = []
                for symbol, quote in quotes.items():
                    data.append({
                        '代码': symbol,
                        '名称': quote.name,
                        '最新价': f"¥{quote.close:.2f}",
                        '涨跌': f"{(quote.close / quote.open - 1) * 100:+.2f}%" if quote.open > 0 else "N/A",
                        '开盘': f"¥{quote.open:.2f}",
                        '最高': f"¥{quote.high:.2f}",
                        '最低': f"¥{quote.low:.2f}",
                        '成交量': f"{quote.volume:,.0f}",
                        '成交额': f"¥{quote.amount:,.0f}",
                        '换手率': f"{quote.turnover:.2f}%",
                        '市盈率': f"{quote.pe_ratio:.2f}" if quote.pe_ratio > 0 else "N/A",
                        '市值': f"¥{quote.market_cap:,.0f}" if quote.market_cap > 0 else "N/A"
                    })

                df = pd.DataFrame(data)

                # 显示表格
                st.dataframe(
                    df,
                    use_container_width=True,
                    hide_index=True
                )

                # 导出按钮
                csv = df.to_csv(index=False)
                st.download_button(
                    label="📥 下载CSV",
                    data=csv,
                    file_name=f"quotes_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                    mime="text/csv"
                )
            else:
                st.error("未能获取到行情数据")


# ============================================
# 主应用
# ============================================

def main():
    """主应用"""
    # 渲染侧边栏
    data_dir = render_sidebar()

    # 加载交易日志
    try:
        journal = load_journal(data_dir)
    except Exception as e:
        st.error(f"加载交易日志失败: {e}")
        st.info("请确保数据目录存在且包含有效的数据文件")
        return

    # 根据选择的页面渲染内容
    page = st.session_state.get('page', 'overview')

    if page == 'overview':
        render_overview(journal)
    elif page == 'equity_curve':
        render_equity_curve(journal)
    elif page == 'positions':
        render_positions(journal)
    elif page == 'trades':
        render_trades(journal)
    elif page == 'quotes':
        render_quotes()


if __name__ == "__main__":
    main()
