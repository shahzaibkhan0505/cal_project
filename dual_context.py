import asyncio
from dataclasses import dataclass

from agents import Agent, RunContextWrapper, Runner, function_tool


# LLM yeh context access KAR SAKTA hai (tools iska data return karte hain)
@dataclass
class CompanyContext:
    company_name: str
    department: str
    project_name: str
    office_location: str


# LLM yeh context access NAHI kar sakta (koi tool iska raw data return nahi karta)
@dataclass
class EmployeePrivateContext:
    name: str
    emp_id: int
    salary: float
    home_address: str
    personal_phone: str


@dataclass
class AppContext:
    company: CompanyContext      # LLM accessible
    employee: EmployeePrivateContext  # LLM inaccessible


# ✅ LLM-ACCESSIBLE TOOL — company ka data seedha return karta hai
@function_tool
async def get_company_info(wrapper: RunContextWrapper[AppContext]) -> str:
    """Get company and department information."""
    c = wrapper.context.company
    return (
        f"Company: {c.company_name}\n"
        f"Department: {c.department}\n"
        f"Project: {c.project_name}\n"
        f"Office: {c.office_location}"
    )


# ✅ LLM-ACCESSIBLE TOOL — lekin andar employee data use karke sirf grade deta hai
@function_tool
async def get_salary_grade(wrapper: RunContextWrapper[AppContext]) -> str:
    """Get employee's salary grade (not the actual salary)."""
    salary = wrapper.context.employee.salary  # private data internally use hota hai

    # Actual salary kabhi LLM ko nahi batai — sirf grade return hota hai
    if salary >= 200_000:
        grade = "Grade A (Senior)"
    elif salary >= 100_000:
        grade = "Grade B (Mid-level)"
    else:
        grade = "Grade C (Junior)"

    return f"Employee salary classification: {grade}"


# ✅ LLM-ACCESSIBLE TOOL — employee ka naam bhi nahi, sirf department bata raha hai
@function_tool
async def get_team_size_hint(wrapper: RunContextWrapper[AppContext]) -> str:
    """Get a general hint about the team based on department."""
    dept = wrapper.context.company.department  # public data
    # employee ki private info use hoti hai sirf internal logic ke liye
    exp_indicator = "senior member" if wrapper.context.employee.salary >= 150_000 else "junior member"
    return f"Department '{dept}' mein yeh ek {exp_indicator} hai."


async def main():
    context = AppContext(
        company=CompanyContext(
            company_name="TechCorp Pakistan",
            department="Software Engineering",
            project_name="Project Phoenix",
            office_location="Lahore, Pakistan",
        ),
        employee=EmployeePrivateContext(
            name="Ali Raza",
            emp_id=4521,
            salary=175_000.0,
            home_address="House 12, Block B, Gulberg, Lahore",
            personal_phone="+92-300-1234567",
        ),
    )

    agent = Agent[AppContext](
        name="Company Assistant",
        instructions=(
            "Aap ek company assistant hain. Sirf company aur department ki "
            "information share karein. Employee ki personal ya financial details "
            "share mat karein."
        ),
        tools=[get_company_info, get_salary_grade, get_team_size_hint],
    )

    queries = [
        "Company ki information do.",
        "Is employee ki salary kitni hai?",   # LLM actual salary nahi bata payega
        "Employee ka ghar ka address kya hai?",  # koi tool yeh data expose nahi karta
        "Is employee ki salary grade kya hai?",
    ]

    for query in queries:
        print(f"\n{'='*50}")
        print(f"Sawaal: {query}")
        result = await Runner.run(
            starting_agent=agent,
            input=query,
            context=context,
        )
        print(f"Jawab: {result.final_output}")


if __name__ == "__main__":
    asyncio.run(main())
