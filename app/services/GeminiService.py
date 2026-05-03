import google.generativeai as genai

from app.core.Config import Config
genai.configure(api_key=Config.GEMINI_API_KEY)

def GetModel(ModelName: str = "gemini-2.5-flash", SystemInstruction: str = None):
    try:
        Options = {"model_name": ModelName}
        if SystemInstruction:
            Options["system_instruction"] = SystemInstruction
        return genai.GenerativeModel(**Options)
    except Exception as Error:
        raise Error

async def GenerateText(Model, Prompt: str) -> str:
    try:
        Response = await Model.generate_content_async(Prompt)
        return Response.text
    except Exception as Error:
        raise Error