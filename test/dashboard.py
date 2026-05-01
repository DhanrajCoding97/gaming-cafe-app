# test/dashboard.py
from agent import GCAgent
import time
import os

def clear_screen():
    os.system('cls' if os.name == 'nt' else 'clear')

def create_dashboard():
    agents = {i: GCAgent(i, "PS" if i > 3 else "PC") for i in range(1, 6)}
    
    print("🎮 Gaming Cafe Simulation Dashboard")
    print("Press '1-5' to start PC, 'e1-5' to extend, 'q' to quit\n")
    
    while True:
        clear_screen()
        print("="*60)
        print("                    GAMING CAFE STATUS")
        print("="*60)
        
        for pc_id, agent in agents.items():
            status = agent.get_status()
            icon = "🟢" if status['session_active'] else "🔴"
            type_icon = "💻" if agent.pc_type == "PC" else "🎮"
            bar_len = min(40, status['time_remaining'])
            bar = "█" * (bar_len // 2) + "░" * (20 - (bar_len // 2))
            
            print(f"{type_icon} PC-{pc_id} {icon}  {bar}  {status['time_remaining']}min")
        
        print("="*60)
        print("Commands: [1-5]=Start PC | e[1-5]=Extend | s=Status | q=Quit")
        
        cmd = input("\n> ").strip().lower()
        
        if cmd == 'q':
            break
        elif cmd in ['1','2','3','4','5']:
            pc_id = int(cmd)
            mins = int(input("Duration (minutes): "))
            agents[pc_id].start_session(mins, f"user_{pc_id}", f"booking_{pc_id}")
        elif cmd.startswith('e') and len(cmd) > 1:
            pc_id = int(cmd[1])
            mins = int(input("Extra minutes: "))
            agents[pc_id].extend_session(mins)

if __name__ == "__main__":
    create_dashboard()