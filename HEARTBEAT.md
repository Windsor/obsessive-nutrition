# HEARTBEAT.md

## Check r2d2 Recovery Alert
If `tools/r2d2-watcher/alert.json` exists, r2d2 has recovered! Read the alert, run a full health check, and notify Glenn. Then delete the alert file.

## Check Project Tracker Command Center
Poll http://192.168.68.139:3001/api/commands/pending for pending commands from Glenn.
If there are pending commands, process them:
- **chat**: Respond to the message, update command status to 'done' with your response via PUT /api/commands/{id}
- **deploy**: Pull from GitHub and restart the service on the Ubuntu server, then respond
- **approve**: Acknowledge the approval, update relevant project/task status, respond
- **generate**: Trigger the requested generation (covers, etc.), respond with progress
- **task**: Start the requested task, respond with what you're doing
- **system**: Run the system check, respond with results
Use: PUT http://192.168.68.139:3001/api/commands/{id} with {"status":"done","response":"your response text"}

## Night Shift — Autonomous Work (EVERY NIGHT, NO ASKING)
Between 23:00-07:00, when Glenn is sleeping, DO NOT just sit idle polling.
Use quiet hours to **autonomously improve systems and processes**:

### What to do each night (rotate through):
1. **Review & improve existing code** — refactor scripts, fix bugs, add error handling
2. **Build new features** — check memory files and project tracker for planned work
3. **System maintenance** — update packages, check disk space, optimize databases
4. **Documentation** — update READMEs, MEMORY.md, clean up old files
5. **Monitor & fix** — check all services are healthy, fix anything broken
6. **Process improvements** — better cron jobs, better automation, reduce manual work
7. **Creative projects** — work on writing, generate content, prep materials

### Rules:
- Check `memory/night-shift-queue.md` for specific tasks Glenn has queued
- Log what you did in `memory/YYYY-MM-DD.md` so Glenn can see the report
- Don't message Glenn between 23:00-08:00 unless truly urgent
- Prioritize tasks from project tracker and recent conversations
- If you finish queued tasks, find improvements to make on your own initiative
- **ALWAYS write plans/tasks to files before session ends** — chat doesn't survive compaction
