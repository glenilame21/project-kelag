import getpass
import os
import httpx
import json
from dotenv import load_dotenv
from langchain.schema.runnable import RunnableLambda
from langchain_core.prompts import (
    PromptTemplate,
    FewShotChatMessagePromptTemplate,
    ChatPromptTemplate,
)
from langchain_openai import ChatOpenAI
from langchain_anthropic import ChatAnthropic
import langchain_core.prompts
from typing import Optional
from pydantic import BaseModel, Field
from langchain_core.messages import HumanMessage, SystemMessage


def SENTIMENT_CLF(text):
    """
    BECAUSE AN ANSAMBLE OF LLMS IS PROPOSED IF YOU WANT TO ADD A THIRD OR FOURTH MODEL YOU CAN DO SO HERE
    ADD THE API KEY TO THE ENV LIST AND ADD THE MODEL TO THE MODELS LIST
    MAKE SURE TO CREATE AN INSTANCE OF THE MODEL AND ALSO PASS IT DOWN THE CHAINS
    """
    if load_dotenv():
        print("Loading .env file")
    else:
        print("No .env file found")
    
    OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
    ANTHROPIC_API_KEY = os.getenv("ANTHROPIC_API_KEY")

    if not OPENAI_API_KEY or not ANTHROPIC_API_KEY:
        raise ValueError("API keys for OpenAI or Anthropic are missing")
    """
HERE WE DEFINE THE FEW SHOTS AND HOW THEY ARE EXPTECTED BY THE MODEL
CURRENTLY STORED IN A JSON FILE AND TRANSFORMED INTO A LIST FURTHER DOWN IN THE CODE
"""
    sentiment_fewshots = PromptTemplate.from_template("Input: {input}\n{output}")

    with open(
        "C:/Users/Z_LAME/Desktop/Crawler/Lang Chain/fewshotsrandom.json",
        encoding="latin",
    ) as f:
        few_shots = json.load(f)

    sentiment_examples = [
        {
            "input": f"""Title: {example['title']}\n Subtitle: {example['subtitle']}\n Body: {example['body']}""",
            "output": example["Sentiment"],
        }
        for example in few_shots
    ]

    sentiment_example_prompt = ChatPromptTemplate.from_messages(
        [
            ("human", "{input}"),
            ("ai", "{output}"),
        ]
    )
    few_shot_prompt = FewShotChatMessagePromptTemplate(
        example_prompt=sentiment_example_prompt,
        examples=sentiment_examples,
    )

    """" 
HERE WE CREATE INSTANCES OF THE LLMS
I HAVE COMMENTED OUT THE MAX TOKENS PARAMETER BECAUSE WE ARE NOW USING STRUCTURED OUTPUTS
"""

    llm = ChatOpenAI(
        model="gpt-4o",
        temperature=0.1,
        # max_tokens=1,
        timeout=None,
        max_retries=2,
    )

    ## create the model instance for claude - we load the model and assign the max tokens to 3 so that it outputs only 3 tokens - Bullish, Bearish or Neutral
    llm_claude = ChatAnthropic(
        model="claude-3-5-sonnet-20240620",
        temperature=0.1,
        # max_tokens=3,
        timeout=None,
        max_retries=2,
    )

    # First class for structured output is here
    # classification and a weight score is given by the model/s
    class sentiment(BaseModel):
        sentiment: str = Field(
            description="Sentiment Classification with respect to energy market prices, should be one of 'Bearish', 'Bullish', 'Neutral'"
        )
        weight_score: float = Field(description="Weighted score of the sentiment")

    ## prompt for classyfing the sentiment and giving a weight score
    ## do not change unless you're a trader or a financial analyst
    prompt = ChatPromptTemplate.from_messages([
        SystemMessage(
            content="""
            You are an expert in the energy market, specializing in analyzing news articles to determine their potential impact on energy market prices.
            Your task is to classify each news article based on its expected influence on energy prices.
            Here are the possible scenarios:
            Bullish: If the news suggests that energy prices will increase.
            Bearish: If the news suggests that energy prices will decrease.
            Neutral: If the news have no impact on energy prices.
            Please review the provided news article and respond with one of the following classifications: Bullish, Bearish, or Neutral.
            Your response should be concise and limited to just one word.
            Step 2 | Weighted Score
            Not all news are equally important.
            Some news may have a greater impact on energy prices than others.
            Assign a weighted score to the sentiment classification, reflecting the news article's potential impact on energy prices.
            Consider the following guidelines when assigning the score:
            Bullish news: Assign a score between 1 and 3, where:
            1 indicates a slightly positive impact on energy prices
            2 indicates a moderately positive impact on energy prices
            3 indicates a significantly positive impact on energy prices
            Bearish news: Assign a score between -1 and -3, where:
            -1 indicates a slightly negative impact on energy prices
            -2 indicates a moderately negative impact on energy prices
            -3 indicates a significantly negative impact on energy prices
            Neutral news: Assign a score of 0, indicating no impact on energy prices.
            Please respond with a single number from the range (-3 to 3).
            Here are a few examples:"""
    ),
    few_shot_prompt,
    HumanMessage(content="{text}")
])
    
    """ 
CHAINING THE MODELS WITH THE PROMPTS + STRUCTURED OUTPUTS

"""

    structured_llm = llm.with_structured_output(sentiment)
    chain = prompt | structured_llm

    structured_llm_claude = llm_claude.with_structured_output(sentiment)
    chain_claude = prompt | structured_llm_claude

    ## Here we invoke the models to get the sentiment and the weight score
    chat_sentiment = chain.invoke({"text": text})
    claude_sentiment = chain_claude.invoke({"text": text})

    ## print the sentiment and the weight score
    print("CHATGPT classification: ", chat_sentiment.sentiment)
    print("CHATGPT Score: ", chat_sentiment.weight_score)

    ## print claude sentiment and the weight score
    print("Claude classification: ", claude_sentiment.sentiment)
    print("Claude score: ", claude_sentiment.weight_score)

    """
NOW WE WILL MOVE INTO THE LLM VOTING ENSAMBLE
WE WILL CREATE A LIST OF MODELS AND PASS THE TEXT TO EACH MODEL ALONGSIDE THE PREVIOUS CLASSIFICATION THAT WAS MADE
"""

    llm_vote = PromptTemplate(
        input_variables=["data", "sentiment", "weight"],
        template="""
    You will be given another LLM model's classification of the news article.
    Remember, you are still  an expert in the energy market, specializing in analyzing news articles to determine their potential impact on energy market prices.
    For your niche consider the following fact table:
    Bullish: If the news suggests that energy prices will increase.
    Bearish: If the news suggests that energy prices will decrease.
    Neutral: If the news have no impact on energy prices.
    Your task is to review both classifications and say how much you agree with the other model's classification.
    Sentiment: {sentiment}
    Weighted Score: {weight}
    Do you agree with the other model's classification? If so, please provide a brief explanation.
    If you think the classification is incorrect, please explain why.
    Start the answer with " I Agree" or "I Disagree" and then provide your reasoning.
    This is the news article:
    Original News: {text}
    """,
    )

    # structured output for the llm vote
    class llm_ensamble(BaseModel):
        explination: str = Field(
            description="Give a brief explonation with max 150 tokens on why you think the sentiment is correct or incorrect"
        )
        weight_score: float = Field(
            description="Based on your explonation also say if you think the weight score is correct or incorrect"
        )

    claude_ensamble = llm_claude.with_structured_output(llm_ensamble)
    chat_ensamble = llm.with_structured_output(llm_ensamble)

    evaluation_chain_claude = llm_vote | claude_ensamble
    evaluation_chain_chat = llm_vote | chat_ensamble

    chat_argument = evaluation_chain_chat.invoke(
        {
            "text": text,
            "sentiment": claude_sentiment.sentiment,
            "weight": claude_sentiment.weight_score,
        }
    )
    claude_argument = evaluation_chain_claude.invoke(
        {
            "text": text,
            "sentiment": chat_sentiment.sentiment,
            "weight": chat_sentiment.weight_score,
        }
    )

    print("claude argument: ", claude_argument.explination)
    print("claude weight: ", claude_argument.weight_score)

    print("chat argument: ", chat_argument.explination)
    print("chat weight: ", chat_argument.weight_score)

    """ 

FINAL SAY
I HAVE LET CLAUDE DO THE FINAL JUDGEMENT, YOU CAN CHANGE THE MODEL THAT MAKES THE FINAL JUDGMENT BELOW

"""

    llm_finalvote = PromptTemplate(
        input_variables=[
            "Sentiment_CHATGPT",
            "Sentiment_Claude",
            "Weight_CHATGPT",
            "Weight_Claude",
            "CHATGPT_Argument",
            "Claude_Argument",
        ],
        template=f"""
        You're a trading expert at an energy company that trades energy on the spot and future markets.
        You will receive the sentiment classifications and weight scores from two different LLM models.
        You will also receive an argument for each classification from the opposing model.
        You task is to review all outouputs and make a final decision.
        Remember that as an energy company we want to gauge the market right - so news that have no impact to the spot and future market must be classifed as neutral with weight 0.
        Follow the same logic for Bullish and Bearish news. Bullish when the news suggests that energy prices will increase and Bearish when the news suggests that energy prices will decrease.
        Here are the sentiments from the other 2 agents: {{Sentiment_CHATGPT}} & {{Sentiment_Claude}},
        Here are their respective impact scores: {{Weight_CHATGPT}} & {{Weight_Claude}}, 
        Here are the arguments from the opposing model {{CHATGPT_Argument}} & {{Claude_Argument}}.
        Your task is to review all outputs and make a final decision on the sentiment classification and weight score.
        Now, based on the provided inputs, please provide a final sentiment classification and weight score.
        """,
    )

    class final_vote(BaseModel):
        final_sentiment: str = Field(
            description="Final Sentiment Classification after reviewing both models outputs & arguments. "
        )
        final_score: int = Field(
            description="Final Score of the sentiment after reviewing both models & arguments. It should still remain within the range of -3 to 3"
        )

    final_chain = llm_finalvote | llm_claude.with_structured_output(final_vote)

    final_classification = final_chain.invoke(
        {
            "Sentiment_CHATGPT": chat_sentiment.sentiment,
            "Sentiment_Claude": claude_sentiment.sentiment,
            "Weight_CHATGPT": chat_sentiment.weight_score,
            "Weight_Claude": claude_sentiment.weight_score,
            "CHATGPT_Argument": chat_argument.explination,
            "Claude_Argument": claude_argument.explination,
        }
    )

    print("Final Classification: ", final_classification.final_sentiment)
    print("Final Score: ", final_classification.final_score)

    return final_classification.final_sentiment, final_classification.final_score


# Kelag_Sentiment()
