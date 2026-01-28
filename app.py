from flask import Flask, render_template, jsonify
import json
import os
from datetime import datetime
import traceback

app = Flask(__name__)

# 数据路径
DATA_DIR = os.path.join(os.path.dirname(__file__), 'data')
PROCESSED_DIR = os.path.join(DATA_DIR, 'processed')


# 首页路由
@app.route('/')
def index():
    return render_template('index.html')


# 基础数据API接口
@app.route('/api/<dataset>')
def get_data(dataset):
    valid_datasets = ['year_counts', 'month_counts', 'hour_counts', 'city_counts', 'type_counts', 'apriori_results',
                      'processed_data', 'year_month_counts']
    if dataset not in valid_datasets:
        return jsonify({"error": "Invalid dataset"}), 404

    try:
        filepath = os.path.join(PROCESSED_DIR, f'{dataset}.json')
        print(f"读取文件: {filepath}")
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return jsonify(data)
    except FileNotFoundError:
        print(f"文件不存在: {filepath}")
        return jsonify({"error": "Dataset not found"}), 404
    except Exception as e:
        print(f"读取文件错误: {str(e)}")
        return jsonify({"error": str(e)}), 500


# 获取城市列表
@app.route('/api/cities')
def get_cities():
    try:
        filepath = os.path.join(PROCESSED_DIR, 'city_counts.json')
        with open(filepath, 'r', encoding='utf-8') as f:
            cities = json.load(f)
        city_names = [city['city'] for city in cities]
        return jsonify(city_names)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 获取统计数据
@app.route('/api/stats')
def get_stats():
    try:
        # 读取各统计文件
        stats = {}

        # 年份统计
        with open(os.path.join(PROCESSED_DIR, 'year_counts.json'), 'r', encoding='utf-8') as f:
            year_data = json.load(f)
            stats['total_cases'] = sum(item['count'] for item in year_data)
            years = [item['year'] for item in year_data]
            if years:
                stats['time_range'] = f"{min(years)}-{max(years)}"

        # 城市统计
        with open(os.path.join(PROCESSED_DIR, 'city_counts.json'), 'r', encoding='utf-8') as f:
            city_data = json.load(f)
            stats['city_count'] = len(city_data)

        # 类型统计
        with open(os.path.join(PROCESSED_DIR, 'type_counts.json'), 'r', encoding='utf-8') as f:
            type_data = json.load(f)
            stats['type_count'] = len(type_data)

        return jsonify(stats)
    except Exception as e:
        return jsonify({"error": str(e)}), 500


