from ..utils.abs_metric import AbsMetric

class TravelTime(AbsMetric):
    def __init__(self, tempo_chegada, tempo_partida):
        self.tempo_chegada = tempo_chegada
        self.tempo_partida = tempo_partida

    def extract(self):
        return self.tempo_chegada - self.tempo_partida if self.tempo_chegada > self.tempo_partida else 0
