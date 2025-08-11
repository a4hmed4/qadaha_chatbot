from typing import Dict, List, Any, Optional
import logging
import json
import requests
from langchain_ollama import OllamaLLM

logger = logging.getLogger(__name__)

class QueryAnalyzer:
    def __init__(self, config: Dict[str, Any]):
        """Initialize the QueryAnalyzer with configuration."""
        self.config = config
        
        # Initialize Ollama for query analysis
        self.base_url = config.get('ollama_base_url', 'http://localhost:11434')
        
        self.model = OllamaLLM(
            model=config.get('model_name'),
            base_url=self.base_url,
            temperature=0.2,  # Lower temperature for more deterministic analysis
            top_p=0.95,
            top_k=40
        )
        
        # Define system prompt for query analysis in Arabic
        self.analysis_prompt = """
        أنت محلل ذكي متخصص في فهم المسائل والاستعلامات الرياضية.
        مهمتك هي تحليل استعلام المستخدم وتقديم معلومات مفيدة لمساعدة نظام استرجاع المعلومات على فهم الاستعلام بشكل أفضل.
        
        قم بتحليل الاستعلام التالي وإخراج النتائج بتنسيق JSON فقط. في تحليلك، حدد:
        
        1. query_type: نوع الاستعلام (جبري/هندسي/تفاضل_وتكامل/إحصاء/نظرية_الأعداد/تطبيقي)
        2. topics: المواضيع الرئيسية في الاستعلام (قائمة)
        3. is_multi_part: هل السؤال متعدد الأجزاء؟ (true/false)
        4. sub_queries: إذا كان متعدد الأجزاء، قسمه إلى أسئلة فرعية (قائمة)
        5. retrieval_strategy: استراتيجية الاسترجاع المناسبة (default/comprehensive/precise)
        6. refined_query: صياغة محسنة للاستعلام للبحث
        
        الاستعلام: {query}
        
        أعد فقط JSON بالتنسيق التالي بدون أي نص إضافي:
        {{
          "query_type": "جبري/هندسي/تفاضل_وتكامل/إحصاء/نظرية_الأعداد/تطبيقي",
          "topics": ["موضوع 1", "موضوع 2"],
          "is_multi_part": true/false,
          "sub_queries": ["سؤال فرعي 1", "سؤال فرعي 2"],
          "retrieval_strategy": "default/comprehensive/precise",
          "refined_query": "صياغة محسنة للاستعلام"
        }}
        
        يجب عليك اختيار الإجابة وتحديدها بشكل صريح وواضح.
        """
    
    def analyze(self, query: str, conversation_history: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        تحليل الاستعلام لتحديد خصائصه.
        
        المعاملات:
            query: استعلام المستخدم
            conversation_history: سجل المحادثة السابقة
            
        العائد:
            قاموس يحتوي على نتائج التحليل
        """
        try:
            # تنسيق المطالبة
            formatted_prompt = self.analysis_prompt.format(query=query)
            
            # الحصول على التحليل من Ollama
            logger.info(f"تحليل الاستعلام: {query}")
            response = self.model.invoke(formatted_prompt)
            
            # الاستجابة من Ollama هي سلسلة نصية بسيطة
            response_text = response
            
            # معالجة أساسية لأخطاء تحليل JSON
            try:
                # استخراج JSON إذا كان داخل كتلة رمز
                if "```json" in response_text:
                    json_str = response_text.split("```json")[1].split("```")[0].strip()
                    analysis_result = json.loads(json_str)
                elif "```" in response_text:
                    json_str = response_text.split("```")[1].split("```")[0].strip()
                    analysis_result = json.loads(json_str)
                else:
                    analysis_result = json.loads(response_text)
                
                logger.info(f"نتيجة تحليل الاستعلام: {analysis_result}")
                
                # التأكد من أن النتيجة تحتوي على جميع الحقول المطلوبة
                required_fields = ["query_type", "topics", "is_multi_part", "sub_queries", "retrieval_strategy", "refined_query"]
                for field in required_fields:
                    if field not in analysis_result:
                        logger.warning(f"الحقل المطلوب {field} غير موجود في نتيجة التحليل، استخدام القيمة الافتراضية")
                        if field == "query_type":
                            analysis_result[field] = "عام"
                        elif field in ["topics", "sub_queries"]:
                            analysis_result[field] = []
                        elif field == "is_multi_part":
                            analysis_result[field] = False
                        elif field == "retrieval_strategy":
                            analysis_result[field] = "default"
                        elif field == "refined_query":
                            analysis_result[field] = query
                
                return analysis_result
                
            except json.JSONDecodeError:
                logger.error(f"فشل في تحليل JSON من الاستجابة: {response_text}")
                # الرجوع إلى التحليل الأساسي
                return self._fallback_analysis(query)
                
        except Exception as e:
            logger.error(f"خطأ في تحليل الاستعلام: {str(e)}")
            return self._fallback_analysis(query)
    
    def _fallback_analysis(self, query: str) -> Dict[str, Any]:
        """الرجوع إلى التحليل الأساسي القائم على القواعد إذا فشل تحليل النموذج اللغوي."""
        logger.info("استخدام تحليل الاستعلام الاحتياطي")
        
        # اكتشاف أساسي للأسئلة متعددة الأجزاء
        is_multi_part = any(marker in query for marker in [",", "?", ";", "و", "ثم"])
        
        # القيم الافتراضية للسياق الرياضي
        return {
            "query_type": "عام",
            "topics": [],
            "is_multi_part": is_multi_part,
            "sub_queries": [query] if is_multi_part else [],
            "retrieval_strategy": "default",
            "refined_query": query
        }