from pydantic_ai import Agent

agent = Agent('gemini-2.0-flash')

result_sync = agent.run_sync(user_prompt= 'What is the capital of Italy?')
print(result_sync.output)