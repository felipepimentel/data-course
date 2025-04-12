"""
Detector de Viés Cognitivo para análise de feedback.

Identifica padrões de viés cognitivo na autopercepção versus feedback externo,
mapeando áreas onde a pessoa tem pontos cegos.
"""
import re
import numpy as np
from typing import List, Dict, Any, Optional, Tuple, Set
from dataclasses import dataclass


class CognitiveBiasDetector:
    """
    Detector de Viés Cognitivo para o ciclo de feedback integrado.
    
    Capaz de identificar padrões comuns de viés cognitivo na autopercepção
    versus feedback externo, ajudando a conscientizar sobre pontos cegos.
    """
    
    def __init__(self):
        """Inicializa o detector de viés cognitivo."""
        # Bias patterns - padrões de viés cognitivo conhecidos
        self.bias_patterns = {
            "dunning_kruger": {
                "pattern": "alta autopercepção em áreas de baixa competência real",
                "description": "Efeito Dunning-Kruger: tendência a superestimar habilidades em áreas onde temos menor competência.",
                "detection": lambda self_score, external_scores: 
                    self_score > 4.0 and np.mean(external_scores) < 3.0,
                "recommendations": [
                    "Buscar feedback mais frequente e específico nesta área",
                    "Investir em avaliações objetivas de competência",
                    "Praticar a metacognição: refletir sobre o que você realmente sabe e não sabe"
                ]
            },
            "impostor_syndrome": {
                "pattern": "baixa autopercepção em áreas de alta competência real",
                "description": "Síndrome do Impostor: tendência a subestimar habilidades em áreas onde temos maior competência.",
                "detection": lambda self_score, external_scores: 
                    self_score < 3.0 and np.mean(external_scores) > 4.0,
                "recommendations": [
                    "Documentar conquistas e feedback positivo recebido",
                    "Reconhecer e valorizar contribuições objetivas",
                    "Praticar autoafirmações positivas baseadas em evidências concretas"
                ]
            },
            "confirmation_bias": {
                "pattern": "seletividade no processamento de feedback",
                "description": "Viés de Confirmação: tendência a valorizar feedback que confirma nossas crenças e descartar o que as contradiz.",
                "detection": lambda self_score, external_scores: 
                    np.std(external_scores) > 1.0 and abs(self_score - np.mean(external_scores)) > 1.0,
                "recommendations": [
                    "Considerar ativamente pontos de vista contrários",
                    "Buscar feedback de fontes diversas",
                    "Praticar pensamento crítico ao receber feedback"
                ]
            },
            "blind_spots": {
                "pattern": "áreas específicas com gap persistente",
                "description": "Pontos Cegos: áreas específicas onde há discrepância consistente entre autopercepção e feedback externo.",
                "detection": lambda self_score, external_scores: 
                    abs(self_score - np.mean(external_scores)) > 1.5,
                "recommendations": [
                    "Solicitar exemplos concretos de comportamentos nesta área",
                    "Definir métricas objetivas de avaliação",
                    "Fazer autoavaliações periódicas com critérios específicos"
                ]
            },
            "fundamental_attribution_error": {
                "pattern": "atribuição externa para falhas",
                "description": "Erro Fundamental de Atribuição: tendência a atribuir falhas a fatores externos, mas sucessos a fatores internos.",
                "detection": None,  # Baseado em análise textual
                "text_patterns": [
                    r"não.+minha culpa",
                    r"circunstâncias",
                    r"outros.+impediram",
                    r"não tive oportunidade",
                    r"condições.+desfavoráveis"
                ],
                "recommendations": [
                    "Praticar a assunção de responsabilidade em retrospectivas",
                    "Identificar fatores controláveis vs não controláveis",
                    "Adotar mentalidade de crescimento focada em aprendizado"
                ]
            },
            "halo_effect": {
                "pattern": "generalização de competências",
                "description": "Efeito Halo: tendência a generalizar competência de uma área para outra sem evidências.",
                "detection": None,  # Requer análise mais complexa de padrões
                "recommendations": [
                    "Avaliar cada competência separadamente com critérios específicos",
                    "Buscar feedback específico para cada área de atuação",
                    "Identificar transferências legítimas vs generalizações injustificadas"
                ]
            }
        }
    
    def analyze_bias(self, self_score: Optional[float], 
                     external_scores: List[float],
                     feedback_texts: List[str]) -> Dict[str, Any]:
        """
        Analisa potenciais vieses cognitivos com base na diferença entre
        autopercepção e feedback externo.
        
        Args:
            self_score: Score de autoavaliação (pode ser None)
            external_scores: Lista de scores de avaliação externa
            feedback_texts: Textos de feedback associados
            
        Returns:
            Dicionário com análise de viés encontrado
        """
        result = {
            "biases_detected": [],
            "pattern": None,
            "recommendations": []
        }
        
        # Se não temos autoavaliação, análise limitada
        if self_score is None:
            result["pattern"] = "Sem autoavaliação para comparação"
            result["recommendations"] = [
                "Realizar autoavaliação para identificar possíveis pontos cegos",
                "Solicitar feedback específico em áreas de incerteza"
            ]
            return result
        
        # Converter para numpy array para facilitar cálculos
        external_scores_np = np.array(external_scores)
        
        # Verificar cada padrão de viés baseado em scores
        for bias_id, bias_info in self.bias_patterns.items():
            detector_func = bias_info.get("detection")
            
            if detector_func and detector_func(self_score, external_scores_np):
                result["biases_detected"].append(bias_id)
                
                # Adicionar primeira detecção como padrão principal
                if result["pattern"] is None:
                    result["pattern"] = bias_info["description"]
                
                # Adicionar recomendações
                result["recommendations"].extend(bias_info["recommendations"])
        
        # Análise de texto para vieses que requerem inspeção de feedback textual
        for bias_id, bias_info in self.bias_patterns.items():
            text_patterns = bias_info.get("text_patterns", [])
            
            if text_patterns:
                # Concatenar todos os textos para análise
                all_text = " ".join(feedback_texts).lower()
                
                # Verificar padrões de texto
                matched = False
                for pattern in text_patterns:
                    if re.search(pattern, all_text):
                        matched = True
                        break
                
                if matched and bias_id not in result["biases_detected"]:
                    result["biases_detected"].append(bias_id)
                    
                    # Adicionar primeira detecção como padrão principal se ainda não definido
                    if result["pattern"] is None:
                        result["pattern"] = bias_info["description"]
                    
                    # Adicionar recomendações
                    result["recommendations"].extend(bias_info["recommendations"])
        
        # Se não encontramos vieses específicos mas há gap significativo
        if not result["biases_detected"] and abs(self_score - np.mean(external_scores_np)) > 1.0:
            result["pattern"] = "Gap significativo sem padrão específico identificado"
            result["recommendations"] = [
                "Solicitar exemplos concretos de comportamentos ou situações",
                "Estabelecer métricas objetivas para avaliar progresso",
                "Buscar feedback mais frequente para calibrar autopercepção"
            ]
        
        # Remover duplicatas de recomendações
        result["recommendations"] = list(dict.fromkeys(result["recommendations"]))
        
        return result
    
    def analyze_historical_bias(self, 
                               self_scores: List[float], 
                               external_scores: List[List[float]],
                               timestamps: List[str]) -> Dict[str, Any]:
        """
        Analisa tendências históricas de viés cognitivo ao longo do tempo.
        
        Args:
            self_scores: Lista histórica de autoavaliações
            external_scores: Lista de listas de avaliações externas correspondentes
            timestamps: Lista de timestamps para cada conjunto de avaliações
            
        Returns:
            Dicionário com análise de tendências de viés
        """
        result = {
            "persistent_biases": [],
            "improving_areas": [],
            "worsening_areas": [],
            "trend_description": None,
            "recommendations": []
        }
        
        # Se temos menos de 2 pontos no tempo, não podemos analisar tendências
        if len(self_scores) < 2:
            result["trend_description"] = "Dados históricos insuficientes para análise de tendência"
            return result
        
        # Calcular gaps ao longo do tempo
        gaps = []
        for i in range(len(self_scores)):
            ext_mean = np.mean(external_scores[i]) if external_scores[i] else None
            if ext_mean is not None:
                gap = self_scores[i] - ext_mean
                gaps.append(gap)
            else:
                gaps.append(None)
        
        # Filtrar pontos sem dados
        valid_gaps = [(i, gap) for i, gap in enumerate(gaps) if gap is not None]
        if len(valid_gaps) < 2:
            result["trend_description"] = "Dados comparáveis insuficientes para análise de tendência"
            return result
        
        # Analisar se os gaps estão diminuindo ou aumentando ao longo do tempo
        first_valid_gap = valid_gaps[0][1]
        last_valid_gap = valid_gaps[-1][1]
        gap_change = last_valid_gap - first_valid_gap
        
        # Verificar consistência do viés
        consistent_overestimation = all(gap > 0.5 for _, gap in valid_gaps)
        consistent_underestimation = all(gap < -0.5 for _, gap in valid_gaps)
        
        # Avaliar tendências
        if abs(gap_change) < 0.3:
            # Gap permanece relativamente estável
            if consistent_overestimation:
                result["persistent_biases"].append("superestimação consistente")
                result["trend_description"] = "Tendência persistente de superestimar competências"
                result["recommendations"] = [
                    "Estabelecer métricas objetivas de avaliação",
                    "Buscar feedback mais frequente e detalhado",
                    "Trabalhar com um mentor para calibrar autopercepção"
                ]
            elif consistent_underestimation:
                result["persistent_biases"].append("subestimação consistente")
                result["trend_description"] = "Tendência persistente de subestimar competências"
                result["recommendations"] = [
                    "Documentar conquistas e sucessos objetivos",
                    "Praticar reconhecimento de forças e competências",
                    "Trabalhar com coach para desenvolver autoconfiança realista"
                ]
            else:
                result["trend_description"] = "Variação de autopercepção sem padrão claro"
                result["recommendations"] = [
                    "Estabelecer checkins regulares para calibragem de percepção",
                    "Desenvolver maior consciência situacional",
                    "Praticar reflexão estruturada sobre desempenho"
                ]
        elif gap_change < 0:
            # Gap está diminuindo (melhorando calibragem)
            result["improving_areas"].append("calibragem geral de autopercepção")
            result["trend_description"] = "Melhoria na calibragem entre autopercepção e feedback externo"
            result["recommendations"] = [
                "Continuar práticas atuais de reflexão e calibragem",
                "Documentar abordagens eficazes para aprendizado futuro",
                "Ampliar para outras áreas de competência"
            ]
        else:
            # Gap está aumentando (piorando calibragem)
            result["worsening_areas"].append("calibragem geral de autopercepção")
            result["trend_description"] = "Aumento na discrepância entre autopercepção e feedback externo"
            result["recommendations"] = [
                "Aumentar frequência de check-ins de feedback",
                "Estabelecer avaliações com critérios mais objetivos",
                "Explorar possíveis fatores contribuindo para o desalinhamento"
            ]
        
        return result
    
    def identify_bias_patterns_in_text(self, text: str) -> List[Dict[str, Any]]:
        """
        Identifica padrões de viés cognitivo em texto de feedback ou autoavaliação.
        
        Args:
            text: Texto a ser analisado
            
        Returns:
            Lista de padrões de viés identificados
        """
        text = text.lower()
        patterns_found = []
        
        # Dicionário de padrões textuais e biases associados
        text_pattern_mapping = {
            # Dunning-Kruger (superestimação em áreas de baixa competência)
            "dunning_kruger": [
                r"sei (tudo|muito) sobre",
                r"domino completamente",
                r"sou especialista em",
                r"não preciso (melhorar|aprender mais)",
                r"já sei o suficiente"
            ],
            
            # Síndrome do Impostor
            "impostor_syndrome": [
                r"foi sorte",
                r"não mereço",
                r"vão descobrir que não sou capaz",
                r"qualquer um conseguiria",
                r"não sou bom o suficiente"
            ],
            
            # Viés de confirmação
            "confirmation_bias": [
                r"isso confirma o que eu já sabia",
                r"este feedback não é válido",
                r"eles estão errados sobre",
                r"não concordo com essa avaliação",
                r"isso não se aplica a mim"
            ],
            
            # Erro fundamental de atribuição
            "fundamental_attribution_error": [
                r"não.+minha culpa",
                r"culpa d[aoe]s? (circunstâncias|outros)",
                r"não me deram (recursos|apoio|suporte)",
                r"não tive oportunidade",
                r"(ambiente|situação).+impediu"
            ],
            
            # Viés de autoserviço
            "self_serving_bias": [
                r"mérito foi (meu|minha|todo meu)",
                r"consegui sozinho",
                r"graças ao meu esforço",
                r"falha foi d[aoe]s? outr[aoe]s",
                r"equipe não colaborou"
            ],
            
            # Efeito halo
            "halo_effect": [
                r"como sou bom em .+, também sou bom em",
                r"minhas habilidades se transferem para",
                r"naturalmente bom em tudo",
                r"tenho talento em todas as áreas",
                r"facilidade para aprender qualquer coisa"
            ]
        }
        
        # Verificar cada padrão
        for bias_id, patterns in text_pattern_mapping.items():
            for pattern in patterns:
                if re.search(pattern, text):
                    # Encontrou um padrão deste viés
                    bias_info = self.bias_patterns.get(bias_id, {})
                    patterns_found.append({
                        "bias_id": bias_id,
                        "description": bias_info.get("description", f"Viés de {bias_id}"),
                        "matched_pattern": pattern,
                        "recommendations": bias_info.get("recommendations", [])
                    })
                    # Encontrar apenas uma ocorrência de cada tipo de viés
                    break
        
        return patterns_found 