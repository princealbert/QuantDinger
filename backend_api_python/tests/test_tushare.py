"""
测试 Tushare 数据源
"""
import os
import sys
from datetime import datetime

# 添加项目路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.data_sources.tushare import TushareDataSource
from app.utils.logger import setup_logger

# 设置日志
setup_logger()


def test_tushare_kline():
    """测试获取K线数据"""
    print("\n" + "=" * 60)
    print("测试 Tushare K线数据获取")
    print("=" * 60)

    try:
        source = TushareDataSource()

        # 测试股票列表
        test_cases = [
            {'symbol': '000001', 'name': '平安银行 (深圳)'},
            {'symbol': '600000', 'name': '浦发银行 (上海)'},
            {'symbol': '000001.SZ', 'name': '平安银行 (Tushare格式)'},
            {'symbol': '600000.SH', 'name': '浦发银行 (Tushare格式)'},
        ]

        for test in test_cases:
            print(f"\n测试: {test['name']}")
            print(f"股票代码: {test['symbol']}")

            # 获取日线数据
            print("  获取日线数据...")
            klines = source.get_kline(test['symbol'], '1D', 10)

            if klines:
                print(f"  ✓ 成功获取 {len(klines)} 条K线数据")
                print(f"  最新数据: {datetime.fromtimestamp(klines[-1]['time']).strftime('%Y-%m-%d')}")
                print(f"  收盘价: {klines[-1]['close']}")
                print(f"  成交量: {klines[-1]['volume']}")
            else:
                print(f"  ✗ 未获取到数据")

        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_tushare_ticker():
    """测试获取实时报价"""
    print("\n" + "=" * 60)
    print("测试 Tushare 实时报价")
    print("=" * 60)

    try:
        source = TushareDataSource()

        test_symbols = ['000001', '600000']

        for symbol in test_symbols:
            print(f"\n测试股票: {symbol}")
            ticker = source.get_ticker(symbol)

            if ticker and ticker.get('last', 0) > 0:
                print(f"  ✓ 获取成功")
                print(f"  最新价: {ticker['last']}")
                print(f"  涨跌额: {ticker.get('change', 'N/A')}")
                print(f"  涨跌幅: {ticker.get('changePercent', 'N/A')}%")
                print(f"  最高价: {ticker.get('high', 'N/A')}")
                print(f"  最低价: {ticker.get('low', 'N/A')}")
                print(f"  开盘价: {ticker.get('open', 'N/A')}")
            else:
                print(f"  ✗ 未获取到报价")

        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_tushare_stock_list():
    """测试获取股票列表"""
    print("\n" + "=" * 60)
    print("测试 Tushare 股票列表")
    print("=" * 60)

    try:
        source = TushareDataSource()

        print("\n获取A股列表...")
        df = source.get_stock_list(market='A')

        if df is not None and not df.empty:
            print(f"✓ 成功获取 {len(df)} 只A股")
            print("\n前10只股票:")
            print(df.head(10).to_string())
        else:
            print("✗ 未获取到股票列表")

        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_tushare_index_list():
    """测试获取指数列表"""
    print("\n" + "=" * 60)
    print("测试 Tushare 指数列表")
    print("=" * 60)

    try:
        source = TushareDataSource()

        print("\n获取指数列表...")
        df = source.get_index_list()

        if df is not None and not df.empty:
            print(f"✓ 成功获取 {len(df)} 个指数")
            print("\n前10个指数:")
            print(df.head(10).to_string())
        else:
            print("✗ 未获取到指数列表")

        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def test_tushare_symbol_conversion():
    """测试股票代码转换"""
    print("\n" + "=" * 60)
    print("测试 Tushare 股票代码转换")
    print("=" * 60)

    try:
        source = TushareDataSource()

        test_cases = [
            '000001',
            '600000',
            '000001.SZ',
            '600000.SH',
            '300001',
            '688001'
        ]

        print("\n股票代码转换测试:")
        for code in test_cases:
            ts_code = source._to_tushare_symbol(code)
            print(f"  {code:12s} -> {ts_code}")

        print("\n" + "=" * 60)
        print("测试完成")
        print("=" * 60)

    except Exception as e:
        print(f"✗ 测试失败: {e}")
        import traceback
        traceback.print_exc()


def main():
    """主测试函数"""
    print("\n")
    print("*" * 60)
    print("* Tushare 数据源测试")
    print("*" * 60)

    # 检查环境变量
    token = os.getenv('TUSHARE_TOKEN')
    if not token:
        print("\n⚠ 警告: TUSHARE_TOKEN 环境变量未设置")
        print("请先设置 TUSHARE_TOKEN 环境变量")
        return

    print(f"\nTUSHARE_TOKEN: {token[:10]}...{token[-10:]}")

    # 运行测试
    test_tushare_symbol_conversion()
    test_tushare_kline()
    test_tushare_ticker()
    test_tushare_stock_list()
    test_tushare_index_list()


if __name__ == '__main__':
    main()
