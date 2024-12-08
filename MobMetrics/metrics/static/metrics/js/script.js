document.addEventListener('DOMContentLoaded', function() {
    // A função será executada apenas depois que o DOM estiver completamente carregado
    function createHistogram() {
        const metricsData = JSON.parse('{{ metrics|escapejs }}');
        const tTrvTValues = metricsData.map(metric => metric.fields.TTrvT);

        const trace = {
            x: tTrvTValues,
            type: 'histogram',
            opacity: 0.75,
            marker: {
                color: 'rgb(58, 71, 80)',
                line: { color: 'rgb(0,0,0)', width: 1 }
            }
        };

        const layout = {
            title: 'Histograma de TTrvT',
            xaxis: { title: 'TTrvT' },
            yaxis: { title: 'Contagem' },
            bargap: 0.05
        };

        Plotly.newPlot('metricsHistogram', [trace], layout);
    }

    createHistogram()
    // Aqui você pode chamar a função assim que o DOM estiver pronto
    // createHistogram();
});
