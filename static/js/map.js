document.addEventListener('DOMContentLoaded', () => {
    // 设置云南省中心点和缩放级别
    const map = L.map('map').setView([24.8, 102.9], 7.5);
    
    // 使用深色主题地图，与科技感主题保持一致
    L.tileLayer('https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png', {
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> contributors &copy; <a href="https://carto.com/attributions">CARTO</a>',
        subdomains: 'abcd',
        maxZoom: 19
    }).addTo(map);

    fetch('/api/city_counts')
        .then(r => r.json())
        .then(data => {
            // 热力图数据
            const heatPoints = data.map(d => [d.latitude, d.longitude, d.count * 0.1]);
            
            // 改进热力图样式
            L.heatLayer(heatPoints, {
                radius: 30,
                blur: 25,
                maxZoom: 17,
                minOpacity: 0.3,
                gradient: {
                    0.4: '#00d4ff',
                    0.65: '#0099ff',
                    0.8: '#3366ff',
                    1: '#ff0066'
                }
            }).addTo(map);

            // 城市标记
            data.forEach(city => {
                // 计算标记大小，使差异更明显
                const radius = Math.max(5, Math.min(20, Math.sqrt(city.count) * 0.8));
                
                L.circleMarker([city.latitude, city.longitude], {
                    radius: radius,
                    fillColor: '#00d4ff',
                    color: '#ffffff',
                    weight: 2,
                    opacity: 0.9,
                    fillOpacity: 0.7,
                    stroke: true
                })
                .bindPopup(`<div style="color: #000; font-weight: bold;">${city.city}</div><div style="color: #333;">${city.count}起案件</div>`)
                .addTo(map);
            });
        });
});