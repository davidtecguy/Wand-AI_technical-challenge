from typing import Dict, Any, List
from .base import BaseTool
from app.models import ToolType
import re
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TextProcessorTool(BaseTool):
    """Tool for processing and analyzing text data"""
    
    def __init__(self):
        super().__init__(
            name="text_processor",
            description="Processes and analyzes text data with various operations",
            tool_type=ToolType.TEXT_PROCESSOR
        )
        self.parameters_schema = {
            "operation": {"type": "string", "enum": ["analyze", "summarize", "extract_keywords", "sentiment", "translate", "clean"], "required": True},
            "text": {"type": "string", "description": "Text to process", "required": True},
            "language": {"type": "string", "default": "en"},
            "max_length": {"type": "integer", "default": 1000},
            "include_metadata": {"type": "boolean", "default": True}
        }
    
    def validate_parameters(self, parameters: Dict[str, Any]) -> bool:
        required_fields = ["operation", "text"]
        if not all(field in parameters for field in required_fields):
            return False
        
        valid_operations = ["analyze", "summarize", "extract_keywords", "sentiment", "translate", "clean"]
        if parameters["operation"] not in valid_operations:
            return False
        
        if not isinstance(parameters["text"], str) or len(parameters["text"].strip()) == 0:
            return False
        
        return True
    
    async def execute(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        try:
            operation = parameters["operation"]
            text = parameters["text"]
            language = parameters.get("language", "en")
            max_length = parameters.get("max_length", 1000)
            include_metadata = parameters.get("include_metadata", True)
            
            if operation == "analyze":
                result = self._analyze_text(text, language, include_metadata)
            elif operation == "summarize":
                result = self._summarize_text(text, max_length, include_metadata)
            elif operation == "extract_keywords":
                result = self._extract_keywords(text, language, include_metadata)
            elif operation == "sentiment":
                result = self._analyze_sentiment(text, include_metadata)
            elif operation == "translate":
                result = self._translate_text(text, language, include_metadata)
            elif operation == "clean":
                result = self._clean_text(text, include_metadata)
            else:
                raise ValueError(f"Unsupported operation: {operation}")
            
            return {
                "success": True,
                "operation": operation,
                "result": result,
                "processed_at": str(datetime.utcnow())
            }
            
        except Exception as e:
            logger.error(f"Error processing text: {e}")
            return {
                "success": False,
                "error": str(e),
                "operation": parameters.get("operation", "unknown")
            }
    
    def _analyze_text(self, text: str, language: str, include_metadata: bool) -> Dict[str, Any]:
        """Analyze text and provide comprehensive statistics"""
        words = text.split()
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        char_count = len(text)
        word_count = len(words)
        sentence_count = len(sentences)
        
        avg_word_length = sum(len(word) for word in words) / word_count if word_count > 0 else 0
        avg_sentence_length = word_count / sentence_count if sentence_count > 0 else 0
        
        result = {
            "statistics": {
                "characters": char_count,
                "words": word_count,
                "sentences": sentence_count,
                "avg_word_length": round(avg_word_length, 2),
                "avg_sentence_length": round(avg_sentence_length, 2)
            }
        }
        
        if include_metadata:
            result["metadata"] = {
                "language": language,
                "processing_time": str(datetime.utcnow())
            }
        
        return result
    
    def _summarize_text(self, text: str, max_length: int, include_metadata: bool) -> Dict[str, Any]:
        """Generate a summary of the text"""
        words = text.split()
        
        if len(words) <= max_length:
            summary = text
        else:
            summary = " ".join(words[:max_length]) + "..."
        
        result = {
            "summary": summary,
            "original_length": len(words),
            "summary_length": len(summary.split())
        }
        
        if include_metadata:
            result["metadata"] = {
                "max_length": max_length,
                "compression_ratio": round(len(summary.split()) / len(words), 2)
            }
        
        return result
    
    def _extract_keywords(self, text: str, language: str, include_metadata: bool) -> Dict[str, Any]:
        """Extract keywords from text"""
        words = re.findall(r'\b\w+\b', text.lower())
        
        stop_words = {"the", "a", "an", "and", "or", "but", "in", "on", "at", "to", "for", "of", "with", "by"}
        filtered_words = [word for word in words if word not in stop_words and len(word) > 2]
        
        word_freq = {}
        for word in filtered_words:
            word_freq[word] = word_freq.get(word, 0) + 1
        
        keywords = sorted(word_freq.items(), key=lambda x: x[1], reverse=True)[:10]
        
        result = {
            "keywords": [{"word": word, "frequency": freq} for word, freq in keywords],
            "total_keywords": len(keywords)
        }
        
        if include_metadata:
            result["metadata"] = {
                "language": language,
                "min_word_length": 3
            }
        
        return result
    
    def _analyze_sentiment(self, text: str, include_metadata: bool) -> Dict[str, Any]:
        """Analyze text sentiment (simplified implementation)"""
        positive_words = {"good", "great", "excellent", "amazing", "wonderful", "happy", "love", "like", "best"}
        negative_words = {"bad", "terrible", "awful", "horrible", "sad", "hate", "dislike", "worst", "terrible"}
        
        words = text.lower().split()
        positive_count = sum(1 for word in words if word in positive_words)
        negative_count = sum(1 for word in words if word in negative_words)
        
        total_words = len(words)
        if total_words == 0:
            sentiment_score = 0
        else:
            sentiment_score = (positive_count - negative_count) / total_words
        
        if sentiment_score > 0.1:
            sentiment = "positive"
        elif sentiment_score < -0.1:
            sentiment = "negative"
        else:
            sentiment = "neutral"
        
        result = {
            "sentiment": sentiment,
            "sentiment_score": round(sentiment_score, 3),
            "positive_words": positive_count,
            "negative_words": negative_count
        }
        
        if include_metadata:
            result["metadata"] = {
                "total_words": total_words,
                "analysis_method": "lexicon_based"
            }
        
        return result
    
    def _translate_text(self, text: str, target_language: str, include_metadata: bool) -> Dict[str, Any]:
        """Translate text (placeholder implementation)"""
        result = {
            "original_text": text,
            "translated_text": f"[TRANSLATED TO {target_language.upper()}] {text}",
            "target_language": target_language
        }
        
        if include_metadata:
            result["metadata"] = {
                "translation_service": "placeholder",
                "confidence": 0.0
            }
        
        return result
    
    def _clean_text(self, text: str, include_metadata: bool) -> Dict[str, Any]:
        """Clean and normalize text"""
        cleaned = re.sub(r'\s+', ' ', text.strip())
        
        cleaned = re.sub(r'[^\w\s\.\,\!\?\-\']', '', cleaned)
        
        cleaned = cleaned.replace('"', '"').replace('"', '"')
        cleaned = cleaned.replace(''', "'").replace(''', "'")
        
        result = {
            "cleaned_text": cleaned,
            "original_length": len(text),
            "cleaned_length": len(cleaned),
            "characters_removed": len(text) - len(cleaned)
        }
        
        if include_metadata:
            result["metadata"] = {
                "cleaning_operations": ["whitespace_normalization", "special_char_removal", "quote_normalization"]
            }
        
        return result
