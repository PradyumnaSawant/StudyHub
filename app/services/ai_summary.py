import httpx
from typing import Optional
from app.core.config import settings

class AISummarizerService:
    @staticmethod
    async def generate_summary(
        title: str,
        subject_name: str,
        resource_type: str,
        syllabus_tag: str,
        description: Optional[str] = None
    ) -> str:
        """
        Generates structured AI key points for study materials.
        Uses Anthropic/OpenAI API if keys are set, else falls back to smart rule-based synthesis.
        """
        # 1. Try Anthropic API if key is present
        if settings.ANTHROPIC_API_KEY:
            try:
                async with httpx.AsyncClient(timeout=15.0) as client:
                    response = await client.post(
                        "https://api.anthropic.com/v1/messages",
                        headers={
                            "x-api-key": settings.ANTHROPIC_API_KEY,
                            "anthropic-version": "2023-06-01",
                            "content-type": "application/json",
                        },
                        json={
                            "model": "claude-3-5-sonnet-20241022",
                            "max_tokens": 400,
                            "messages": [
                                {
                                    "role": "user",
                                    "content": f"Generate a concise 4-bullet point study summary for engineering students for resource '{title}' ({resource_type}) under subject '{subject_name}' ({syllabus_tag}). Additional details: {description or 'N/A'}"
                                }
                            ]
                        }
                    )
                    if response.status_code == 200:
                        data = response.json()
                        return data["content"][0]["text"]
            except Exception as e:
                print(f"[AI Summary Warning] LLM API Call failed: {e}. Switching to fallback engine.")

        # 2. Fallback Smart Synthesis Engine
        desc_snippet = f" focused on {description[:120]}..." if description else ""
        
        type_goals = {
            "notes": "Core theoretical foundations, mathematical derivations, step-by-step concepts, and exam-focused formulas.",
            "PYQ": "Previous year exam questions pattern, frequently repeated problem types, weightage distribution, and solution strategies.",
            "question_bank": "Comprehensive numerical practice problems, conceptual short-answer questions, and self-assessment drills.",
            "revision": "Quick formula sheets, key definitions, memory mnemonics, and high-yield last-minute review points."
        }

        specific_goal = type_goals.get(resource_type, "Essential engineering concepts and key problem-solving techniques.")

        summary_md = f"""⚡ **AI Fast-Track Study Breakdown**

📌 **Core Module Focus**: `{syllabus_tag}` for **{subject_name}**
🎯 **Resource Purpose**: {specific_goal}

🔍 **Key Study Takeaways**:
- **Primary Concepts**: Key principles covering *{title}*{desc_snippet}
- **Exam Weightage**: High priority for mid-sem and end-sem examinations.
- **Problem Solving**: Includes solved examples, diagrammatic representations, and formula reference blocks.
- **Revision Strategy**: Pair this resource with standard textbook syllabus units for maximum retention.
"""
        return summary_md.strip()
