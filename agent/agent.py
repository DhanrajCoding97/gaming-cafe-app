# # agent/agent.py
# import json
# import time
# import threading
# import platform
# import os
# from datetime import datetime, timedelta
# from typing import Dict, Optional
# import socket  # For local testing

# class GCAgent:
#     """
#     Gaming Cafe PC Agent
#     Can run multiple instances on same machine for testing
#     """
    
#     def __init__(self, pc_id: int, pc_type: str = "PC", use_real_controls: bool = False):
#         self.pc_id = pc_id
#         self.pc_type = pc_type  # "PC" or "PS"
#         self.use_real_controls = use_real_controls  # Mock for testing
        
#         # Session state
#         self.session_active = False
#         self.session_end_time: Optional[datetime] = None
#         self.current_user_id = None
#         self.current_booking_id = None
        
#         self.log_file = f"logs/pc_{pc_id}.log"
#         os.makedirs("logs", exist_ok=True)
        
#         # Stats tracking
#         self.total_minutes_played = 0
        
#     def log(self, message: str):
#         """Log with timestamp to file and console"""
#         timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
#         log_msg = f"[{timestamp}] PC-{self.pc_id}: {message}"
#         print(log_msg)
#         with open(self.log_file, "a") as f:
#             f.write(log_msg + "\n")
    
#     def lock_pc(self):
#         """Lock the PC (real or simulated)"""
#         if self.use_real_controls and platform.system() == "Windows":
#             import subprocess
#             subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
#         else:
#             # Simulated lock for testing
#             self.log(" PC LOCKED (simulated)")
#             # Create a lock file to track state
#             with open(f"logs/pc_{self.pc_id}_locked.txt", "w") as f:
#                 f.write(f"Locked at {datetime.now()}")
    
#     def unlock_pc(self):
#         """Unlock the PC"""
#         if self.use_real_controls:
#             # In production, you'd auto-login here
#             pass
#         else:
#             self.log(" PC UNLOCKED (simulated)")
#             if os.path.exists(f"logs/pc_{self.pc_id}_locked.txt"):
#                 os.remove(f"logs/pc_{self.pc_id}_locked.txt")
    
#     def logout_user(self):
#         """Force logout current user"""
#         if self.use_real_controls and platform.system() == "Windows":
#             import subprocess
#             subprocess.run("shutdown /l /f", shell=True)
#         else:
#             self.log("User logged out (simulated)")
    
#     def start_session(self, duration_minutes: int, user_id: str, booking_id: str):
#         """Start a new gaming session"""
#         self.session_active = True
#         self.session_end_time = datetime.now() + timedelta(minutes=duration_minutes)
#         self.current_user_id = user_id
#         self.current_booking_id = booking_id
        
#         self.log(f"SESSION STARTED - User: {user_id}, Duration: {duration_minutes}min")
#         self.unlock_pc()
        
#         # Start monitoring thread
#         monitor_thread = threading.Thread(target=self._monitor_session, daemon=True)
#         monitor_thread.start()
    
#     def extend_session(self, extra_minutes: int):
#         """Extend current session"""
#         if self.session_active and self.session_end_time:
#             old_end = self.session_end_time
#             self.session_end_time += timedelta(minutes=extra_minutes)
#             self.log(f" SESSION EXTENDED +{extra_minutes}min (was {self._format_timeleft(old_end)}, now {self._format_timeleft(self.session_end_time)})")
#             return True
#         return False
    
#     def end_session(self):
#         """End current session"""
#         if self.session_active:
#             # Calculate actual play time
#             played_minutes = (datetime.now() - (self.session_end_time - timedelta(minutes=self.get_remaining_minutes()))).total_seconds() / 60
#             self.total_minutes_played += played_minutes
            
#             self.log(f" SESSION ENDED - User: {self.current_user_id}, Played: {played_minutes:.1f}min, Total: {self.total_minutes_played:.1f}min")
            
#             self.session_active = False
#             self.current_user_id = None
#             self.lock_pc()
#             self.logout_user()
    
#     def get_remaining_minutes(self) -> int:
#         """Get minutes remaining in current session"""
#         if not self.session_active or not self.session_end_time:
#             return 0
#         remaining = (self.session_end_time - datetime.now()).total_seconds()
#         return max(0, int(remaining // 60))
    
#     def get_status(self) -> Dict:
#         """Get current PC status"""
#         return {
#             "pc_id": self.pc_id,
#             "type": self.pc_type,
#             "session_active": self.session_active,
#             "time_remaining": self.get_remaining_minutes(),
#             "current_user": self.current_user_id,
#             "is_locked": not self.session_active
#         }
    
