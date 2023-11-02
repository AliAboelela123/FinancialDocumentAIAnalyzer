from langchain.prompts import (
    ChatPromptTemplate,
    MessagesPlaceholder,
    SystemMessagePromptTemplate,
    HumanMessagePromptTemplate,
)
from langchain.chains import LLMChain # Library for facilitating conversations
from langchain.chat_models import ChatOpenAI # The open AI model
from langchain.memory import ConversationBufferMemory # Giving our model memory of the chat history

# LLM
llm = ChatOpenAI(temperature=0, openai_api_key="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")

# Prompt: Anytime a query is made, a prompt is constructed which contains more than just the query itself
prompt = ChatPromptTemplate(
    input_variables=[
        "system_msg",
        "chat_history",
        "question"
    ],
    messages=[
        # This system message will appear in any prompt, every time
        SystemMessagePromptTemplate.from_template("{system_msg}"),
        # The `variable_name` here is what must align with memory. This here will be the chat history.
        MessagesPlaceholder(variable_name="chat_history"),
        # Since we use {} we define a variable. This variable represents any system messages we might want to modify mid session
        SystemMessagePromptTemplate.from_template("{context}"),
        # Since we use {} we define a variable. This variable represents the user's query.
        HumanMessagePromptTemplate.from_template("{question}")
    ]
)

# Notice that we `return_messages=True` to fit into the MessagesPlaceholder
# Notice that `"chat_history"` aligns with the MessagesPlaceholder name
memory = ConversationBufferMemory(memory_key="chat_history", input_key="question", return_messages=True)
conversation = LLMChain(
    llm=llm,
    prompt=prompt,
    verbose=True,
    memory=memory
)

def get_response(query, complexity, context=None):
    # Set the system message (complexity & context)
    system_msg = "You are a friendly chatbot having a conversation with a human. You are an expert in finance. The user you are speaking with has a " + complexity + " understanding of finance."
    if context == None:
        context_msg = ""
    else:
        context_msg = "The user has uploaded a document. A relevant excerpt from the document has been provided. It may assist you with the user's next question: <START_EXCERPT>" + context + " <END_EXCERPT>"
    result = conversation({"question": query, "system_msg": system_msg, "context": context_msg})
    return result["text"]