from langchain_core.messages import AIMessage, HumanMessage

from rag_chatbot.services.chat_engine import ChatEngine


class FakeChatResponse:
    def __init__(self, content: str) -> None:
        self.content = content


class FakeChatModel:
    def __init__(self) -> None:
        self.invoked_messages = []

    def invoke(self, messages):
        self.invoked_messages.append(messages)
        return FakeChatResponse("Mocked model answer.")


def test_send_message_without_context_does_not_call_model() -> None:
    fake_model = FakeChatModel()
    engine = ChatEngine(chat_model=fake_model)

    response = engine.send_message("What is this about?", context="")

    assert response == (
        "I cannot answer this question without document context. "
        "Please upload a relevant PDF or text file first."
    )
    assert fake_model.invoked_messages == []
    assert engine.chat_history == []


def test_send_message_with_context_calls_model_and_saves_history() -> None:
    fake_model = FakeChatModel()
    engine = ChatEngine(chat_model=fake_model)

    response = engine.send_message(
        user_message="What is attention?",
        context="Attention is a mechanism used in transformers.",
    )

    assert response == "Mocked model answer."
    assert len(fake_model.invoked_messages) == 1

    assert len(engine.chat_history) == 2
    assert isinstance(engine.chat_history[0], HumanMessage)
    assert isinstance(engine.chat_history[1], AIMessage)
    assert engine.chat_history[0].content == "What is attention?"
    assert engine.chat_history[1].content == "Mocked model answer."


def test_reset_conversation_clears_chat_history() -> None:
    fake_model = FakeChatModel()
    engine = ChatEngine(chat_model=fake_model)

    engine.send_message(
        user_message="Summarise this.",
        context="This is some document context.",
    )

    result = engine.reset_conversation()

    assert result == "Conversation history has been reset."
    assert engine.chat_history == []