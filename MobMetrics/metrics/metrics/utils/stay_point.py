import logging
from .utils import distance  # Função para calcular a distância entre dois pontos
from ...models import StayPointModel, VisitModel  # Modelos Django para StayPoint e Visit

class StayPoints:
    """
    Classe para calcular e salvar stay points e visitas associadas.
    """
    
    def __init__(self, trace, distance_threshold, time_threshold, entity_id):
        """
        Inicializa a classe StayPoints com os parâmetros fornecidos.

        :param trace: DataFrame contendo o dataset com a trajetória.
        :param distance_threshold: Limiar de distância para considerar pontos próximos.
        :param time_threshold: Limiar de tempo para considerar pontos como parte de uma mesma estadia.
        :param entity_id: Identificador único para a entidade (usuário, veículo, etc.).
        """
        self.trace = trace  # Dados da trajetória (como um DataFrame)
        self.distance_threshold = distance_threshold  # Limiar de distância em metros
        self.time_threshold = time_threshold  # Limiar de tempo em segundos
        self.entity_id = entity_id  # ID da entidade (ex.: usuário ou veículo)

    def extract(self):
        """
        Extrai os stay points da trajetória e os salva no banco de dados.

        Para cada stay point, uma nova visita é criada no modelo VisitModel.
        Retorna o DataFrame atualizado com o spId atribuído a cada ponto.
        """
        logging.info("Calculando Stay Points")  # Log de início do cálculo dos stay points

        self.trace['spId'] = 0  # Inicializa uma nova coluna para os IDs de stay points
        stay_point_id = 1  # Começa com o primeiro ID de stay point
        m = 0  # Inicia o processamento dos dados da trajetória

        while m < len(self.trace):
            # Pula pontos que já possuem um spId atribuído
            if self.trace.iloc[m]['spId'] != 0:
                m += 1
                continue

            # Variáveis para calcular o stay point
            arvT = self.trace.iloc[m]['time']  # Hora de chegada
            lat_sum = self.trace.iloc[m]['x']  # Soma das latitudes
            lgnt_sum = self.trace.iloc[m]['y']  # Soma das longitudes
            alt_sum = self.trace.iloc[m]['z']  # Soma das altitudes
            buffer = 1  # Buffer para contar o número de pontos na estadia

            i = m + 1  # Inicia a busca para agrupar pontos na estadia
            while i < len(self.trace) and distance(self.trace.iloc[m], self.trace.iloc[i]) <= self.distance_threshold:
                lat_sum += self.trace.iloc[i]['x']
                lgnt_sum += self.trace.iloc[i]['y']
                alt_sum += self.trace.iloc[i]['z']
                buffer += 1  # Aumenta o número de pontos na estadia
                i += 1

            levT = self.trace.iloc[i - 1]['time']  # Hora de partida (último ponto da estadia)

            # Verifica se a duração da estadia excede o limiar de tempo
            if (levT - arvT) >= self.time_threshold:
                # Calcula as coordenadas médias da estadia
                x = round(lat_sum / buffer, 5)
                y = round(lgnt_sum / buffer, 5)
                z = round(alt_sum / buffer, 5)

                exist = True  # Flag para verificar se o stay point já existe
                # Verifica se um stay point similar já existe no banco de dados
                for aux in StayPointModel.objects.all():
                    if distance({'x': aux.x, 'y': aux.y, 'z': aux.z}, {'x': x, 'y': y, 'z': z}) <= self.distance_threshold:
                        # Se um ponto similar existir, atualiza o spId para os pontos da trajetória
                        self.trace.iloc[m:i, self.trace.columns.get_loc('spId')] = aux.spId
                        aux.numVisits += 1  # Incrementa o número de visitas
                        aux.save()  # Salva o stay point atualizado

                        # Cria uma visita para o stay point
                        VisitModel.objects.create(
                            entityId=self.entity_id,
                            spId=aux.spId,
                            arvT=arvT,
                            levT=levT,
                            visitT=levT - arvT  # Duração da visita
                        )
                        exist = False  # Stay point já existe
                        break

                if exist:
                    # Se nenhum stay point similar existir, cria um novo stay point
                    new_stay_point = StayPointModel.objects.create(
                        spId=stay_point_id,
                        x=x,
                        y=y,
                        z=z,
                        numVisits=1  # Esta é a primeira visita ao stay point
                    )
                    # Atribui o novo spId aos pontos da trajetória
                    self.trace.iloc[m:i, self.trace.columns.get_loc('spId')] = stay_point_id

                    # Cria uma visita para o novo stay point
                    VisitModel.objects.create(
                        entityId=self.entity_id,
                        spId=stay_point_id,
                        arvT=arvT,
                        levT=levT,
                        visitT=levT - arvT  # Duração da visita
                    )

                    stay_point_id += 1  # Incrementa o ID do próximo stay point

            m = i  # Avança para o próximo ponto na trajetória

        logging.info("Stay Points Calculados com Sucesso")  # Log de conclusão do cálculo
        return self.trace  # Retorna o DataFrame atualizado com os IDs de stay points atribuídos
