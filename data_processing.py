import pandas as pd
import re
import json
from pathlib import Path
from datetime import datetime
import logging
import numpy as np
from apriori import Apriori

# 配置日志记录
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('data_processing.log'),
        logging.StreamHandler()
    ]
)


def extract_time_component(time_str, component='hour'):
    """
    多功能时间提取函数，支持年/月/日/小时提取
    component: 'year'|'month'|'day'|'hour'|'minute'
    """
    if pd.isna(time_str) or not time_str:
        return None

    # 尝试解析标准时间格式
    try:
        dt = pd.to_datetime(time_str)
        return getattr(dt, component)
    except (ValueError, TypeError):
        pass

    # 处理中文文本格式
    if isinstance(time_str, str):
        # 格式1: "2013年8月12日22时许"
        pattern1 = r'(\d{4})年(\d{1,2})月(\d{1,2})日(\d{1,2})[点时]许'
        # 格式2: "2014年1月的一天"
        pattern2 = r'(\d{4})年(\d{1,2})月'
        # 格式3: "2015-08-07 00:00:00"
        pattern3 = r'(\d{4})-(\d{2})-(\d{2}) (\d{2}):(\d{2}):(\d{2})'

        for pattern in [pattern1, pattern2, pattern3]:
            match = re.search(pattern, time_str)
            if match:
                groups = match.groups()
                if component == 'year' and len(groups) >= 1:
                    return int(groups[0])
                elif component == 'month' and len(groups) >= 2:
                    return int(groups[1])
                elif component == 'day' and len(groups) >= 3:
                    return int(groups[2])
                elif component == 'hour' and len(groups) >= 4:
                    return int(groups[3])
                elif component == 'minute' and len(groups) >= 5:
                    return int(groups[4])

    # 处理数字时间戳
    try:
        dt = datetime.fromtimestamp(float(time_str))
        return getattr(dt, component)
    except:
        return None


def generate_date_column(df):
    """
    生成标准日期格式的列，用于时间筛选
    """
    df['time'] = None

    for idx, row in df.iterrows():
        year = row.get('year')
        month = row.get('month')
        day = 1  # 如果没有具体日期，默认设为1号

        if pd.notna(year) and pd.notna(month):
            try:
                # 确保年份和月份是整数
                year_int = int(year)
                month_int = int(month)

                # 验证月份范围
                if 1 <= month_int <= 12:
                    # 创建标准日期格式
                    df.at[idx, 'time'] = f"{year_int:04d}-{month_int:02d}-{day:02d}"
            except:
                df.at[idx, 'time'] = None

    return df


def generate_year_month_statistics(df):
    """
    生成年月组合统计数据（用于热力图）
    """
    logging.info("正在生成年月组合统计数据...")

    # 过滤有年份和月份的数据
    year_month_data = df.dropna(subset=['year', 'month'])

    if year_month_data.empty:
        logging.warning("没有找到有效的年份和月份数据")
        return []

    # 确保年份和月份都是整数
    year_month_data = year_month_data.copy()
    try:
        year_month_data['year'] = year_month_data['year'].astype(int)
        year_month_data['month'] = year_month_data['month'].astype(int)
    except:
        logging.warning("年份或月份数据转换失败")
        return []

    # 过滤掉不合理的年月
    year_month_data = year_month_data[
        (year_month_data['year'] >= 1990) &
        (year_month_data['year'] <= 2025) &
        (year_month_data['month'] >= 1) &
        (year_month_data['month'] <= 12)
        ]

    if year_month_data.empty:
        logging.warning("过滤后没有有效的年月数据")
        return []

    # 统计每个年月组合的案件数量
    try:
        year_month_counts = year_month_data.groupby(['year', 'month']) \
            .size() \
            .reset_index(name='count')
    except Exception as e:
        logging.error(f"统计年月组合失败: {e}")
        return []

    # 转换为前端需要的格式
    result = []
    if not year_month_counts.empty:
        for _, row in year_month_counts.iterrows():
            try:
                result.append({
                    'year': int(row['year']),
                    'month': int(row['month']),
                    'count': int(row['count'])
                })
            except Exception as e:
                logging.warning(f"转换年月数据失败: {e}")
                continue

    logging.info(f"生成了 {len(result)} 条年月组合数据")
    return result


