import openai
client = openai.OpenAI(base_url="http://localhost:8000/v1", api_key="none")
print("Sending test...")
response = client.chat.completions.create(model="phi-4", messages=[{"role": "user", "content": "Hi"}])
print(response.choices[0].message.content)