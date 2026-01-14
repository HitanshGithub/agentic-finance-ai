"""
Recurring Expense Detector

Analyzes expense history to identify recurring charges (subscriptions, bills, etc.)
"""


def detect_recurring_expenses(expenses: list) -> dict:
    """
    Analyze expenses to find recurring patterns.
    
    Args:
        expenses: List of expenses [{ category, amount, date? }]
    
    Returns:
        {
            recurring: [{ category, amount, frequency, annual_cost }],
            total_monthly: float,
            total_annual: float,
            suggestions: [str]
        }
    """
    # Group expenses by category and amount
    expense_groups = {}
    
    for exp in expenses:
        category = exp.get("category", "Unknown").lower().strip()
        amount = exp.get("amount", 0)
        
        # Create a key for grouping similar expenses
        key = f"{category}_{amount}"
        
        if key not in expense_groups:
            expense_groups[key] = {
                "category": exp.get("category", "Unknown"),
                "amount": amount,
                "count": 0
            }
        expense_groups[key]["count"] += 1
    
    # Identify recurring expenses (appear more than once or match subscription patterns)
    subscription_keywords = [
        "netflix", "spotify", "amazon", "prime", "hulu", "disney",
        "subscription", "membership", "gym", "insurance", "phone",
        "internet", "electricity", "water", "gas", "rent", "mortgage",
        "youtube", "apple", "google", "microsoft", "adobe", "cloud"
    ]
    
    recurring = []
    
    for key, data in expense_groups.items():
        is_subscription = any(
            keyword in data["category"].lower() 
            for keyword in subscription_keywords
        )
        
        # Consider it recurring if it appears multiple times OR matches subscription keywords
        if data["count"] > 1 or is_subscription:
            monthly_amount = data["amount"]
            annual_cost = monthly_amount * 12
            
            recurring.append({
                "category": data["category"],
                "amount": monthly_amount,
                "frequency": "monthly",
                "annual_cost": annual_cost,
                "occurrences": data["count"]
            })
    
    # Sort by annual cost (highest first)
    recurring.sort(key=lambda x: x["annual_cost"], reverse=True)
    
    # Calculate totals
    total_monthly = sum(r["amount"] for r in recurring)
    total_annual = total_monthly * 12
    
    # Generate suggestions
    suggestions = []
    
    if total_monthly > 0:
        suggestions.append(
            f"You have ${total_monthly:.2f}/month in recurring expenses (${total_annual:.2f}/year)"
        )
    
    # Find potentially unnecessary subscriptions
    entertainment_keywords = ["netflix", "spotify", "hulu", "disney", "youtube", "gaming"]
    entertainment_subs = [
        r for r in recurring 
        if any(kw in r["category"].lower() for kw in entertainment_keywords)
    ]
    
    if len(entertainment_subs) > 2:
        total_entertainment = sum(s["amount"] for s in entertainment_subs)
        suggestions.append(
            f"You have {len(entertainment_subs)} entertainment subscriptions totaling ${total_entertainment:.2f}/month. Consider consolidating."
        )
    
    # High-cost recurring expenses
    high_cost = [r for r in recurring if r["amount"] > 100]
    if high_cost:
        suggestions.append(
            f"Review your {len(high_cost)} high-cost recurring expense(s) for potential savings."
        )
    
    return {
        "recurring": recurring,
        "total_monthly": total_monthly,
        "total_annual": total_annual,
        "suggestions": suggestions
    }
