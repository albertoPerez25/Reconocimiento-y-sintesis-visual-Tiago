import os
os.environ["RAGAS_DO_NOT_TRACK"] = "true"
os.environ["HF_HUB_DISABLE_SYMLINKS_WARNING"] = "1"

import torch
import typing as t
import re
import gc
import nltk
from transformers import AutoModelForSequenceClassification, AutoTokenizer
from rouge_score import rouge_scorer
from bert_score import score as bert_score_fn
from dataclasses import dataclass, field
from ragas.metrics.base import SingleTurnMetric
from ragas.dataset_schema import SingleTurnSample

@dataclass
class RougeScoreMetric(SingleTurnMetric):
    """Calcula la cobertura de conceptos esenciales usando RECALL en ROUGE-1 optimizado para Español"""
    name: str = "rouge_score_recall_es"

    def __post_init__(self):
        try:
            nltk.data.find('stemmers/snowball_data')
        except LookupError:
            nltk.download('snowball_data', quiet=True)
            
        self.scorer = rouge_scorer.RougeScorer(['rouge1'], use_stemmer=True)
        
        self.stopwords = {
            "el", "la", "los", "las", "un", "una", "unos", "unas", "y", "o", "pero", "de", "en", 
            "para", "por", "con", "que", "es", "son", "del", "al", "su", "sus", "este", "esta", 
            "como", "se", "lo", "le", "les", "me", "nos", "te"
        }

    def init(self, run_config):
        pass

    def _clean_and_filter(self, text: str) -> str:
        text = text.lower()
        text = re.sub(r'[áäâà]', 'a', text)
        text = re.sub(r'[éëêè]', 'e', text)
        text = re.sub(r'[íïîì]', 'i', text)
        text = re.sub(r'[óöôò]', 'o', text)
        text = re.sub(r'[úüûù]', 'u', text)
        text = re.sub(r'[^\w\s]', ' ', text)
        
        words = text.split()
        filtered_words = [w for w in words if w not in self.stopwords]
        return " ".join(filtered_words)

    async def _single_turn_ascore(self, sample: SingleTurnSample, callbacks: t.Any = None) -> float:
        gt = sample.reference or ""
        ans = sample.response or ""
        if not gt or not ans:
            return 0.0
            
        # Volvemos a RECALL para valorar la retención de datos sin penalizar la longitud del resumen
        scores = self.scorer.score(self._clean_and_filter(gt), self._clean_and_filter(ans))
        return float(scores['rouge1'].recall)


@dataclass
class BERTScoreMetric(SingleTurnMetric):
    """
    Usa BERTScore con el modelo multilingüe oficial por defecto para 
    evitar problemas con diccionarios de HuggingFace.
    """
    name: str = "bert_score_es"

    def init(self, run_config):
        pass

    async def _single_turn_ascore(self, sample: SingleTurnSample, callbacks: t.Any = None) -> float:
        gt = sample.reference or ""
        ans = sample.response or ""
        if not gt or not ans:
            return 0.0

        # Al omitir model_type y pasar lang="es", bert_score usa de forma segura
        # su modelo oficial interno pre-configurado para evitar KeyErrors.
        P, R, F1 = bert_score_fn([ans], [gt], lang="es", verbose=False)
        return float(F1.item())


@dataclass
class HHEMFidelity(SingleTurnMetric):
    """
    NLI optimizado que extrae mini-frases y suaviza penalizaciones si el LLM
    menciona detalles correctos mezclados con zonas vacías.
    """
    name: str = "hhem_fidelity_balanced"
    model_name: str = "Recognai/bert-base-spanish-wwm-cased-xnli"
    
    _is_loaded: bool = field(default=False, init=False)
    tokenizer: t.Any = field(default=None, init=False)
    model: t.Any = field(default=None, init=False)
    _entail_idx: int = field(default=0, init=False)
    _contradict_idx: int = field(default=2, init=False)

    def __post_init__(self):
        try:
            self.tokenizer = AutoTokenizer.from_pretrained(self.model_name, local_files_only=False)
            self.model = AutoModelForSequenceClassification.from_pretrained(self.model_name, local_files_only=False)
            self.model.eval()
            
            labels = {v.lower(): k for k, v in self.model.config.id2label.items()}
            self._entail_idx = labels.get("entailment", 0)
            self._contradict_idx = labels.get("contradiction", 2)
            self._is_loaded = True
        except Exception as e:
            self._is_loaded = False

    def init(self, run_config):
        pass

    def _split_into_sentences(self, text: str) -> t.List[str]:
        sentences = re.split(r'(?<!\w\.\w.)(?<![A-Z][a-z]\.)(?<=\.|\?|\!|\,)\s', text)
        return [s.strip() for s in sentences if len(s.strip()) > 8]

    async def _single_turn_ascore(self, sample: SingleTurnSample, callbacks: t.Any = None) -> float:
        if not self._is_loaded:
            return 0.0

        gt_text = sample.reference or ""
        response_text = sample.response or ""

        gt_clean = re.sub(r'[\{\}\[\]"”]', ' ', gt_text).strip()
        summary_sentences = self._split_into_sentences(response_text)
        
        if not summary_sentences or not gt_clean:
            return 0.0

        score_accum = 0.0
        valid_sentences_count = 0
        
        for sentence in summary_sentences:
            if any(p in sentence.lower() for p in ["resumen global", "informe combina", "a continuación"]):
                continue
                
            valid_sentences_count += 1
            
            inputs = self.tokenizer(
                gt_clean, 
                sentence, 
                return_tensors="pt", 
                truncation=True, 
                max_length=512
            )
            
            with torch.no_grad():
                outputs = self.model(**inputs)
                probs = torch.softmax(outputs.logits, dim=-1)
                
                # CORRECCIÓN: Agregado el índice de lote [0] antes del índice de etiqueta para evitar IndexError
                p_entail = float(probs[0][self._entail_idx].item())
                p_contradict = float(probs[0][self._contradict_idx].item())
            
            if p_entail > 0.35:
                score_accum += 1.0  
            elif p_contradict > 0.60:
                score_accum += 0.0  
            else:
                score_accum += 0.5  

        if valid_sentences_count == 0:
            return 0.0

        return float(score_accum / valid_sentences_count)
