from ..utils.abs_metric import AbsMetric

class TravelAverageSpeed(AbsMetric):
    def __init__(self, distancia, tempo):
        """
        Inicializa com a distância e o tempo.
        """
        self.distancia = distancia
        self.tempo = tempo

    def extract(self):
        """
        Calcula a velocidade média (distância / tempo).
        """
        return self.distancia / self.tempo if self.tempo > 0 else 0