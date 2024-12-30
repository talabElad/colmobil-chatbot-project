from langchain_aws import ChatBedrockConverse
from langchain_core.tools import tool

@tool(response_format="content_and_artifact")
def simple_calculator(a: int, b: int):
    """Use this tool to calcuate the sum of two integers.

    Args:
        a (int): The first integer.
        b (int): The second integer.

    Returns:
        int: The sum of the two integers.
    """
    return a + b

llm = ChatBedrockConverse(
    model="us.anthropic.claude-3-5-sonnet-20241022-v2:0",
    temperature=0,
    region_name="us-east-1",
    provider="anthropic"
).bind_tools(tools=[simple_calculator])

a = llm.stream(
    input=[
        ("human", "Hello"),
    ],
)

full = next(a)

for x in a:
    print(x)
    full += x

print(full)