# 按州市和时间范围过滤数据的API端点 - 主要接口
@app.route('/api/filter/<dataset>/<city>/<start_time>/<end_time>')
def get_filtered_data_with_time(dataset, city, start_time, end_time):
    """
    综合过滤：按州市和时间范围
    city: 州市名称或'all'
    start_time: 开始时间，格式 YYYY-MM 或 'all'
    end_time: 结束时间，格式 YYYY-MM 或 'all'
    """
    try:
        print(f"\n=== API请求 ===")
        print(f"数据集: {dataset}")
        print(f"城市: {city}")
        print(f"开始时间: {start_time}")
        print(f"结束时间: {end_time}")

        # 读取完整数据
        filepath = os.path.join(PROCESSED_DIR, 'processed_data.json')
        with open(filepath, 'r', encoding='utf-8') as f:
            full_data = json.load(f)

        print(f"总数据量: {len(full_data)}")

        # 先按州市过滤
        if city == 'all':
            filtered_data = full_data
            print(f"使用全部城市数据")
        else:
            # 处理城市名称映射
            city_mapping = {
                '迪庆州': '迪庆藏族自治州',
                '楚雄州': '楚雄彝族自治州',
                '红河州': '红河哈尼族彝族自治州',
                '文山州': '文山壮族苗族自治州',
                '西双版纳州': '西双版纳傣族自治州',
                '大理州': '大理白族自治州',
                '德宏州': '德宏傣族景颇族自治州',
                '怒江州': '怒江傈僳族自治州'
            }

            actual_city = city_mapping.get(city, city)
            print(f"映射城市名称: '{city}' -> '{actual_city}'")

            filtered_data = [d for d in full_data if d.get('city') == actual_city]
            print(f"州市过滤后数据量: {len(filtered_data)}")

        # 再按时间范围过滤（如果指定了时间范围）
        if start_time != 'all' and end_time != 'all':
            try:
                time_filtered_data = []
                for item in filtered_data:
                    # 尝试从多个字段获取时间
                    time_value = None

                    # 优先使用标准time字段
                    if 'time' in item and item['time']:
                        time_value = item['time']
                    # 其次使用year和month组合
                    elif 'year' in item and 'month' in item:
                        try:
                            year = int(item['year'])
                            month = int(item['month'])
                            if 1 <= month <= 12:
                                time_value = f"{year:04d}-{month:02d}-01"
                        except:
                            pass

                    if time_value:
                        try:
                            item_time = datetime.strptime(time_value, "%Y-%m-%d")
                            start_date = datetime.strptime(start_time + "-01", "%Y-%m-%d")
                            end_date = datetime.strptime(end_time + "-01", "%Y-%m-%d")

                            # 如果end_time的月份需要包含整个月
                            if end_date.month == 12:
                                next_year = end_date.year + 1
                                end_date = datetime(next_year, 1, 1)
                            else:
                                end_date = datetime(end_date.year, end_date.month + 1, 1)

                            if start_date <= item_time < end_date:
                                time_filtered_data.append(item)
                        except ValueError as ve:
                            continue
                        except Exception as e:
                            print(f"时间处理错误: {str(e)}")
                            continue

                filtered_data = time_filtered_data
                print(f"时间过滤后数据量: {len(filtered_data)}")

            except Exception as e:
                print(f"时间解析错误: {str(e)}")
                return jsonify({"error": f"时间解析失败: {str(e)}"}), 400

        # 生成统计结果
        result = generate_dataset_statistics(dataset, filtered_data, city, start_time, end_time)
        print(f"返回数据量: {len(result.get_json()) if hasattr(result, 'get_json') else 'N/A'}")
        print("=== API处理完成 ===\n")

        return result

    except FileNotFoundError:
        print(f"数据文件不存在")
        return jsonify({"error": "数据文件不存在"}), 404
    except Exception as e:
        print(f"服务器错误: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": f"服务器错误: {str(e)}"}), 500


# 原始的州市过滤接口（保持向后兼容）
@app.route('/api/filter/<dataset>/<city>')
def get_filtered_data(dataset, city):
    # 调用带时间筛选的接口，时间参数设为'all'
    return get_filtered_data_with_time(dataset, city, 'all', 'all')


