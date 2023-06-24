import os

from dotenv import load_dotenv
from langchain import ConversationChain
from langchain.agents import AgentType, initialize_agent, load_tools
from langchain.chains import LLMChain
from langchain.llms import OpenAI
from langchain.prompts import PromptTemplate

load_dotenv()


def main():
    llm = OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"))
    # prompt = "What is the fastest car in the world?"
    # response = llm(prompt=prompt)

    template = PromptTemplate(
        input_variables=["country", "property"],
        template="What is the {property} of {country}?",
    )
    chain = LLMChain(llm=llm, prompt=template)
    response = chain.run(country="Adelaide", property="population")
    print(response)


def agent():
    llm = OpenAI(openai_api_key=os.getenv("OPENAI_API_KEY"), temperature=0)
    tools = load_tools(["serpapi", "llm-math"], llm=llm)
    agent = initialize_agent(
        tools,
        llm,
        agent=AgentType.ZERO_SHOT_REACT_DESCRIPTION,
        verbose=True,
    )
    agent.run(
        (
            "What was the high temperature in SF yesterday in Fahrenheit?"
            " What is that number raised to the .023 power?"
        )
    )


def conversation():
    llm = OpenAI(temperature=0)
    conversation = ConversationChain(llm=llm, verbose=True)
    response = conversation.predict(input="How can I optimize a pytorch model for deployment on a GPU?")
    print(response)
    response = conversation.predict(input="How can I achieve this if I'm coding in C++?")
    print(response)


if __name__ == "__main__":
    conversation()
