"""
Research Assistant with OpenAI Web Search

A simple research tool that uses OpenAI's Agents SDK with Web Search capabilities
to provide research summaries on any topic through a Gradio chat interface.

Requirements:
    pip install gradio openai-agents-sdk python-dotenv
"""

import os
import gradio as gr
from dotenv import load_dotenv
from datetime import datetime
import asyncio

# Import OpenAI Agents SDK
try:
    from agents import Agent, WebSearchTool, Runner
except ImportError as e:
    print("❌ OpenAI Agents SDK not found!")
    print("\nThe 'agents' package needs to be installed from GitHub:")
    print("  pip install git+https://github.com/openai/openai-agents-python.git")
    print("\nOr if you're using uv:")
    print("  uv pip install git+https://github.com/openai/openai-agents-python.git")
    print("\nMake sure you're in the correct environment where the labs are working.")
    raise e

# Load environment variables
load_dotenv(override=True)

# Check for OpenAI API key
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise ValueError("OPENAI_API_KEY environment variable not set. Please set it in your .env file or environment.")

# Research agent instructions
RESEARCH_INSTRUCTIONS = """You are an expert research assistant with access to web search capabilities.

Your task is to:
1. Conduct thorough research on the given topic using web search
2. Synthesize information from multiple sources
3. Provide a comprehensive, well-structured summary
4. Include key findings, insights, and relevant data
5. Cite sources when possible

Guidelines:
- Be thorough but concise (aim for 3-5 paragraphs)
- Focus on recent and credible information
- Highlight important facts, statistics, and trends
- Organize information logically
- Use clear, professional language

Remember: You are helping users understand complex topics quickly and accurately.
"""

# Create research agent
research_agent = Agent(
    name="Research Assistant",
    instructions=RESEARCH_INSTRUCTIONS,
    tools=[WebSearchTool(search_context_size="low")],
    model="gpt-4o-mini",
)

async def conduct_research(topic: str) -> str:
    """
    Conduct research on a given topic using the research agent
    
    Args:
        topic: The research topic/question
        
    Returns:
        Research results as formatted string
    """
    try:
        # Run the agent
        result = await Runner.run(research_agent, topic)
        return result.final_output
            
    except Exception as e:
        return f"❌ Error conducting research: {str(e)}\n\nPlease check your API key and try again."

def sync_conduct_research(topic: str) -> str:
    """Synchronous wrapper for async research function"""
    return asyncio.run(conduct_research(topic))

def process_research(user_input: str, history: list) -> tuple:
    """
    Process the research query and return results
    
    Args:
        user_input: The research topic
        history: Gradio chat display state (not stored, just for UI display)
        
    Returns:
        Updated chat display and empty input
    """
    user_input = user_input.strip()
    
    if not user_input:
        return history, ""
    
    # Add user message
    history.append({"role": "user", "content": user_input})
    
    # Show thinking message
    thinking_msg = f"🔍 Researching: **{user_input}**\n\n⏳ Searching the web and analyzing information..."
    history.append({"role": "assistant", "content": thinking_msg})
    
    # Yield to update UI
    yield history, ""
    
    try:
        # Conduct research
        research_result = sync_conduct_research(user_input)
        
        # Add timestamp
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # Format final response
        final_response = f"""📊 **Research Results**

{research_result}

---
_Research completed at {timestamp}_
🌐 _Powered by OpenAI Web Search_
"""
        
        # Replace thinking message with results
        history[-1] = {"role": "assistant", "content": final_response}
        
        yield history, ""
        
    except Exception as e:
        error_msg = f"❌ **Error**\n\n{str(e)}\n\nPlease try again or check your API configuration."
        history[-1] = {"role": "assistant", "content": error_msg}
        yield history, ""

def create_gradio_interface():
    """Create and configure the Gradio chat interface"""
    
    with gr.Blocks(title="Research Assistant", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🔬 Research Assistant
        
        **AI-Powered Research with Real-Time Web Search**
        
        Get comprehensive research summaries on any topic using OpenAI's advanced web search capabilities.
        
        ### 🚀 How to use:
        1. **Enter a research topic** - Can be a question, subject, or area of interest
        2. **Wait for analysis** - The AI will search the web and synthesize information
        3. **Review results** - Get a comprehensive summary with key findings
         
        ⚠️ **Note:** Web search queries cost ~$0.025 each. Use responsibly.
        """)
        
        chatbot = gr.Chatbot(
            label="Research Chat",
            height=600,
            type='messages',
            show_copy_button=True,
            placeholder="Enter a research topic below to get started..."
        )
        
        with gr.Row():
            msg = gr.Textbox(
                placeholder="Enter your research topic or question...",
                label="Research Topic",
                scale=4,
                lines=2
            )
            submit_btn = gr.Button("🔍 Research", variant="primary", scale=1)
        
        clear_btn = gr.Button("🗑️ Clear Chat", variant="secondary")
        
        # Event handlers
        def clear_chat():
            """Clear the chat"""
            return [], ""
        
        # Connect events
        submit_btn.click(
            process_research,
            inputs=[msg, chatbot],
            outputs=[chatbot, msg]
        )
        
        msg.submit(
            process_research,
            inputs=[msg, chatbot],
            outputs=[chatbot, msg]
        )
        
        clear_btn.click(clear_chat, outputs=[chatbot, msg])
        
        # Examples
        gr.Examples(
            examples=[
                "What are the latest trends in artificial intelligence for 2025?",
                "Explain quantum computing and its current applications",
                "What is the current state of renewable energy technology?",
                "Compare the top programming languages in 2025",
                "What are recent breakthroughs in cancer research?",
                "How is climate change affecting global agriculture?",
                "What are the most innovative companies in 2025?",
                "Explain the impact of generative AI on creative industries",
                "What are the latest developments in space exploration?",
                "How does 5G technology differ from 4G?"
            ],
            inputs=msg,
            label="📚 Example Research Topics"
        )
    
    return demo

def main():
    """Main function to launch the research assistant"""
    try:
        # Verify API key
        if not OPENAI_API_KEY:
            print("❌ OPENAI_API_KEY not found!")
            print("Please set it in your .env file or environment variables")
            return
        
        print("🚀 Starting Research Assistant...")
        print("🔍 Features: OpenAI Web Search + GPT-4o-mini + Interactive Chat")
        print("💡 Ready to research any topic!")
        
        # Create and launch interface
        demo = create_gradio_interface()
        
        demo.launch(
            share=False,  # Set to True for public link
            server_name="0.0.0.0",
            server_port=None,  # Auto-find available port
            show_error=True
        )
        
    except Exception as e:
        print(f"❌ Error starting application: {e}")
        raise

# Create interface at module level for Hugging Face Spaces
demo = create_gradio_interface()

if __name__ == "__main__":
    main()
