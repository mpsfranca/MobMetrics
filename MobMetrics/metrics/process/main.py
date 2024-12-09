import pandas as pd
import logging
logging.basicConfig(level=logging.DEBUG, filename="logging.log", format="%(asctime)s - %(filename)s - %(levelname)s - %(message)s")

from ..models import MetricsModel, TraceModel, TravelsModel, StayPointModel, VisitModel

from .factory import Factory
from .format import Format

def main(trace_file, parameters):
    logging.info("Program Started")

    trace = pd.read_csv(trace_file)
    trace = Format(trace).extract()

    MetricsModel.objects.all().delete()
    TraceModel.objects.all().delete()
    TravelsModel.objects.all().delete()
    StayPointModel.objects.all().delete()
    VisitModel.objects.all().delete()



    ids = trace['id'].unique()

    num = len(ids)
    for id in ids:
        print(f'metric {id} of {num}')
        filtred_trace = trace[trace['id'] == id]
        Factory().extract(filtred_trace, parameters, id)

    Factory().travels()
    Factory().reextract()


    logging.info("Metrics Calculated")