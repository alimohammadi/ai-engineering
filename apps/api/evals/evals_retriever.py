from api.agents.retrieval_generation import rag_pipeline

import openai
from langsmith import Client
from qdrant_client import QdrantClient
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from ragas.embeddings import LangchainEmbeddingsWrapper
from ragas.llms import LangchainLLMWrapper
from ragas.dataset_schema import SingleTurnSample
from ragas.metrics import IDBasedContextPrecision, IDBasedContextRecall, Faithfulness, ResponseRelevency

ls_client = Client()
qdrant_client = QdrantClient("localhost", port=6333)

ragas_llm = LangchainLLMWrapper(ChatOpenAI(model="gpt-4.1-mini"))
ragas_embeddings = LangchainEmbeddingsWrapper(OpenAIEmbeddings(model="text-embedding-3-small"))

async def ragas_faithfulness(run, example):
    sample = SingleTurnSample(
        user_input = run["question"],
        response = run["answer"],
        retrieved_context = run["retrieved_context"]
    )

    scorer = Faithfulness(llm=ragas_llm)

    return await scorer.single_turn_ascore(sample)

async def ragas_response_relevancy(run, example):
    sample = SingleTurnSample(
        user_input = run["question"],
        response = run["answer"],
        retrieved_context = run["retrieved_context"] 
    )

    scorer = ResponseRelevency(llm= ragas_llm, embeddings = ragas_embeddings)

    return await scorer.single_turn_ascore(sample)

async def ragas_context_precision_id_based(run, example):
    sample = SingleTurnSample(
        retrieved_context_ids = run["retrieved_context_ids"],
        reference_context_ids = example["reference_context_ids"],
    )
    scorer = IDBasedContextPrecision()

    return await scorer.single_turn_ascore(sample)

async def ragas_context_recall_id_based(run, example):
    sample = SingleTurnSample(
        retrieved_context_ids = run["retrieved_context_ids"],
        reference_context_ids = example["reference_context_ids"],
    )

    scorer = IDBasedContextRecall()

    return await scorer.single_turn_ascore(sample)

result = ls_client.evaluate(
    lambda x: rag_pipeline(x["question"], qdrant_client),
    data="rag-evaluation-dataset",
    evaluators=[
        ragas_faithfulness,
        ragas_response_relevancy,
        ragas_context_precision_id_based,
        ragas_context_recall_id_based
    ],
    experiment_prefix="retriever",
    max_concurrency=2
)