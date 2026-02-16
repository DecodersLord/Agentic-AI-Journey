from google import genai
from google.genai import types
import dotenv



def main():
    api_key = dotenv.get_key(".env", "GEMINI_AI_API");
    client = genai.Client(api_key=api_key);

    analyze_code_function = {
        "name": "analyze_code",
        "description": "Analyze the code and return the number of lines, functions, and classes",
        "parameters": {
            "type": "object",
            "properties": {
                "code": {
                    "type": "string",
                    "description": "The code to analyze"
                }
            },
            "required": ["code"]
        }
    }

    tools = types.Tool(
        function_declarations=[
            analyze_code_function
        ]
    )

    config = types.GenerateContentConfig(
        tools=[tools]
    )

    while True:
        user_code = input("enter your code:");

        if user_code != "":

            response = client.models.generate_content(model="gemini-3-flash-preview", contents=user_code, config=config);
            print(response);

            if (response.candidates[0].content.parts[0].function_call):
                function_call = response.candidates[0].content.parts[0].function_call;
                function_name = function_call.name;
                function_args = function_call.args;
                
                result = analyze_code(function_call.args["code"])

                final_response = client.models.generate_content(
                    model="gemini-3-flash-preview",
                    contents=f"The user asked to analyze this code: {user_code}\n\nHere is the analysis result: {result}\n\nPlease summarize the analysis for the user."
                );
                print(final_response.text);
                break;
            else:
                print(response.text);
                break;
        else:
            print("Please enter a valid code");

def analyze_code(user_code):
    lines = len(user_code.split("\n"));
    function = user_code.count("def");
    classes = user_code.count("class");
    
    return {"lines":lines,"function":function,"class":classes}



if __name__ == "__main__":
    main()