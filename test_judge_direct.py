"""
test_judge_direct.py - Directly test Ollama mistral model with format="json"
"""

from langchain_ollama import ChatOllama
import json

print("=" * 70)
print("       STEP 3: DIRECT TESTING OF OLLAMA MISTRAL (format='json')")
print("=" * 70)

llm = ChatOllama(model="mistral", format="json", temperature=0)

prompt = """Extract the key facts from the text as a JSON object with a single key 'statements' containing a list of string statements.
Text: Paris is the capital of France.
Return ONLY valid JSON complying with: {"statements": ["..."]}"""

print("\nInvoking ChatOllama(model='mistral', format='json')...")
response = llm.invoke(prompt)

raw_content = response.content
print("\n--- RAW MODEL RESPONSE ---")
print(repr(raw_content))

# Verify strict JSON parsing
try:
    parsed = json.loads(raw_content)
    print("\n--- JSON PARSE SUCCESS ---")
    print("Parsed Object:", parsed)
    if "statements" in parsed and isinstance(parsed["statements"], list):
        print("\n✅ PASSED STEP 3: Model returns valid JSON conforming to the schema!")
    else:
        print("\n❌ FAILED STEP 3: JSON keys do not match schema.")
except Exception as e:
    print(f"\n❌ FAILED STEP 3: Output is not valid JSON! Error: {e}")
