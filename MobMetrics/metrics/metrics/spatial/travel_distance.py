from ..utils.utils import distance
from ..utils.abs_metric import AbsMetric

class TravelDistance(AbsMetric):
    def __init__(self, traces):
        """
        Inicializa com os rastros da viagem.
        """
        self.traces = traces

    def extract(self):
        """
        Calcula a distância total percorrida entre os pontos de rastro.
        """
        distancia_total = 0
        previous_trace = self.traces.first()  # O primeiro ponto é o ponto de partida
        
        for trace in self.traces[1:]:  # Percorrer os rastros após o primeiro ponto
            # Converter os pontos para o formato de dicionário esperado pela função `distance`
            first_point = {'x': previous_trace.x, 'y': previous_trace.y, 'z': previous_trace.z}
            second_point = {'x': trace.x, 'y': trace.y, 'z': trace.z}

            distancia_total += distance(first_point, second_point)
            previous_trace = trace
        
        return distancia_total