from crewai import Agent, Crew, Process, Task
from crewai.project import CrewBase, agent, crew, task

@CrewBase
class MyengTeam():
    """MyengTeam crew"""

    agents_config = 'config/agents.yaml'
    tasks_config = 'config/tasks.yaml'

    @agent
    def engineering_lead(self) -> Agent:
        return Agent(
            config=self.agents_config['engineering_lead'],
            verbose=True,
        )

    @agent
    def backend_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['backend_engineer'],
            allow_code_execution=True,
            code_execution_mode="safe",
            max_execution_time=300,
            max_retry_limit=5,
            verbose=True,
        )

    @agent
    def frontend_engineer(self) -> Agent:
        return Agent(   
            config=self.agents_config['frontend_engineer'],
            verbose=True,
        )
    
    @agent
    def test_engineer(self) -> Agent:
        return Agent(
            config=self.agents_config['test_engineer'],
            allow_code_execution=True,
            code_execution_mode="safe",
            max_execution_time=300,
            max_retry_limit=5,
            verbose=True,
        )
    @task
    def design_task(self) -> Task:
        return Task(
            config=self.tasks_config['design_task'],
        )

    @task
    def code_task(self) -> Task:
        return Task(
            config=self.tasks_config['code_task'],
            verbose=True,
        )
    

    @task
    def frontend_task(self) -> Task:
        return Task(
            config=self.tasks_config['frontend_task'],
            verbose=True,
        )

    @task
    def test_task(self) -> Task:
        return Task(
            config=self.tasks_config['test_task'],
            verbose=True,
        )

    @crew
    def crew(self) -> Crew:
        """Creates the MyengTeam crew"""
        return Crew(
            agents=self.agents,
            tasks=self.tasks,
            process=Process.sequential,
            verbose=True,
        )
