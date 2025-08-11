from typing import List, Dict, Any, Optional, Tuple, TypedDict
import logging
from query_analyzer import QueryAnalyzer
from document_retriever import DocumentRetriever
from context_processor import ContextProcessor
from response_generator import ResponseGenerator
import yaml
from langgraph.graph import StateGraph

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class GraphValues(TypedDict, total=False):
    message: str
    conversation_history: List[str]
    query_type: str
    topics: List[str]
    is_multi_part: bool
    sub_queries: List[str]
    retrieval_strategy: str
    analyzed_query: str
    retrieved_documents: List[Dict[str, Any]]
    processed_context: str
    multi_part_results: List[Dict[str, Any]]
    response: str

class MathRagGraph:
    def __init__(self, config_path: str = "config.yaml"):
        """Initialize the MathRagGraph with components and build the graph."""
        # Load configuration
        with open(config_path, 'r', encoding='utf-8') as file:
            self.config = yaml.safe_load(file)
        
        # Initialize components
        self.query_analyzer = QueryAnalyzer(self.config)
        self.document_retriever = DocumentRetriever(self.config)
        self.context_processor = ContextProcessor(self.config)
        self.response_generator = ResponseGenerator(self.config)
        
        # Build the graph
        self.graph = self._build_graph()
    
    def _build_graph(self) -> StateGraph:
        """Build the LangGraph workflow."""
        # Create the graph with TypedDict state
        workflow = StateGraph(GraphValues)
        
        # Add nodes
        workflow.add_node("query_analyzer", self._analyze_query)
        workflow.add_node("document_retriever", self._retrieve_documents)
        workflow.add_node("context_processor", self._process_context)
        workflow.add_node("response_generator", self._generate_response)
        
        # Add conditional edge for handling multi-part questions
        workflow.add_conditional_edges(
            "query_analyzer",
            self._is_multi_part_question,
            {
                True: "handle_multi_part",
                False: "document_retriever",
            }
        )
        
        # Add node for multi-part question handling
        workflow.add_node("handle_multi_part", self._handle_multi_part)
        workflow.add_edge("handle_multi_part", "document_retriever")
        
        # Add normal edges
        workflow.add_edge("document_retriever", "context_processor")
        workflow.add_edge("context_processor", "response_generator")
        
        # Set the entry point
        workflow.set_entry_point("query_analyzer")
        
        # Compile the graph
        return workflow.compile()
    
    def _analyze_query(self, state: GraphValues) -> GraphValues:
        """Analyze the query to determine its type and characteristics."""
        logger.info("تحليل الاستفسار")
        query = state.get("message", "")
        conversation_history = state.get("conversation_history", [])
        
        analysis_result = self.query_analyzer.analyze(
            query=query,
            conversation_history=conversation_history
        )
        
        # Create a new state with updated values
        new_state = state.copy()
        new_state.update({
            "query_type": analysis_result.get("query_type"),
            "topics": analysis_result.get("topics", []),
            "is_multi_part": analysis_result.get("is_multi_part", False),
            "sub_queries": analysis_result.get("sub_queries", []),
            "retrieval_strategy": analysis_result.get("retrieval_strategy", "default"),
            "analyzed_query": analysis_result.get("refined_query", query)
        })
        
        return new_state
    
    def _is_multi_part_question(self, state: GraphValues) -> bool:
        """Determine if the question has multiple parts that should be handled separately."""
        return state.get("is_multi_part", False)
    
    def _handle_multi_part(self, state: GraphValues) -> GraphValues:
        """Handle multi-part questions by processing each part separately."""
        logger.info("معالجة سؤال متعدد الأجزاء")
        sub_queries = state.get("sub_queries", [])
        results = []
        
        for i, sub_query in enumerate(sub_queries):
            logger.info(f"معالجة السؤال الفرعي {i+1}/{len(sub_queries)}: {sub_query}")
            
            # Retrieve documents for this sub-query
            retrieved_docs = self.document_retriever.retrieve(
                query=sub_query,
                k=self.config.get('retrieval_k', 5),
                score_threshold=self.config.get('similarity_threshold', 0.35)
            )
            
            # Process context for this sub-query
            processed_context = self.context_processor.process(
                query=sub_query,
                documents=retrieved_docs
            )
            
            results.append({
                "sub_query": sub_query,
                "documents": retrieved_docs,
                "processed_context": processed_context
            })
        
        # Update state with all results
        new_state = state.copy()
        new_state["multi_part_results"] = results
        
        return new_state
    
    def _retrieve_documents(self, state: GraphValues) -> GraphValues:
        """Retrieve relevant documents based on the query."""
        logger.info("استرجاع المستندات")
        
        # Create a new state to return
        new_state = state.copy()
        
        # If this is a multi-part question that's already been processed
        if state.get("multi_part_results"):
            logger.info("استخدام نتائج معالجة الأسئلة متعددة الأجزاء المسبقة")
            return new_state
        
        query = state.get("analyzed_query", state.get("message", ""))
        retrieval_strategy = state.get("retrieval_strategy", "default")
        
        # Adjust retrieval parameters based on query type
        k = self.config.get('retrieval_k', 5)
        score_threshold = self.config.get('similarity_threshold', 0.35)
        
        if retrieval_strategy == "comprehensive":
            k = k * 2
            score_threshold = score_threshold * 0.8
        elif retrieval_strategy == "precise":
            k = max(3, k - 2)
            score_threshold = score_threshold * 1.2
        
        # Retrieve documents
        retrieved_docs = self.document_retriever.retrieve(
            query=query,
            k=k,
            score_threshold=score_threshold
        )
        
        # Update state
        new_state["retrieved_documents"] = retrieved_docs
        
        return new_state
    
    def _process_context(self, state: GraphValues) -> GraphValues:
        """Process the retrieved context to prepare for response generation."""
        logger.info("معالجة السياق")
        
        # Create a new state to return
        new_state = state.copy()
        
        # Handle multi-part questions differently
        if state.get("multi_part_results"):
            # Context already processed for each sub-query
            combined_context = ""
            for result in state.get("multi_part_results", []):
                combined_context += result.get("processed_context", "") + "\n\n"
            
            new_state["processed_context"] = combined_context
            return new_state
        
        # For single-part questions
        query = state.get("analyzed_query", state.get("message", ""))
        query_type = state.get("query_type", "general")
        documents = state.get("retrieved_documents", [])
        
        processed_context = self.context_processor.process(
            query=query,
            documents=documents,
            query_type=query_type
        )
        
        new_state["processed_context"] = processed_context
        return new_state
    
    def _generate_response(self, state: GraphValues) -> GraphValues:
        """Generate the final response using the processed context."""
        logger.info("إنشاء الاستجابة")
        
        query = state.get("message", "")
        processed_context = state.get("processed_context", "")
        query_type = state.get("query_type", "general")
        conversation_history = state.get("conversation_history", [])
        
        response = self.response_generator.generate(
            query=query,
            context=processed_context,
            conversation_history=conversation_history,
            query_type=query_type,
            is_multi_part=state.get("is_multi_part", False)
        )
        
        # Create a new state with the response
        new_state = state.copy()
        new_state["response"] = response
        return new_state
    
    def chat(self, message: str, conversation_history: Optional[List[str]] = None) -> str:
        """Process a chat request and return the response."""
        logger.info(f"معالجة طلب المحادثة: {message}")
        
        # Set initial state
        initial_state = {
            "message": message,
            "conversation_history": conversation_history or []
        }
        
        # Run the graph
        final_state = self.graph.invoke(initial_state)
        
        # Return the response
        return final_state.get("response", "عذرًا، حدث خطأ أثناء معالجة طلبك. يرجى المحاولة مرة أخرى.")