#     def _monitor_session(self):
#         """Background monitor that ends session when time expires"""
#         while self.session_active:
#             time.sleep(10)  # Check every 10 seconds
#             if self.get_remaining_minutes() <= 0:
#                 self.log("Time's up! Ending session...")
#                 self.end_session()
#                 break
    
#     def _format_timeleft(self, end_time: datetime) -> str:
#         """Format remaining time for logging"""
#         remaining = (end_time - datetime.now()).total_seconds()
#         if remaining > 0:
#             minutes = int(remaining // 60)
#             return f"{minutes}min"
#         return "expired"

# # Example usage for testing
# if __name__ == "__main__":
#     # Create 5 agents on one laptop
#     agents = {
#         1: GCAgent(1, "PC"),
#         2: GCAgent(2, "PC"),
#         3: GCAgent(3, "PC"),
#         4: GCAgent(4, "PS"),
#         5: GCAgent(5, "PS"),
#     }
    
#     # Start PC 1 session for testing
#     agents[1].start_session(30, "test_user_001", "booking_001")
    
#     # Run interactive test
#     print("\n=== Gaming Cafe Agent Test Environment ===")
#     print("Available commands:")
#     print("  status              - Show all PC status")
#     print("  start <pc_id> <mins> - Start session")
#     print("  extend <pc_id> <mins> - Extend session")
#     print("  end <pc_id>        - End session")
#     print("  simulate_all       - Simulate usage of all 5 PCs")
#     print("  quit               - Exit")
    
#     while True:
#         cmd = input("\n> ").strip().split()
#         if not cmd:
#             continue
            
#         if cmd[0] == "quit":
#             break
#         elif cmd[0] == "status":
#             for pc_id, agent in agents.items():
#                 status = agent.get_status()
#                 print(f"PC-{pc_id} ({status['type']}): {'🎮ACTIVE' if status['session_active'] else 'LOCKED'} - {status['time_remaining']}min left")
                
#         elif cmd[0] == "start" and len(cmd) >= 3:
#             pc_id = int(cmd[1])
#             mins = int(cmd[2])
#             if pc_id in agents:
#                 agents[pc_id].start_session(mins, f"user_{pc_id}", f"booking_{pc_id}")
                
#         elif cmd[0] == "extend" and len(cmd) >= 3:
#             pc_id = int(cmd[1])
#             mins = int(cmd[2])
#             if pc_id in agents:
#                 agents[pc_id].extend_session(mins)
                
#         elif cmd[0] == "end" and len(cmd) >= 2:
#             pc_id = int(cmd[1])
#             if pc_id in agents:
#                 agents[pc_id].end_session()
                
#         elif cmd[0] == "simulate_all":
#             print("\n🔄 Simulating all 5 PCs...")
#             for pc_id in agents:
#                 print(f"  Starting PC-{pc_id} session...")
#                 agents[pc_id].start_session(15, f"sim_user_{pc_id}", f"sim_booking_{pc_id}")
#             print("All sessions started!")

# __all__ = ["GCAgent"]

import json
import time
import threading
import platform
import os
import asyncio
import websockets
from datetime import datetime, timedelta
from typing import Dict, Optional


