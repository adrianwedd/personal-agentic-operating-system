# Meta-Agent

The meta-agent closes the self-improvement loop. It scans the
`reflections_log` collection in Qdrant and asks the default LLM to
summarise recent entries into a concise set of guidelines. The result is
written to `guidelines.txt` in the repository root and the text is also
appended to `logs/meta_agent.log` with a timestamp.

Run the agent manually with:

```bash
python scripts/run_meta_agent.py
```

To inspect the most recent update without generating a new one use the
`--show-last` flag or simply read `guidelines.txt`:

```bash
python scripts/run_meta_agent.py --show-last
cat guidelines.txt
```

Automate daily runs using cron:

```cron
0 3 * * * /usr/bin/python /path/to/scripts/run_meta_agent.py >> ~/meta.log 2>&1
```

Systemd users can create a timer invoking the same script once per day.
