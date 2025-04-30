function switchTab(id) {
  document.querySelectorAll('.tab').forEach(t => t.classList.remove('active'));
  document.querySelectorAll('.content').forEach(c => c.classList.add('hidden'));
  document.querySelector(`.tab[onclick="switchTab('${id}')"]`).classList.add('active');
  document.getElementById(id).classList.remove('hidden');
}

// ==================== Plotly Gráficos ====================
const pcaMetrics = JSON.parse('{{ pca_metrics|escapejs }}');
const pcaGlobal = JSON.parse('{{ pca_global|escapejs }}');
const tsneMetrics = JSON.parse('{{ tsne_metrics|escapejs }}');
const tsneGlobal = JSON.parse('{{ tsne_global|escapejs }}');

function prepareDataByLabel(data, xKey, yKey) {
  const grouped = {};
  data.forEach(item => {
    const label = item.label || 'undefined';
    if (!grouped[label]) grouped[label] = { x: [], y: [], name: label };
    grouped[label].x.push(item[xKey]);
    grouped[label].y.push(item[yKey]);
  });
  return Object.values(grouped).map(group => ({
    x: group.x,
    y: group.y,
    mode: 'markers',
    type: 'scatter',
    name: group.name
  }));
}

Plotly.newPlot('pcaMetricsPlot', prepareDataByLabel(pcaMetrics, 'PC1', 'PC2'), {
  title: 'PCA - MetricsModel',
  xaxis: { title: 'PC1' },
  yaxis: { title: 'PC2' }
});

Plotly.newPlot('pcaGlobalPlot', prepareDataByLabel(pcaGlobal, 'PC1', 'PC2'), {
  title: 'PCA - GlobalMetricsModel',
  xaxis: { title: 'PC1' },
  yaxis: { title: 'PC2' }
});

Plotly.newPlot('tsneMetricsPlot', prepareDataByLabel(tsneMetrics, 'TSNE1', 'TSNE2'), {
  title: 't-SNE - MetricsModel',
  xaxis: { title: 'TSNE1' },
  yaxis: { title: 'TSNE2' }
});

Plotly.newPlot('tsneGlobalPlot', prepareDataByLabel(tsneGlobal, 'TSNE1', 'TSNE2'), {
  title: 't-SNE - GlobalMetricsModel',
  xaxis: { title: 'TSNE1' },
  yaxis: { title: 'TSNE2' }
});