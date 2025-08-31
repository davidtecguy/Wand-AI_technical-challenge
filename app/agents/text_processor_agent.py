from typing import Dict, Any, List
from .base import BaseAgent
from app.tools import TextProcessorTool
import logging
from datetime import datetime

logger = logging.getLogger(__name__)

class TextProcessorAgent(BaseAgent):
    """Agent specialized in processing and analyzing text data"""
    
    def __init__(self):
        super().__init__(
            name="TextProcessorAgent",
            agent_type="text_processor",
            capabilities=["text_analysis", "text_summarization", "sentiment_analysis", "keyword_extraction"]
        )
        
        # Register the text processor tool
        self.register_tool(TextProcessorTool())
        
        logger.info(f"TextProcessorAgent initialized with ID: {self.id}")
    
    def can_handle_task(self, task_type: str) -> bool:
        """Check if this agent can handle a specific task type"""
        return task_type in ["analyze_text", "summarize_text", "extract_keywords", "analyze_sentiment", "clean_text", "batch_text_processing"]
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a text processing task"""
        try:
            task_type = task_data.get("task_type", "analyze_text")
            parameters = task_data.get("parameters", {})
            
            logger.info(f"TextProcessorAgent processing task: {task_type}")
            
            if task_type == "analyze_text":
                return await self._analyze_text(parameters)
            elif task_type == "summarize_text":
                return await self._summarize_text(parameters)
            elif task_type == "extract_keywords":
                return await self._extract_keywords(parameters)
            elif task_type == "analyze_sentiment":
                return await self._analyze_sentiment(parameters)
            elif task_type == "clean_text":
                return await self._clean_text(parameters)
            elif task_type == "batch_text_processing":
                return await self._batch_text_processing(parameters)
            else:
                raise ValueError(f"Unsupported task type: {task_type}")
                
        except Exception as e:
            logger.error(f"Error processing task in TextProcessorAgent: {e}")
            raise
    
    async def _analyze_text(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze text and provide comprehensive statistics"""
        try:
            # Execute the text processor tool
            result = await self.execute_tool("text_processor", {
                "operation": "analyze",
                "text": parameters.get("text", ""),
                "language": parameters.get("language", "en"),
                "include_metadata": parameters.get("include_metadata", True)
            })
            
            if result.get("success"):
                # Add agent-specific metadata
                result["agent_id"] = self.id
                result["analysis_timestamp"] = str(datetime.utcnow())
                result["input_parameters"] = parameters
                
                logger.info(f"Text analysis completed successfully for {len(parameters.get('text', ''))} characters")
                return result
            else:
                logger.error(f"Text analysis failed: {result.get('error', 'Unknown error')}")
                return result
                
        except Exception as e:
            logger.error(f"Error in _analyze_text: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.id
            }
    
    async def _summarize_text(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a summary of the text"""
        try:
            result = await self.execute_tool("text_processor", {
                "operation": "summarize",
                "text": parameters.get("text", ""),
                "max_length": parameters.get("max_length", 1000),
                "include_metadata": parameters.get("include_metadata", True)
            })
            
            if result.get("success"):
                result["agent_id"] = self.id
                result["summarization_timestamp"] = str(datetime.utcnow())
                result["input_parameters"] = parameters
                
                logger.info(f"Text summarization completed successfully")
                return result
            else:
                logger.error(f"Text summarization failed: {result.get('error', 'Unknown error')}")
                return result
                
        except Exception as e:
            logger.error(f"Error in _summarize_text: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.id
            }
    
    async def _extract_keywords(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Extract keywords from text"""
        try:
            result = await self.execute_tool("text_processor", {
                "operation": "extract_keywords",
                "text": parameters.get("text", ""),
                "language": parameters.get("language", "en"),
                "include_metadata": parameters.get("include_metadata", True)
            })
            
            if result.get("success"):
                result["agent_id"] = self.id
                result["extraction_timestamp"] = str(datetime.utcnow())
                result["input_parameters"] = parameters
                
                logger.info(f"Keyword extraction completed successfully")
                return result
            else:
                logger.error(f"Keyword extraction failed: {result.get('error', 'Unknown error')}")
                return result
                
        except Exception as e:
            logger.error(f"Error in _extract_keywords: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.id
            }
    
    async def _analyze_sentiment(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze text sentiment"""
        try:
            result = await self.execute_tool("text_processor", {
                "operation": "sentiment",
                "text": parameters.get("text", ""),
                "include_metadata": parameters.get("include_metadata", True)
            })
            
            if result.get("success"):
                result["agent_id"] = self.id
                result["sentiment_analysis_timestamp"] = str(datetime.utcnow())
                result["input_parameters"] = parameters
                
                logger.info(f"Sentiment analysis completed successfully")
                return result
            else:
                logger.error(f"Sentiment analysis failed: {result.get('error', 'Unknown error')}")
                return result
                
        except Exception as e:
            logger.error(f"Error in _analyze_sentiment: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.id
            }
    
    async def _clean_text(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Clean and normalize text"""
        try:
            result = await self.execute_tool("text_processor", {
                "operation": "clean",
                "text": parameters.get("text", ""),
                "include_metadata": parameters.get("include_metadata", True)
            })
            
            if result.get("success"):
                result["agent_id"] = self.id
                result["cleaning_timestamp"] = str(datetime.utcnow())
                result["input_parameters"] = parameters
                
                logger.info(f"Text cleaning completed successfully")
                return result
            else:
                logger.error(f"Text cleaning failed: {result.get('error', 'Unknown error')}")
                return result
                
        except Exception as e:
            logger.error(f"Error in _clean_text: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.id
            }
    
    async def _batch_text_processing(self, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Process multiple text items in batch"""
        texts = parameters.get("texts", [])
        operations = parameters.get("operations", ["analyze"])
        
        if not texts:
            return {
                "success": False,
                "error": "No texts provided for batch processing",
                "agent_id": self.id
            }
        
        try:
            batch_results = []
            failed_items = []
            
            for i, text in enumerate(texts):
                try:
                    item_result = {
                        "text_index": i,
                        "text_length": len(text),
                        "operations": {}
                    }
                    
                    # Process each operation
                    for operation in operations:
                        if operation == "analyze":
                            op_result = await self.execute_tool("text_processor", {
                                "operation": "analyze",
                                "text": text,
                                "include_metadata": False
                            })
                            item_result["operations"]["analyze"] = op_result
                        
                        elif operation == "summarize":
                            op_result = await self.execute_tool("text_processor", {
                                "operation": "summarize",
                                "text": text,
                                "max_length": parameters.get("max_length", 1000),
                                "include_metadata": False
                            })
                            item_result["operations"]["summarize"] = op_result
                        
                        elif operation == "extract_keywords":
                            op_result = await self.execute_tool("text_processor", {
                                "operation": "extract_keywords",
                                "text": text,
                                "include_metadata": False
                            })
                            item_result["operations"]["extract_keywords"] = op_result
                        
                        elif operation == "sentiment":
                            op_result = await self.execute_tool("text_processor", {
                                "operation": "sentiment",
                                "text": text,
                                "include_metadata": False
                            })
                            item_result["operations"]["sentiment"] = op_result
                        
                        elif operation == "clean":
                            op_result = await self.execute_tool("text_processor", {
                                "operation": "clean",
                                "text": text,
                                "include_metadata": False
                            })
                            item_result["operations"]["clean"] = op_result
                    
                    batch_results.append(item_result)
                    
                except Exception as e:
                    failed_items.append({
                        "text_index": i,
                        "error": str(e),
                        "text_length": len(text) if text else 0
                    })
            
            return {
                "success": True,
                "total_texts": len(texts),
                "successfully_processed": len(batch_results),
                "failed_items": len(failed_items),
                "batch_results": batch_results,
                "failed_items": failed_items,
                "batch_processing_timestamp": str(datetime.utcnow()),
                "agent_id": self.id
            }
            
        except Exception as e:
            logger.error(f"Error in batch text processing: {e}")
            return {
                "success": False,
                "error": str(e),
                "agent_id": self.id
            }

