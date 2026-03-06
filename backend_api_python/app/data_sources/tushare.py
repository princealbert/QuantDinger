"""
Tushare 数据源
提供中国A股、港股、基金、期货等金融数据
"""
import os
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import pandas as pd

from app.data_sources.base import BaseDataSource
from app.utils.logger import get_logger

logger = get_logger(__name__)

# Optional dependency: tushare
try:
    import tushare as ts
    HAS_TUSHARE = True
    logger.debug("tushare is available")
except ImportError:
    HAS_TUSHARE = False
    logger.warning("tushare is not installed; tushare-based features are disabled")


class TushareDataSource(BaseDataSource):
    """
    Tushare 数据源
    支持获取A股、港股、指数、基金等数据

    注意：需要设置 TUSHARE_TOKEN 环境变量
    """

    name = "Tushare"

    # 时间周期映射
    PERIOD_MAP = {
        '1m': '1min',
        '5m': '5min',
        '15m': '15min',
        '30m': '30min',
        '1H': '60min',
        '4H': None,  # 不直接支持，需要聚合
        '1D': 'daily',
        '1W': 'weekly',
        '1M': 'monthly'
    }

    def __init__(self):
        """初始化 Tushare 数据源"""
        self._pro = None
        self._token = os.getenv('TUSHARE_TOKEN')

        if not self._token:
            logger.warning("TUSHARE_TOKEN environment variable not set")

    @property
    def pro(self):
        """获取 Tushare pro 实例（懒加载）"""
        if self._pro is None:
            if not HAS_TUSHARE:
                raise ImportError("tushare is not installed. Install with: pip install tushare")

            if not self._token:
                raise ValueError("TUSHARE_TOKEN environment variable is not set")

            ts.set_token(self._token)
            self._pro = ts.pro_api()

        return self._pro

    def get_kline(
        self,
        symbol: str,
        timeframe: str,
        limit: int,
        before_time: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        获取K线数据

        Args:
            symbol: 股票代码（如 000001.SZ, 600000.SH）
            timeframe: 时间周期
            limit: 数据条数
            before_time: 获取此时间之前的数据（Unix时间戳，秒）

        Returns:
            K线数据列表
        """
        if not HAS_TUSHARE:
            logger.error("tushare not installed")
            return []

        if not self._token:
            logger.error("TUSHARE_TOKEN not set")
            return []

        klines = []

        # 转换 Tushare 格式
        ts_code = self._to_tushare_symbol(symbol)
        if not ts_code:
            logger.warning(f"Invalid symbol format: {symbol}")
            return []

        # 获取周期
        period = self.PERIOD_MAP.get(timeframe)
        if not period:
            logger.warning(f"Unsupported timeframe: {timeframe}")
            return []

        # 4H 需要特殊处理
        if timeframe == '4H':
            return self._fetch_aggregated_kline(ts_code, '60min', 4, limit, before_time)

        try:
            # 计算日期范围
            if before_time:
                end_date = datetime.fromtimestamp(before_time)
            else:
                end_date = datetime.now()

            # 计算开始日期（多获取一些数据以确保充足）
            if timeframe in ['1D', '1W', '1M']:
                days = limit * 2 if timeframe == '1D' else limit * 7 if timeframe == '1W' else limit * 30
                start_date = end_date - timedelta(days=days)
            else:
                # 分钟级数据，限制获取范围
                start_date = end_date - timedelta(days=7)  # 最多获取7天

            logger.debug(f"Tushare: Fetching {ts_code} {timeframe} from {start_date.date()} to {end_date.date()}")

            # 调用 Tushare API
            if timeframe in ['1D', '1W', '1M']:
                df = self.pro.daily(
                    ts_code=ts_code,
                    start_date=start_date.strftime('%Y%m%d'),
                    end_date=end_date.strftime('%Y%m%d')
                )
            else:
                # 分钟级数据需要使用 bar 接口（如果可用）
                df = self._fetch_minute_data(ts_code, period, start_date, end_date)

            if df is not None and not df.empty:
                # 排序
                df = df.sort_values('trade_date').tail(limit)

                # 转换格式
                for _, row in df.iterrows():
                    # Tushare 返回日期字符串 '2024-01-01'
                    trade_date = row.get('trade_date', row.get('cal_date', ''))
                    if trade_date:
                        try:
                            # 处理日期格式
                            if isinstance(trade_date, str):
                                dt = datetime.strptime(trade_date, '%Y%m%d')
                            else:
                                dt = trade_date

                            ts = int(dt.timestamp())

                            klines.append(self.format_kline(
                                timestamp=ts,
                                open_price=float(row['open']),
                                high=float(row['high']),
                                low=float(row['low']),
                                close=float(row['close']),
                                volume=float(row['vol'])
                            ))
                        except (ValueError, KeyError) as e:
                            logger.debug(f"Failed to parse row: {row}, error: {e}")
                            continue

                logger.info(f"Tushare: Fetched {len(klines)} klines for {symbol}")

            else:
                logger.warning(f"Tushare: No data for {symbol}")

        except Exception as e:
            logger.error(f"Tushare: Failed to fetch kline data: {e}")
            import traceback
            logger.error(traceback.format_exc())

        return klines

    def _fetch_minute_data(
        self,
        ts_code: str,
        period: str,
        start_date: datetime,
        end_date: datetime
    ) -> pd.DataFrame:
        """
        获取分钟级数据

        注意：Tushare 的分钟级数据需要积分等级，普通用户可能无法获取
        """
        try:
            # 尝试使用标准分钟级接口
            if hasattr(self.pro, 'minute'):
                df = self.pro.minute(
                    ts_code=ts_code,
                    freq=period,
                    start_date=start_date.strftime('%Y%m%d %H:%M:%S'),
                    end_date=end_date.strftime('%Y%m%d %H:%M:%S')
                )
                return df
            else:
                logger.warning(f"Tushare minute data not available for {ts_code} (requires pro account)")
                return pd.DataFrame()

        except Exception as e:
            logger.warning(f"Tushare minute data fetch failed: {e}")
            return pd.DataFrame()

    def _fetch_aggregated_kline(
        self,
        ts_code: str,
        base_period: str,
        agg_factor: int,
        limit: int,
        before_time: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        获取并聚合K线数据（如从1H聚合为4H）

        Args:
            ts_code: Tushare代码
            base_period: 基础周期
            agg_factor: 聚合因子
            limit: 数据条数
            before_time: 时间限制
        """
        # 获取基础周期数据（多获取一些）
        base_limit = limit * agg_factor + 10
        base_klines = self.get_kline_from_ts_code(
            ts_code,
            base_period,
            base_limit,
            before_time
        )

        if not base_klines:
            return []

        # 聚合
        aggregated = []
        i = 0
        while i < len(base_klines):
            batch = base_klines[i:i + agg_factor]
            if len(batch) < agg_factor:
                break

            aggregated.append(self.format_kline(
                timestamp=batch[0]['time'],
                open_price=batch[0]['open'],
                high=max(k['high'] for k in batch),
                low=min(k['low'] for k in batch),
                close=batch[-1]['close'],
                volume=sum(k['volume'] for k in batch)
            ))
            i += agg_factor

        return aggregated[-limit:] if len(aggregated) > limit else aggregated

    def get_kline_from_ts_code(
        self,
        ts_code: str,
        period: str,
        limit: int,
        before_time: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """直接使用 Tushare 代码获取K线（内部方法）"""
        klines = []

        try:
            if period.endswith('min'):
                # 分钟级数据
                df = self._fetch_minute_data(
                    ts_code,
                    period,
                    datetime.now() - timedelta(days=7),
                    datetime.now()
                )
            else:
                # 日线/周线/月线数据
                end_date = datetime.fromtimestamp(before_time) if before_time else datetime.now()
                start_date = end_date - timedelta(days=limit * 2)

                df = self.pro.daily(
                    ts_code=ts_code,
                    start_date=start_date.strftime('%Y%m%d'),
                    end_date=end_date.strftime('%Y%m%d')
                )

            if df is not None and not df.empty:
                df = df.tail(limit)
                for _, row in df.iterrows():
                    trade_date = row.get('trade_date', '')
                    if trade_date:
                        dt = datetime.strptime(str(trade_date), '%Y%m%d')
                        klines.append(self.format_kline(
                            timestamp=int(dt.timestamp()),
                            open_price=float(row['open']),
                            high=float(row['high']),
                            low=float(row['low']),
                            close=float(row['close']),
                            volume=float(row['vol'])
                        ))

        except Exception as e:
            logger.debug(f"Failed to fetch from ts_code {ts_code}: {e}")

        return klines

    def get_ticker(self, symbol: str) -> Dict[str, Any]:
        """
        获取实时报价

        Args:
            symbol: 股票代码

        Returns:
            报价数据字典
        """
        if not HAS_TUSHARE:
            return {'last': 0, 'symbol': symbol}

        try:
            ts_code = self._to_tushare_symbol(symbol)
            if not ts_code:
                return {'last': 0, 'symbol': symbol}

            # 获取最新日线数据（作为最新报价）
            end_date = datetime.now()
            start_date = end_date - timedelta(days=2)

            df = self.pro.daily(
                ts_code=ts_code,
                start_date=start_date.strftime('%Y%m%d'),
                end_date=end_date.strftime('%Y%m%d')
            )

            if df is not None and not df.empty:
                df = df.tail(1)
                row = df.iloc[0]
                prev_close = float(row['pre_close'])

                return {
                    'last': float(row['close']),
                    'open': float(row['open']),
                    'high': float(row['high']),
                    'low': float(row['low']),
                    'previousClose': prev_close,
                    'change': float(row['close']) - prev_close,
                    'changePercent': (float(row['close']) - prev_close) / prev_close * 100 if prev_close > 0 else 0,
                    'volume': float(row['vol']),
                    'amount': float(row.get('amount', 0))
                }

        except Exception as e:
            logger.debug(f"Tushare ticker failed for {symbol}: {e}")

        return {'last': 0, 'symbol': symbol}

    def _to_tushare_symbol(self, symbol: str) -> Optional[str]:
        """
        转换为 Tushare 格式

        Args:
            symbol: 股票代码（如 000001, 600000）

        Returns:
            Tushare 格式代码（如 000001.SZ, 600000.SH）
        """
        symbol = symbol.strip()

        # 已经是 Tushare 格式
        if '.' in symbol:
            return symbol.upper()

        # 转换为 Tushare 格式
        if symbol.startswith('6'):
            return f"{symbol}.SH"
        elif symbol.startswith('0') or symbol.startswith('3'):
            return f"{symbol}.SZ"
        elif symbol.startswith('4') or symbol.startswith('8'):
            return f"{symbol}.BJ"
        else:
            logger.warning(f"Unknown symbol format: {symbol}")
            return None

    def get_stock_list(self, market: str = 'A') -> pd.DataFrame:
        """
        获取股票列表

        Args:
            market: 市场类型 ('A'=A股, 'HK'=港股)

        Returns:
            股票列表 DataFrame
        """
        try:
            if market == 'A':
                df = self.pro.stock_basic(exchange='', list_status='L')
            elif market == 'HK':
                df = self.pro.stock_basic(exchange='', list_status='L', ts_code='HK')
            else:
                logger.warning(f"Unsupported market: {market}")
                return pd.DataFrame()

            if df is not None and not df.empty:
                logger.info(f"Tushare: Fetched {len(df)} stocks from {market} market")
                return df
            else:
                logger.warning(f"Tushare: No stock list for {market} market")
                return pd.DataFrame()

        except Exception as e:
            logger.error(f"Tushare: Failed to get stock list: {e}")
            return pd.DataFrame()

    def get_index_list(self) -> pd.DataFrame:
        """获取指数列表"""
        try:
            df = self.pro.index_basic(market='')
            if df is not None and not df.empty:
                logger.info(f"Tushare: Fetched {len(df)} indices")
                return df
            else:
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Tushare: Failed to get index list: {e}")
            return pd.DataFrame()

    def get_fund_list(self) -> pd.DataFrame:
        """获取基金列表"""
        try:
            df = self.pro.fund_basic(market='')
            if df is not None and not df.empty:
                logger.info(f"Tushare: Fetched {len(df)} funds")
                return df
            else:
                return pd.DataFrame()
        except Exception as e:
            logger.error(f"Tushare: Failed to get fund list: {e}")
            return pd.DataFrame()