def process_data():
    try:
        # 设置路径
        base_dir = Path(__file__).parent
        data_dir = base_dir / 'data'
        processed_dir = data_dir / 'processed'
        input_file = data_dir / 'Yunnan_crime——.json'

        # 创建输出目录
        processed_dir.mkdir(parents=True, exist_ok=True)

        # 检查输入文件
        if not input_file.exists():
            raise FileNotFoundError(f"输入文件不存在: {input_file}")

        logging.info(f"开始处理文件: {input_file}")

        # 读取数据
        with open(input_file, 'r', encoding='utf-8') as f:
            data = json.load(f)

        df = pd.json_normalize(data) if isinstance(data, list) else pd.DataFrame.from_dict(data, orient='index').T

        # 数据质量检查
        logging.info(f"\n原始数据样例:\n{df[['incident_time', 'formatted_datetime']].head()}")
        logging.info(f"\n字段类型:\n{df.dtypes}")

        # 1. 时间字段处理
        logging.info("\n正在处理时间字段...")

        # 提取年份（从incident_time）并过滤掉不合理的年份
        df['year'] = df['incident_time'].apply(lambda x: extract_time_component(x, 'year'))
        # 过滤掉不合理的年份（只保留1990-2025年的数据）
        df['year'] = df['year'].apply(lambda x: x if x and 1990 <= x <= 2025 else None)

        # 2. 犯罪类型规范化处理
        logging.info("\n正在处理犯罪类型...")

        # 犯罪类型规范化映射
        def normalize_case_type(case_type):
            if pd.isna(case_type) or not case_type:
                return None

            # 转换为小写方便匹配
            case_type = str(case_type).lower()

            # 基础罪名规范化
            if '盗窃' in case_type and '抢劫' not in case_type and '抢夺' not in case_type:
                return '盗窃罪'
            elif '抢劫' in case_type:
                return '抢劫罪'
            elif '抢夺' in case_type:
                return '抢夺罪'
            elif '故意伤害' in case_type:
                return '故意伤害罪'
            elif '毒品' in case_type or '贩毒' in case_type:
                if '运输' in case_type:
                    return '运输毒品罪'
                elif '贩卖' in case_type:
                    return '贩卖毒品罪'
                else:
                    return '非法持有毒品罪'
            elif '危险驾驶' in case_type:
                return '危险驾驶罪'
            elif '寻衅滋事' in case_type:
                return '寻衅滋事罪'
            elif '故意杀人' in case_type:
                return '故意杀人罪'
            elif '交通肇事' in case_type:
                return '交通肇事罪'
            elif '诈骗' in case_type:
                return '诈骗罪'
            elif '敲诈勒索' in case_type:
                return '敲诈勒索罪'
            elif '开设赌场' in case_type:
                return '开设赌场罪'
            elif '故意毁坏财物' in case_type:
                return '故意毁坏财物罪'
            elif '职务侵占' in case_type:
                return '职务侵占罪'
            elif '强奸' in case_type:
                return '强奸罪'
            elif '非法持有枪支' in case_type:
                return '非法持有枪支罪'
            elif '合同诈骗' in case_type:
                return '合同诈骗罪'
            # 过滤掉通用标签和文书类型
            elif any(keyword in case_type for keyword in ['刑事', '民事', '判决书', '判决', '附带', '一审', '纠纷']):
                return None
            # 保留其他未匹配的类型
            else:
                return str(case_type)

        # 应用犯罪类型规范化
        df['case_type'] = df['case_type'].apply(normalize_case_type)
        # 过滤掉None值
        df = df[df['case_type'].notna()]

        # 提取月份（从incident_time）
        df['month'] = df['incident_time'].apply(lambda x: extract_time_component(x, 'month'))
        # 确保月份在1-12范围内
        df['month'] = df['month'].apply(lambda x: x if x and 1 <= x <= 12 else None)

        # 提取小时（优先从formatted_datetime，失败则从incident_time尝试）
        df['hour'] = df['formatted_datetime'].apply(lambda x: extract_time_component(x, 'hour'))
        if df['hour'].isna().any():
            logging.warning("formatted_datetime中存在缺失小时，尝试从incident_time补充...")
            df['hour'] = df.apply(
                lambda row: extract_time_component(row['incident_time'], 'hour')
                if pd.isna(row['hour']) else row['hour'],
                axis=1
            )

        # 生成标准日期格式列（用于时间筛选）
        df = generate_date_column(df)

        # 验证时间提取结果
        time_stats = pd.DataFrame({
            '字段': ['year', 'month', 'hour', 'time'],
            '有效值比例': [
                df['year'].notna().mean(),
                df['month'].notna().mean(),
                df['hour'].notna().mean(),
                df['time'].notna().mean()
            ]
        })
        logging.info(f"\n时间字段提取效果:\n{time_stats}")

        # 2. 生成统计数据
        logging.info("\n正在生成统计数据...")

        # 年份统计
        year_counts = df['year'].value_counts() \
            .sort_index() \
            .reset_index()
        year_counts.columns = ['year', 'count']
        year_counts.to_json(processed_dir / 'year_counts.json', orient='records', force_ascii=False)

        # 月份统计 - 创建完整的12个月数据
        month_names = ['1月', '2月', '3月', '4月', '5月', '6月',
                       '7月', '8月', '9月', '10月', '11月', '12月']

        # 统计实际月份数据
        valid_months = df['month'].dropna().astype(int)
        month_counts_raw = valid_months.value_counts().to_dict()

        # 创建完整的月份数据
        complete_month_data = []
        for i in range(12):
            month_num = i + 1
            month_name = month_names[i]
            count = month_counts_raw.get(month_num, 0)

            complete_month_data.append({
                'month': month_name,
                'month_num': month_num,
                'count': int(count)
            })

        # 保存月份统计数据
        month_counts_file = processed_dir / 'month_counts.json'
        with open(month_counts_file, 'w', encoding='utf-8') as f:
            json.dump(complete_month_data, f, ensure_ascii=False, indent=2)

        # 小时统计（确保0-23点完整）
        hour_counts = df['hour'].dropna().astype(int).value_counts() \
            .reindex(range(24), fill_value=0) \
            .reset_index()
        hour_counts.columns = ['hour', 'count']
        hour_counts.to_json(processed_dir / 'hour_counts.json', orient='records', force_ascii=False)

        # 城市统计 - 去重和清洗
        # 先按city分组，计算数量
        city_counts = df.groupby(['city']).size().reset_index(name='count')
        # 获取每个城市的经纬度
        city_coords = df.groupby(['city']).agg({
            'latitude': 'first',
            'longitude': 'first'
        }).reset_index()
        # 合并数量和经纬度
        city_counts = city_counts.merge(city_coords, on='city', how='left')
        # 过滤掉无效的经纬度
        city_counts = city_counts.dropna(subset=['latitude', 'longitude'])
        # 移除重复的城市记录
        city_counts = city_counts.drop_duplicates(subset=['city'])
        city_counts.to_json(processed_dir / 'city_counts.json', orient='records', force_ascii=False)

        # 犯罪类型统计
        type_counts = df['case_type'].value_counts() \
            .reset_index()
        type_counts.columns = ['type', 'count']
        type_counts.to_json(processed_dir / 'type_counts.json', orient='records', force_ascii=False)

        # 3. 生成年月组合统计数据（用于热力图）
        year_month_data = generate_year_month_statistics(df)
        year_month_file = processed_dir / 'year_month_counts.json'
        with open(year_month_file, 'w', encoding='utf-8') as f:
            json.dump(year_month_data, f, ensure_ascii=False, indent=2)
        logging.info(f"热力图数据已保存: {len(year_month_data)} 条记录")

        # 4. 保存处理后的完整数据
        processed_data = df.copy()
        # 移除不需要的字段
        redundant_columns = ['case_number', 'court_name', 'defendant', 'victim', 'incident_province',
                             'incident_county', 'details', 'judgment']
        processed_data = processed_data.drop(
            columns=[col for col in redundant_columns if col in processed_data.columns])
        # 移除重复行
        processed_data = processed_data.drop_duplicates()
        processed_data_path = processed_dir / 'processed_data.json'
        processed_data.to_json(processed_data_path, orient='records', force_ascii=False)
        logging.info(f"处理后的数据已保存，共 {len(processed_data)} 条记录")

        # 5. 生成事务数据集并运行Apriori算法
        logging.info("\n正在生成事务数据集并运行Apriori算法...")

        # 定义节假日月份（包含法定节假日的月份）
        holiday_months = [1, 2, 4, 5, 6, 9, 10]  # 1月(元旦), 2月(春节), 4月(清明), 5月(劳动), 6月(端午), 9月(中秋), 10月(国庆)
        
        # 定义旅游旺季月份（云南旅游旺季）
        peak_season_months = [3, 4, 5, 9, 10, 11]  # 春季和秋季是云南旅游旺季
        
        # 定义失业率水平（根据年份）
        def get_unemployment_level(year):
            if year < 2010:
                return "失业率:低"
            elif 2010 <= year < 2015:
                return "失业率:中"
            elif 2015 <= year < 2020:
                return "失业率:中高"
            else:
                return "失业率:高"
        
        # 准备事务数据：每条记录包含犯罪类型、城市、时间时段等信息
        transactions = []
        for _, row in df.iterrows():
            transaction = []

            # 添加犯罪类型
            if pd.notna(row['case_type']) and row['case_type']:
                transaction.append(f"类型:{row['case_type']}")

            # 添加城市
            if pd.notna(row['city']) and row['city']:
                transaction.append(f"城市:{row['city']}")

            # 添加地区（市级）
            if pd.notna(row['incident_city']) and row['incident_city']:
                transaction.append(f"地区:{row['incident_city']}")

            # 添加时间时段（早上、下午、晚上、深夜）
            if pd.notna(row['hour']):
                hour = int(row['hour'])
                if 6 <= hour < 12:
                    transaction.append("时段:早上")
                elif 12 <= hour < 18:
                    transaction.append("时段:下午")
                elif 18 <= hour < 24:
                    transaction.append("时段:晚上")
                else:
                    transaction.append("时段:深夜")

            # 添加月份（按季节划分）
            if pd.notna(row['month']):
                month = int(row['month'])
                if month in [3, 4, 5]:
                    transaction.append("季节:春季")
                elif month in [6, 7, 8]:
                    transaction.append("季节:夏季")
                elif month in [9, 10, 11]:
                    transaction.append("季节:秋季")
                else:
                    transaction.append("季节:冬季")
                
                # 添加节假日信息
                if month in holiday_months:
                    transaction.append("节假日:是")
                else:
                    transaction.append("节假日:否")
                
                # 添加旅游旺季信息
                if month in peak_season_months:
                    transaction.append("旅游旺季:是")
                else:
                    transaction.append("旅游旺季:否")
            
            # 添加失业率信息
            if pd.notna(row['year']):
                year = int(row['year'])
                transaction.append(get_unemployment_level(year))

            # 只保留有意义的事务（至少包含2个不同类型的项）
            if len(transaction) >= 2:
                transactions.append(transaction)

        # 运行Apriori算法，调整参数生成更有价值的规则
        apriori = Apriori(min_support=0.02, min_confidence=0.5)
        frequent_itemsets, rules = apriori.fit(transactions)

        # 保存关联规则结果
        apriori.save_results(processed_dir)
        logging.info(f"生成了 {len(rules)} 条关联规则")

        # 保存事务数据用于调试
        transactions_path = processed_dir / 'transactions.json'
        with open(transactions_path, 'w', encoding='utf-8') as f:
            json.dump(transactions, f, ensure_ascii=False, indent=2)
        logging.info(f"事务数据已保存到: {transactions_path.name}")

        # 6. 打印统计摘要
        logging.info("\n" + "=" * 50)
        logging.info("数据处理完成！生成文件:")
        logging.info("=" * 50)

        for f in processed_dir.glob('*.json'):
            if f.name in ['year_counts.json', 'month_counts.json', 'hour_counts.json',
                          'type_counts.json', 'year_month_counts.json']:
                with open(f, 'r', encoding='utf-8') as json_file:
                    data = json.load(json_file)
                    logging.info(f"- {f.name}: {len(data)} 条记录 ({f.stat().st_size / 1024:.1f} KB)")
            else:
                logging.info(f"- {f.name} ({f.stat().st_size / 1024:.1f} KB)")

        # 数据质量报告
        logging.info("\n数据质量报告:")
        logging.info(f"总记录数: {len(df)}")
        logging.info(f"有效年份数据: {df['year'].notna().sum()} ({df['year'].notna().mean() * 100:.1f}%)")
        logging.info(f"有效月份数据: {df['month'].notna().sum()} ({df['month'].notna().mean() * 100:.1f}%)")
        logging.info(f"有效时间数据: {df['time'].notna().sum()} ({df['time'].notna().mean() * 100:.1f}%)")
        logging.info(f"有效小时数据: {df['hour'].notna().sum()} ({df['hour'].notna().mean() * 100:.1f}%)")
        logging.info(f"犯罪类型种类: {df['case_type'].nunique()}")

    except Exception as e:
        logging.error(f"处理失败: {str(e)}", exc_info=True)
        raise


if __name__ == '__main__':
    try:
        process_data()
    except Exception as e:
        logging.critical(f"程序终止: {str(e)}")
        exit(1)