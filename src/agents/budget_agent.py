"""
BudgetAgent - Specialized agent for budget allocation and tracking.

According to development rules:
- Stateless agent that uses tools for external data
- Validates inputs/outputs with schemas
- Graceful degradation when APIs unavailable
- No direct network calls - must go through tools
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Any, List, Optional, Tuple
from datetime import datetime

from src.orchestrator.schemas import TripRequest, Money
from src.utils.openai_client import get_llm_client


@dataclass
class BudgetCategory:
    """Single budget category with allocation."""
    name: str
    allocated_amount: float
    spent_amount: float = 0.0
    currency: str = "USD"
    percentage_of_total: float = 0.0
    items: List[Dict[str, Any]] = None  # Individual expenses in this category
    recommendations: List[str] = None


@dataclass
class BudgetAllocation:
    """Complete budget allocation breakdown."""
    total_budget: float
    currency: str
    categories: List[BudgetCategory]
    remaining_budget: float
    daily_budget: float
    contingency_fund: float
    recommendations: List[str] = None
    cost_saving_tips: List[str] = None


@dataclass
class BudgetConstraints:
    """Budget constraints and preferences."""
    total_budget: float
    currency: str
    duration_days: int
    priority_categories: Optional[List[str]] = None  # What to spend more on
    budget_style: str = "balanced"  # "budget", "balanced", "luxury"
    must_include: Optional[List[str]] = None  # Essential expenses
    flexible_categories: Optional[List[str]] = None  # Where to save if needed


@dataclass
class BudgetAgent:
    """
    Specialized agent for budget allocation and financial planning.
    
    Responsibilities:
    - Allocate total budget across trip categories
    - Track expenses and remaining budget
    - Provide cost optimization recommendations
    - Handle currency conversion and local pricing
    - Suggest money-saving alternatives
    """
    
    def allocate_budget(
        self,
        request: TripRequest,
        planned_expenses: Dict[str, Any],
        constraints: Optional[BudgetConstraints] = None
    ) -> BudgetAllocation:
        """
        Allocate budget across trip categories based on planned expenses.
        
        Args:
            request: The trip request with budget information
            planned_expenses: Results from other agents (flights, hotels, etc.)
            constraints: Optional budget constraints and preferences
            
        Returns:
            BudgetAllocation with category breakdowns and recommendations
        """
        # Extract budget constraints from request
        if not constraints:
            constraints = self._extract_constraints_from_request(request)
        
        # Analyze planned expenses from other agents
        expense_analysis = self._analyze_planned_expenses(planned_expenses)
        
        # Create budget allocation
        allocation = self._create_allocation(constraints, expense_analysis)
        
        # Add recommendations and tips
        allocation.recommendations = self._generate_recommendations(allocation, constraints)
        allocation.cost_saving_tips = self._generate_cost_saving_tips(allocation, constraints)
        
        return allocation
    
    def track_expenses(
        self,
        current_allocation: BudgetAllocation,
        new_expenses: Dict[str, Any]
    ) -> BudgetAllocation:
        """
        Update budget allocation with new expenses.
        
        Args:
            current_allocation: Current budget state
            new_expenses: New expenses to add
            
        Returns:
            Updated budget allocation
        """
        # Update expense tracking
        for category in current_allocation.categories:
            if category.name.lower() in new_expenses:
                expense_data = new_expenses[category.name.lower()]
                if isinstance(expense_data, dict) and 'cost' in expense_data:
                    cost = self._parse_cost(expense_data['cost'])
                    category.spent_amount += cost
                    
                    # Add to items list
                    if not category.items:
                        category.items = []
                    category.items.append({
                        'description': expense_data.get('description', 'Expense'),
                        'amount': cost,
                        'date': datetime.now().strftime('%Y-%m-%d')
                    })
        
        # Recalculate remaining budget
        total_spent = sum(cat.spent_amount for cat in current_allocation.categories)
        current_allocation.remaining_budget = current_allocation.total_budget - total_spent
        
        return current_allocation
    
    def optimize_budget(
        self,
        allocation: BudgetAllocation,
        constraints: BudgetConstraints
    ) -> BudgetAllocation:
        """
        Optimize budget allocation based on spending patterns and constraints.
        
        Args:
            allocation: Current budget allocation
            constraints: Budget constraints and preferences
            
        Returns:
            Optimized budget allocation
        """
        llm_client = get_llm_client()
        
        # Use LLM to analyze spending and suggest optimizations
        prompt = self._create_optimization_prompt(allocation, constraints)
        
        try:
            optimization_response = llm_client.complete(prompt)
            return self._apply_optimizations(allocation, optimization_response)
        except Exception:
            # Fallback to rule-based optimization
            return self._rule_based_optimization(allocation, constraints)
    
    def _extract_constraints_from_request(self, request: TripRequest) -> BudgetConstraints:
        """Extract budget constraints from trip request."""
        # Get total budget
        total_budget = 2000.0  # Default budget
        currency = "USD"
        
        if request.global_budget:
            total_budget = request.global_budget.amount
            currency = request.global_budget.currency
        
        # Calculate duration
        duration_days = 7  # Default
        if request.legs and request.legs[0].dates:
            dates = request.legs[0].dates
            if dates.duration_days:
                duration_days = dates.duration_days
            elif dates.fixed and len(dates.fixed) >= 2:
                try:
                    start = datetime.fromisoformat(dates.fixed[0])
                    end = datetime.fromisoformat(dates.fixed[1])
                    duration_days = (end - start).days
                except:
                    duration_days = 7
        
        # Determine budget style from preferences
        budget_style = "balanced"
        priority_categories = []
        
        if request.preferences:
            # Infer budget style from accommodation class
            if request.preferences.accommodation_class == "luxury":
                budget_style = "luxury"
            elif request.preferences.accommodation_class == "budget":
                budget_style = "budget"
            
            # Determine priorities from interests
            if request.preferences.interests:
                for interest in request.preferences.interests:
                    if any(food_term in interest.lower() for food_term in ['food', 'restaurant', 'dining', 'cuisine']):
                        priority_categories.append("Food & Dining")
                    if any(culture_term in interest.lower() for culture_term in ['museum', 'art', 'culture', 'history']):
                        priority_categories.append("Activities & Attractions")
                    if any(shopping_term in interest.lower() for shopping_term in ['shopping', 'souvenir']):
                        priority_categories.append("Shopping & Souvenirs")
        
        return BudgetConstraints(
            total_budget=total_budget,
            currency=currency,
            duration_days=duration_days,
            priority_categories=priority_categories,
            budget_style=budget_style
        )
    
    def _analyze_planned_expenses(self, planned_expenses: Dict[str, Any]) -> Dict[str, float]:
        """Analyze planned expenses from other agents."""
        analysis = {
            "flights": 0.0,
            "accommodation": 0.0,
            "transportation": 0.0,
            "activities": 0.0
        }
        
        # Extract flight costs
        if "FlightAgent" in planned_expenses:
            flight_data = planned_expenses["FlightAgent"]
            if isinstance(flight_data, dict) and "total_cost" in flight_data:
                analysis["flights"] = self._parse_cost(flight_data["total_cost"])
        
        # Extract hotel costs
        if "HotelAgent" in planned_expenses:
            hotel_data = planned_expenses["HotelAgent"]
            if isinstance(hotel_data, dict) and "hotel" in hotel_data:
                hotel_info = hotel_data["hotel"]
                if "total_cost" in hotel_info:
                    analysis["accommodation"] = self._parse_cost(hotel_info["total_cost"])
        
        # Extract transportation costs
        if "TransportAgent" in planned_expenses:
            transport_data = planned_expenses["TransportAgent"]
            if isinstance(transport_data, dict) and "transportation" in transport_data:
                # Estimate transport costs from description
                analysis["transportation"] = self._estimate_transport_costs(transport_data["transportation"])
        
        # Extract activity costs (estimated)
        if "ActivitiesAgent" in planned_expenses:
            analysis["activities"] = 200.0  # Rough estimate for activities
        
        return analysis
    
    def _parse_cost(self, cost_string: str) -> float:
        """Parse cost from string format."""
        if isinstance(cost_string, (int, float)):
            return float(cost_string)
        
        # Remove currency symbols and formatting
        cleaned = str(cost_string).replace("£", "").replace("€", "").replace("$", "").replace("¥", "").replace(",", "")
        
        # Extract first number from string
        import re
        numbers = re.findall(r'\d+\.?\d*', cleaned)
        if numbers:
            return float(numbers[0])
        
        return 0.0
    
    def _estimate_transport_costs(self, transport_info: Dict[str, Any]) -> float:
        """Estimate transportation costs from transport agent info."""
        total_cost = 0.0
        
        for key, value in transport_info.items():
            if isinstance(value, str):
                # Extract costs from descriptions
                cost = self._parse_cost(value)
                total_cost += cost
        
        return total_cost
    
    def _create_allocation(
        self,
        constraints: BudgetConstraints,
        expense_analysis: Dict[str, float]
    ) -> BudgetAllocation:
        """Create budget allocation based on constraints and planned expenses."""
        
        # Standard allocation percentages by budget style
        allocation_percentages = {
            "budget": {
                "Flights": 0.40,
                "Accommodation": 0.25,
                "Food & Dining": 0.15,
                "Transportation": 0.08,
                "Activities & Attractions": 0.07,
                "Shopping & Souvenirs": 0.03,
                "Contingency": 0.02
            },
            "balanced": {
                "Flights": 0.35,
                "Accommodation": 0.25,
                "Food & Dining": 0.20,
                "Transportation": 0.08,
                "Activities & Attractions": 0.10,
                "Shopping & Souvenirs": 0.05,
                "Contingency": 0.05
            },
            "luxury": {
                "Flights": 0.30,
                "Accommodation": 0.30,
                "Food & Dining": 0.25,
                "Transportation": 0.05,
                "Activities & Attractions": 0.08,
                "Shopping & Souvenirs": 0.07,
                "Contingency": 0.05
            }
        }
        
        base_percentages = allocation_percentages[constraints.budget_style]
        
        # Adjust percentages based on priorities
        if constraints.priority_categories:
            for priority in constraints.priority_categories:
                if priority in base_percentages:
                    # Increase priority category by 20%
                    base_percentages[priority] *= 1.2
                    
            # Normalize to ensure total = 1.0
            total = sum(base_percentages.values())
            base_percentages = {k: v/total for k, v in base_percentages.items()}
        
        # Create budget categories
        categories = []
        for category_name, percentage in base_percentages.items():
            allocated_amount = constraints.total_budget * percentage
            
            category = BudgetCategory(
                name=category_name,
                allocated_amount=allocated_amount,
                currency=constraints.currency,
                percentage_of_total=percentage * 100,
                items=[]
            )
            
            # Add planned expenses as initial items
            if category_name == "Flights" and expense_analysis.get("flights", 0) > 0:
                category.spent_amount = expense_analysis["flights"]
                category.items = [{"description": "Planned flights", "amount": expense_analysis["flights"]}]
            elif category_name == "Accommodation" and expense_analysis.get("accommodation", 0) > 0:
                category.spent_amount = expense_analysis["accommodation"]
                category.items = [{"description": "Planned accommodation", "amount": expense_analysis["accommodation"]}]
            
            categories.append(category)
        
        # Calculate remaining budget and daily budget
        total_spent = sum(cat.spent_amount for cat in categories)
        remaining_budget = constraints.total_budget - total_spent
        daily_budget = remaining_budget / constraints.duration_days
        
        # Calculate contingency fund
        contingency_category = next((cat for cat in categories if cat.name == "Contingency"), None)
        contingency_fund = contingency_category.allocated_amount if contingency_category else constraints.total_budget * 0.05
        
        return BudgetAllocation(
            total_budget=constraints.total_budget,
            currency=constraints.currency,
            categories=categories,
            remaining_budget=remaining_budget,
            daily_budget=daily_budget,
            contingency_fund=contingency_fund
        )
    
    def _generate_recommendations(
        self,
        allocation: BudgetAllocation,
        constraints: BudgetConstraints
    ) -> List[str]:
        """Generate budget recommendations."""
        recommendations = []
        
        # Check if any category is over-allocated
        for category in allocation.categories:
            if category.spent_amount > category.allocated_amount:
                overage = category.spent_amount - category.allocated_amount
                recommendations.append(
                    f"⚠️ {category.name} is over budget by {allocation.currency}{overage:.0f}. "
                    f"Consider reducing costs in other categories."
                )
        
        # Daily budget guidance
        recommendations.append(
            f"💰 Daily spending budget: {allocation.currency}{allocation.daily_budget:.0f} "
            f"({constraints.duration_days} days)"
        )
        
        # Currency-specific advice
        if allocation.currency in ["JPY", "¥"]:
            recommendations.append("🏧 Japan is cash-heavy - withdraw yen in advance, many places don't accept cards")
        elif allocation.currency in ["EUR", "€"]:
            recommendations.append("💳 Europe widely accepts cards, but carry some cash for small vendors")
        
        # Budget style specific advice
        if constraints.budget_style == "budget":
            recommendations.append("🥪 Save money by eating at local markets and cooking some meals")
            recommendations.append("🚌 Use public transportation and walking to reduce transport costs")
        elif constraints.budget_style == "luxury":
            recommendations.append("🍾 Consider booking restaurant reservations and premium experiences in advance")
        
        return recommendations
    
    def _generate_cost_saving_tips(
        self,
        allocation: BudgetAllocation,
        constraints: BudgetConstraints
    ) -> List[str]:
        """Generate cost-saving tips."""
        tips = [
            "🎟️ Look for city tourist passes that include multiple attractions",
            "🍜 Try local street food and markets for authentic, affordable meals",
            "🚶 Walk when possible - it's free and you'll see more of the city",
            "💧 Carry a refillable water bottle to avoid buying drinks",
            "📱 Use free WiFi instead of expensive roaming charges",
            "🎁 Set a specific souvenir budget to avoid overspending",
            "⏰ Book attractions in advance for potential discounts",
            "🌅 Take advantage of free activities like parks, beaches, and viewpoints"
        ]
        
        # Add destination-specific tips
        if any("japan" in cat.name.lower() for cat in allocation.categories):
            tips.extend([
                "🎌 Get a JR Pass for unlimited train travel if visiting multiple cities",
                "🍱 Convenience store meals (konbini) are cheap and high quality",
                "♨️ Public baths (sento) are affordable relaxation options"
            ])
        
        return tips
    
    def _create_optimization_prompt(
        self,
        allocation: BudgetAllocation,
        constraints: BudgetConstraints
    ) -> str:
        """Create LLM prompt for budget optimization."""
        prompt = f"""
