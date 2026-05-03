import json
import logging
from dataclasses import dataclass

from app.Core.Config import Config
from app.Services.GeminiService import GenerateText, GetModel

Logger = logging.getLogger(__name__)

ClassifierPrompt = """You are a strict question classifier. Determine whether the user's input is a general knowledge question.

General knowledge topics INCLUDE:
  history, science, geography, literature, art, music, sports, mathematics (facts only),
  technology facts, culture, nature, biology, astronomy, mythology, language, politics (historical/factual),
  economics (factual), philosophy, religion (factual), famous people, world records, trivia.

Topics that are NOT general knowledge:
  coding help, programming tasks, personal advice, medical advice, legal advice, financial advice,
  creative writing, essay writing, translation, arithmetic calculations, opinion-based questions,
  therapy, relationship advice, current news commentary, recipes, how-to instructions.

Respond with ONLY a valid JSON object — no markdown fences, no extra text:
{{"isGeneralKnowledge": true|false, "category": "<topic or 'out-of-scope'>", "reason": "<one sentence>"}}

User input: """

AnswerSystemPrompt = """You are Know-Genius, a warm, enthusiastic, and knowledgeable general knowledge assistant.

Personality and tone:
- Friendly, approachable, and encouraging.
- Use clear, well-structured answers with a conversational feel.
- If a question has a fascinating backstory, briefly share it.

Strict rules:
- ONLY answer general knowledge questions (history, science, geography, literature, art, music,
  sports, technology facts, culture, nature, language, famous people, trivia, etc.).
- Politely decline anything outside general knowledge and suggest a relevant question instead.
- Never provide medical, legal, or financial advice.
- Never write, debug, or explain code.
- Keep answers accurate and honest."""

def BuildOutOfScopeMessage(Category: str) -> str:
    try:
        return (
            f"I specialise exclusively in **general knowledge** — things like history, science, "
            f"geography, art, and fascinating facts about the world!\n\n"
            f"Your question falls under **{Category}**, which is outside my area of expertise.\n\n"
            f"Here are some things you can ask me:\n"
            f'- "What is the largest ocean on Earth?"\n'
            f'- "Who discovered penicillin?"\n'
            f'- "Which artist painted the Sistine Chapel ceiling?"\n\n'
            f"Feel free to ask anything from the world of general knowledge!"
        )
    except Exception as Error:
        raise Error

@dataclass
class Classification:
    IsGeneralKnowledge: bool
    Category: str
    Reason: str

@dataclass
class AgentResponse:
    Answer: str
    Category: str
    AnsweredByAgent: bool

class KnowledgeAgent:
    def __init__(self):
        self.Classifier = GetModel(Config.GEMINI_MODEL)
        self.Answerer = GetModel(Config.GEMINI_MODEL, AnswerSystemPrompt)

    async def Classify(self, Question: str) -> Classification:
        try:
            Raw = await GenerateText(self.Classifier, ClassifierPrompt + Question)
            Cleaned = Raw.strip().removeprefix("```json").removeprefix("```").removesuffix("```").strip()
            Data = json.loads(Cleaned)
            return Classification(
                IsGeneralKnowledge=bool(Data.get("isGeneralKnowledge", True)),
                Category=Data.get("category", "unknown"),
                Reason=Data.get("reason", ""),
            )
        except Exception:
            Logger.warning("Classifier parse failed; defaulting to general knowledge.", exc_info=True)
            return Classification(IsGeneralKnowledge=True, Category="unknown", Reason="parse error")

    async def Answer(self, Question: str, History: list) -> str:
        try:
            GeminiHistory = [
                {
                    "role": "model" if Msg["role"] == "assistant" else "user",
                    "parts": [Msg["content"]],
                }
                for Msg in History
            ]
            Chat = self.Answerer.start_chat(history=GeminiHistory)
            Response = await Chat.send_message_async(Question)
            return Response.text
        except Exception as Error:
            raise Error

    async def Process(self, Question: str, History: list = None) -> AgentResponse:
        try:
            Result = await self.Classify(Question)
            if not Result.IsGeneralKnowledge:
                return AgentResponse(
                    Answer=BuildOutOfScopeMessage(Result.Category),
                    Category=Result.Category,
                    AnsweredByAgent=False,
                )
            AnswerText = await self.Answer(Question, History or [])
            return AgentResponse(
                Answer=AnswerText,
                Category=Result.Category,
                AnsweredByAgent=True,
            )
        except Exception as Error:
            raise Error

KnowledgeAgentInstance = KnowledgeAgent()