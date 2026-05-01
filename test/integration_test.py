# test/integration_test.py
import requests
import time
import threading
import sys
import os
# Add the parent directory to path so Python can find the 'agent' package
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Now import using the package structure
from agent import GCAgent

SERVER_URL = "http://localhost:8000"

class IntegrationTester:
    def __init__(self):
        self.agents = {}
        
    def setup_agents(self):
        """Create 5 agents for testing"""
        for i in range(1, 6):
            pc_type = "PS" if i > 3 else "PC"
            self.agents[i] = GCAgent(i, pc_type)
        print("Created 5 agents")
        
    def test_start_session(self):
        """Test starting a session"""
        print("\n TEST: Start Session")
        
        # Start session on PC 1
        pc_id = 1
        duration = 30
        
        # API call to server
        response = requests.post(f"{SERVER_URL}/api/session/start", json={
            "pc_id": pc_id,
            "duration": duration,
            "user_id": "test_user",
            "booking_id": "test_booking"
        })
        
        if response.status_code == 200:
            print(f"Server accepted session request for PC-{pc_id}")
            # Tell agent to start
            self.agents[pc_id].start_session(duration, "test_user", "test_booking")
        else:
            print(f"Failed: {response.text}")
            
    def test_extend_session(self):
        """Test extending a session"""
        print("\nTEST: Extend Session")
        
        pc_id = 1
        extra = 15
        
        response = requests.post(f"{SERVER_URL}/api/session/extend", json={
            "pc_id": pc_id,
            "extra_minutes": extra
        })
        
        if response.status_code == 200:
            print(f"Server accepted extension for PC-{pc_id}")
            self.agents[pc_id].extend_session(extra)
        else:
            print(f"Failed: {response.text}")
            
    def test_full_workflow(self):
        """Complete workflow test"""
        print("\n" + "="*50)
        print("🔄 FULL WORKFLOW TEST")
        print("="*50)
        
        # Start session on all PCs
        for pc_id in range(1, 6):
            print(f"\n Starting PC-{pc_id}...")
            self.agents[pc_id].start_session(20, f"user_{pc_id}", f"booking_{pc_id}")
            time.sleep(1)  # Stagger starts
            
        # Show status
        print("\n Status after starting all PCs:")
        for pc_id, agent in self.agents.items():
            status = agent.get_status()
            print(f"  PC-{pc_id}: {'ACTIVE' if status['session_active'] else 'LOCKED'} - {status['time_remaining']}min left")
        
        # Wait 10 seconds
        print("\n Waiting 10 seconds...")
        time.sleep(10)
        
        # Extend PC 1 and PC 4
        print("\n Extending PC-1 (+15min) and PC-4 (+10min)...")
        self.agents[1].extend_session(15)
        self.agents[4].extend_session(10)
        
        # Show final status
        print("\nFinal Status:")
        for pc_id, agent in self.agents.items():
            status = agent.get_status()
            print(f"  PC-{pc_id} ({agent.pc_type}): {'ACTIVE' if status['session_active'] else 'LOCKED'} - {status['time_remaining']}min left")
        
        # Let sessions run until some expire
        print("\nMonitoring sessions for 30 seconds...")
        for _ in range(6):
            time.sleep(5)
            active_count = sum(1 for agent in self.agents.values() if agent.session_active)
            print(f"Active sessions: {active_count}/5")
        
        print("\nIntegration test complete!")

if __name__ == "__main__":
    tester = IntegrationTester()
    tester.setup_agents()
    
    # Run individual tests
    tester.test_start_session()
    time.sleep(2)
    tester.test_extend_session()
    
    # Run full workflow
    tester.test_full_workflow()