Analyze this travel budget and suggest optimizations:

CURRENT ALLOCATION:
Total Budget: {allocation.currency}{allocation.total_budget}
Remaining: {allocation.currency}{allocation.remaining_budget}
Daily Budget: {allocation.currency}{allocation.daily_budget}

CATEGORIES:
{self._format_categories_for_prompt(allocation.categories)}

CONSTRAINTS:
- Budget Style: {constraints.budget_style}
- Duration: {constraints.duration_days} days
- Priorities: {constraints.priority_categories or 'None specified'}

Please suggest optimizations to:
1. Balance over/under-allocated categories
2. Maximize value for money
3. Align with budget style and priorities

Respond with JSON format:
{{
    "optimizations": [
        {{
            "category": "<category_name>",
            "adjustment": <amount>,
            "reason": "<explanation>"
        }}
    ],
    "overall_recommendation": "<summary>"
}}
"""
        return prompt
    
    def _format_categories_for_prompt(self, categories: List[BudgetCategory]) -> str:
        """Format budget categories for LLM prompt."""
        formatted = ""
        for cat in categories:
            status = "✅" if cat.spent_amount <= cat.allocated_amount else "⚠️"
            formatted += f"- {cat.name}: Allocated {cat.currency}{cat.allocated_amount:.0f}, "
            formatted += f"Spent {cat.currency}{cat.spent_amount:.0f} {status}\n"
        return formatted
    
    def _apply_optimizations(
        self,
        allocation: BudgetAllocation,
        optimization_response: str
    ) -> BudgetAllocation:
        """Apply LLM-suggested optimizations to budget allocation."""
        try:
            import json
            optimizations = json.loads(optimization_response.strip())
            
            for opt in optimizations.get("optimizations", []):
                category_name = opt.get("category")
                adjustment = opt.get("adjustment", 0)
                
                # Find and adjust category
                for category in allocation.categories:
                    if category.name == category_name:
                        category.allocated_amount += adjustment
                        break
            
            return allocation
            
        except Exception:
            # Fallback to rule-based optimization
            return self._rule_based_optimization(allocation, None)
    
    def _rule_based_optimization(
        self,
        allocation: BudgetAllocation,
        constraints: Optional[BudgetConstraints]
    ) -> BudgetAllocation:
        """Simple rule-based budget optimization."""
        # Move money from over-allocated to under-allocated categories
        over_allocated = []
        under_allocated = []
        
        for category in allocation.categories:
            remaining = category.allocated_amount - category.spent_amount
            if remaining < 0:
                over_allocated.append((category, abs(remaining)))
            elif remaining > category.allocated_amount * 0.5:  # More than 50% unspent
                under_allocated.append((category, remaining))
        
        # Simple rebalancing: move excess from under-allocated to over-allocated
        for over_cat, deficit in over_allocated:
            for under_cat, excess in under_allocated:
                if excess > deficit:
                    # Move money from under to over
                    transfer_amount = min(deficit, excess * 0.3)  # Transfer up to 30% of excess
                    over_cat.allocated_amount += transfer_amount
                    under_cat.allocated_amount -= transfer_amount
                    break
        
        return allocation
