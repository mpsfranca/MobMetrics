import pandas as pd
from ..utils.utils import distance  # Importando a função distance
from tqdm import tqdm  # type: ignore
from ...models import ContactModel  # Importando o modelo Django

class DetectContact:
    def __init__(self, parameters, name, trace):
        """
        Inicializa a classe com os parâmetros necessários para detecção de contatos.
        
        :param parameters: Um dicionário com as configurações do arquivo CSV, incluindo:
            - distance_threshold: O valor limite de distância para considerar um contato.
            - time_threshold: O valor limite de tempo para considerar um contato.
            - radius_threshold: O raio utilizado para calcular a proximidade entre os objetos.
        :param name: Nome do arquivo para ser incluído na tabela de saída.
        :param trace: DataFrame pandas com os dados dos objetos.
        """
        self.parameters = parameters  # Dicionário contendo os três parâmetros
        self.name = name              # Nome do arquivo
        self.trace = trace            # DataFrame contendo os dados dos objetos

    def extract(self):
        """
        Extrai os contatos entre os objetos com base nos thresholds fornecidos e os salva no banco de dados.
        
        :return: None
        """
        contacts = []  # Lista para armazenar os contatos detectados
        trace = self.trace
        distance_threshold = self.parameters[2]
        
        # Obtém os diferentes instantes de tempo únicos
        unique_times = trace['time'].unique()
        
        for t in tqdm(unique_times, desc="Processando contatos"):
            subset = trace[trace['time'] == t]  # Filtra os objetos para o instante de tempo atual
            
            if len(subset) < 2:
                continue  # Se houver menos de dois objetos, não há contatos para verificar
            
            objects = subset.to_dict(orient='records')  # Converte para lista de dicionários
            
            for i in range(len(objects)):
                for j in range(i + 1, len(objects)):
                    obj1, obj2 = objects[i], objects[j]
                    
                    # Calcula a distância entre os dois objetos
                    dist = distance(obj1, obj2)
                    
                    if dist < distance_threshold:
                        # Salva o contato no banco de dados
                        contact = ContactModel(
                            fileName=self.name,
                            id1=obj1['id'],
                            id2=obj2['id'],
                            contact_timestamp=t,
                            start_x_id_1=obj1['x'],
                            start_x_id_2=obj2['x'],
                            start_y_id_1=obj1['y'],
                            start_y_id_2=obj2['y'],
                            start_z_id_1=obj1['z'],
                            start_z_id_2=obj2['z'],
                            end_x_id_1=obj1['x'],
                            end_x_id_2=obj2['x'],
                            end_y_id_1=obj1['y'],
                            end_y_id_2=obj2['y'],
                            end_z_id_1=obj1['z'],
                            end_z_id_2=obj2['z']
                        )
                        contact.save()  # Salva o objeto no banco de dados
