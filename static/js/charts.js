// charts.js - 完整修复版

// 全局变量
let currentCity = 'all';
let currentStartTime = '';
let currentEndTime = '';
let allCharts = {};

// 科技感主题配色
const techTheme = {
    color: ['#00d4ff', '#0099ff', '#3366ff', '#6633ff', '#9933ff'],
    backgroundColor: 'transparent',
    textStyle: {
        color: '#ffffff'
    },
    title: {
        show: false, // 隐藏内部标题，使用外部的蓝色标题
        textStyle: {
            color: '#00d4ff',
            fontSize: 16,
            fontWeight: 'bold'
        }
    },
    tooltip: {
        backgroundColor: 'rgba(15, 12, 41, 0.8)',
        borderColor: 'rgba(0, 212, 255, 0.3)',
        textStyle: {
            color: '#ffffff'
        },
        axisPointer: {
            lineStyle: {
                color: '#00d4ff'
            }
        }
    },
    grid: {
        left: '3%',
        right: '4%',
        bottom: '3%',
        containLabel: true
    },
    xAxis: {
        axisLine: {
            lineStyle: {
                color: 'rgba(0, 212, 255, 0.5)'
            }
        },
        axisLabel: {
            color: 'rgba(255, 255, 255, 0.8)'
        },
        axisTick: {
            lineStyle: {
                color: 'rgba(0, 212, 255, 0.5)'
            }
        },
        splitLine: {
            lineStyle: {
                color: 'rgba(0, 212, 255, 0.1)'
            }
        }
    },
    yAxis: {
        axisLine: {
            lineStyle: {
                color: 'rgba(0, 212, 255, 0.5)'
            }
        },
        axisLabel: {
            color: 'rgba(255, 255, 255, 0.8)'
        },
        axisTick: {
            lineStyle: {
                color: 'rgba(0, 212, 255, 0.5)'
            }
        },
        splitLine: {
            lineStyle: {
                color: 'rgba(0, 212, 255, 0.1)'
            }
        }
    },
    legend: {
        textStyle: {
            color: 'rgba(255, 255, 255, 0.8)'
        }
    }
};

// 城市名称映射（前端显示名称 -> 后端数据名称）
const cityMapping = {
    '迪庆州': '迪庆藏族自治州',
    '楚雄州': '楚雄彝族自治州',
    '红河州': '红河哈尼族彝族自治州',
    '文山州': '文山壮族苗族自治州',
    '西双版纳州': '西双版纳傣族自治州',
    '大理州': '大理白族自治州',
    '德宏州': '德宏傣族景颇族自治州',
    '怒江州': '怒江傈僳族自治州'
};

// 获取实际城市名称
function getActualCity(city) {
    return cityMapping[city] || city;
}

// 初始化所有图表
function initAllCharts() {
    initYearChart();
    initMonthChart();
    initHourChart();
    initTypeChart();
    initHeatmapChart();
    initAprioriChart();
}

// 初始化年份图表
function initYearChart() {
    const chartDom = document.getElementById('city-year-chart');
    if (chartDom) {
        allCharts.yearChart = echarts.init(chartDom);
    }
}

// 初始化月份图表
function initMonthChart() {
    const chartDom = document.getElementById('city-month-chart');
    if (chartDom) {
        allCharts.monthChart = echarts.init(chartDom);
    }
}

// 初始化小时图表
function initHourChart() {
    const chartDom = document.getElementById('city-hour-chart');
    if (chartDom) {
        allCharts.hourChart = echarts.init(chartDom);
    }
}

// 初始化类型图表
function initTypeChart() {
    const chartDom = document.getElementById('city-type-chart');
    if (chartDom) {
        allCharts.typeChart = echarts.init(chartDom);
    }
}

// 初始化热力图
function initHeatmapChart() {
    const chartDom = document.getElementById('heatmap-chart');
    if (chartDom) {
        allCharts.heatmapChart = echarts.init(chartDom);
    }
}

// 初始化关联规则图表
function initAprioriChart() {
    const chartDom = document.getElementById('apriori-chart');
    if (chartDom) {
        allCharts.aprioriChart = echarts.init(chartDom);
        // 关联规则不需要筛选，直接加载
        loadAprioriData();
    }
}

