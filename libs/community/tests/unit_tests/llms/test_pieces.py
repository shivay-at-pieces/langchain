import unittest
from unittest.mock import Mock
from unittest.mock import patch
from langchain_core.outputs import GenerationChunk, LLMResult
from typing import Any, List, Mapping, Optional, Iterator
from langchain_core.callbacks import CallbackManagerForLLMRun
from langchain_core.language_models.llms import BaseLLM
from langchain_core.outputs import GenerationChunk, LLMResult
from langchain_community.llms.pieces import PiecesOSLLM  
from pieces_copilot_sdk import PiecesClient

class TestPiecesOSLLM(unittest.TestCase):

    def setUp(self):
        self.mock_copilot = Mock()
        self.mock_client = Mock(spec=PiecesClient)
        self.mock_client.copilot = self.mock_copilot
        self.mock_client.available_models_names = [
            '(Gemini) Chat Model', '(PaLM2) Chat Model', 'GPT-3.5-turbo-16k Chat Model',
            'Claude 3 Sonnet Chat Model', 'Gemini-1.5 Flash Chat Model', 'Claude 3.5 Sonnet Chat Model',
            'GPT-3.5-turbo Chat Model', 'GPT-4 Turbo Chat Model', 'Codey (PaLM2) Chat Model',
            'Claude 3 Opus Chat Model', 'GPT-4 Chat Model', 'Gemini-1.5 Pro Chat Model',
            'Claude 3 Haiku Chat Model', 'GPT-4o Mini Chat Model', 'GPT-4o Chat Model'
        ]
        self.llm = PiecesOSLLM(client=self.mock_client)

    def test_llm_type(self):
        self.assertEqual(self.llm._llm_type, "pieces_os")

    def test_identifying_params(self):
        self.assertEqual(self.llm._identifying_params, {"model": "pieces_os"})

    def test_call(self):
        mock_response = Mock()
        mock_response.question.answers = [Mock(text="Test answer")]
        self.mock_copilot.ask_question.return_value = mock_response

        result = self.llm._call("Test prompt")
        self.assertEqual(result, "Test answer")
        self.mock_copilot.ask_question.assert_called_once_with("Test prompt")

    def test_call_error(self):
        self.mock_copilot.ask_question.side_effect = Exception("API Error")
        result = self.llm._call("Test prompt")
        self.assertEqual(result, "Error asking question")

    def test_generate(self):
        mock_response = Mock()
        mock_response.question.answers = [Mock(text="Test answer")]
        self.mock_copilot.ask_question.return_value = mock_response

        result = self.llm._generate(["Test prompt 1", "Test prompt 2"])
        self.assertIsInstance(result, LLMResult)
        self.assertEqual(len(result.generations), 2)
        self.assertEqual(result.generations[0][0].text, "Test answer")
        self.assertEqual(result.generations[1][0].text, "Test answer")

    def test_stream(self):
        mock_response = Mock()
        mock_response.question.answers.iterable = [
            Mock(text="Test "),
            Mock(text="streaming "),
            Mock(text="response")
        ]
        self.mock_copilot.stream_question.return_value = [mock_response]

        result = list(self.llm.stream("Test prompt"))
        self.assertEqual(len(result), 3)
        self.assertEqual("".join(chunk.text for chunk in result), "Test streaming response")

    def test_get_supported_models(self):
        supported_models = self.llm.get_supported_models()
        self.assertIsInstance(supported_models, list)
        self.assertEqual(supported_models, self.mock_client.available_models_names)

    def test_set_model_valid(self):
        self.llm.set_model("GPT-4 Chat Model")
        self.assertEqual(self.llm.model, "GPT-4 Chat Model")

    def test_set_model_invalid(self):
        invalid_model = "INVALID_MODEL"
        self.llm.set_model(invalid_model)
        self.assertEqual(self.llm.model, invalid_model)
        print_patch = patch('builtins.print')
        with print_patch as mock_print:
            self.llm.set_model(invalid_model)
            mock_print.assert_called_once_with(f"Model set to {invalid_model}.")

if __name__ == "__main__":
    unittest.main()
