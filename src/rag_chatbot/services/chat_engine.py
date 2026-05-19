from langchain_core.messages import AIMessage, BaseMessage, HumanMessage
from langchain_core.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI


class ChatEngine:
    def __init__(self, chat_model: ChatOpenAI) -> None:
        self.chat_model = chat_model
        self.chat_history: list[BaseMessage] = []

        self.system_prompt = (
            "You are a helpful RAG assistant. Answer the user's question using only "
            "the provided context. If the context is empty or does not contain the "
            "answer, say that you cannot answer from the uploaded documents."
        )

        self.prompt = ChatPromptTemplate.from_messages(
            [
                ("system", self.system_prompt),
                MessagesPlaceholder(variable_name="chat_history"),
                (
                    "human",
                    "Context:\n{context}\n\nQuestion:\n{question}",
                ),
            ]
        )

    def send_message(self, user_message: str, context: str = "") -> str:
        if not context.strip():
            return (
                "I cannot answer this question without document context. "
                "Please upload a relevant PDF or text file first."
            )

        messages = self.prompt.format_messages(
            chat_history=self.chat_history,
            context=context,
            question=user_message,
        )

        response = self.chat_model.invoke(messages)

        self.chat_history.append(HumanMessage(content=user_message))
        self.chat_history.append(AIMessage(content=response.content))

        return response.content

    def reset_conversation(self) -> str:
        self.chat_history = []
        return "Conversation history has been reset."