// 刷新所有图表（核心函数）
function refreshAllCharts() {
    const city = document.getElementById('city-select').value;
    const startTime = document.getElementById('start-time').value;
    const endTime = document.getElementById('end-time').value;

    console.log('🎯 刷新所有图表:', {
        city: city,
        startTime: startTime,
        endTime: endTime
    });

    // 更新统计信息
    updateStats(city, startTime, endTime);

    if (startTime && endTime) {
        // 验证时间格式
        const timeRegex = /^\d{4}-\d{2}$/;
        if (!timeRegex.test(startTime) || !timeRegex.test(endTime)) {
            console.error('时间格式错误');
            return;
        }
        loadDataWithTime(city, startTime, endTime);
    } else {
        loadAllData(city);
    }
}

// 加载所有数据（无时间筛选）
function loadAllData(city) {
    currentCity = city;
    currentStartTime = '';
    currentEndTime = '';

    console.log(`📊 加载 ${city === 'all' ? '全省' : city} 的所有数据`);

    // 清除时间输入框
    document.getElementById('start-time').value = '';
    document.getElementById('end-time').value = '';

    // 年份图表
    fetch(`/api/filter/year_counts/${city}`)
        .then(response => {
            if (!response.ok) throw new Error(`年份数据请求失败: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log('年份数据:', data);
            renderYearChart(data, city, '', '');
        })
        .catch(error => {
            console.error('加载年份数据失败:', error);
            renderYearChart([], city, '', '');
        });

    // 月份图表
    fetch(`/api/filter/month_counts/${city}`)
        .then(response => {
            if (!response.ok) throw new Error(`月份数据请求失败: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log('月份数据:', data);
            renderMonthChart(data, city, '', '');
        })
        .catch(error => {
            console.error('加载月份数据失败:', error);
            renderMonthChart([], city, '', '');
        });

    // 小时图表
    fetch(`/api/filter/hour_counts/${city}`)
        .then(response => {
            if (!response.ok) throw new Error(`小时数据请求失败: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log('小时数据:', data);
            renderHourChart(data, city, '', '');
        })
        .catch(error => {
            console.error('加载小时数据失败:', error);
            renderHourChart([], city, '', '');
        });

    // 类型图表
    fetch(`/api/filter/type_counts/${city}`)
        .then(response => {
            if (!response.ok) throw new Error(`类型数据请求失败: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log('类型数据:', data);
            renderTypeChart(data, city, '', '');
        })
        .catch(error => {
            console.error('加载类型数据失败:', error);
            renderTypeChart([], city, '', '');
        });

    // 热力图
    fetch(`/api/filter/year_month_counts/${city}`)
        .then(response => {
            if (!response.ok) throw new Error(`热力图数据请求失败: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log('热力图数据:', data);
            renderHeatmapChart(data, city, '', '');
        })
        .catch(error => {
            console.error('加载热力图数据失败:', error);
            renderHeatmapChart([], city, '', '');
        });

    // 关联规则（保持不变）
    loadAprioriData();
}

// 加载带时间筛选的数据
function loadDataWithTime(city, startTime, endTime) {
    currentCity = city;
    currentStartTime = startTime;
    currentEndTime = endTime;

    // 构建API参数
    const startParam = startTime || 'all';
    const endParam = endTime || 'all';

    console.log(`⏰ 加载带时间筛选的数据: city=${city}, start=${startParam}, end=${endParam}`);

    // 1. 年份图表
    fetch(`/api/filter/year_counts/${city}/${startParam}/${endParam}`)
        .then(response => {
            if (!response.ok) throw new Error(`年份数据请求失败: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log('年份数据:', data);
            renderYearChart(data, city, startTime, endTime);
        })
        .catch(error => {
            console.error('加载年份数据失败:', error);
            renderYearChart([], city, startTime, endTime);
        });

    // 2. 月份图表
    fetch(`/api/filter/month_counts/${city}/${startParam}/${endParam}`)
        .then(response => {
            if (!response.ok) throw new Error(`月份数据请求失败: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log('月份数据:', data);
            renderMonthChart(data, city, startTime, endTime);
        })
        .catch(error => {
            console.error('加载月份数据失败:', error);
            renderMonthChart([], city, startTime, endTime);
        });

    // 3. 小时图表
    fetch(`/api/filter/hour_counts/${city}/${startParam}/${endParam}`)
        .then(response => {
            if (!response.ok) throw new Error(`小时数据请求失败: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log('小时数据:', data);
            renderHourChart(data, city, startTime, endTime);
        })
        .catch(error => {
            console.error('加载小时数据失败:', error);
            renderHourChart([], city, startTime, endTime);
        });

    // 4. 类型图表
    fetch(`/api/filter/type_counts/${city}/${startParam}/${endParam}`)
        .then(response => {
            if (!response.ok) throw new Error(`类型数据请求失败: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log('类型数据:', data);
            renderTypeChart(data, city, startTime, endTime);
        })
        .catch(error => {
            console.error('加载类型数据失败:', error);
            renderTypeChart([], city, startTime, endTime);
        });

    // 5. 热力图
    fetch(`/api/filter/year_month_counts/${city}/${startParam}/${endParam}`)
        .then(response => {
            if (!response.ok) throw new Error(`热力图数据请求失败: ${response.status}`);
            return response.json();
        })
        .then(data => {
            console.log('热力图数据:', data);
            renderHeatmapChart(data, city, startTime, endTime);
        })
        .catch(error => {
            console.error('加载热力图数据失败:', error);
            renderHeatmapChart([], city, startTime, endTime);
        });

    // 关联规则数据保持不变
    loadAprioriData();
}

// 加载关联规则数据
function loadAprioriData() {
    fetch('/api/apriori_results')
        .then(response => response.json())
        .then(data => {
            renderAprioriChart(data);
        })
        .catch(error => console.error('加载关联规则数据失败:', error));
}

// 渲染年份图表
function renderYearChart(data, city, startTime, endTime) {
    if (!allCharts.yearChart) {
        initYearChart();
    }

    // 构建标题
    let titleText = `📈 年度趋势分析`;
    let subtext = '';

    if (city !== 'all') {
        titleText += ` (${city})`;
    } else {
        titleText += ` (全省)`;
    }

    if (startTime && endTime) {
        subtext = `时间范围: ${startTime} 至 ${endTime}`;
    } else {
        subtext = '全部时间';
    }

    // 检查数据
    if (!data || !Array.isArray(data) || data.length === 0) {
        console.log('年份数据为空，显示空图表');
        const option = {
            ...techTheme,
            title: {
                show: false, // 隐藏内部标题
                text: titleText,
                subtext: subtext,
                left: 'center',
                textStyle: {
                    color: '#00d4ff',
                    fontSize: 16,
                    fontWeight: 'bold'
                }
            },
            graphic: {
                type: 'text',
                left: 'center',
                top: 'middle',
                style: {
                    text: '暂无数据',
                    fill: '#ffffff',
                    fontSize: 14,
                    fontWeight: 'normal'
                }
            }
        };
        allCharts.yearChart.setOption(option);
        return;
    }

    // 处理数据
    const years = data.map(item => item.year);
    const counts = data.map(item => item.count);

    const option = {
        ...techTheme,
        title: {
            show: false, // 隐藏内部标题
            text: titleText,
            subtext: subtext,
            left: 'center',
            textStyle: {
                color: '#00d4ff',
                fontSize: 16,
                fontWeight: 'bold'
            }
        },
        tooltip: {
            ...techTheme.tooltip,
            formatter: function(params) {
                return `年份: ${params[0].axisValue}<br/>案件数量: ${params[0].data}`;
            }
        },
        xAxis: {
            ...techTheme.xAxis,
            type: 'category',
            data: years,
            axisLabel: {
                color: 'rgba(255, 255, 255, 0.8)'
            }
        },
        yAxis: techTheme.yAxis,
        series: [{
            name: '案件数量',
            type: 'line',
            data: counts,
            smooth: true,
            lineStyle: {
                width: 3,
                color: '#00d4ff',
                shadowColor: 'rgba(0, 212, 255, 0.5)',
                shadowBlur: 10
            },
            areaStyle: {
                color: {
                    type: 'linear',
                    x: 0,
                    y: 0,
                    x2: 0,
                    y2: 1,
                    colorStops: [{
                        offset: 0, color: 'rgba(0, 212, 255, 0.3)'
                    }, {
                        offset: 1, color: 'rgba(0, 212, 255, 0.05)'
                    }]
                }
            },
            itemStyle: {
                color: '#00d4ff',
                borderColor: '#ffffff',
                borderWidth: 2,
                shadowColor: 'rgba(0, 212, 255, 0.8)',
                shadowBlur: 10
            }
        }]
    };

    allCharts.yearChart.setOption(option);
}

// 渲染月份图表
function renderMonthChart(data, city, startTime, endTime) {
    if (!allCharts.monthChart) {
        initMonthChart();
    }

    // 构建标题
    let titleText = `📅 月度分布`;
    let subtext = '';

    if (city !== 'all') {
        titleText += ` (${city})`;
    } else {
        titleText += ` (全省)`;
    }

    if (startTime && endTime) {
        subtext = `时间范围: ${startTime} 至 ${endTime}`;
    } else {
        subtext = '全部时间';
    }

    // 月份名称
    const monthNames = ['1月', '2月', '3月', '4月', '5月', '6月',
                       '7月', '8月', '9月', '10月', '11月', '12月'];

    // 处理数据，确保12个月都有
    let completeData = [];
    if (Array.isArray(data) && data.length > 0) {
        // 创建月份名称到数据的映射
        const dataMap = {};
        data.forEach(item => {
            if (item.month && item.count !== undefined) {
                dataMap[item.month] = item.count;
            }
        });

        // 创建完整的12个月数据
        for (let i = 0; i < 12; i++) {
            const monthName = monthNames[i];
            const count = dataMap[monthName] || 0;
            completeData.push({
                month: monthName,
                count: count
            });
        }
    } else {
        // 如果数据无效，创建空的12个月数据
        for (let i = 0; i < 12; i++) {
            completeData.push({
                month: monthNames[i],
                count: 0
            });
        }
    }

    const months = completeData.map(item => item.month);
    const counts = completeData.map(item => item.count);

    const option = {
        ...techTheme,
        title: {
            show: false, // 隐藏内部标题
            text: titleText,
            subtext: subtext,
            left: 'center',
            textStyle: {
                color: '#00d4ff',
                fontSize: 16,
                fontWeight: 'bold'
            }
        },
        tooltip: {
            ...techTheme.tooltip,
            formatter: function(params) {
                return `月份: ${params[0].axisValue}<br/>案件数量: ${params[0].data}`;
            }
        },
        xAxis: {
            ...techTheme.xAxis,
            type: 'category',
            data: months,
            axisLabel: {
                color: 'rgba(255, 255, 255, 0.8)'
            }
        },
        yAxis: techTheme.yAxis,
        series: [{
            name: '案件数量',
            type: 'line',
            data: counts,
            smooth: true,
            lineStyle: {
                width: 3,
                color: '#0099ff',
                shadowColor: 'rgba(0, 153, 255, 0.5)',
                shadowBlur: 10
            },
            areaStyle: {
                color: {
                    type: 'linear',
                    x: 0,
                    y: 0,
                    x2: 0,
                    y2: 1,
                    colorStops: [{
                        offset: 0, color: 'rgba(0, 153, 255, 0.3)'
                    }, {
                        offset: 1, color: 'rgba(0, 153, 255, 0.05)'
                    }]
                }
            },
            itemStyle: {
                color: '#0099ff',
                borderColor: '#ffffff',
                borderWidth: 2,
                shadowColor: 'rgba(0, 153, 255, 0.8)',
                shadowBlur: 10
            }
        }]
    };

    allCharts.monthChart.setOption(option);
}

// 渲染小时图表
function renderHourChart(data, city, startTime, endTime) {
    if (!allCharts.hourChart) {
        initHourChart();
    }

    // 构建标题
    let titleText = `⏰ 时段分析`;
    let subtext = '';

    if (city !== 'all') {
        titleText += ` (${city})`;
    } else {
        titleText += ` (全省)`;
    }

    if (startTime && endTime) {
        subtext = `时间范围: ${startTime} 至 ${endTime}`;
    } else {
        subtext = '全部时间';
    }

    // 检查数据
    if (!data || !Array.isArray(data) || data.length === 0) {
        console.log('小时数据为空');
        const option = {
            ...techTheme,
            title: {
                show: false,
                text: titleText,
                subtext: subtext,
                left: 'center',
                textStyle: {
                    color: '#00d4ff',
                    fontSize: 16,
                    fontWeight: 'bold'
                }
            },
            graphic: {
                type: 'text',
                left: 'center',
                top: 'middle',
                style: {
                    text: '暂无数据',
                    fill: '#ffffff',
                    fontSize: 14
                }
            }
        };
        allCharts.hourChart.setOption(option);
        return;
    }

    // 处理数据，确保24小时都有
    let completeData = [];
    const hourLabels = [];

    for (let hour = 0; hour < 24; hour++) {
        hourLabels.push(`${hour}:00`);
        const hourData = data.find(d => d.hour === hour);
        completeData.push(hourData ? hourData.count : 0);
    }

    const option = {
        ...techTheme,
        title: {
            show: false,
            text: titleText,
            subtext: subtext,
            left: 'center',
            textStyle: {
                color: '#00d4ff',
                fontSize: 16,
                fontWeight: 'bold'
            }
        },
        tooltip: {
            ...techTheme.tooltip,
            formatter: function(params) {
                return `时间: ${params[0].axisValue}<br/>案件数量: ${params[0].data}`;
            }
        },
        xAxis: {
            ...techTheme.xAxis,
            type: 'category',
            data: hourLabels,
            axisLabel: {
                color: 'rgba(255, 255, 255, 0.8)'
            }
        },
        yAxis: techTheme.yAxis,
        series: [{
            name: '案件数量',
            type: 'bar',
            data: completeData,
            barWidth: '60%',
            itemStyle: {
                color: {
                    type: 'linear',
                    x: 0,
                    y: 0,
                    x2: 0,
                    y2: 1,
                    colorStops: [{
                        offset: 0, color: '#3366ff'
                    }, {
                        offset: 1, color: '#00d4ff'
                    }]
                },
                borderRadius: [4, 4, 0, 0],
                shadowColor: 'rgba(0, 153, 255, 0.5)',
                shadowBlur: 8
            }
        }]
    };

    allCharts.hourChart.setOption(option);
}

// 渲染类型图表
function renderTypeChart(data, city, startTime, endTime) {
    if (!allCharts.typeChart) {
        initTypeChart();
    }

    // 构建标题
    let titleText = `⚖️ 犯罪类型分布`;
    let subtext = '';

    if (city !== 'all') {
        titleText += ` (${city})`;
    } else {
        titleText += ` (全省)`;
    }

    if (startTime && endTime) {
        subtext = `时间范围: ${startTime} 至 ${endTime}`;
    } else {
        subtext = '全部时间';
    }

    // 检查数据
    if (!data || !Array.isArray(data) || data.length === 0) {
        console.log('类型数据为空');
        const option = {
            ...techTheme,
            title: {
                text: titleText,
                subtext: subtext,
                left: 'center',
                textStyle: {
                    color: '#00d4ff',
                    fontSize: 16,
                    fontWeight: 'bold'
                }
            },
            graphic: {
                type: 'text',
                left: 'center',
                top: 'middle',
                style: {
                    text: '暂无数据',
                    fill: '#ffffff',
                    fontSize: 14
                }
            }
        };
        allCharts.typeChart.setOption(option);
        return;
    }

    // 限制显示的类型数量
    const displayData = data.slice(0, 10);

    const option = {
        ...techTheme,
        title: {
            text: titleText,
            subtext: subtext,
            left: 'center',
            textStyle: {
                color: '#00d4ff',
                fontSize: 16,
                fontWeight: 'bold'
            }
        },
        tooltip: {
            ...techTheme.tooltip,
            formatter: '{b}: {c} 起 ({d}%)'
        },
        legend: {
            show: false
        },
        series: {
            name: '犯罪类型',
            type: 'pie',
            data: displayData.map(d => ({ name: d.type, value: d.count })),
            radius: ['35%', '70%'],
            center: ['50%', '50%'],
            avoidLabelOverlap: true,
            itemStyle: {
                borderRadius: 8,
                borderColor: 'rgba(15, 12, 41, 0.8)',
                borderWidth: 2,
                shadowColor: 'rgba(0, 212, 255, 0.3)',
                shadowBlur: 10
            },
            label: {
                show: true,
                position: 'inside',
                formatter: '{b}',
                fontSize: 10,
                color: '#ffffff',
                fontWeight: 'bold',
                textShadowBlur: 3,
                textShadowColor: 'rgba(0, 0, 0, 0.5)',
                overflow: 'truncate',
                width: 60
            },
            emphasis: {
                label: {
                    show: true,
                    fontSize: 12,
                    fontWeight: 'bold',
                    formatter: '{b}\n{c} 起\n{d}%'
                }
            },
            labelLine: {
                show: false
            }
        }
    };

    allCharts.typeChart.setOption(option);
}

// 渲染热力图
function renderHeatmapChart(data, city, startTime, endTime) {
    if (!allCharts.heatmapChart) {
        initHeatmapChart();
    }

    // 构建标题
    let titleText = `🔥 时空热力图`;
    let subtext = '';

    if (city !== 'all') {
        titleText += ` (${city})`;
    } else {
        titleText += ` (全省)`;
    }

    if (startTime && endTime) {
        subtext = `时间范围: ${startTime} 至 ${endTime}`;
    } else {
        subtext = '全部时间';
    }

    // 检查数据
    if (!data || !Array.isArray(data) || data.length === 0) {
        console.log('热力图数据为空');
        const option = {
            ...techTheme,
            title: {
                show: false,
                text: titleText,
                subtext: subtext,
                left: 'center',
                textStyle: {
                    color: '#00d4ff',
                    fontSize: 16,
                    fontWeight: 'bold'
                }
            },
            graphic: {
                type: 'text',
                left: 'center',
                top: 'middle',
                style: {
                    text: '暂无数据',
                    fill: '#ffffff',
                    fontSize: 14
                }
            }
        };
        allCharts.heatmapChart.setOption(option);
        return;
    }

    // 处理热力图数据
    const years = [...new Set(data.map(item => item.year))].sort((a, b) => a - b);
    const months = ['1月', '2月', '3月', '4月', '5月', '6月',
                   '7月', '8月', '9月', '10月', '11月', '12月'];

    const heatmapData = [];
    data.forEach(item => {
        const yearIndex = years.indexOf(item.year);
        if (yearIndex !== -1) {
            heatmapData.push([yearIndex, item.month - 1, item.count || 0]);
        }
    });

    const option = {
        ...techTheme,
        title: {
            show: false,
            text: titleText,
            subtext: subtext,
            left: 'center',
            textStyle: {
                color: '#00d4ff',
                fontSize: 16,
                fontWeight: 'bold'
            }
        },
        tooltip: {
            position: 'top',
            formatter: function(params) {
                const year = years[params.value[0]];
                const month = params.value[1] + 1;
                return `${year}年${month}月<br/>案件数量: ${params.value[2]}`;
            },
            backgroundColor: 'rgba(15, 12, 41, 0.9)',
            borderColor: '#00d4ff',
            textStyle: {
                color: '#ffffff'
            }
        },
        grid: {
            height: '70%',
            top: '15%'
        },
        xAxis: {
            type: 'category',
            data: years,
            splitArea: {
                show: true
            },
            axisLabel: {
                color: '#ffffff',
                fontSize: 12
            }
        },
        yAxis: {
            type: 'category',
            data: months,
            splitArea: {
                show: true
            },
            axisLabel: {
                color: '#ffffff',
                fontSize: 12
            }
        },
        visualMap: {
            min: 0,
            max: Math.max(...data.map(item => item.count)),
            calculable: true,
            orient: 'vertical',
            left: 'right',
            top: 'center',
            textStyle: {
                color: '#ffffff'
            },
            inRange: {
                color: ['#313695', '#4575b4', '#74add1', '#abd9e9', '#e0f3f8', '#ffffbf', '#fee090', '#fdae61', '#f46d43', '#d73027', '#a50026']
            }
        },
        series: [{
            name: '案件数量',
            type: 'heatmap',
            data: heatmapData,
            label: {
                show: false
            },
            emphasis: {
                itemStyle: {
                    shadowBlur: 10,
                    shadowColor: 'rgba(0, 0, 0, 0.5)'
                }
            }
        }]
    };

    allCharts.heatmapChart.setOption(option);
}

// 渲染关联规则图表
function renderAprioriChart(data) {
    if (!allCharts.aprioriChart) {
        initAprioriChart();
    }

    const rules = data.rules || [];
    
    // 扩展类型映射，包含新的因素类型
    const typeMap = {
        '类型': '类型',
        '城市': '城市',
        '地区': '地区',
        '时段': '时段',
        '季节': '季节',
        '节假日': '节假日',
        '旅游旺季': '旅游旺季',
        '失业率': '失业率'
    };
    
    // 简化项名称的函数
    function simplifyItem(item) {
        if (item.includes(':')) {
            const parts = item.split(':');
            const type = parts[0];
            const value = parts[1];
            return `${typeMap[type] || type}:${value}`;
        }
        return item;
    }
    
    // 过滤和处理规则，只保留犯罪类型作为结果的规则，且置信度较高
    const filteredRules = rules.filter(rule => {
        // 只保留后果是犯罪类型的规则
        const consequentIsType = rule.consequent.some(item => item.startsWith('类型:'));
        // 只保留前因不是犯罪类型的规则（因素→犯罪类型）
        const antecedentNotType = !rule.antecedent.some(item => item.startsWith('类型:'));
        // 只保留高置信度规则
        return consequentIsType && antecedentNotType && rule.confidence >= 0.3;
    });
    
    // 构建关系图数据
    const nodes = new Map();
    const links = [];
    
    filteredRules.forEach(rule => {
        // 处理前因（因素）
        rule.antecedent.forEach(antecedent => {
            const antName = simplifyItem(antecedent);
            if (!nodes.has(antName)) {
                nodes.set(antName, {
                    name: antName,
                    category: 0, // 因素节点
                    symbolSize: 30,
                    itemStyle: { color: '#00d4ff' }
                });
            }
        });
        
        // 处理后果（犯罪类型）
        rule.consequent.forEach(consequent => {
            const consName = simplifyItem(consequent);
            if (!nodes.has(consName)) {
                nodes.set(consName, {
                    name: consName,
                    category: 1, // 犯罪类型节点
                    symbolSize: 40,
                    itemStyle: { color: '#ff6b6b' }
                });
            }
        });
        
        // 处理边（关联关系）
        rule.antecedent.forEach(antecedent => {
            const antName = simplifyItem(antecedent);
            rule.consequent.forEach(consequent => {
                const consName = simplifyItem(consequent);
                links.push({
                    source: antName,
                    target: consName,
                    value: rule.confidence * 100, // 边的粗细表示置信度
                    confidence: rule.confidence * 100,
                    support: rule.support * 100,
                    lift: rule.lift
                });
            });
        });
    });
    
    // 如果没有规则，显示提示
    if (nodes.size === 0) {
        const option = {
            ...techTheme,
            title: {
                show: false,
                text: '🔗 关联规则分析',
                subtext: '因素与犯罪类型的关联关系',
                left: 'center',
                textStyle: {
                    color: '#00d4ff',
                    fontSize: 16,
                    fontWeight: 'bold'
                }
            },
            graphic: {
                type: 'text',
                left: 'center',
                top: 'middle',
                style: {
                    text: '暂无关联规则数据',
                    fill: '#ffffff',
                    fontSize: 14
                }
            }
        };
        allCharts.aprioriChart.setOption(option);
        return;
    }
    
    // 构建关系图配置
    const option = {
        ...techTheme,
        title: {
            show: false,
            text: '🔗 关联规则分析',
            subtext: '因素与犯罪类型的关联关系',
            left: 'center',
            textStyle: {
                color: '#00d4ff',
                fontSize: 16,
                fontWeight: 'bold'
            }
        },
        tooltip: {
            ...techTheme.tooltip,
            formatter: function(params) {
                if (params.dataType === 'edge') {
                    const edge = params.data;
                    return `${edge.source} → ${edge.target}<br/>
                           置信度: ${edge.confidence.toFixed(2)}%<br/>
                           支持度: ${edge.support.toFixed(2)}%<br/>
                           Lift值: ${edge.lift.toFixed(3)}`;
                } else {
                    return params.name;
                }
            }
        },
        legend: {
            data: ['因素', '犯罪类型'],
            textStyle: {
                color: 'rgba(255, 255, 255, 0.8)'
            },
            top: 10
        },
        animationDurationUpdate: 1500,
        animationEasingUpdate: 'quinticInOut',
        series: [{
            name: '关联规则',
            type: 'graph',
            layout: 'force',
            force: {
                repulsion: 1000,
                gravity: 0.1,
                edgeLength: 150,
                layoutAnimation: true
            },
            data: Array.from(nodes.values()),
            links: links,
            categories: [
                { name: '因素', itemStyle: { color: '#00d4ff' } },
                { name: '犯罪类型', itemStyle: { color: '#ff6b6b' } }
            ],
            roam: true, // 允许缩放和平移
            label: {
                show: true,
                position: 'right',
                formatter: function(params) {
                    // 简化显示，只显示值，不显示类型前缀
                    return params.name.replace(/^[^:]+:/, '');
                },
                fontSize: 10,
                color: '#ffffff',
                fontWeight: 'bold',
                backgroundColor: 'rgba(15, 12, 41, 0.8)',
                padding: [2, 6, 2, 6],
                borderRadius: 4
            },
            edgeLabel: {
                show: false
            },
            edgeSymbol: ['none', 'arrow'],
            edgeSymbolSize: 8,
            edgeStyle: {
                width: function(params) {
                    // 边的粗细根据置信度动态调整
                    return Math.max(1, params.data.value / 20);
                },
                color: '#6633ff',
                curveness: 0.2,
                opacity: 0.7
            },
            emphasis: {
                focus: 'adjacency',
                lineStyle: {
                    width: 5
                }
            }
        }]
    };
    
    allCharts.aprioriChart.setOption(option);
}

// 更新统计信息
function updateStats(city, startTime, endTime) {
    const startParam = startTime || 'all';
    const endParam = endTime || 'all';

    // 获取统计信息
    fetch(`/api/filter/year_counts/${city}/${startParam}/${endParam}`)
        .then(response => response.json())
        .then(data => {
            if (data && Array.isArray(data)) {
                const totalCases = data.reduce((sum, item) => sum + (item.count || 0), 0);
                document.getElementById('total-cases').textContent = totalCases.toLocaleString();

                if (data.length > 0) {
                    const years = data.map(item => item.year).filter(year => year);
                    if (years.length > 0) {
                        const minYear = Math.min(...years);
                        const maxYear = Math.max(...years);
                        document.getElementById('time-range').textContent = `${minYear}-${maxYear}`;
                    }
                }
            }
        })
        .catch(error => {
            console.error('更新统计信息失败:', error);
        });
}

// 窗口大小变化时重新调整图表大小
function resizeAllCharts() {
    Object.values(allCharts).forEach(chart => {
        if (chart && typeof chart.resize === 'function') {
            chart.resize();
        }
    });
}

// 全局函数，供HTML调用
function applyTimeFilter() {
    const city = document.getElementById('city-select').value;
    const startTime = document.getElementById('start-time').value;
    const endTime = document.getElementById('end-time').value;

    console.log('🔄 应用时间筛选:', {city, startTime, endTime});

    if (!startTime || !endTime) {
        alert('请选择开始时间和结束时间');
        return;
    }

    // 验证时间格式
    const timeRegex = /^\d{4}-\d{2}$/;
    if (!timeRegex.test(startTime)) {
        alert('开始时间格式错误，请使用 YYYY-MM 格式');
        return;
    }
    if (!timeRegex.test(endTime)) {
        alert('结束时间格式错误，请使用 YYYY-MM 格式');
        return;
    }

    refreshAllCharts();
}

function resetTimeFilter() {
    console.log('🔄 重置时间筛选');
    document.getElementById('start-time').value = '';
    document.getElementById('end-time').value = '';
    refreshAllCharts();
}

// 初始化
document.addEventListener('DOMContentLoaded', function() {
    console.log('🚀 初始化图表系统');

    // 初始化所有图表
    initAllCharts();

    // 添加窗口大小变化监听
    window.addEventListener('resize', resizeAllCharts);

    // 添加州市选择事件监听
    const citySelect = document.getElementById('city-select');
    if (citySelect) {
        citySelect.addEventListener('change', function() {
            console.log('🌍 城市选择改变:', this.value);
            refreshAllCharts();
        });
    }

    // 初始加载数据
    setTimeout(() => {
        console.log('📦 初始加载数据');
        refreshAllCharts();
    }, 100);
});