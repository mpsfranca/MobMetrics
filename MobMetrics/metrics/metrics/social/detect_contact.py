import pandas as pd
from ..utils.utils import distance  # Importando a função distance
from tqdm import tqdm  # type: ignore

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
        Extrai todos os contatos entre os objetos no trace (DataFrame), verificando a distância e o tempo.
        
        :return: DataFrame contendo os contatos detectados.
        """
        # Preparar as variáveis para armazenar os resultados
        contacts = []
        trace = self.trace
        
        # Usar um loop para iterar sobre as linhas e calcular a distância de maneira vetorizada
        trace['distances'] = trace.apply(
            lambda row: pd.Series(
                [distance(
                    {'x': row['x'], 'y': row['y'], 'z': row['z']},
                    {'x': other_row['x'], 'y': other_row['y'], 'z': other_row['z']}
                ) for idx, other_row in trace.iterrows() if row['time'] == other_row['time']]
            ), axis=1
        )

        # Em vez de fazer a comparação de todas as linhas no loop, otimizamos a comparação de distâncias
        for i, obj1 in tqdm(trace.iterrows(), total=len(trace), desc="Detecting contacts", unit="iteration"):
            for j, obj2 in enumerate(trace.iloc[i+1:].values):
                dist = self.parameters[2]  # Pegue o valor do threshold para distância
                if dist < 2*self.parameters[2]:
                    contacts.append({
                        'fileName': self.name,
                        'id1': obj1['id'],
                        'id2': obj2['id'],
                        'start_time': obj1['time'],
                        'end_time': obj2['time'],
                        'start_x_id_1': obj1['x'],
                        'start_x_id_2': obj2['x'],
                        'start_y_id_1': obj1['y'],
                        'start_y_id_2': obj2['y'],
                        'start_z_id_1': obj1['z'],
                        'start_z_id_2': obj2['z'],
                        'end_x_id_1': obj1['x'],
                        'end_x_id_2': obj2['x'],
                        'end_y_id_1': obj1['y'],
                        'end_y_id_2': obj2['y'],
                        'end_z_id_1': obj1['z'],
                        'end_z_id_2': obj2['z']
                    })
        
        contacts_df = pd.DataFrame(contacts)
        return contacts_df
