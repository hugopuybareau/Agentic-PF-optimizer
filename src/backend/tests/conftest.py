import os
from unittest.mock import MagicMock, patch

import pytest

# Set test environment variables - load the actual Azure key from .env
from dotenv import load_dotenv

load_dotenv()

os.environ["ENVIRONMENT"] = "test"

@pytest.fixture(autouse=True)
def mock_azure_openai():
    """Mock Azure OpenAI API calls"""
    with patch('silveragents.agents.chat_agent.AzureChatOpenAI') as mock_llm_class:
        mock_instance = MagicMock()

        # Mock intent classification responses
        def mock_invoke(messages):
            # Extract content from message list (formatted messages from ChatPromptTemplate)
            content = ""
            if hasattr(messages, '__iter__'):
                for msg in messages:
                    if hasattr(msg, 'content'):
                        content += msg.content + " "
                    else:
                        content += str(msg) + " "
            else:
                content = str(messages)

            content = content.lower()

            if "that's all" in content:
                return MagicMock(content="complete_portfolio")
            elif "100 shares of apple" in content or ("shares" in content and "apple" in content):
                return MagicMock(content="add_asset")
            elif "remove tesla" in content:
                return MagicMock(content="remove_asset")
            elif "show me my current portfolio" in content:
                return MagicMock(content="list_assets")
            elif "hello" in content:
                return MagicMock(content="greeting")
            elif "pe ratio" in content:
                return MagicMock(content="ask_question")
            else:
                return MagicMock(content="unclear")

        mock_instance.invoke = mock_invoke
        mock_llm_class.return_value = mock_instance
        yield mock_instance

@pytest.fixture
def mock_entity_extraction():
    """Mock entity extraction"""
    with patch('silveragents.agents.chat_agent.ChatAgent._extract_entities') as mock_extract:
        def mock_extraction(state):
            message = state.get("user_message", "")
            entities = {}

            if "100 shares of AAPL" in message:
                entities = {"type": "stock", "ticker": "AAPL", "shares": 100}
            elif "0.5 Bitcoin" in message:
                entities = {"type": "crypto", "symbol": "BTC", "amount": 0.5}
            elif "house at 123 Main St is worth $500k" in message:
                entities = {"type": "real_estate", "address": "123 Main St", "value": 500000}

            state["entities"] = entities
            return state

        mock_extract.side_effect = mock_extraction
        yield mock_extract
