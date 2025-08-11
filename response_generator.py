import logging
import requests
import json
from langchain_ollama.llms import OllamaLLM
from langchain.schema.runnable import RunnablePassthrough
from langchain_core.prompts import ChatPromptTemplate
from langchain.schema.output_parser import StrOutputParser
from typing import Dict, Any, List, Optional

logger = logging.getLogger(__name__)

class ResponseGenerator:
    def __init__(self, config: Dict[str, Any]):
        """Initialize the ResponseGenerator with configuration."""
        self.config = config
        
        # Initialize Ollama for response generation
        self.base_url = config.get('ollama_base_url', 'http://localhost:11434')
        
        self.model = OllamaLLM(
            model=config.get('model_name'),
            base_url=self.base_url,
            temperature=config.get('temperature', 0.2),
            top_p=0.95,
            top_k=64,
            num_predict=4096,
            timeout=200
        )
        
        # Define the prompt template for response generation
        self.prompt = ChatPromptTemplate.from_template("""
            أنت مساعد ذكي متخصص في الرياضيات، مع خبرة عميقة في حل المسائل الرياضية وشرح المفاهيم الرياضية بطريقة واضحة ومفهومة. يجب عليك التفكير والإجابة باللغة العربية فقط.

            معايير الإجابة الأساسية:
            1. استخلاص المعرفة: قم بتحليل المستندات المقدمة بالكامل، واستخرج المعلومات ذات الصلة من جميع أجزاء السياق المتاح.
            2. التكامل المعرفي: اجمع بين المعلومات من مختلف أقسام النص لتكوين إجابات شاملة ومتكاملة.
            3. الدقة الرياضية: انقل المعادلات والصيغ الرياضية بدقة تامة، مع الإشارة إلى الخطوات المتبعة في الحل.
            4. الالتزام بالسياق: قدم إجابات تستند حصرياً إلى المعلومات الموجودة في السياق المقدم.

            حدود الإجابة:
            1. الشفافية المعرفية: عند عدم توفر معلومات كافية، صرّح بوضوح: "لا تتوفر معلومات كافية حول هذه المسألة في النصوص المتاحة."
            2. منع الاستنتاج: امتنع عن إضافة معلومات من خارج السياق إلا إذا كانت ضرورية لتوضيح مفهوم رياضي أساسي.
            3. الاعتراف بالنقص: عند توفر إجابة جزئية فقط، قدم المعلومات المتاحة مع الإشارة إلى محدوديتها.
            4. منع التخمين: لا تستنتج معلومات غير مذكورة صراحةً في السياق.
            5. في الملفات الموجودة، قد تجد صيغ LaTeX للمعادلات الرياضية. استخدمها بدقة في إجابتك عند الحاجة.

            معايير الصياغة:
            1. الشمولية: قدم إجابات مفصلة وشاملة تغطي جميع جوانب المسألة الرياضية.
            2. البنية المنطقية: نظّم الإجابات بتسلسل منطقي واضح مع خطوات الحل مرتبة بشكل متسلسل.
            3. التوثيق: أشر إلى مصدر المعلومات ضمن السياق المقدم.
            4. الشرح التعليمي: اشرح المفاهيم الرياضية بأسلوب تعليمي واضح يساعد على الفهم.
            5. اللغة: يجب أن تكون جميع إجاباتك باللغة العربية فقط، بما في ذلك مرحلة التفكير.

            نوع الاستفسار: {query_type}
            السياق المتاح:
            {context}

            السؤال:
            {question}

            عملية التفكير (يجب أن تكون بالعربية):
            <think>
            فكر بالمسألة خطوة بخطوة باللغة العربية. حلل المعطيات، وحدد المطلوب، واشرح طريقة الحل بالتفصيل. تأكد من استخدام المعلومات الموجودة في السياق فقط.
            </think>

            الإجابة (من السياق فقط، ويجب أن تكون بالعربية):
        """)
        
        # Create the chain
        self.chain = (
            RunnablePassthrough()
            | self.prompt
            | self.model
            | StrOutputParser()
        )
    
    def generate(self, query: str, context: str, conversation_history: Optional[List[str]] = None, 
                query_type: str = "general", is_multi_part: bool = False) -> str:
        """
        Generate a response based on the query and context.
        """
        logger.info(f"Generating response for query type: {query_type}, is_multi_part: {is_multi_part}")
        
        # تقييد طول السياق للاستجابات متعددة الأجزاء
        if is_multi_part and len(context) > 50000:
            # اقتصر على 50000 حرف كحد أقصى للسياق للأسئلة متعددة الأجزاء
            logger.warning(f"Context too long ({len(context)} chars), truncating to 50000 chars")
            context = context[:50000] + "..."
        
        # Format the input for the chain
        formatted_input = {
            "conversation_history": "\n".join(conversation_history) if conversation_history else "",
            "context": context,
            "question": query,
            "query_type": query_type
        }
        
        # Add retry logic
        max_retries = 3
        retry_count = 0
        
        while retry_count <= max_retries:
            try:
                # Invoke the chain
                logger.info(f"Trying to generate response with LangChain (attempt {retry_count + 1}/{max_retries + 1})")
                response = self.chain.invoke(formatted_input)
                
                # Check for empty response
                if not response or response.strip() == "":
                    logger.warning(f"Empty response received on attempt {retry_count + 1}")
                    retry_count += 1
                    
                    # On last retry, raise error to trigger fallback
                    if retry_count > max_retries:
                        logger.error("Maximum retries reached with empty responses")
                        raise ValueError("Empty response after maximum retries")
                    
                    # Adjust parameters for retry
                    self.model.temperature = min(0.7, self.model.temperature + 0.15)
                    continue
                    
                return response
                
            except Exception as e:
                logger.error(f"Error generating response with LangChain (attempt {retry_count + 1}): {str(e)}")
                retry_count += 1
                
                # If we've reached max retries, fall back to direct API call
                if retry_count > max_retries:
                    logger.info("Maximum retries reached, falling back to direct Ollama API call")
                    break
                
                # Adjust parameters for retry
                self.model.temperature = min(0.7, self.model.temperature + 0.15)
            
        # If we get here, all LangChain attempts failed, use direct API
        try:
            # Fallback to direct Ollama API call with different parameters
            options = {
                "temperature": 0.7,
                "top_p": 0.95,
                "top_k": 64,
                "num_predict": 2048,
            }
            
            # Create URL for the Ollama API
            api_url = f"{self.base_url}/api/generate"
            
            # تبسيط المطالبة للاستدعاء المباشر مع تحسين التعليمات
            system_instructions = """
            أنت مساعد ذكي متخصص في الرياضيات، مهمتك تقديم إجابات دقيقة ومفصلة عن المسائل الرياضية، معتمداً فقط على المعلومات المقدمة في السياق. يجب عليك شرح المفاهيم الرياضية بطريقة واضحة ومفهومة، وتوضيح خطوات الحل بشكل منطقي ومتسلسل. يجب عليك التفكير والإجابة باللغة العربية فقط، ولا تستخدم اللغة الإنجليزية مطلقاً في إجاباتك.
            """
            
            user_prompt = f"""
            السؤال: {query}
            
            السياق المتوفر (مقتطفات من المصادر):
            {context[:10000] if len(context) > 10000 else context}
            
            عملية التفكير (يجب أن تكون بالعربية):
            فكر بالمسألة خطوة بخطوة باللغة العربية. حلل المعطيات، وحدد المطلوب، واشرح طريقة الحل بالتفصيل. تأكد من استخدام المعلومات الموجودة في السياق فقط.
            
            أجب على السؤال بدقة ووضوح اعتمادًا على المعلومات المذكورة في السياق فقط. وضح المصطلحات الرياضية إذا لزم الأمر.
            إذا لم تتوفر معلومات كافية، وضّح ذلك وقدم أفضل إجابة ممكنة استنادًا إلى ما هو متاح.
            تذكر: يجب أن تكون إجابتك باللغة العربية فقط، ولا تستخدم اللغة الإنجليزية مطلقاً في إجابتك.
            """
            
            try:
                # Try using the system instructions approach first
                response = self.model.generate(
                    [
                        {"role": "system", "parts": [system_instructions]},
                        {"role": "user", "parts": [user_prompt]}
                    ]
                )
                
                if hasattr(response, 'text') and response.text:
                    return response.text
                elif hasattr(response, 'parts'):
                    text_content = ''.join(part.text for part in response.parts if hasattr(part, 'text'))
                    if text_content:
                        return text_content
            except:
                # If the system instructions approach fails, fall back to simpler prompt
                logger.warning("System instructions approach failed, using simple prompt")
                response = self.model.generate(user_prompt)
                
                if hasattr(response, 'text') and response.text:
                    return response.text
                elif hasattr(response, 'parts'):
                    text_content = ''.join(part.text for part in response.parts if hasattr(part, 'text'))
                    if text_content:
                        return text_content
                
            # في حالة فشل جميع المحاولات، قدم استجابة عامة تناسب المسألة الرياضية باللغة العربية
            return "عذرًا، لم أتمكن من معالجة المسألة الرياضية بشكل كامل. يرجى إعادة صياغة المسألة أو تقديم مزيد من التفاصيل."
                
        except Exception as direct_e:
            logger.error(f"Direct Ollama API call also failed: {str(direct_e)}")
            return "عذرًا، حدث خطأ أثناء معالجة المسألة الرياضية. يرجى المحاولة مرة أخرى."