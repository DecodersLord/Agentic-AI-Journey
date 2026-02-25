import sys
import os
import json

from google import genai
from google.genai import types
import dotenv

# Add the parent directory so we can import from the tools/ folder
sys.path.append(os.path.join(os.path.dirname(__file__), ".."))
from tools.analyze_code import analyze_code_declaration, analyze_code


def main():
    api_key = dotenv.get_key(".env", "GEMINI_AI_API")
    client = genai.Client(api_key=api_key)

    # Register the analyze_code tool with Gemini
    tools = types.Tool(function_declarations=[analyze_code_declaration])
    config = types.GenerateContentConfig(
        tools=[tools],
        system_instruction=(
            "You are a code analysis agent. "
            "When the user provides any code snippet, you MUST use the analyze_code tool to analyze it. "
            "Do not try to analyze code yourself — always use the tool first. "
            "After receiving the tool result, provide a clear and friendly summary of the analysis. "
            "If the user asks follow-up questions about the code (like improvements or suggestions), "
            "use the tool results you already have and your own knowledge to give helpful advice."
        ),
    )

    # Map tool names to their Python functions
    available_tools = {
        "analyze_code": analyze_code,
    }

    # Conversation history — this is what gives the agent "memory"
    # Each item is a types.Content object (a message from the user or the model)
    history = []

    print("🤖 Code Analyzer Agent")
    print("Type 'exit' to quit.\n")

    while True:
        user_input = input("You: ").strip()

        if user_input.lower() in ("exit", "quit"):
            print("Goodbye!")
            break

        if not user_input:
            continue

        # Add the user's message to the conversation history
        history.append(types.Content(role="user", parts=[types.Part.from_text(text=user_input)]))

        # Step 1: Send the FULL history to Gemini (not just the latest message)
        response = client.models.generate_content(
            model="gemini-3-flash-preview",
            contents=history,
            config=config,
        )

        part = response.candidates[0].content.parts[0]

        # Step 2: If Gemini wants to call a tool, execute it and send the result BACK
        if part.function_call:
            name = part.function_call.name
            args = dict(part.function_call.args)

            print(f"\n🔧 Using tool: {name}")
            result = available_tools[name](**args)
            print(f"📊 Tool Result: {json.dumps(result, indent=2)}")

            # Add Gemini's tool call to history (so it remembers it asked for this)
            history.append(response.candidates[0].content)

            # Now send the tool result BACK to Gemini so it can reason about it
            tool_response = types.Content(
                role="user",
                parts=[types.Part.from_function_response(
                    name=name,
                    response=result,
                )],
            )
            history.append(tool_response)

            # Step 3: Gemini now sees the tool result and can write a proper response
            follow_up = client.models.generate_content(
                model="gemini-3-flash-preview",
                contents=history,
                config=config,
            )

            agent_reply = follow_up.text
            print(f"\nAgent: {agent_reply}")

            # Add the agent's final reply to history too
            history.append(follow_up.candidates[0].content)

        # Step 4: If Gemini just wants to talk (no tool needed), print its response
        else:
            agent_reply = response.text
            print(f"\nAgent: {agent_reply}")

            # Add the agent's reply to history
            history.append(response.candidates[0].content)


if __name__ == "__main__":
    main()