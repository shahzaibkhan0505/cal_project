import asyncio
from dataclasses import dataclass

from agents import Agent, RunContextWrapper, Runner, function_tool


@dataclass
class Employee:
    name: str
    emp_id: int
    department: str
    salary: float
    years_of_experience: int


@function_tool
async def fetch_employee_details(wrapper: RunContextWrapper[Employee]) -> str:
    """Fetch complete details of the employee from context."""
    emp = wrapper.context
    return (
        f"Employee Name: {emp.name}\n"
        f"Employee ID: {emp.emp_id}\n"
        f"Department: {emp.department}\n"
        f"Years of Experience: {emp.years_of_experience}"
    )


@function_tool
async def fetch_employee_salary(wrapper: RunContextWrapper[Employee]) -> str:
    """Fetch the salary of the employee from context."""
    emp = wrapper.context
    return f"{emp.name} ki monthly salary {emp.salary:,.0f} rupees hai."


@function_tool
async def fetch_employee_department(wrapper: RunContextWrapper[Employee]) -> str:
    """Fetch the department of the employee from context."""
    emp = wrapper.context
    return f"{emp.name} ka department '{emp.department}' hai."


async def main():
    employee_info = Employee(
        name="Ali Raza",
        emp_id=4521,
        department="Software Engineering",
        salary=150000.0,
        years_of_experience=5,
    )

    agent = Agent[Employee](
        name="HR Assistant",
        instructions="Aap ek helpful HR assistant hain. Employee ke bare mein pooche gaye sawaalon ke jawab dein.",
        tools=[fetch_employee_details, fetch_employee_salary, fetch_employee_department],
    )

    queries = [
        "Is employee ki poori details batao.",
        "Is employee ki salary kitni hai?",
        "Yeh employee kis department mein kaam karta hai?",
    ]

    for query in queries:
        print(f"\nSawaal: {query}")
        result = await Runner.run(
            starting_agent=agent,
            input=query,
            context=employee_info,
        )
        print(f"Jawab: {result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
