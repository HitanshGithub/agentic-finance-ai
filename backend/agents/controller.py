from agents.expense_agent import ExpenseAgent
from agents.budget_agent import BudgetAgent
from agents.investment_agent import InvestmentAgent
from agents.fraud_agent import FraudAgent

class ControllerAgent:
    def __init__(self):
        self.expense_agent = ExpenseAgent()
        self.budget_agent = BudgetAgent()
        self.investment_agent = InvestmentAgent()
        self.fraud_agent = FraudAgent()

    def run(self, data):
        try:
            expense_report = self.expense_agent.run(data["expenses"])
            budget_report = self.budget_agent.run(
                data["income"], expense_report
            )
            investment_report = self.investment_agent.run(
                data["profile"], budget_report
            )
            fraud_report = self.fraud_agent.run(data["expenses"])

            return {
                "expense_analysis": expense_report,
                "budget_plan": budget_report,
                "investment_plan": investment_report,
                "fraud_alerts": fraud_report
            }

        except Exception as e:
            # 🔥 ALWAYS RETURN JSON
            return {
                "error": "Agent pipeline failed",
                "details": str(e)
            }
