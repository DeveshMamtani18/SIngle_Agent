import os
import requests
import streamlit as st

from dotenv import load_dotenv
from langchain.tools import tool
from langchain_groq import ChatGroq
from langchain_community.tools.tavily_search import TavilySearchResults
from langchain.agents import create_agent


# ============================================================
# LOAD ENVIRONMENT VARIABLES
# ============================================================

load_dotenv()

groq_api_key = os.getenv("GROQ_API_KEY")
tavily_api_key = os.getenv("TAVILY_API_KEY")
weather_api_key = os.getenv("WEATHER_API_KEY")


# ============================================================
# STREAMLIT CONFIG
# ============================================================

st.set_page_config(
    page_title="AI Agent",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)


# ============================================================
# CUSTOM CSS
# ============================================================

st.markdown(
    """
    <style>

    /* Main background */
    .stApp {
        background-color: #0e1117;
    }

    /* Main container */
    .block-container {
        max-width: 1100px;
        padding-top: 2rem;
        padding-bottom: 5rem;
    }

    /* Title */
    .title {
        font-size: 42px;
        font-weight: 700;
        margin-bottom: 5px;
    }

    .subtitle {
        color: #9ca3af;
        font-size: 17px;
        margin-bottom: 30px;
    }

    /* Tool cards */
    .tool-card {
        padding: 14px;
        border-radius: 10px;
        background-color: #161b22;
        border: 1px solid #30363d;
        margin-bottom: 10px;
    }

    .tool-title {
        font-size: 16px;
        font-weight: 600;
    }

    .tool-description {
        color: #8b949e;
        font-size: 13px;
        margin-top: 4px;
    }

    </style>
    """,
    unsafe_allow_html=True
)


# ============================================================
# LLM
# ============================================================

llm = ChatGroq(
    api_key=groq_api_key,
    model="llama-3.3-70b-versatile",
    temperature=0
)


# ============================================================
# CALCULATOR TOOL
# ============================================================

@tool
def calci(expression: str) -> str:
    """Calculate a mathematical expression."""

    try:
        return str(eval(expression))

    except Exception:
        return "Unable to calculate the expression."


# ============================================================
# WEATHER TOOL
# ============================================================

@tool
def get_weather(city: str) -> str:
    """Fetch current weather information for a city."""

    url = (
        f"https://api.weatherstack.com/current?"
        f"access_key={weather_api_key}&query={city}"
    )

    try:

        response = requests.get(
            url,
            timeout=10
        )

        data = response.json()

        if "current" not in data:

            return f"Could not fetch weather data for {city}"

        return (
            f"City: {city}\n"
            f"Temperature: "
            f"{data['current']['temperature']}°C\n"
            f"Weather: "
            f"{data['current']['weather_descriptions'][0]}\n"
            f"Humidity: "
            f"{data['current']['humidity']}%"
        )

    except Exception as e:

        return f"Weather API error: {str(e)}"


# ============================================================
# TAVILY SEARCH TOOL
# ============================================================

search_tool = TavilySearchResults(
    max_results=2
)


# ============================================================
# ALL TOOLS
# ============================================================

tools = [
    search_tool,
    calci,
    get_weather
]


# ============================================================
# CREATE AGENT
# ============================================================

agent = create_agent(
    model=llm,
    tools=tools,
    system_prompt="""
    You are a helpful AI assistant.

    You have access to three tools:

    1. Calculator:
       Use it for mathematical calculations.

    2. Weather:
       Use it when the user asks for current weather information.

    3. Web Search:
       Use it when the user needs current or external information.

    Select the appropriate tool when necessary.

    Give clear and concise answers.
    """
)


# ============================================================
# SESSION STATE
# ============================================================

if "messages" not in st.session_state:

    st.session_state.messages = []


# ============================================================
# SIDEBAR
# ============================================================

