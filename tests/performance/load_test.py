"""
Performance/Load tests using Locust.
Run with: locust -f tests/performance/load_test.py
"""
from locust import HttpUser, task, between
import random


class KayakUser(HttpUser):
    """Simulates a typical Kayak user."""
    
    wait_time = between(1, 3)  # Wait 1-3 seconds between tasks
    
    @task(3)
    def search_flights(self):
        """Search for flights - most common operation."""
        airports = ["SFO", "JFK", "LAX", "ORD", "DFW"]
        dep = random.choice(airports)
        arr = random.choice([a for a in airports if a != dep])
        
        self.client.get(
            f"/flights/search",
            params={
                "departure_airport": dep,
                "arrival_airport": arr,
                "page": 1,
                "page_size": 20
            },
            name="/flights/search"
        )
    
    @task(2)
    def search_hotels(self):
        """Search for hotels."""
        cities = ["San Francisco", "New York", "Los Angeles", "Chicago"]
        
        self.client.get(
            f"/hotels/search",
            params={
                "city": random.choice(cities),
                "page": 1,
                "page_size": 20
            },
            name="/hotels/search"
        )
    
    @task(1)
    def search_cars(self):
        """Search for cars."""
        cities = ["San Francisco", "New York", "Los Angeles"]
        
        self.client.get(
            f"/cars/search",
            params={
                "city": random.choice(cities),
                "page": 1
            },
            name="/cars/search"
        )
    
    @task(1)
    def view_flight_details(self):
        """View a specific flight."""
        flight_ids = ["AA123", "UA456", "DL789"]
        self.client.get(
            f"/flights/{random.choice(flight_ids)}",
            name="/flights/[id]"
        )
    
    @task(1)
    def health_check(self):
        """Check service health."""
        self.client.get("/health")


class AdminUser(HttpUser):
    """Simulates an admin user checking analytics."""
    
    wait_time = between(5, 10)
    
    @task
    def get_revenue_analytics(self):
        """Check revenue analytics."""
        self.client.get(
            "/analytics/revenue",
            params={"period": "monthly"},
            name="/analytics/revenue"
        )
    
    @task
    def get_top_properties(self):
        """Get top properties."""
        self.client.get(
            "/analytics/top-properties",
            params={"limit": 10},
            name="/analytics/top-properties"
        )


class AIServiceUser(HttpUser):
    """Simulates users interacting with AI service."""
    
    wait_time = between(2, 5)
    
    @task(2)
    def get_deals(self):
        """Get current deals."""
        self.client.get("/api/deals", name="/api/deals")
    
    @task(1)
    def chat_with_concierge(self):
        """Chat with AI concierge."""
        messages = [
            "Find me flights to Miami",
            "What hotels are available in New York?",
            "I need a car rental in Los Angeles"
        ]
        
        self.client.post(
            "/api/chat",
            json={
                "message": random.choice(messages),
                "user_id": f"test-user-{random.randint(1, 100)}"
            },
            name="/api/chat"
        )

