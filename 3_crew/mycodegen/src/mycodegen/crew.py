from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task
from crewai.agents.agent_builder.base_agent import BaseAgent
from typing import List


@CrewBase
class Mycodegen():
    """Mycodegen crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'
    

    @agent
    def coder(self) -> Agent:
        return Agent(
            config=self.agents_config['coder'], # type: ignore[index]
            verbose=True,
            allow_code_execution=True,  # Enable code execution
            code_execution_mode="unsafe",  # Unsafe mode to access .env and network (runs locally)
            max_execution_time=120,  # Increased timeout for API calls
            max_retry_limit=2  # Reduced retries to fail faster
        )

    
    @task
    def coding_task(self) -> Task:
        return Task(
            config=self.tasks_config['coding_task'], # type: ignore[index]
            
        )

    @crew
    def crew(self) -> Crew:
        """Creates the Mycodegen crew"""
        

        return Crew(
            agents=self.agents, # Automatically created by the @agent decorator
            tasks=self.tasks, # Automatically created by the @task decorator
            process=Process.sequential,
            verbose=True,
            # process=Process.hierarchical, # In case you wanna use that instead https://docs.crewai.com/how-to/Hierarchical/
        )
