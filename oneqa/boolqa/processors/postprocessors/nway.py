from collections import defaultdict
from itertools import groupby
from operator import itemgetter
from typing import List, Dict, Any

from datasets import Dataset
from tqdm import tqdm
import numpy as np
from datetime import datetime
import torch
import logging
from transformers import EvalPrediction

from oneqa.mrc.processors.postprocessors.abstract import AbstractPostProcessor
from oneqa.mrc.processors.postprocessors.scorers import initialize_scorer
from oneqa.mrc.data_models.target_type import TargetType
from oneqa.mrc.data_models.eval_prediction_with_processing import EvalPredictionWithProcessing
from oneqa.mrc.processors.postprocessors.scorers import SupportedSpanScorers


logger = logging.getLogger(__name__)


class NWayClassifierPostProcessor(AbstractPostProcessor):
    def __init__(self, 
                drop_label: str,
                id_key: str,
                label_list: List[str],
                output_label_prefix: str,
                *args, **kwargs):
        super().__init__(1, 1)
        self.id_key=id_key
        self.drop_label = drop_label
        self.label_list = label_list
        self.output_label_prefix = output_label_prefix


    def process(self, examples: Dataset, features: Dataset, predictions: tuple):
        """
        Convert data and model predictions into MRC answers.
        """
        pass

    def prepare_examples_as_references(self, examples: Dataset) -> List[Dict[str, Any]]:
        """
        Convert examples into references for use with metrics.
        """
        pass

    def _get_prediction_from_predict_scores(self, predict_scores):
        if self.drop_label:
            # dropping NONE to get binary predictions from 3-way classifier
            # TODO maybe this should be model dependent rather than task dependent
            label_list=np.array(self.label_list)
            mask=label_list==self.drop_label
            masked_predict_scores=predict_scores.copy()
            masked_predict_scores[:,mask]=-9e19
        else:
            masked_predict_scores=predict_scores

        predictions = np.argmax(masked_predict_scores, axis=1)
        return predictions



    # TODO we aren't handling reference, metrics yet
    def process_references_and_predictions(self, examples, features, predict_scores) -> EvalPrediction:
        print('in process_references_and_predictions')
#        references = self.prepare_examples_as_references(examples)
        ipredictions=self._get_prediction_from_predict_scores(predict_scores)
        #predictions = self.process(examples, features, predict_scores)
        preds_by_id = {}
        


        fields = zip(features[self.id_key],
            features["question"],
            examples['language'],
            ipredictions, 
            predict_scores)
        for index, (example_id, question, language, item, scores) in enumerate(fields):
            item_label = self.label_list[item]
            preds_by_id[example_id] = {}
            preds_by_id[example_id]["pred"] = str(item_label)
            preds_by_id[example_id]["conf"] = str(scores[item])
            preds_by_id[example_id]["question"] = question
            preds_by_id[example_id]["language"] = language
            preds_by_id[example_id]["scores"] = { label:float(score) for label,score in zip(self.label_list, scores)}

        predictions_for_metric = list(preds_by_id.values())

        examples_json={}
        for ex, p in zip(examples, predictions_for_metric):
            ex[self.output_label_prefix+'_pred'] = p['pred']
            ex[self.output_label_prefix+'_scores'] = p['scores']
            ex[self.output_label_prefix+'_conf'] = p['conf']
            examples_json[ex['example_id']] = [ ex ]


        # noinspection PyTypeChecker
        return EvalPredictionWithProcessing(
            label_ids=None,
            predictions=examples_json,
            processed_predictions=predictions_for_metric,
        )    