class GCAgent:
    """
    Gaming Cafe PC Agent
    Handles session management + WebSocket connection to backend
    """

    def __init__(self, pc_id: int, pc_type: str = "PC", use_real_controls: bool = False,
                 server_url: str = "ws://localhost:8000"):
        self.pc_id = pc_id
        self.pc_type = pc_type
        self.use_real_controls = use_real_controls
        self.server_url = server_url

        # Session state
        self.session_active = False
        self.session_end_time: Optional[datetime] = None
        self.current_user_id = None
        self.current_booking_id = None

        # WebSocket state
        self.ws = None                  # active websocket connection
        self.connected = False
        self._ws_loop = None            # the asyncio loop WS runs on

        self.log_file = f"logs/pc_{pc_id}.log"
        os.makedirs("logs", exist_ok=True)

        # Stats
        self.total_minutes_played = 0

    # ─────────────────────────────────────────────
    # Logging
    # ─────────────────────────────────────────────

    def log(self, message: str):
        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        log_msg = f"[{timestamp}] PC-{self.pc_id}: {message}"
        print(log_msg)
        with open(self.log_file, "a") as f:
            f.write(log_msg + "\n")

    # ─────────────────────────────────────────────
    # PC Controls (real or simulated)
    # ─────────────────────────────────────────────

    def lock_pc(self):
        if self.use_real_controls and platform.system() == "Windows":
            import subprocess
            subprocess.run("rundll32.exe user32.dll,LockWorkStation", shell=True)
        else:
            self.log("🔒 PC LOCKED (simulated)")
            with open(f"logs/pc_{self.pc_id}_locked.txt", "w") as f:
                f.write(f"Locked at {datetime.now()}")

    def unlock_pc(self):
        if self.use_real_controls:
            pass  # production: trigger auto-login here
        else:
            self.log("🔓 PC UNLOCKED (simulated)")
            lock_file = f"logs/pc_{self.pc_id}_locked.txt"
            if os.path.exists(lock_file):
                os.remove(lock_file)

    def logout_user(self):
        if self.use_real_controls and platform.system() == "Windows":
            import subprocess
            subprocess.run("shutdown /l /f", shell=True)
        else:
            self.log("👤 User logged out (simulated)")

    # ─────────────────────────────────────────────
    # Session Management
    # ─────────────────────────────────────────────

    def start_session(self, duration_minutes: int, user_id: str, booking_id: str):
        self.session_active = True
        self.session_end_time = datetime.now() + timedelta(minutes=duration_minutes)
        self.current_user_id = user_id
        self.current_booking_id = booking_id

        self.log(f"▶ SESSION STARTED — User: {user_id}, Duration: {duration_minutes}min")
        self.unlock_pc()

        # Monitor runs in a background thread so it doesn't block the WS loop
        monitor_thread = threading.Thread(target=self._monitor_session, daemon=True)
        monitor_thread.start()

    def extend_session(self, extra_minutes: int):
        if self.session_active and self.session_end_time:
            old_end = self.session_end_time
            self.session_end_time += timedelta(minutes=extra_minutes)
            self.log(f"⏱ SESSION EXTENDED +{extra_minutes}min "
                     f"(was {self._format_timeleft(old_end)}, "
                     f"now {self._format_timeleft(self.session_end_time)})")
            return True
        return False

    def end_session(self):
        if not self.session_active:
            return

        remaining = self.get_remaining_minutes()
        played_minutes = (
            datetime.now() - (self.session_end_time - timedelta(minutes=remaining))
        ).total_seconds() / 60
        self.total_minutes_played += played_minutes

        self.log(f"⏹ SESSION ENDED — User: {self.current_user_id}, "
                 f"Played: {played_minutes:.1f}min, "
                 f"Total: {self.total_minutes_played:.1f}min")

        self.session_active = False
        self.current_user_id = None
        self.current_booking_id = None
        self.session_end_time = None

        self.lock_pc()
        self.logout_user()

        # Notify server that session ended (fire-and-forget)
        self._send_status_nowait()

    def get_remaining_minutes(self) -> int:
        if not self.session_active or not self.session_end_time:
            return 0
        remaining = (self.session_end_time - datetime.now()).total_seconds()
        return max(0, int(remaining // 60))

    def get_status(self) -> Dict:
        return {
            "pc_id": self.pc_id,
            "type": self.pc_type,
            "session_active": self.session_active,
            "time_remaining": self.get_remaining_minutes(),
            "current_user": self.current_user_id,
            "current_booking": self.current_booking_id,
            "is_locked": not self.session_active,
        }

    def _monitor_session(self):
        """Background thread: ends session when time expires."""
        while self.session_active:
            time.sleep(10)
            if self.get_remaining_minutes() <= 0:
                self.log("⏰ Time's up! Ending session...")
                self.end_session()
                break

    def _format_timeleft(self, end_time: datetime) -> str:
        remaining = (end_time - datetime.now()).total_seconds()
        return f"{int(remaining // 60)}min" if remaining > 0 else "expired"

    # ─────────────────────────────────────────────
    # WebSocket — receiving commands from backend
    # ─────────────────────────────────────────────

    def _handle_event(self, event: Dict):
        """
        Dispatch an incoming server event to the right session method.
        Add new actions here as your backend grows.
        """
        action = event.get("action")

        if action == "start_session":
            self.start_session(
                duration_minutes=event["duration_minutes"],
                user_id=event["user_id"],
                booking_id=event["booking_id"],
            )
        elif action == "end_session":
            self.end_session()

        elif action == "extend_session":
            self.extend_session(event["extra_minutes"])

        elif action == "get_status":
            pass  # status is always sent back after every event

        else:
            self.log(f"⚠ Unknown action received: {action}")

    def _send_status_nowait(self):
        """
        Push current status to the server without awaiting.
        Called from sync code (e.g. end_session inside a thread).
        """
        if self.ws and self.connected and self._ws_loop:
            status = json.dumps(self.get_status())
            asyncio.run_coroutine_threadsafe(
                self.ws.send(status),
                self._ws_loop
            )

    async def _connect(self):
        """
        Core async loop: connects to backend, handles messages,
        retries automatically on disconnect.
        """
        uri = f"{self.server_url}/ws/station/{self.pc_id}"

        while True:  # retry loop
            try:
                self.log(f"🔌 Connecting to {uri} ...")
                async with websockets.connect(uri) as ws:
                    self.ws = ws
                    self.connected = True
                    self.log("✅ Connected to server")

                    # Send initial status so server knows we're up
                    await ws.send(json.dumps(self.get_status()))

                    async for raw_message in ws:
                        event = json.loads(raw_message)
                        self.log(f"📨 Received: {event}")

                        # Handle the event (sync session logic)
                        self._handle_event(event)

                        # Always reply with latest status
                        await ws.send(json.dumps(self.get_status()))

            except (websockets.exceptions.ConnectionClosed,
                    ConnectionRefusedError, OSError) as e:
                self.connected = False
                self.ws = None
                self.log(f"❌ Disconnected ({e}). Retrying in 5s...")
                await asyncio.sleep(5)

            except Exception as e:
                self.connected = False
                self.ws = None
                self.log(f"💥 Unexpected error: {e}. Retrying in 5s...")
                await asyncio.sleep(5)

    def run(self):
        """
        Blocking call — starts the WebSocket connection.
        Run this in the main thread (or its own thread).

        Usage:
            agent = GCAgent(pc_id=1)
            agent.run()          # blocks forever, reconnects on drop
        """
        loop = asyncio.new_event_loop()
        self._ws_loop = loop
        asyncio.set_event_loop(loop)
        try:
            loop.run_until_complete(self._connect())
        finally:
            loop.close()

    def run_in_background(self):
        """
        Non-blocking — starts WebSocket in a background thread.
        Useful when you want to control the agent from the same script.

        Usage:
            agent = GCAgent(pc_id=1)
            agent.run_in_background()
            # do other stuff here
        """
        t = threading.Thread(target=self.run, daemon=True)
        t.start()
        return t


__all__ = ["GCAgent"]


# ─────────────────────────────────────────────────────────────────
# Quick test — run: python agent.py
# Make sure backend is running first (uvicorn backend.main:app)
# ─────────────────────────────────────────────────────────────────
if __name__ == "__main__":
    agents = {
        1: GCAgent(1, "PC"),
        2: GCAgent(2, "PC"),
        3: GCAgent(3, "PC"),
        4: GCAgent(4, "PS"),
        5: GCAgent(5, "PS"),
    }

    print("\n=== Gaming Cafe Agent — Local Simulation ===")
    print("Start your backend first: uvicorn backend.main:app --reload")
    print("\nCommands:")
    print("  connect <pc_id>          - Connect agent to backend via WS")
    print("  status                   - Show all PC status")
    print("  start <pc_id> <mins>     - Start session locally (no server)")
    print("  extend <pc_id> <mins>    - Extend session")
    print("  end <pc_id>              - End session")
    print("  simulate_all             - Connect all 5 agents to backend")
    print("  quit                     - Exit\n")

    while True:
        try:
            cmd = input("> ").strip().split()
        except KeyboardInterrupt:
            print("\nExiting...")
            break

        if not cmd:
            continue

        if cmd[0] == "quit":
            break

        elif cmd[0] == "status":
            for pc_id, agent in agents.items():
                s = agent.get_status()
                state = "🎮 ACTIVE" if s["session_active"] else "🔒 LOCKED"
                print(f"  PC-{pc_id} ({s['type']}): {state} — {s['time_remaining']}min left "
                      f"| connected: {agent.connected}")

        elif cmd[0] == "connect" and len(cmd) >= 2:
            pc_id = int(cmd[1])
            if pc_id in agents:
                print(f"Connecting PC-{pc_id} in background...")
                agents[pc_id].run_in_background()
            else:
                print(f"No agent for PC-{pc_id}")

        elif cmd[0] == "simulate_all":
            print("Connecting all agents to backend...")
            for pc_id, agent in agents.items():
                agent.run_in_background()
                time.sleep(0.3)  # slight delay so logs don't collide
            print("All agents connecting — watch the logs above.")

        elif cmd[0] == "start" and len(cmd) >= 3:
            pc_id, mins = int(cmd[1]), int(cmd[2])
            if pc_id in agents:
                agents[pc_id].start_session(mins, f"user_{pc_id}", f"booking_{pc_id}")

        elif cmd[0] == "extend" and len(cmd) >= 3:
            pc_id, mins = int(cmd[1]), int(cmd[2])
            if pc_id in agents:
                agents[pc_id].extend_session(mins)

        elif cmd[0] == "end" and len(cmd) >= 2:
            pc_id = int(cmd[1])
            if pc_id in agents:
                agents[pc_id].end_session()

        else:
            print("Unknown command. Type 'quit' to exit.")