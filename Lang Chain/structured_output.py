import os
import json
import random
from dotenv import load_dotenv
from typing import Optional
from pydantic import BaseModel, Field
from langchain.schema.runnable import RunnableLambda
from langchain_core.prompts import (
    PromptTemplate,
    FewShotChatMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_core.messages import HumanMessage, SystemMessage
from langchain_openai import AzureChatOpenAI

# =========================
# Model & Class Definitions
# =========================

class SentimentOutput(BaseModel):
    sentiment: str = Field(
        description="Sentiment Classification: 'Bearish', 'Bullish', or 'Neutral'"
    )
    weight_score: float = Field(description="Weighted score of the sentiment")

class LLMEnsembleOutput(BaseModel):
    explanation: str = Field(
        description="Brief explanation (max 150 tokens) on why the sentiment is correct or incorrect"
    )
    weight_score: float = Field(
        description="Opinion on whether the weight score is correct or incorrect"
    )

class FinalVoteOutput(BaseModel):
    final_sentiment: str = Field(
        description="Final Sentiment Classification after reviewing both models' outputs & arguments."
    )
    final_score: int = Field(
        description="Final Score of the sentiment after reviewing both models & arguments. Range: -3 to 3"
    )

class TimeframeClassification(BaseModel):
    timeframe: str = Field(
        description="Timeframe impact classification: 'Short', 'Long', or 'Neutral'"
    )
    reasoning: str = Field(
        description="Brief explanation for the timeframe classification"
    )

# =========================
# Utility Functions
# =========================

def load_few_shots(path, n=10):
    with open(path, encoding="latin") as f:
        few_shots = json.load(f)
    selected = random.sample(few_shots, min(n, len(few_shots)))
    return [
        {
            "input": f"""Title: {ex['title']}\n Subtitle: {ex['subtitle']}\n Body: {ex['body']}""",
            "output": ex["Sentiment"],
        }
        for ex in selected
    ]

def get_llm(deployment="gpt-4o", api_key=None):
    # Load API key from environment variable for security
    api_key = api_key or os.getenv("AZURE_OPENAI_API_KEY")
    if not api_key:
        raise ValueError("Azure OpenAI API key not found. Set AZURE_OPENAI_API_KEY in your environment variables.")
    return AzureChatOpenAI(
        default_headers={"Ocp-Apim-Subscription-Key": api_key},
        azure_deployment=deployment,
        api_version="2025-01-01-preview",
        temperature=0
    )

def build_few_shot_prompt(sentiment_examples):
    sentiment_example_prompt = ChatPromptTemplate.from_messages([
        ("human", "{input}"),
        ("ai", "{output}"),
    ])
    return FewShotChatMessagePromptTemplate(
        example_prompt=sentiment_example_prompt,
        examples=sentiment_examples,
    )

# =========================
# Main Workflow
# =========================

def SENTIMENT_CLF(text):
    # Load environment
    load_dotenv()

    # Few-shot examples
    few_shots_path = "C:/Users/Z_LAME/Desktop/Crawler/Lang Chain/fewshotsrandom.json"
    sentiment_examples = load_few_shots(few_shots_path)

    # Few-shot prompt
    few_shot_prompt = build_few_shot_prompt(sentiment_examples)

    # LLMs
    llm = get_llm()
    llm_claude = get_llm()

    sentiment_prompt = ChatPromptTemplate.from_messages([
        SystemMessage(
            content=(
                "You are an expert in the energy market, specializing in analyzing news articles to determine their potential impact on energy market prices.\n"
                "Your task is to classify each news article based on its expected influence on energy prices.\n"
                "Here are the possible scenarios:\n"
                "Bullish: If the news suggests that energy prices will increase.\n"
                "Bearish: If the news suggests that energy prices will decrease.\n"
                "Neutral: If the news have no impact on energy prices.\n"
                "Please review the provided news article and respond with one of the following classifications: Bullish, Bearish, or Neutral.\n"
                "Your response should be concise and limited to just one word.\n"
                "Step 2 | Weighted Score\n"
                "Not all news are equally important.\n"
                "Some news may have a greater impact on energy prices than others.\n"
                "Assign a weighted score to the sentiment classification, reflecting the news article's potential impact on energy prices.\n"
                "Consider the following guidelines when assigning the score:\n"
                "Bullish news: Assign a score between 1 and 3, where:\n"
                "1 indicates a slightly positive impact on energy prices\n"
                "2 indicates a moderately positive impact on energy prices\n"
                "3 indicates a significantly positive impact on energy prices\n"
                "Bearish news: Assign a score between -1 and -3, where:\n"
                "-1 indicates a slightly negative impact on energy prices\n"
                "-2 indicates a moderately negative impact on energy prices\n"
                "-3 indicates a significantly negative impact on energy prices\n"
                "Neutral news: Assign a score of 0, indicating no impact on energy prices.\n"
                "Please respond with a single number from the range (-3 to 3).\n"
                "Here are a few examples:"
            )
        ),
        few_shot_prompt,
        ("human", "{text}")
    ])

    # Chains
    structured_llm = llm.with_structured_output(SentimentOutput)
    structured_llm_claude = llm_claude.with_structured_output(SentimentOutput)
    chain = sentiment_prompt | structured_llm
    chain_claude = sentiment_prompt | structured_llm_claude

    # Get sentiment outputs
    chat_sentiment = chain.invoke({"text": text})
    claude_sentiment = chain_claude.invoke({"text": text})

    print("CHATGPT classification:", chat_sentiment.sentiment)
    print("CHATGPT Score:", chat_sentiment.weight_score)
    print("Claude classification:", claude_sentiment.sentiment)
    print("Claude score:", claude_sentiment.weight_score)

    # LLM voting ensemble
    llm_vote = PromptTemplate(
        input_variables=["data", "sentiment", "weight"],
        template=(
            "You will be given another LLM model's classification of the news article.\n"
            "Sentiment: {sentiment}\nWeighted Score: {weight}\n"
            "Do you agree or disagree with the other model's classification? Provide a brief explanation.\n"
            "Original News: {text}"
        ),
    )

    claude_ensemble = llm_claude.with_structured_output(LLMEnsembleOutput)
    chat_ensemble = llm.with_structured_output(LLMEnsembleOutput)
    evaluation_chain_claude = llm_vote | claude_ensemble
    evaluation_chain_chat = llm_vote | chat_ensemble

    chat_argument = evaluation_chain_chat.invoke({
        "text": text,
        "sentiment": claude_sentiment.sentiment,
        "weight": claude_sentiment.weight_score,
    })
    claude_argument = evaluation_chain_claude.invoke({
        "text": text,
        "sentiment": chat_sentiment.sentiment,
        "weight": chat_sentiment.weight_score,
    })

    print("claude argument:", claude_argument.explanation)
    print("claude weight:", claude_argument.weight_score)
    print("chat argument:", chat_argument.explanation)
    print("chat weight:", chat_argument.weight_score)

    # Final vote
    llm_finalvote = PromptTemplate(
        input_variables=[
            "Sentiment_CHATGPT", "Sentiment_Claude",
            "Weight_CHATGPT", "Weight_Claude",
            "CHATGPT_Argument", "Claude_Argument",
        ],
        template=(
            "You're a trading expert at an energy company.\n"
            "You will receive the sentiment classifications and weight scores from two different LLM models.\n"
            "Here are the sentiments: {Sentiment_CHATGPT} & {Sentiment_Claude}\n"
            "Scores: {Weight_CHATGPT} & {Weight_Claude}\n"
            "Arguments: {CHATGPT_Argument} & {Claude_Argument}\n"
            "Make a final decision on the sentiment classification and weight score."
        ),
    )
    final_chain = llm_finalvote | llm_claude.with_structured_output(FinalVoteOutput)
    final_classification = final_chain.invoke({
        "Sentiment_CHATGPT": chat_sentiment.sentiment,
        "Sentiment_Claude": claude_sentiment.sentiment,
        "Weight_CHATGPT": chat_sentiment.weight_score,
        "Weight_Claude": claude_sentiment.weight_score,
        "CHATGPT_Argument": chat_argument.explanation,
        "Claude_Argument": claude_argument.explanation,
    })

    print("Final Classification:", final_classification.final_sentiment)
    print("Final Score:", final_classification.final_score)

    # Timeframe classification
    def analyze_timeframe_ensemble(text, final_sentiment, final_score, llm_model):
        system_content = (
            f"You are an energy market analyst. Classify the timeframe impact of this news article.\n"
            f"Final Sentiment: {final_sentiment}\n"
            f"Final Weight Score: {final_score}\n"
            "Classification rules:\n"
            "1. If sentiment is 'Neutral' OR weight score is 0: return 'Neutral'\n"
            "2. If sentiment is 'Bullish' or 'Bearish' with weight score != 0, determine timeframe:\n"
            "SHORT TERM: supply disruptions, weather, immediate events\n"
            "LONG TERM: policy, infrastructure, structural changes\n"
            "Choose: Short, Long, or Neutral"
        )
        messages = [
            SystemMessage(content=system_content),
            HumanMessage(content=f"News article: {text}")
        ]
        return llm_model.with_structured_output(TimeframeClassification).invoke(messages)

    timeframe_result = analyze_timeframe_ensemble(
        text, final_classification.final_sentiment, final_classification.final_score, llm_claude
    )

    print("\n" + "="*50)
    print("TIMEFRAME CLASSIFICATION RESULTS")
    print("="*50)
    print(f"Timeframe: {timeframe_result.timeframe}")
    print(f"Reasoning: {timeframe_result.reasoning}")
    print("="*50)

    # Optional: Ensemble timeframe classification
    system_content_alt = (
        f"You are a senior energy trading analyst. Evaluate the timeframe impact of this news.\n"
        f"Final sentiment: {final_classification.final_sentiment} (score: {final_classification.final_score})\n"
        "Guidelines:\n"
        "- Neutral sentiment or 0 score → 'Neutral' timeframe\n"
        "- Immediate operational impacts → 'Short' (0-2 months)\n"
        "- Structural/policy changes → 'Long' (2+ months)\n"
        "Consider both immediate market reactions and underlying structural changes."
    )
    messages_alt = [
        SystemMessage(content=system_content_alt),
        HumanMessage(content=f"Analyze: {text}")
    ]
    timeframe_claude_alt = llm_claude.with_structured_output(TimeframeClassification).invoke(messages_alt)

    print(f"\nTimeframe Ensemble:")
    print(f"Model 1: {timeframe_result.timeframe} - {timeframe_result.reasoning}")
    print(f"Model 2: {timeframe_claude_alt.timeframe} - {timeframe_claude_alt.reasoning}")

    # Simple ensemble logic for timeframe
    if timeframe_result.timeframe == timeframe_claude_alt.timeframe:
        final_timeframe = timeframe_result.timeframe
        final_timeframe_reasoning = f"Both models agree: {timeframe_result.timeframe}"
    elif final_classification.final_score == 0 or final_classification.final_sentiment == "Neutral":
        final_timeframe = "Neutral"
        final_timeframe_reasoning = "Neutral sentiment/score overrides disagreement"
    else:
        final_timeframe = timeframe_result.timeframe
        final_timeframe_reasoning = f"Disagreement resolved: chose {timeframe_result.timeframe}"

    print(f"\nFinal Timeframe: {final_timeframe}")
    print(f"Final Reasoning: {final_timeframe_reasoning}")

    return (
        final_classification.final_sentiment,
        final_classification.final_score,
        final_timeframe,
        final_timeframe_reasoning
    )