#!/usr/bin/env python3
"""Re-run failed RA rounds with working providers."""
import json, urllib.request, time, os

DIR = "/tmp/agentic-compiler"

SYSTEM = "You are a visionary computer scientist working on the Lucineer agentic compiler project. Write deeply, with concrete examples and architectural specifics. Minimum 4000 characters."

# Load completed rounds for context
ctx = ""
for i in [2, 4, 6, 8]:
    path = f"{DIR}/round-{i}.md"
    try:
        with open(path) as f:
            text = f.read()
            # Extract first 500 chars after header
            lines = text.split("---\n", 1)
            if len(lines) > 1:
                snippet = lines[1].strip()[:400]
                ctx += f"\nRound {i} (completed): {snippet}...\n"
    except: pass

ROUNDS = [
    (1, "10-Year Vision (2036)", """Imagine it is 2036. The Agentic Compiler is mature and widely used. Describe in vivid detail:
1. What does the TUI/IDE look like? Walk through a user session.
2. What does it FEEL like to use — the emotional experience of programming when compilation is deliberation?
3. What capabilities exist that are impossible with today's tools?
4. How do developers interact with the swarm? What's the conversation like?
5. Show a concrete example: developer writes markdown, swarm deliberates, runtime evolves.
6. What surprised people most about how programming changed?
7. What does "compilation" mean to a 12-year-old learning to code in 2036?"""),
    (3, "Error as Signal", """Explore the inversion of "error as signal, not failure":
1. What does a world look like where errors generate training data instead of frustration?
2. The user writes broken code. What happens? Walk through the experience second by second.
3. How does the stable runtime continue while experimental code fails?
4. "Breaking code is merely a clue to another routine" — what routines? How are they discovered?
5. The emotional design: how do you make failure feel like progress?
6. Error taxonomy for the agentic compiler. What kinds of errors exist? How are they classified?
7. A concrete scenario: memory leak discovered through error signal analysis."""),
    (5, "Git as Instruction Manual", """Explore git as the first-class organizational principle:
1. How does the compiler READ git history to understand the project?
2. What signals in git history are most valuable?
3. The compiler encounters a new project. Walk through what it learns from git history.
4. How does the compiler use past experiments to inform current deliberations?
5. "The git structure is the instruction manual" — design that reading process.
6. How does fork-based collaboration work with agentic compilation?
7. A concrete scenario: compiler learns from history that project always breaks when X changes."""),
    (7, "Swarm Deliberation Protocol", """Design how agents argue and deliberate during compilation:
1. What does "deliberation" actually mean? What's the conversation format?
2. How do agents disagree? How are conflicts resolved?
3. Agent roles: advocate, critic, synthesizer, experimenter, historian.
4. How does the swarm reach consensus?
5. What happens when the swarm is split 50/50?
6. The role of the human developer in deliberation.
7. Concrete dialogue: three agents debating how to compile a recursive function."""),
    (9, "5-Year Bridge Synthesis", f"""SYNTHESIS ROUND. Prior completed rounds:{ctx}
Now synthesize:
1. What is the MINIMUM VIABLE agentic compiler for 2028?
2. What can be built TODAY with current tools?
3. What requires advances we don't have yet?
4. The critical path: what MUST be built first?
5. Three concrete milestones for the next 2 years.
6. What can we ship as a real product in 6 months?"""),
    (10, "Dynamic Roadmap", f"""FINAL ROUND. Comprehensive roadmap:{ctx}
1. Current state: Lucineer ecosystem (deckboss, cocapn, 200+ repos, vessel-bridge, fleet-knowledge)
2. Phase 1 (0-6 months): Build immediately. Concrete repos and features.
3. Phase 2 (6-18 months): Deliberation layer.
4. Phase 3 (18-36 months): Swarm compilation.
5. Phase 4 (3-5 years): Bridge to 10-year vision.
6. Phase 5 (5-10 years): Full vision.
7. Plot holes and gaps.
8. External dependencies.
9. Risk factors and mitigations.
10. The ONE thing that makes everything else easier."""),
]

def call_deepseek(user_msg, model="deepseek-chat", temp=0.8, retry=True):
    body = json.dumps({"model": model, "messages": [
        {"role": "system", "content": SYSTEM},
        {"role": "user", "content": user_msg}
    ], "max_tokens": 4000, "temperature": temp}).encode()
    try:
        r = urllib.request.Request("https://api.deepseek.com/chat/completions", data=body, method="POST",
            headers={"Authorization": "Bearer sk-5fc339a4fcc748ffba658c615bc2564d", "Content-Type": "application/json"})
        with urllib.request.urlopen(r, timeout=120) as resp:
            data = json.loads(resp.read())
            return data["choices"][0]["message"]["content"]
    except Exception as e:
        if retry:
            print(f"  RETRY: {e}")
            time.sleep(5)
            return call_deepseek(user_msg, model, temp, False)
        return f"[ERROR: {e}]"

def run_round(num, title, prompt):
    print(f"\n{'='*60}")
    print(f"ROUND {num}: {title}")
    print(f"{'='*60}")
    
    model = "deepseek-reasoner" if num in [9, 10] else "deepseek-chat"
    temp = 0.7 if num in [9, 10] else 0.85
    
    full = (f"CONTEXT FROM COMPLETED ROUNDS:\n{ctx}\n\n" if ctx else "") + prompt
    result = call_deepseek(full, model, temp)
    
    path = f"{DIR}/round-{num}.md"
    with open(path, "w") as f:
        f.write(f"# Round {num}: {title}\n\n**Model**: {model}  \n**Date**: {time.strftime('%Y-%m-%d %H:%M')}\n\n---\n\n")
        f.write(result)
    
    print(f"  {len(result)} chars -> {path}")
    return result

if __name__ == "__main__":
    total = 0
    for num, title, prompt in ROUNDS:
        result = run_round(num, title, prompt)
        total += len(result)
        time.sleep(1)
    
    print(f"\nALL 6 RERUN ROUNDS COMPLETE ({total} chars)")