with st.sidebar:

    st.title("🤖 AI Agent")

    st.success("Agent Online")

    st.divider()

    st.subheader("🛠️ Available Tools")

    st.markdown(
        """
        <div class="tool-card">

        <div class="tool-title">
        🧮 Calculator
        </div>

        <div class="tool-description">
        Performs mathematical calculations.
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="tool-card">

        <div class="tool-title">
        🌤️ Weather
        </div>

        <div class="tool-description">
        Gets current weather information.
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.markdown(
        """
        <div class="tool-card">

        <div class="tool-title">
        🔎 Tavily Search
        </div>

        <div class="tool-description">
        Searches the web for current information.
        </div>

        </div>
        """,
        unsafe_allow_html=True
    )

    st.divider()

    st.subheader("💡 Try asking")

    st.markdown(
        """
        **🌤️ Weather**

        What's the weather in Mumbai?

        **🧮 Calculator**

        Calculate 25% of 8500

        **🔎 Search**

        What are the latest AI developments?
        """
    )

    st.divider()

    if st.button(
        "🗑️ Clear Conversation",
        use_container_width=True
    ):

        st.session_state.messages = []

        st.rerun()


# ============================================================
# MAIN HEADER
# ============================================================

st.markdown(
    '<div class="title">🤖 AI Agent</div>',
    unsafe_allow_html=True
)

st.markdown(
    '<div class="subtitle">'
    'An intelligent assistant that can choose and use tools.'
    '</div>',
    unsafe_allow_html=True
)


# ============================================================
# DISPLAY CHAT HISTORY
# ============================================================

for message in st.session_state.messages:

    with st.chat_message(message["role"]):

        st.markdown(message["content"])

        # Display tools used for this response
        if message["role"] == "assistant":

            tool_calls = message.get("tool_calls", [])

            for tool_call in tool_calls:

                tool_name = tool_call.get(
                    "name",
                    "Unknown"
                )

                tool_args = tool_call.get(
                    "args",
                    {}
                )

                with st.expander(
                    f"🔧 Used tool: {tool_name}"
                ):

                    st.write("Arguments:")

                    st.code(
                        str(tool_args)
                    )


# ============================================================
# CHAT INPUT
# ============================================================

user_input = st.chat_input(
    "Ask me anything..."
)


if user_input:

    # --------------------------------------------------------
    # Display user message
    # --------------------------------------------------------

    st.session_state.messages.append(
        {
            "role": "user",
            "content": user_input
        }
    )

    with st.chat_message("user"):

        st.markdown(user_input)


    # --------------------------------------------------------
    # Generate agent response
    # --------------------------------------------------------

    with st.chat_message("assistant"):

        with st.spinner(
            "🤔 Agent is thinking..."
        ):

            try:

                response = agent.invoke(
                    {
                        "messages": [
                            {
                                "role": "user",
                                "content": user_input
                            }
                        ]
                    }
                )


                # ------------------------------------------------
                # Find tool calls
                # ------------------------------------------------

                tool_calls = []


                for message in response["messages"]:

                    if hasattr(
                        message,
                        "tool_calls"
                    ):

                        if message.tool_calls:

                            for tool_call in message.tool_calls:

                                tool_calls.append(
                                    {
                                        "name": tool_call["name"],
                                        "args": tool_call["args"]
                                    }
                                )


                # ------------------------------------------------
                # Display tools used
                # ------------------------------------------------

                for tool_call in tool_calls:

                    tool_name = tool_call["name"]

                    tool_args = tool_call["args"]


                    with st.expander(
                        f"🔧 Using tool: {tool_name}",
                        expanded=True
                    ):

                        st.write(
                            "The agent selected this tool."
                        )

                        st.write(
                            "Arguments:"
                        )

                        st.code(
                            str(tool_args)
                        )


                # ------------------------------------------------
                # Get final answer
                # ------------------------------------------------

                answer = response[
                    "messages"
                ][-1].content


            except Exception as e:

                answer = (
                    "❌ Something went wrong.\n\n"
                    f"`{str(e)}`"
                )


        # ----------------------------------------------------
        # Display final answer
        # ----------------------------------------------------

        st.markdown(answer)


    # ========================================================
    # SAVE ASSISTANT MESSAGE
    # ========================================================

    st.session_state.messages.append(
        {
            "role": "assistant",
            "content": answer,
            "tool_calls": tool_calls
        }
    )