# 生成数据统计的辅助函数
def generate_dataset_statistics(dataset, filtered_data, city='all', start_time='all', end_time='all'):
    try:
        print(f"生成统计: {dataset}, 数据量: {len(filtered_data)}")

        if dataset == 'year_counts':
            # 统计年份分布
            year_counts = {}
            for item in filtered_data:
                year = item.get('year')
                if year:
                    try:
                        year = int(year)
                        year_counts[year] = year_counts.get(year, 0) + 1
                    except (ValueError, TypeError):
                        continue

            # 如果没有数据，返回空数组
            if not year_counts:
                print("年份数据为空")
                return jsonify([])

            # 按年份排序
            sorted_years = sorted(year_counts.items(), key=lambda x: x[0])
            result = [{'year': year, 'count': count} for year, count in sorted_years]
            print(f"年份统计结果: {len(result)} 条记录")
            return jsonify(result)

        elif dataset == 'month_counts':
            # 统计月份分布 (1-12月)
            month_counts = [0] * 12
            month_names = ['1月', '2月', '3月', '4月', '5月', '6月',
                           '7月', '8月', '9月', '10月', '11月', '12月']

            for item in filtered_data:
                # 优先从 month 字段获取
                if 'month' in item and item['month'] is not None:
                    try:
                        month = int(item['month']) - 1
                        if 0 <= month < 12:
                            month_counts[month] += 1
                        continue
                    except (ValueError, TypeError):
                        pass

                # 如果 month 字段无效，尝试从 time 字段解析
                if 'time' in item and item['time']:
                    try:
                        item_time = datetime.strptime(item['time'], "%Y-%m-%d")
                        month = item_time.month - 1
                        month_counts[month] += 1
                        continue
                    except ValueError:
                        continue

            # 确保返回完整12个月的数据
            result = []
            for i, count in enumerate(month_counts):
                result.append({
                    'month': month_names[i],
                    'month_num': i + 1,
                    'count': count
                })
            print(f"月份统计结果: {len(result)} 条记录")
            return jsonify(result)

        elif dataset == 'hour_counts':
            # 统计小时分布
            hour_counts = [0] * 24
            for item in filtered_data:
                hour = item.get('hour')
                if hour is not None:
                    try:
                        hour = int(hour)
                        if 0 <= hour < 24:
                            hour_counts[hour] += 1
                    except (ValueError, TypeError):
                        continue

            result = [{'hour': hour, 'count': count} for hour, count in enumerate(hour_counts)]
            print(f"小时统计结果: {len(result)} 条记录")
            return jsonify(result)

        elif dataset == 'type_counts':
            # 统计犯罪类型分布
            type_counts = {}
            for item in filtered_data:
                case_type = item.get('case_type')
                if case_type:
                    type_counts[case_type] = type_counts.get(case_type, 0) + 1

            # 如果没有数据，返回空数组
            if not type_counts:
                print("类型数据为空")
                return jsonify([])

            result = [{'type': case_type, 'count': count} for case_type, count in type_counts.items()]
            print(f"类型统计结果: {len(result)} 条记录")
            return jsonify(result)

        elif dataset == 'year_month_counts':
            # 统计年月组合分布（用于热力图）
            year_month_counts = {}
            for item in filtered_data:
                # 优先从 time 字段提取
                if 'time' in item and item['time']:
                    try:
                        item_time = datetime.strptime(item['time'], "%Y-%m-%d")
                        year_month = f"{item_time.year}-{item_time.month:02d}"
                        year_month_counts[year_month] = year_month_counts.get(year_month, 0) + 1
                        continue
                    except ValueError:
                        pass

                # 如果没有 time 字段，尝试从 year 和 month 字段组合
                if 'year' in item and 'month' in item:
                    try:
                        year = int(item['year'])
                        month = int(item['month'])
                        if 1 <= month <= 12:
                            year_month = f"{year}-{month:02d}"
                            year_month_counts[year_month] = year_month_counts.get(year_month, 0) + 1
                    except (ValueError, TypeError):
                        continue

            # 如果没有数据，返回空数组
            if not year_month_counts:
                print("年月组合数据为空")
                return jsonify([])

            # 格式化为前端需要的格式
            result = []
            for year_month, count in year_month_counts.items():
                try:
                    year, month = map(int, year_month.split('-'))
                    result.append({
                        'year': year,
                        'month': month,
                        'count': count
                    })
                except:
                    continue

            # 按年份和月份排序
            result.sort(key=lambda x: (x['year'], x['month']))
            print(f"年月组合统计结果: {len(result)} 条记录")
            return jsonify(result)

        else:
            return jsonify({"error": "Invalid dataset"}), 404

    except Exception as e:
        print(f"生成统计错误: {str(e)}")
        print(traceback.format_exc())
        return jsonify({"error": f"生成统计失败: {str(e)}"}), 500


if __name__ == '__main__':
    app.run(debug=True, port=5000, host='127.0.0.1')