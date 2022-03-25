# bert imports
# from colbert.modeling.colbert import ColBERT
from colbert.modeling.hf_colbert import HF_ColBERT
from colbert.modeling.tokenization import QueryTokenizer, DocTokenizer
from colbert.utils.utils import print_message


# xlmr imports
from colbert.modeling.hf_colbert_xlmr import HF_ColBERT_XLMR
from colbert.modeling.tokenization.doc_tokenization_xlmr import DocTokenizerXLMR
from colbert.modeling.tokenization.query_tokenization_xlmr import QueryTokenizerXLMR

import os


# Based on model type to associate to a proper model and tokennizers(query, doc)
#----------------------------------------------------------------
def get_colbert_from_pretrained(name, colbert_config):
    # in V2, these come from
    # training::colbert = ColBERT(name=config.checkpoint, colbert_config=config)

    # currently, support bert and xlmr, ONLY and tinybert is hard wired.

    local_models_repository = colbert_config.local_models_repository
    model_type = name
    if colbert_config.model_type is not None:
        model_type = colbert_config.model_type
    print_message(f"model type: {model_type}")

    if model_type=='bert-base-uncased' or model_type=='bert-large-uncased':
        colbert = HF_ColBERT.from_pretrained(name, colbert_config)
    elif model_type == 'tinybert':
        if not local_models_repository:
            raise ValueError("Please specify the local repository for additional models.")
        #  hard wired for local Tinybert model
        colbert = HF_ColBERT.from_pretrained(os.path.join(local_models_repository, 'tinybert/TinyBERT_General_4L_312D'), colbert_config)
        # e.g. from https://huggingface.co/huawei-noah/TinyBERT_General_4L_312D/tree/main
    elif model_type=='xlm-roberta-base' or model_type=='xlm-roberta-large':
        colbert = HF_ColBERT_XLMR.from_pretrained(name, colbert_config)
    else:
        raise NotImplementedError

    colbert.model_type=model_type
    return colbert

#----------------------------------------------------------------
def get_query_tokenizer(model_type, maxlen, attend_to_mask_tokens):

    if model_type=='bert-base-uncased' or model_type=='bert-large-uncased':
        return QueryTokenizer(maxlen,model_type, attend_to_mask_tokens)
    elif model_type=='tinybert':
        return QueryTokenizer(maxlen, 'bert-base-uncased',attend_to_mask_tokens)
    elif model_type=='xlm-roberta-base' or model_type=='xlm-roberta-large':
        return QueryTokenizerXLMR(maxlen, model_type)
    else:
        raise NotImplementedError

#----------------------------------------------------------------
def get_doc_tokenizer(model_type, maxlen):

    if model_type=='bert-base-uncased' or model_type=='bert-large-uncased':
        return DocTokenizer(maxlen, model_type)
    elif model_type=='tinybert':
        return DocTokenizer(maxlen, 'bert-base-uncased')
    elif model_type=='xlm-roberta-base' or model_type=='xlm-roberta-large':
        return DocTokenizerXLMR(maxlen, model_type)
    else:
        raise NotImplementedError
