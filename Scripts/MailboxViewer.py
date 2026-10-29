#!/usr/bin/env python3
"""
================================================================================
One Boss Fight — Team Mailbox Monitor & Live AI Coordination Dashboard
================================================================================
Monitors Documentation/TEAM_MAILBOX.md in real time with:
  1. Live AI Task Board: tracks Codex, Claude, Antigravity, and Owner directives.
  2. Mobile View Optimization: fully responsive on smartphones, tablets & desktop.
  3. Interactive Message Composer: type and send messages directly into the mailbox
     so all AI agents (Codex, Claude, Antigravity) immediately receive and act on them.
  4. Dual Interface: Zero-dependency background HTTP dashboard (port 8080) +
     optional Native Tkinter desktop GUI.

Usage:
    python Scripts/MailboxViewer.py [--port 8080] [--web-only]
================================================================================
"""

import os
import sys
import re
import json
import time
import socket
import threading
import webbrowser
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse

# Determine project paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
MAILBOX_PATH = os.path.join(PROJECT_ROOT, "Documentation", "TEAM_MAILBOX.md")

# Default HTTP server port
DEFAULT_PORT = 8080


def get_lan_ip():
    """Detects the host machine's primary LAN IP for mobile phone connectivity."""
    try:
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        s.connect(('8.8.8.8', 80))
        ip = s.getsockname()[0]
        s.close()
        return ip
    except Exception:
        return "127.0.0.1"


# ==============================================================================
# 1. PARSER & DATA MODEL
# ==============================================================================

class MailboxParser:
    """Parses TEAM_MAILBOX.md into structured message models with action extraction."""

    HEADER_REGEX = re.compile(
        r'(?m)^### \[(?P<id>[^\]]+)\]\s*(?P<sender>[^->\n\r]+?)\s*->\s*(?P<recipient>[^,\n\r]+?)(?:,\s*(?P<timestamp>[^\r\n]*))?$'
    )

    @staticmethod
    def parse_timestamp(raw_ts):
        """
        Parses header timestamp string into date, time, timezone, and explicit recorded flag.
        Never derives per-message time from file mtime or fabricates midnight.
        """
        if not raw_ts:
            return {
                "raw": "",
                "date": "",
                "time": "",
                "tz": "",
                "time_recorded": False,
                "display": "[time not recorded]"
            }

        raw = raw_ts.strip()
        date_match = re.search(r'\b(\d{4}-\d{2}-\d{2})\b', raw)
        date_str = date_match.group(1) if date_match else ""

        # Time HH:MM or HH:MM:SS (must be preceded by whitespace or T)
        time_match = re.search(r'(?:[\sT])(\d{1,2}:\d{2}(?::\d{2})?)\b', raw)
        time_str = time_match.group(1) if time_match else ""

        # Timezone offset: e.g. +05:30, +00:00, -04:00, Z, UTC, GMT, IST, etc.
        tz_match = re.search(r'(?:[\s])([+-]\d{2}:?\d{2}|Z|UTC|GMT|IST)\b', raw)
        tz_str = tz_match.group(1) if tz_match else ""

        time_recorded = bool(time_str)

        if time_recorded:
            parts = []
            if date_str:
                parts.append(date_str)
            parts.append(time_str)
            if tz_str:
                parts.append(tz_str)
            display = " ".join(parts)
        else:
            if date_str:
                extra = raw.replace(date_str, "").strip(" ,()-")
                if extra and extra.lower() != "local":
                    display = f"{date_str} · [time not recorded] ({extra})"
                elif extra and extra.lower() == "local":
                    display = f"{date_str} · [time not recorded] (local)"
                else:
                    display = f"{date_str} · [time not recorded]"
            else:
                display = f"{raw} · [time not recorded]"

        return {
            "raw": raw,
            "date": date_str,
            "time": time_str,
            "tz": tz_str,
            "time_recorded": time_recorded,
            "display": display
        }

    @classmethod
    def parse_text_blocks(cls, text):
        matches = list(cls.HEADER_REGEX.finditer(text))
        messages = []
        for i, match in enumerate(matches):
            start = match.start()
            end = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            block = text[start:end]

            msg_id = match.group("id").strip()
            sender = match.group("sender").strip()
            recipient = match.group("recipient").strip()
            timestamp = (match.group("timestamp") or "").strip()

            header_line = match.group(0).strip()
            body = block[len(header_line):].strip()

            sender_norm = cls._normalize_agent(sender)
            recipient_norm = cls._normalize_agent(recipient)

            action_points = cls._extract_action_points(body)
            has_actions = any(len(v) > 0 for v in action_points.values())

            ts_info = cls.parse_timestamp(timestamp)

            messages.append({
                "index": i + 1,
                "id": msg_id,
                "sender": sender,
                "sender_norm": sender_norm,
                "recipient": recipient,
                "recipient_norm": recipient_norm,
                "timestamp": ts_info["display"],
                "raw_timestamp": timestamp,
                "time_recorded": ts_info["time_recorded"],
                "date_str": ts_info["date"],
                "time_str": ts_info["time"],
                "tz_str": ts_info["tz"],
                "body": body,
                "char_count": len(body),
                "action_points": action_points,
                "has_actions": has_actions
            })
        return messages

    @classmethod
    def parse_file(cls, filepath=MAILBOX_PATH):
        """Parses the mailbox markdown file into a full structured report, resolving archive links seamlessly."""
        if not os.path.isfile(filepath):
            return {
                "exists": False,
                "error": f"Mailbox not found at: {filepath}",
                "messages": [],
                "latest": None,
                "count": 0,
                "mtime": 0
            }

        mtime = os.path.getmtime(filepath)
        size = os.path.getsize(filepath)

        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                text = f.read()
        except Exception as e:
            return {
                "exists": False,
                "error": str(e),
                "messages": [],
                "latest": None,
                "count": 0,
                "mtime": mtime
            }

        # Check for archive reference
        archive_match = re.search(r'\[(?:TEAM_MAILBOX_before[^\]]*|MailboxArchive[^\]]*)\]\(([^)]+)\)', text)
        messages = []
        if archive_match:
            arch_raw_path = archive_match.group(1).replace('/', os.sep)
            if not os.path.isabs(arch_raw_path):
                arch_path = os.path.normpath(os.path.join(os.path.dirname(filepath), arch_raw_path))
            else:
                arch_path = os.path.normpath(arch_raw_path)

            if os.path.isfile(arch_path):
                try:
                    with open(arch_path, "r", encoding="utf-8", errors="replace") as af:
                        messages = cls.parse_text_blocks(af.read())
                except Exception:
                    pass

        # Parse active messages
        end_idx = text.find("END ARCHIVED MESSAGE HEADING INDEX")
        active_chunk = text[end_idx:] if end_idx != -1 else text
        active_msgs = cls.parse_text_blocks(active_chunk)

        if not messages:
            messages = cls.parse_text_blocks(text)
        else:
            arch_ids = {m["id"] for m in messages}
            for am in active_msgs:
                if am["id"] not in arch_ids:
                    messages.append(am)
                else:
                    idx = next((i for i, x in enumerate(messages) if x["id"] == am["id"]), None)
                    if idx is not None and am["char_count"] > messages[idx]["char_count"]:
                        messages[idx] = am

        for i, msg in enumerate(messages):
            msg["index"] = i + 1

        latest = messages[-1] if messages else None

        action_summary = {
            "Claude": sum(len(m["action_points"]["Claude"]) for m in messages),
            "Codex": sum(len(m["action_points"]["Codex"]) for m in messages),
            "Antigravity": sum(len(m["action_points"]["Antigravity"]) for m in messages),
            "Owner": sum(len(m["action_points"]["Owner"]) for m in messages)
        }

        ai_tasks = cls._extract_ai_tasks(messages)

        return {
            "exists": True,
            "filepath": filepath,
            "mtime": mtime,
            "size_bytes": size,
            "count": len(messages),
            "messages": messages,
            "latest": latest,
            "action_summary": action_summary,
            "ai_tasks": ai_tasks
        }

    @staticmethod
    def _normalize_agent(text):
        t = text.lower()
        if "claude" in t:
            return "Claude"
        if "codex" in t or "astra" in t:
            return "Codex"
        if "antigravity" in t or "ag" in t:
            return "Antigravity"
        if "owner" in t:
            return "Owner"
        return "Team"

    @classmethod
    def _extract_action_points(cls, body):
        actions = {"Claude": [], "Codex": [], "Antigravity": [], "Owner": [], "General": []}
        lines = body.splitlines()

        for line in lines:
            sline = line.strip()
            if not sline:
                continue

            m_codex = re.match(r'^(?:CODEX|OPEN FOR CODEX|CODEX QUEUE|FOR CODEX):\s*(.*)', sline, re.I)
            m_ag = re.match(r'^(?:ANTIGRAVITY|AG|OPEN FOR AG|FOR AG|FOR ANTIGRAVITY):\s*(.*)', sline, re.I)
            m_claude = re.match(r'^(?:CLAUDE|OPEN FOR CLAUDE|FOR CLAUDE):\s*(.*)', sline, re.I)
            m_owner = re.match(r'^(?:OWNER|DECISION NEEDED(?:\s*\(owner\))?|OWNER DECISION|FOR OWNER):\s*(.*)', sline, re.I)
            m_task = re.match(r'^(?:TASK|NEXT ACTION|QUEUE|ACTION):\s*(.*)', sline, re.I)

            if m_codex:
                val = m_codex.group(1).strip()
                if val: actions["Codex"].append(val)
            elif m_ag:
                val = m_ag.group(1).strip()
                if val: actions["Antigravity"].append(val)
            elif m_claude:
                val = m_claude.group(1).strip()
                if val: actions["Claude"].append(val)
            elif m_owner:
                val = m_owner.group(1).strip()
                if val: actions["Owner"].append(val)
            elif m_task:
                val = m_task.group(1).strip()
                if val: actions["General"].append(val)

        return actions

    @classmethod
    def _extract_ai_tasks(cls, messages):
        """Builds structured live task profiles dynamically from real messages for Claude, Antigravity, Owner, and Codex."""
        keys_pattern = r'(?:TASK|STATUS|STATUS OF MY REVIEW|EVIDENCE|NEXT ACTION|NEXT CLAUDE ACTUALSOURCE|NEXT|BOUNDARIES|STATE|FINDINGS|RE|WORK ORDER|OBJECTIVE)'

        def extract_field(body, key_list):
            if not body:
                return None
            for k in key_list:
                m = re.search(rf'(?im)\b{re.escape(k)}\s*:\s*(.*?)(?=\b{keys_pattern}\s*:|$)', body)
                if m:
                    val = m.group(1).strip()
                    val = re.sub(r'[\r\n]+', ' ', val).strip()
                    if val:
                        return val[:140]
            return None

        def parse_relative_time(ts_str):
            if not ts_str:
                return "Unknown", 999999
            try:
                m = re.search(r'(\d{4}-\d{2}-\d{2}\s+\d{2}:\d{2})', ts_str)
                if m:
                    dt = datetime.strptime(m.group(1), "%Y-%m-%d %H:%M")
                    now = datetime.now()
                    diff = (now - dt).total_seconds()
                    diff_m = int(diff // 60)
                    if diff_m < 0: diff_m = 0
                    if diff_m < 1: rel = "just now"
                    elif diff_m < 60: rel = f"{diff_m}m ago"
                    elif diff_m < 1440: rel = f"{diff_m//60}h ago"
                    else: rel = f"{diff_m//1440}d ago"
                    return rel, diff_m
            except Exception:
                pass
            return ts_str, 999999

        agents_meta = {
            "Claude": {
                "name": "Claude",
                "avatar": "🟢",
                "role": "Technical Lead & Reviewer",
                "default_directive": "Lead Review & Verification",
                "border_color": "emerald"
            },
            "Antigravity": {
                "name": "Antigravity",
                "avatar": "🔵",
                "role": "Implementer & Build Operator",
                "default_directive": "Content Delivery & Build Operations",
                "border_color": "sky"
            },
            "Owner": {
                "name": "Owner",
                "avatar": "🟡",
                "role": "Project Owner & Steering",
                "default_directive": "Steering & Directives",
                "border_color": "amber"
            },
            "Codex": {
                "name": "Codex",
                "avatar": "🟣",
                "role": "Architecture Advisor",
                "default_directive": "Directives & Oversight",
                "border_color": "purple"
            }
        }

        tasks_data = {}
        for agent_key, meta in agents_meta.items():
            agent_msgs = [msg for msg in messages if msg.get("sender_norm") == agent_key]
            if not agent_msgs:
                tasks_data[agent_key] = {
                    "name": meta["name"],
                    "avatar": meta["avatar"],
                    "role": meta["role"],
                    "status": "No messages logged",
                    "status_color": "slate",
                    "is_active": False,
                    "activity_state": "idle",
                    "last_seen": "None",
                    "active_directive": meta["default_directive"],
                    "current_status": "Idle",
                    "next_action": "",
                    "source_msg_id": "",
                    "latest_sent_id": "",
                    "tasks": []
                }
                continue

            latest_m = agent_msgs[-1]
            rel_time, diff_m = parse_relative_time(latest_m.get("timestamp", ""))

            directive = extract_field(latest_m.get("body", ""), ["TASK", "WORK ORDER", "RE", "OBJECTIVE"])
            if not directive:
                lines = [l.strip() for l in latest_m.get("body", "").splitlines() if l.strip()]
                directive = lines[0][:100] if lines else meta["default_directive"]

            status_text = extract_field(latest_m.get("body", ""), ["STATUS", "STATUS OF MY REVIEW", "REPORT", "FINDINGS", "STATE"]) or "Message Dispatched"
            next_action = extract_field(latest_m.get("body", ""), ["NEXT CLAUDE ACTUALSOURCE", "NEXT ACTION", "NEXT", "WHAT I NEED FROM YOU"]) or ""

            if agent_key == "Codex":
                is_active = (diff_m <= 120)
                activity_state = "active" if is_active else "inactive"
                status_label = f"Active ({rel_time})" if is_active else "Inactive (Retired)"
                status_color = "purple" if is_active else "slate"
            elif diff_m <= 60 or "waiting" in status_text.lower() or "mailboxnext" in next_action.lower():
                is_active = True
                status_color = "emerald" if diff_m <= 60 else "amber"
                if "waiting" in status_text.lower() or "mailboxnext" in next_action.lower():
                    activity_state = "waiting"
                    status_label = f"Waiting ({rel_time})"
                else:
                    activity_state = "active"
                    status_label = f"Active ({rel_time})"
            elif diff_m <= 240:
                is_active = True
                activity_state = "standby"
                status_label = f"Standby ({rel_time})"
                status_color = "sky"
            else:
                is_active = False
                activity_state = "idle"
                status_label = f"Idle ({rel_time})"
                status_color = "slate"

            tasks_list = []
            for m in reversed(agent_msgs[-4:]):
                m_task = extract_field(m.get("body", ""), ["TASK", "WORK ORDER", "RE", "OBJECTIVE"])
                if not m_task:
                    m_lines = [l.strip() for l in m.get("body", "").splitlines() if l.strip()]
                    m_task = m_lines[0][:60] if m_lines else f"Message {m.get('id', '')}"

                m_status = extract_field(m.get("body", ""), ["STATUS", "STATUS OF MY REVIEW", "REPORT", "STATE"]) or "Dispatched"
                icon = "🔄"
                m_full = (m_status + " " + m.get("body", "")[:300]).lower()
                m_full_sanitized = re.sub(r'\b(no\s+failures?|0\s+fails?|0\s+failed|0\s+errors?)\b', 'clean', m_full)
                if any(w in m_full_sanitized for w in ["accepted", "pass", "completed", "pushed", "exit 0"]):
                    icon = "✅"
                elif any(w in m_full_sanitized for w in ["rejected", "fail", "error"]):
                    icon = "❌"
                elif any(w in m_full_sanitized for w in ["waiting", "awaiting", "standby"]):
                    icon = "⏳"

                tasks_list.append({
                    "id": m.get("id", ""),
                    "title": m_task[:55],
                    "status": "completed" if icon == "✅" else ("failed" if icon == "❌" else "in_progress"),
                    "status_icon": icon,
                    "detail": m_status[:100],
                    "source": m.get("id", ""),
                    "timestamp": m.get("timestamp", "")
                })

            tasks_data[agent_key] = {
                "name": meta["name"],
                "avatar": meta["avatar"],
                "role": meta["role"],
                "status": status_label,
                "status_color": status_color,
                "is_active": is_active,
                "activity_state": activity_state,
                "last_seen": rel_time,
                "active_directive": directive,
                "current_status": status_text,
                "next_action": next_action,
                "source_msg_id": latest_m.get("id", ""),
                "latest_sent_id": latest_m.get("id", ""),
                "tasks": tasks_list
            }

        return tasks_data

# ==============================================================================
# 2. MAILBOX WRITER (COMPOSE MESSAGE)
# ==============================================================================

class MailboxWriter:
    """Safely appends structured messages to Documentation/TEAM_MAILBOX.md."""

    @classmethod
    def get_next_id(cls, prefix="O", filepath=MAILBOX_PATH):
        """Calculates the next sequential ID for the given prefix (e.g. O-1, X-164, etc.)."""
        if not os.path.exists(filepath):
            return f"{prefix}-1"
        try:
            with open(filepath, "r", encoding="utf-8", errors="replace") as f:
                content = f.read()
            pattern = re.compile(r'(?m)^### \[' + re.escape(prefix) + r'-(\d+)\]')
            matches = [int(m) for m in pattern.findall(content)]
            next_num = max(matches) + 1 if matches else 1
            return f"{prefix}-{next_num}"
        except Exception:
            return f"{prefix}-1"

    @classmethod
    def append_message(cls, sender="Owner", recipient="All", body="", prefix="O", task="", filepath=MAILBOX_PATH):
        """Appends a new formatted message block to TEAM_MAILBOX.md."""
        if not body.strip():
            raise ValueError("Message body cannot be empty")

        clean_sender = sender.strip() or "Owner"
        clean_recipient = recipient.strip() or "All"
        clean_prefix = (prefix.strip().upper() or "O")

        if clean_sender == "Owner":
            clean_prefix = "O"
        elif clean_sender == "Codex":
            clean_prefix = "X"
        elif clean_sender == "Claude":
            clean_prefix = "C"
        elif clean_sender == "Antigravity":
            clean_prefix = "A"

        msg_id = cls.get_next_id(prefix=clean_prefix, filepath=filepath)
        now = datetime.now().astimezone()
        tz_offset = now.strftime("%z")
        if len(tz_offset) == 5:
            tz_offset = f"{tz_offset[:3]}:{tz_offset[3:]}"
        timestamp_str = now.strftime(f"%Y-%m-%d %H:%M:%S {tz_offset}")

        header = f"### [{msg_id}] {clean_sender} -> {clean_recipient}, {timestamp_str}"

        body_text = body.strip()
        if task.strip() and not re.search(r'^(?:TASK|STATUS|FINDINGS):', body_text, re.I):
            body_text = f"TASK: {task.strip()}\n\n{body_text}"

        formatted_block = f"\n\n{header}\n{body_text}\n"

        with open(filepath, "a", encoding="utf-8") as f:
            f.write(formatted_block)

        return {
            "success": True,
            "message_id": msg_id,
            "header": header,
            "sender": clean_sender,
            "recipient": clean_recipient,
            "timestamp": timestamp_str,
            "body": body_text
        }


# ==============================================================================
# 3. WEB SERVER & RESPONSIVE DASHBOARD
# ==============================================================================

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=5.0, viewport-fit=cover">
  <title>One Boss Fight — Team Mailbox Monitor</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body { background-color: #0f172a; color: #e2e8f0; font-family: system-ui, -apple-system, sans-serif; -webkit-tap-highlight-color: transparent; }
    .custom-scroll::-webkit-scrollbar { width: 6px; height: 6px; }
    .custom-scroll::-webkit-scrollbar-track { background: #1e293b; }
    .custom-scroll::-webkit-scrollbar-thumb { background: #475569; border-radius: 3px; }
    .tag-claude { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }
    .tag-codex { background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.4); }
    .tag-ag { background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); }
    .tag-owner { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }
    .tag-general { background: rgba(148, 163, 184, 0.2); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.4); }

    /* Touch & Responsive Single-Pane / Dual-Pane Layout */
    @media (max-width: 1023px) {
      .mobile-view { display: none !important; }
      .mobile-view.active { display: flex !important; }
      body.mobile-detail-mode #search-filter-bar { display: none !important; }
      textarea, input, select { font-size: 16px !important; } /* Prevent iOS safari zoom */
    }
    @media (min-width: 1024px) {
      .mobile-view { display: flex !important; }
    }
  </style>
</head>
<body class="h-screen flex flex-col overflow-hidden select-none sm:select-auto">

  <!-- Header -->
  <header class="bg-slate-900 border-b border-slate-800 px-3 sm:px-6 py-2.5 flex items-center justify-between shrink-0 shadow-md">
    <div class="flex items-center space-x-2 sm:space-x-3">
      <div class="w-3 h-3 rounded-full bg-emerald-400 animate-pulse"></div>
      <h1 class="text-sm sm:text-lg font-bold text-slate-100 tracking-wide flex items-center gap-1.5 sm:gap-2">
        <span>⚔️ One Boss Fight</span>
        <span class="text-[10px] sm:text-xs bg-slate-800 text-slate-400 px-1.5 py-0.5 rounded border border-slate-700 font-mono">MAILBOX</span>
      </h1>
    </div>

    <!-- Header Quick Actions & Stats -->
    <div class="flex items-center space-x-2 sm:space-x-3 text-xs">
      <!-- Compose Button (Desktop & Mobile) -->
      <button onclick="openComposeModal()"
              class="bg-emerald-600 hover:bg-emerald-500 text-white font-bold px-2.5 py-1.5 sm:px-3 sm:py-1.5 rounded-lg shadow-sm flex items-center gap-1.5 transition cursor-pointer active:scale-95">
        <span>✍️</span>
        <span class="hidden sm:inline">Compose</span>
      </button>

      <!-- Task Board Toggle Button (Desktop) -->
      <button id="task-board-toggle-btn" onclick="toggleTaskBoard()"
              class="hidden lg:flex bg-cyan-950/80 hover:bg-cyan-900 text-cyan-300 border border-cyan-700/80 px-2.5 py-1.5 rounded-lg font-semibold items-center gap-1.5 transition cursor-pointer">
        <span>📋 Tasks</span>
        <span id="toggle-arrow" class="text-[10px]">▲</span>
      </button>

      <!-- Mobile URL Pill -->
      <span id="mobile-url-badge" title="Access this dashboard on your phone via this URL"
            class="hidden md:inline-block bg-slate-800 text-slate-300 border border-slate-700 px-2 py-1 rounded font-mono text-[11px] cursor-pointer hover:border-cyan-500"
            onclick="copyMobileUrl()">
        📱 <span id="lan-ip-text">LAN: ...</span>
      </span>

      <!-- Live Indicator -->
      <span class="text-slate-400 text-[11px] sm:text-xs flex items-center gap-1 font-mono">
        <strong id="msg-count" class="text-emerald-400">0</strong>
        <span class="hidden sm:inline text-slate-500">msgs</span>
      </span>
      <span id="poll-indicator" class="text-emerald-400 font-mono text-[11px] sm:text-xs">● 1s</span>
    </div>
  </header>

  <!-- Mobile View Selector Bar (visible only on screens < 900px) -->
  <nav id="mobile-nav" class="lg:hidden bg-slate-950 border-b border-slate-800 px-2 py-1.5 flex items-center justify-around shrink-0 text-xs">
    <button onclick="switchMobileTab('feed')" id="tab-btn-feed"
            class="mobile-tab-btn flex-1 py-1.5 text-center font-bold text-cyan-400 border-b-2 border-cyan-400 transition">
      📨 Messages
    </button>
    <button onclick="switchMobileTab('detail')" id="tab-btn-detail"
            class="mobile-tab-btn flex-1 py-1.5 text-center font-medium text-slate-400 border-b-2 border-transparent transition">
      📄 Detail
    </button>
    <button onclick="switchMobileTab('tasks')" id="tab-btn-tasks"
            class="mobile-tab-btn flex-1 py-1.5 text-center font-medium text-slate-400 border-b-2 border-transparent transition">
      📋 AI Tasks
    </button>
    <button onclick="openComposeModal()"
            class="py-1 px-3 bg-emerald-700 text-white rounded font-bold transition active:scale-95">
      ✍️ Send
    </button>
  </nav>

  <!-- Expandable AI Task Board (Desktop View) -->
  <section id="ai-task-board" class="hidden lg:block bg-slate-950 border-b border-slate-800 p-3 shrink-0 transition-all">
    <div class="flex items-center justify-between mb-2">
      <div class="flex items-center gap-2">
        <span class="w-2 h-2 rounded-full bg-cyan-400 animate-pulse"></span>
        <span class="text-xs font-bold text-slate-200 tracking-wider uppercase">Active AI Agent Tasks & Directives</span>
        <span class="text-[10px] bg-slate-800 text-slate-400 px-1.5 py-0.2 rounded border border-slate-700 font-mono">AUTO-UPDATING</span>
      </div>
      <span class="text-[11px] text-slate-400">Click any message <span class="text-cyan-400 font-mono underline">[ID]</span> to jump directly to message in feed</span>
    </div>
    <div id="ai-task-cards" class="grid grid-cols-1 md:grid-cols-2 xl:grid-cols-4 gap-2.5">
      <!-- Populated dynamically via JS -->
    </div>
  </section>

  <!-- Compact Directives Bar (visible on desktop when Task Board is collapsed) -->
  <div id="ai-task-compact-bar" class="hidden lg:hidden bg-slate-950 border-b border-slate-800 px-6 py-2 grid grid-cols-4 gap-3 text-xs shrink-0">
    <div class="bg-slate-900/80 p-2 rounded border border-slate-800 cursor-pointer hover:bg-slate-800/80 transition" onclick="toggleTaskBoard()">
      <div class="flex justify-between items-center mb-0.5">
        <span class="font-semibold text-emerald-400">🟢 Claude (Lead Reviewer)</span>
        <span id="compact-claude-src" class="text-[10px] text-slate-500 font-mono"></span>
      </div>
      <p id="compact-claude" class="text-slate-300 truncate">Lead Review</p>
    </div>
    <div class="bg-slate-900/80 p-2 rounded border border-slate-800 cursor-pointer hover:bg-slate-800/80 transition" onclick="toggleTaskBoard()">
      <div class="flex justify-between items-center mb-0.5">
        <span class="font-semibold text-sky-400">🔵 Antigravity (Implementer)</span>
        <span id="compact-ag-src" class="text-[10px] text-slate-500 font-mono"></span>
      </div>
      <p id="compact-ag" class="text-slate-300 truncate">Implementation</p>
    </div>
    <div class="bg-slate-900/80 p-2 rounded border border-slate-800 cursor-pointer hover:bg-slate-800/80 transition" onclick="toggleTaskBoard()">
      <div class="flex justify-between items-center mb-0.5">
        <span class="font-semibold text-amber-400">🟡 Owner (Steering)</span>
        <span id="compact-owner-src" class="text-[10px] text-slate-500 font-mono"></span>
      </div>
      <p id="compact-owner" class="text-slate-300 truncate">Steering & Directives</p>
    </div>
    <div class="bg-slate-900/80 p-2 rounded border border-slate-800 cursor-pointer hover:bg-slate-800/80 transition" onclick="toggleTaskBoard()">
      <div class="flex justify-between items-center mb-0.5">
        <span class="font-semibold text-purple-400">🟣 Codex (Retired)</span>
        <span id="compact-codex-src" class="text-[10px] text-slate-500 font-mono"></span>
      </div>
      <p id="compact-codex" class="text-slate-300 truncate">Budget Exhausted</p>
    </div>
  </div>

  <!-- Search & Filter Controls -->
  <div id="search-filter-bar" class="bg-slate-900 px-3 sm:px-6 py-2 border-b border-slate-800 flex flex-wrap items-center justify-between gap-2 text-xs shrink-0">
    <div class="flex items-center gap-2 flex-1 min-w-[200px]">
      <input type="text" id="search-box" placeholder="Search ID, agent, task, or text..."
             class="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-1.5 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500">
    </div>
    <div class="flex items-center gap-1.5 overflow-x-auto custom-scroll py-0.5">
      <button onclick="setFilter('ALL')" class="filter-btn px-2 py-1 rounded bg-slate-800 border border-slate-700 hover:bg-slate-700 text-slate-200 font-medium" data-filter="ALL">All</button>
      <button onclick="setFilter('ACTIONS')" class="filter-btn px-2 py-1 rounded bg-slate-800/50 border border-slate-700 hover:bg-slate-700 text-amber-300" data-filter="ACTIONS">⚡ Actions</button>
      <button onclick="setFilter('Owner')" class="filter-btn px-2 py-1 rounded bg-slate-800/50 border border-slate-700 hover:bg-slate-700 text-amber-400" data-filter="Owner">Owner</button>
      <button onclick="setFilter('Codex')" class="filter-btn px-2 py-1 rounded bg-slate-800/50 border border-slate-700 hover:bg-slate-700 text-purple-400" data-filter="Codex">Codex</button>
      <button onclick="setFilter('Claude')" class="filter-btn px-2 py-1 rounded bg-slate-800/50 border border-slate-700 hover:bg-slate-700 text-emerald-400" data-filter="Claude">Claude</button>
      <button onclick="setFilter('Antigravity')" class="filter-btn px-2 py-1 rounded bg-slate-800/50 border border-slate-700 hover:bg-slate-700 text-sky-400" data-filter="Antigravity">Antigravity</button>
    </div>
    <div class="hidden sm:flex items-center gap-2">
      <label class="flex items-center gap-1.5 cursor-pointer text-slate-400 text-[11px]" title="When checked, automatically follows new incoming messages. When unchecked, reading is never interrupted.">
        <input type="checkbox" id="auto-scroll" class="rounded bg-slate-800 border-slate-700 text-cyan-500 focus:ring-0">
        <span>Auto-follow live</span>
      </label>
    </div>
  </div>

  <!-- Main Content Layout -->
  <div class="flex-1 flex overflow-hidden relative">

    <!-- Left Message Feed (Mobile View: 'feed' / Desktop View: Left Pane) -->
    <div id="feed-container" class="mobile-view active w-full lg:w-2/5 flex flex-col border-r border-slate-800 overflow-hidden bg-slate-950/40">
      <div id="feed" class="flex-1 overflow-y-auto custom-scroll p-3 sm:p-4 space-y-2.5">
        <!-- Message cards rendered via JS -->
      </div>
    </div>

    <!-- Right Detailed View (Mobile View: 'detail' / Desktop View: Right Pane) -->
    <div id="detail-container" class="mobile-view hidden lg:flex w-full lg:w-3/5 flex-col overflow-hidden bg-slate-900/60">
      <!-- Active Message Header -->
      <div id="detail-header" class="p-3 sm:p-4 border-b border-slate-800 bg-slate-900/95 shrink-0 shadow-sm">
        <!-- Touch & Mobile Navigation Row (all touch targets >= 44px) -->
        <div class="flex items-center justify-between gap-2 mb-2 sm:mb-3 pb-2 border-b border-slate-800/80">
          <button onclick="switchMobileTab('feed')" 
                  style="min-height: 44px;"
                  class="lg:hidden min-h-[44px] px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-cyan-400 font-bold text-xs flex items-center justify-center gap-1.5 border border-slate-700 active:scale-95 transition cursor-pointer touch-manipulation">
            <span>← Back to Feed</span>
          </button>
          
          <div class="flex items-center gap-1.5 ml-auto">
            <button onclick="navigateMessageRelative(1)" id="btn-nav-newer" title="View newer message"
                    style="min-height: 44px;"
                    class="min-h-[44px] px-3.5 py-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-cyan-400 text-xs font-semibold border border-slate-700 flex items-center justify-center gap-1 cursor-pointer transition touch-manipulation disabled:opacity-40 disabled:cursor-not-allowed">
              <span>▲ Newer</span>
            </button>
            <button onclick="navigateMessageRelative(-1)" id="btn-nav-older" title="View older message"
                    style="min-height: 44px;"
                    class="min-h-[44px] px-3.5 py-2 rounded bg-slate-800 hover:bg-slate-700 text-slate-300 hover:text-cyan-400 text-xs font-semibold border border-slate-700 flex items-center justify-center gap-1 cursor-pointer transition touch-manipulation disabled:opacity-40 disabled:cursor-not-allowed">
              <span>▼ Older</span>
            </button>
            <button onclick="replyToCurrentMessage()" title="Compose reply to sender"
                    style="min-height: 44px;"
                    class="ml-1 min-h-[44px] px-3.5 py-2 rounded bg-emerald-700/80 hover:bg-emerald-600 text-emerald-100 text-xs font-semibold border border-emerald-600/80 flex items-center justify-center gap-1 cursor-pointer transition active:scale-95 touch-manipulation">
              <span>✍️ Reply</span>
            </button>
          </div>
        </div>

        <!-- Metadata Row -->
        <div class="flex items-center justify-between flex-wrap gap-2">
          <div class="flex items-center gap-2 sm:gap-3 flex-wrap">
            <span id="detail-id" class="text-sm sm:text-base font-bold text-cyan-400 font-mono px-2 py-0.5 bg-cyan-950/80 rounded border border-cyan-800">[---]</span>
            <span id="detail-sender" class="font-semibold text-slate-200 text-xs sm:text-sm">Select a message</span>
            <span class="text-slate-500">➔</span>
            <span id="detail-recipient" class="text-slate-300 text-xs sm:text-sm font-medium"></span>
          </div>
          <div id="detail-time-container">
            <span id="detail-time" class="text-[11px] sm:text-xs font-mono"></span>
          </div>
        </div>
      </div>

      <!-- Action Points Banner in Detail View -->
      <div id="detail-actions" class="p-3 sm:p-4 border-b border-slate-800 bg-slate-950/70 shrink-0 space-y-2 hidden">
        <!-- Rendered action tags -->
      </div>

      <!-- Message Raw Body Viewer -->
      <div class="flex-1 overflow-y-auto custom-scroll p-4 sm:p-6 font-mono text-xs sm:text-sm text-slate-200 whitespace-pre-wrap leading-relaxed select-text" 
           id="detail-body" 
           style="word-break: break-word; overflow-wrap: anywhere; line-height: 1.65; max-width: 100%;">
        Select a message from the list to view its complete content and parsed action items.
      </div>
    </div>

    <!-- AI Tasks View for Mobile (Mobile View: 'tasks') -->
    <div id="tasks-mobile-container" class="mobile-view hidden w-full flex-col overflow-y-auto custom-scroll p-3 bg-slate-950 space-y-3">
      <div class="flex items-center justify-between pb-2 border-b border-slate-800">
        <span class="text-xs font-bold text-cyan-400 uppercase tracking-wider">Active AI Agent Board</span>
        <span class="text-[11px] text-slate-400">Live 1000ms</span>
      </div>
      <div id="tasks-mobile-cards" class="space-y-3">
        <!-- Populated via JS -->
      </div>
    </div>

  </div>

  <!-- COMPOSE MESSAGE MODAL (Responsive on Mobile & Desktop) -->
  <div id="compose-modal" class="fixed inset-0 z-50 bg-black/70 backdrop-blur-sm flex items-center justify-center p-2 sm:p-4 hidden">
    <div class="bg-slate-900 border border-slate-700 rounded-xl shadow-2xl w-full max-w-2xl max-h-[95vh] flex flex-col overflow-hidden animate-in fade-in zoom-in-95 duration-150">
      
      <!-- Modal Header -->
      <div class="bg-slate-800/80 px-4 py-3 border-b border-slate-700 flex items-center justify-between shrink-0">
        <div class="flex items-center gap-2">
          <span class="text-base sm:text-lg">✍️</span>
          <h2 class="text-sm sm:text-base font-bold text-slate-100">Send Message to Team Mailbox</h2>
        </div>
        <button onclick="closeComposeModal()" class="text-slate-400 hover:text-white text-lg font-bold p-1 cursor-pointer">&times;</button>
      </div>

      <!-- Modal Body / Form -->
      <form id="compose-form" onsubmit="handleSendMessage(event)" class="flex-1 overflow-y-auto custom-scroll p-4 space-y-3 sm:space-y-4">
        
        <!-- Sender & Recipient Pickers -->
        <div class="grid grid-cols-1 sm:grid-cols-2 gap-3">
          <div>
            <label class="block text-xs font-semibold text-slate-400 mb-1">Your Identity (Sender)</label>
            <select id="compose-sender" onchange="updateIdPreview()"
                    class="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 text-sm focus:outline-none focus:border-cyan-500">
              <option value="Owner" selected>Owner (Project Lead / User)</option>
              <option value="Codex">Codex (Technical Lead)</option>
              <option value="Claude">Claude (Implementer)</option>
              <option value="Antigravity">Antigravity (Visuals / Committer)</option>
            </select>
          </div>
          <div>
            <label class="block text-xs font-semibold text-slate-400 mb-1">Send To (Recipient)</label>
            <select id="compose-recipient"
                    class="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 text-sm focus:outline-none focus:border-cyan-500">
              <option value="All" selected>All (Team Broadcast)</option>
              <option value="Codex (lead)">Codex (lead)</option>
              <option value="Claude">Claude</option>
              <option value="Antigravity">Antigravity</option>
              <option value="Owner">Owner</option>
            </select>
          </div>
        </div>

        <!-- Task / Subject Line -->
        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1">
            Task Directive / Subject <span class="text-slate-500 font-normal">(Optional quick summary)</span>
          </label>
          <input type="text" id="compose-task" placeholder="e.g. Review AG05 REV2 and resume runtime testing..."
                 class="w-full bg-slate-950 border border-slate-700 rounded-lg px-3 py-2 text-slate-200 text-sm focus:outline-none focus:border-cyan-500">
        </div>

        <!-- Template Snippet Buttons -->
        <div>
          <div class="flex items-center justify-between mb-1">
            <label class="block text-xs font-semibold text-slate-400">Quick Template Inserts</label>
            <span class="text-[10px] text-cyan-400 font-mono" id="compose-id-preview">Will post as: [O-1]</span>
          </div>
          <div class="flex flex-wrap gap-1.5">
            <button type="button" onclick="insertSnippet('TASK: ')" class="text-[11px] bg-slate-800 hover:bg-slate-700 text-cyan-300 px-2 py-1 rounded border border-slate-700 cursor-pointer">+ TASK</button>
            <button type="button" onclick="insertSnippet('STATUS: ')" class="text-[11px] bg-slate-800 hover:bg-slate-700 text-emerald-300 px-2 py-1 rounded border border-slate-700 cursor-pointer">+ STATUS</button>
            <button type="button" onclick="insertSnippet('FINDINGS: ')" class="text-[11px] bg-slate-800 hover:bg-slate-700 text-amber-300 px-2 py-1 rounded border border-slate-700 cursor-pointer">+ FINDINGS</button>
            <button type="button" onclick="insertSnippet('DECISION NEEDED: ')" class="text-[11px] bg-slate-800 hover:bg-slate-700 text-red-300 px-2 py-1 rounded border border-slate-700 cursor-pointer">+ DECISION</button>
            <button type="button" onclick="insertSnippet('CODEX: ')" class="text-[11px] bg-purple-950 hover:bg-purple-900 text-purple-300 px-2 py-1 rounded border border-purple-800 cursor-pointer">+ CODEX:</button>
            <button type="button" onclick="insertSnippet('ANTIGRAVITY: ')" class="text-[11px] bg-sky-950 hover:bg-sky-900 text-sky-300 px-2 py-1 rounded border border-sky-800 cursor-pointer">+ AG:</button>
            <button type="button" onclick="insertSnippet('CLAUDE: ')" class="text-[11px] bg-emerald-950 hover:bg-emerald-900 text-emerald-300 px-2 py-1 rounded border border-emerald-800 cursor-pointer">+ CLAUDE:</button>
          </div>
        </div>

        <!-- Full Message Body -->
        <div>
          <label class="block text-xs font-semibold text-slate-400 mb-1">Message Body (Markdown supported)</label>
          <textarea id="compose-body" rows="7" required
                    placeholder="Type your message here. Both Codex and Antigravity will automatically read and act on it from TEAM_MAILBOX.md on their next watch cycle..."
                    class="w-full bg-slate-950 border border-slate-700 rounded-lg p-3 font-mono text-xs sm:text-sm text-slate-200 focus:outline-none focus:border-cyan-500 leading-relaxed"></textarea>
        </div>

        <!-- Notification / Error Box -->
        <div id="compose-status" class="text-xs p-2.5 rounded-lg hidden"></div>

        <!-- Submit Controls -->
        <div class="pt-2 flex items-center justify-end gap-2 border-t border-slate-800 shrink-0">
          <button type="button" onclick="closeComposeModal()"
                  class="px-4 py-2 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs sm:text-sm font-semibold transition cursor-pointer">
            Cancel
          </button>
          <button type="submit" id="compose-submit-btn"
                  class="px-5 py-2 rounded-lg bg-gradient-to-r from-emerald-600 to-teal-600 hover:from-emerald-500 hover:to-teal-500 text-white text-xs sm:text-sm font-bold shadow-lg transition cursor-pointer flex items-center gap-1.5 active:scale-95">
            <span>🚀 Send to Mailbox</span>
          </button>
        </div>
      </form>
    </div>
  </div>

  <!-- Toast Notification Container -->
  <div id="toast" class="fixed bottom-4 right-4 z-50 bg-slate-800 border border-slate-600 text-slate-100 px-4 py-2.5 rounded-xl shadow-2xl text-xs sm:text-sm flex items-center gap-2 transform translate-y-20 opacity-0 transition-all duration-300">
    <span id="toast-icon">✅</span>
    <span id="toast-msg">Notification</span>
  </div>

  <script>
    let currentData = null;
    let selectedMsgId = null;
    let activeFilter = 'ALL';
    let searchQuery = '';
    let currentMobileTab = 'feed';
    let nextOwnerId = 'O-1';

    function isSinglePane() {
      return window.innerWidth < 1024;
    }

    // --------------------------------------------------------------------------
    // Mobile Navigation & View Switching
    // --------------------------------------------------------------------------
    function switchMobileTab(tab) {
      currentMobileTab = tab;
      const feedCont = document.getElementById('feed-container');
      const detailCont = document.getElementById('detail-container');
      const tasksCont = document.getElementById('tasks-mobile-container');

      if (tab === 'detail') {
        document.body.classList.add('mobile-detail-mode');
      } else {
        document.body.classList.remove('mobile-detail-mode');
      }

      document.querySelectorAll('.mobile-tab-btn').forEach(b => {
        b.classList.remove('text-cyan-400', 'border-cyan-400', 'font-bold');
        b.classList.add('text-slate-400', 'border-transparent', 'font-medium');
      });

      const activeBtn = document.getElementById('tab-btn-' + tab);
      if (activeBtn) {
        activeBtn.classList.remove('text-slate-400', 'border-transparent', 'font-medium');
        activeBtn.classList.add('text-cyan-400', 'border-cyan-400', 'font-bold');
      }

      feedCont.classList.remove('active');
      detailCont.classList.remove('active');
      tasksCont.classList.remove('active');

      if (tab === 'feed') {
        feedCont.classList.add('active');
      } else if (tab === 'detail') {
        detailCont.classList.add('active');
      } else if (tab === 'tasks') {
        tasksCont.classList.add('active');
      }
    }

    // --------------------------------------------------------------------------
    // Compose Message Functions
    // --------------------------------------------------------------------------
    function openComposeModal() {
      const modal = document.getElementById('compose-modal');
      modal.classList.remove('hidden');
      updateIdPreview();
      setTimeout(() => document.getElementById('compose-body').focus(), 100);
    }

    function closeComposeModal() {
      document.getElementById('compose-modal').classList.add('hidden');
      document.getElementById('compose-status').classList.add('hidden');
    }

    function insertSnippet(text) {
      const ta = document.getElementById('compose-body');
      const start = ta.selectionStart;
      const end = ta.selectionEnd;
      const val = ta.value;
      ta.value = val.substring(0, start) + text + val.substring(end);
      ta.focus();
      ta.selectionStart = ta.selectionEnd = start + text.length;
    }

    function updateIdPreview() {
      const sender = document.getElementById('compose-sender').value;
      let p = 'O';
      if (sender === 'Codex') p = 'X';
      else if (sender === 'Claude') p = 'C';
      else if (sender === 'Antigravity') p = 'A';
      
      const idPreview = document.getElementById('compose-id-preview');
      if (p === 'O') {
        idPreview.textContent = `Will post as: [${nextOwnerId}]`;
      } else {
        idPreview.textContent = `Posting as ${sender} [${p}-*]`;
      }
    }

    async function handleSendMessage(e) {
      e.preventDefault();
      const sender = document.getElementById('compose-sender').value;
      const recipient = document.getElementById('compose-recipient').value;
      const task = document.getElementById('compose-task').value;
      const body = document.getElementById('compose-body').value;
      const btn = document.getElementById('compose-submit-btn');
      const statusBox = document.getElementById('compose-status');

      btn.disabled = true;
      btn.innerHTML = '<span>⏳ Appending...</span>';

      try {
        const res = await fetch('/api/send', {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ sender, recipient, task, body })
        });
        const result = await res.json();

        if (res.ok && result.success) {
          showToast(`✅ Sent! Message [${result.message_id}] posted to TEAM_MAILBOX.md`);
          closeComposeModal();
          document.getElementById('compose-form').reset();
          
          // Force immediate poll and select new message
          await pollMailbox();
          if (result.message_id) {
            selectMessageById(result.message_id, true);
            if (isSinglePane()) {
              switchMobileTab('detail');
            }
          }
        } else {
          statusBox.className = 'text-xs p-2.5 rounded-lg bg-red-950 text-red-200 border border-red-800';
          statusBox.textContent = `Error: ${result.error || 'Failed to append message'}`;
          statusBox.classList.remove('hidden');
        }
      } catch (err) {
        statusBox.className = 'text-xs p-2.5 rounded-lg bg-red-950 text-red-200 border border-red-800';
        statusBox.textContent = `Network error: ${err.message}`;
        statusBox.classList.remove('hidden');
      } finally {
        btn.disabled = false;
        btn.innerHTML = '<span>🚀 Send to Mailbox</span>';
      }
    }

    function showToast(msg, icon='✅') {
      const toast = document.getElementById('toast');
      document.getElementById('toast-msg').textContent = msg;
      document.getElementById('toast-icon').textContent = icon;
      toast.classList.remove('translate-y-20', 'opacity-0');
      toast.classList.add('translate-y-0', 'opacity-100');
      setTimeout(() => {
        toast.classList.remove('translate-y-0', 'opacity-100');
        toast.classList.add('translate-y-20', 'opacity-0');
      }, 3500);
    }

    function copyMobileUrl() {
      if (currentData && currentData.lan_url) {
        navigator.clipboard.writeText(currentData.lan_url).then(() => {
          showToast(`Copied mobile URL: ${currentData.lan_url}`);
        });
      }
    }

    // --------------------------------------------------------------------------
    // Task Board & Layout Toggle
    // --------------------------------------------------------------------------
    function toggleTaskBoard() {
      const board = document.getElementById('ai-task-board');
      const bar = document.getElementById('ai-task-compact-bar');
      const arrow = document.getElementById('toggle-arrow');
      if (board.classList.contains('hidden')) {
        board.classList.remove('hidden');
        bar.classList.add('hidden');
        arrow.textContent = '▲';
        localStorage.setItem('mailbox_taskboard_collapsed', 'false');
      } else {
        board.classList.add('hidden');
        bar.classList.remove('hidden');
        arrow.textContent = '▼';
        localStorage.setItem('mailbox_taskboard_collapsed', 'true');
      }
    }

    function setFilter(f) {
      activeFilter = f;
      document.querySelectorAll('.filter-btn').forEach(b => {
        if (b.getAttribute('data-filter') === f) {
          b.className = 'filter-btn px-2 py-1 rounded bg-slate-700 text-white font-bold border border-slate-600';
        } else {
          b.className = 'filter-btn px-2 py-1 rounded bg-slate-800/50 border border-slate-700 hover:bg-slate-700 text-slate-300 font-medium';
        }
      });
      renderFeed();
    }

    document.getElementById('search-box').addEventListener('input', e => {
      searchQuery = e.target.value.toLowerCase();
      renderFeed();
    });

    function escapeHtml(text) {
      const div = document.createElement('div');
      div.textContent = text || '';
      return div.innerHTML;
    }

    function renderTaskCards(aiTasks) {
      if (!aiTasks) return;
      const containerDesktop = document.getElementById('ai-task-cards');
      const containerMobile = document.getElementById('tasks-mobile-cards');
      let html = '';

      const borderColors = {
        'Claude': 'border-emerald-800/80 bg-emerald-950/20',
        'Antigravity': 'border-sky-800/80 bg-sky-950/20',
        'Owner': 'border-amber-800/80 bg-amber-950/20',
        'Codex': 'border-purple-800/80 bg-purple-950/20'
      };

      const titleColors = {
        'Claude': 'text-emerald-300',
        'Antigravity': 'text-sky-300',
        'Owner': 'text-amber-300',
        'Codex': 'text-purple-300'
      };

      for (const [key, prof] of Object.entries(aiTasks)) {
        const borderCls = borderColors[key] || 'border-slate-800 bg-slate-900/40';
        const titleCls = titleColors[key] || 'text-slate-200';
        const srcBadge = prof.source_msg_id ? `<span class="font-mono text-[10px] text-cyan-400 bg-cyan-950/70 border border-cyan-800/80 px-1.5 py-0.5 rounded hover:underline cursor-pointer" onclick="jumpToMessage('${prof.source_msg_id}')">[${prof.source_msg_id}]</span>` : '';

        // Status pill indicator
        let statusBadge = '';
        if (prof.activity_state === 'active') {
          statusBadge = `<span class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[10px] font-semibold bg-emerald-950/90 text-emerald-400 border border-emerald-700/80"><span class="w-1.5 h-1.5 rounded-full bg-emerald-400 animate-pulse"></span>ACTIVE (${prof.last_seen})</span>`;
        } else if (prof.activity_state === 'waiting') {
          statusBadge = `<span class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[10px] font-semibold bg-amber-950/90 text-amber-400 border border-amber-700/80"><span class="w-1.5 h-1.5 rounded-full bg-amber-400"></span>WAITING (${prof.last_seen})</span>`;
        } else if (prof.activity_state === 'standby') {
          statusBadge = `<span class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[10px] font-semibold bg-sky-950/90 text-sky-400 border border-sky-800/80">STANDBY (${prof.last_seen})</span>`;
        } else {
          statusBadge = `<span class="inline-flex items-center gap-1 px-1.5 py-0.5 rounded-full text-[10px] font-medium bg-slate-900 text-slate-500 border border-slate-800">INACTIVE</span>`;
        }

        let taskListHtml = '';
        if (prof.tasks && prof.tasks.length > 0) {
          taskListHtml = prof.tasks.map(t => {
            const taskSrc = t.source ? `<span class="font-mono text-[9px] text-slate-500 hover:text-cyan-400 cursor-pointer" onclick="jumpToMessage('${t.source}')">[${t.source}]</span>` : '';
            return `
              <li class="flex items-start gap-1.5 text-[11px] leading-tight text-slate-300 bg-slate-900/40 p-1.5 rounded border border-slate-800/60">
                <span class="shrink-0 mt-0.5 text-xs">${t.status_icon}</span>
                <div class="flex-1 min-w-0">
                  <div class="flex items-center justify-between gap-1">
                    <span class="font-medium text-slate-200 truncate">${escapeHtml(t.title)}</span>
                    ${taskSrc}
                  </div>
                  <p class="text-[10px] text-slate-400 leading-snug line-clamp-2 mt-0.5">${escapeHtml(t.detail)}</p>
                </div>
              </li>
            `;
          }).join('');
        } else {
          taskListHtml = '<li class="text-[11px] text-slate-500 italic p-1">No assigned tasks logged</li>';
        }

        const nextActionBlock = prof.next_action ? `
          <div class="text-[10px] text-slate-400 border-t border-slate-800/80 pt-1 mt-1 truncate">
            <span class="text-cyan-400 font-mono">Next:</span> ${escapeHtml(prof.next_action)}
          </div>
        ` : '';

        html += `
          <div class="border rounded-lg p-2.5 flex flex-col justify-between ${borderCls} shadow-sm">
            <div>
              <div class="flex items-center justify-between mb-1.5">
                <div class="flex items-center gap-1.5">
                  <span class="text-sm">${prof.avatar}</span>
                  <div>
                    <span class="font-bold text-xs ${titleCls}">${escapeHtml(prof.name)}</span>
                    <p class="text-[9px] text-slate-400 font-medium">${escapeHtml(prof.role)}</p>
                  </div>
                </div>
                <div class="flex flex-col items-end gap-1">
                  ${statusBadge}
                  ${srcBadge}
                </div>
              </div>
              
              <div class="bg-slate-900/90 border border-slate-800/90 rounded px-2 py-1.5 mb-2">
                <div class="flex items-center justify-between text-[10px] text-slate-500 uppercase font-mono mb-0.5">
                  <span>Current Task:</span>
                  <span class="text-slate-400 lowercase font-sans">${prof.last_seen}</span>
                </div>
                <span class="text-xs font-semibold text-slate-200 leading-tight block truncate">${escapeHtml(prof.active_directive || 'Idle')}</span>
                ${nextActionBlock}
              </div>

              <div class="text-[10px] text-slate-400 font-semibold uppercase font-mono px-0.5 mb-1 flex items-center justify-between">
                <span>Recent History</span>
                <span class="text-[9px] lowercase font-sans text-slate-500">${prof.tasks.length} tasks</span>
              </div>
              <ul class="space-y-1 max-h-36 overflow-y-auto custom-scroll pr-1">
                ${taskListHtml}
              </ul>
            </div>
          </div>
        `;
      }

      if (containerDesktop) containerDesktop.innerHTML = html;
      if (containerMobile) containerMobile.innerHTML = html;

      // Update compact bar summaries
      if (aiTasks.Claude) {
        document.getElementById('compact-claude').textContent = aiTasks.Claude.active_directive || 'Reviewing';
        document.getElementById('compact-claude-src').textContent = aiTasks.Claude.source_msg_id ? `[${aiTasks.Claude.source_msg_id}]` : '';
      }
      if (aiTasks.Antigravity) {
        document.getElementById('compact-ag').textContent = aiTasks.Antigravity.active_directive || 'Operating';
        document.getElementById('compact-ag-src').textContent = aiTasks.Antigravity.source_msg_id ? `[${aiTasks.Antigravity.source_msg_id}]` : '';
      }
      if (aiTasks.Owner) {
        document.getElementById('compact-owner').textContent = aiTasks.Owner.active_directive || 'Directives Ready';
        document.getElementById('compact-owner-src').textContent = aiTasks.Owner.source_msg_id ? `[${aiTasks.Owner.source_msg_id}]` : '';
      }
      if (aiTasks.Codex) {
        document.getElementById('compact-codex').textContent = aiTasks.Codex.active_directive || 'Retired';
        document.getElementById('compact-codex-src').textContent = aiTasks.Codex.source_msg_id ? `[${aiTasks.Codex.source_msg_id}]` : '';
      }
    }

    function renderFeed() {
      if (!currentData || !currentData.messages) return;
      const feed = document.getElementById('feed');
      const messages = currentData.messages;
      feed.innerHTML = '';

      let filtered = messages.filter((m, idx) => {
        m._idx = idx;
        if (activeFilter === 'ACTIONS' && !m.has_actions) return false;
        if (['Claude', 'Codex', 'Antigravity', 'Owner'].includes(activeFilter)) {
          if (m.sender_norm !== activeFilter && m.recipient_norm !== activeFilter) return false;
        }
        if (searchQuery) {
          const hay = (m.id + ' ' + m.sender + ' ' + m.recipient + ' ' + m.body).toLowerCase();
          if (!hay.includes(searchQuery)) return false;
        }
        return true;
      });

      if (filtered.length === 0) {
        feed.innerHTML = '<div class="text-center text-slate-500 text-xs py-8">No messages match filter.</div>';
        return;
      }

      // Reverse append order: render latest appended messages at the top!
      const displayList = filtered.slice().reverse();

      displayList.forEach(m => {
        const isSelected = (selectedMsgId === m.id);
        const card = document.createElement('div');
        card.id = `msg-card-${m.id}`;
        card.className = `p-3 rounded-xl border transition cursor-pointer ${
          isSelected
            ? 'bg-cyan-950/40 border-cyan-500 shadow-lg'
            : 'bg-slate-900 border-slate-800 hover:border-slate-700 hover:bg-slate-800/60'
        }`;
        card.onclick = () => {
          selectMessageById(m.id, true);
          if (isSinglePane()) {
            switchMobileTab('detail');
          }
        };

        const tagClass = m.sender_norm === 'Claude' ? 'tag-claude'
                       : m.sender_norm === 'Codex' ? 'tag-codex'
                       : m.sender_norm === 'Antigravity' ? 'tag-ag'
                       : m.sender_norm === 'Owner' ? 'tag-owner'
                       : 'tag-general';

        const actionBadge = m.has_actions ? '<span class="text-amber-400 font-bold ml-1 text-xs" title="Has Action Items">⚡</span>' : '';
        const newestBadge = (m.index === messages.length) 
          ? '<span class="px-1.5 py-0.2 rounded text-[9px] font-bold bg-cyan-950 text-cyan-300 border border-cyan-700 shrink-0">✨ NEWEST</span>' 
          : '';

        const tsClass = m.time_recorded ? 'text-cyan-300 font-medium' : 'text-slate-400';

        card.innerHTML = `
          <div class="flex items-center justify-between mb-1.5 gap-1">
            <div class="flex items-center gap-1.5 min-w-0">
              <span class="font-mono text-xs font-bold text-slate-100 shrink-0">[${m.id}]</span>
              ${newestBadge}
              ${actionBadge}
            </div>
            <span class="text-[10px] font-mono shrink-0 ${tsClass}">${escapeHtml(m.timestamp)}</span>
          </div>
          <div class="flex items-center gap-1.5 text-xs mb-1.5">
            <span class="px-1.5 py-0.5 rounded text-[10px] font-semibold ${tagClass}">${escapeHtml(m.sender)}</span>
            <span class="text-slate-500 text-[10px]">➔</span>
            <span class="text-slate-300 text-[11px] truncate">${escapeHtml(m.recipient)}</span>
          </div>
          <p class="text-xs text-slate-400 line-clamp-2 leading-relaxed font-mono select-none">${escapeHtml(m.body.substring(0, 160))}</p>
        `;
        feed.appendChild(card);
      });
    }

    function selectMessageById(id, scrollToCard = false) {
      if (!currentData || !currentData.messages) return;
      const m = currentData.messages.find(x => x.id === id);
      if (!m) return;
      selectedMsgId = m.id;

      document.getElementById('detail-id').textContent = `[${m.id}]`;
      document.getElementById('detail-sender').textContent = m.sender;
      document.getElementById('detail-recipient').textContent = m.recipient;
      
      const timeCont = document.getElementById('detail-time');
      if (m.time_recorded) {
        timeCont.innerHTML = `<span class="px-2 py-0.5 rounded text-[11px] sm:text-xs font-mono font-medium bg-cyan-950 text-cyan-300 border border-cyan-800/80 flex items-center gap-1">🕒 ${escapeHtml(m.timestamp)}</span>`;
      } else {
        timeCont.innerHTML = `<span class="px-2 py-0.5 rounded text-[11px] sm:text-xs font-mono text-slate-400 bg-slate-800/90 border border-slate-700 flex items-center gap-1" title="Time was not recorded in header">📅 ${escapeHtml(m.timestamp)}</span>`;
      }

      document.getElementById('detail-body').textContent = m.body;

      // Render Action Points Banner
      const actionBox = document.getElementById('detail-actions');
      if (m.has_actions) {
        actionBox.classList.remove('hidden');
        let html = '<div class="text-[11px] font-bold text-amber-300 uppercase tracking-wider mb-1 flex items-center gap-1"><span>⚡ Action Points</span></div><div class="flex flex-wrap gap-1.5">';
        for (const [agent, list] of Object.entries(m.action_points)) {
          list.forEach(act => {
            const cls = agent === 'Claude' ? 'tag-claude'
                      : agent === 'Codex' ? 'tag-codex'
                      : agent === 'Antigravity' ? 'tag-ag'
                      : agent === 'Owner' ? 'tag-owner'
                      : 'tag-general';
            html += `<span class="px-2 py-0.5 rounded text-[11px] ${cls}"><strong>${agent}:</strong> ${escapeHtml(act)}</span>`;
          });
        }
        html += '</div>';
        actionBox.innerHTML = html;
      } else {
        actionBox.classList.add('hidden');
      }

      // Update Older / Newer nav buttons
      const mIndex = currentData.messages.findIndex(x => x.id === id);
      const btnNewer = document.getElementById('btn-nav-newer');
      const btnOlder = document.getElementById('btn-nav-older');
      if (btnNewer) btnNewer.disabled = (mIndex >= currentData.messages.length - 1);
      if (btnOlder) btnOlder.disabled = (mIndex <= 0);

      renderFeed();

      // Scroll card into view if requested
      if (scrollToCard) {
        const activeCard = document.getElementById(`msg-card-${m.id}`);
        if (activeCard) {
          activeCard.scrollIntoView({ behavior: 'smooth', block: 'nearest' });
        }
      }
    }

    function navigateMessageRelative(delta) {
      if (!currentData || !currentData.messages || !selectedMsgId) return;
      const idx = currentData.messages.findIndex(x => x.id === selectedMsgId);
      if (idx === -1) return;
      const targetIdx = idx + delta;
      if (targetIdx >= 0 && targetIdx < currentData.messages.length) {
        selectMessageById(currentData.messages[targetIdx].id, true);
      }
    }

    function replyToCurrentMessage() {
      if (!currentData || !currentData.messages || !selectedMsgId) {
        openComposeModal();
        return;
      }
      const m = currentData.messages.find(x => x.id === selectedMsgId);
      openComposeModal();
      if (m) {
        const selRecipient = document.getElementById('compose-recipient');
        const cleanSender = m.sender_norm || m.sender;
        for (let opt of selRecipient.options) {
          if (opt.value.toLowerCase().includes(cleanSender.toLowerCase())) {
            selRecipient.value = opt.value;
            break;
          }
        }
        document.getElementById('compose-task').value = `Re: [${m.id}]`;
      }
    }

    function jumpToMessage(msgId) {
      if (!currentData || !currentData.messages) return;
      const cleanId = msgId.replace(/^\[|\]$/g, '').trim();
      const m = currentData.messages.find(x => x.id === cleanId);
      if (m) {
        selectMessageById(m.id, true);
        if (isSinglePane()) {
          switchMobileTab('detail');
        }
      } else {
        showToast(`Message [${cleanId}] not found in feed`, 'ℹ️');
      }
    }

    async function pollMailbox() {
      try {
        const res = await fetch('/api/mailbox');
        const data = await res.json();
        const prevCount = currentData ? currentData.count : 0;
        currentData = data;

        if (data.next_owner_id) {
          nextOwnerId = data.next_owner_id;
          updateIdPreview();
        }

        if (data.lan_ip) {
          document.getElementById('lan-ip-text').textContent = `${data.lan_ip}:8080`;
        }

        document.getElementById('msg-count').textContent = data.count;

        // Render dynamic AI Task Cards
        if (data.ai_tasks) {
          renderTaskCards(data.ai_tasks);
        }

        const autoFollow = document.getElementById('auto-scroll').checked;

        // Handle selection stability
        if (data.count > 0) {
          if (selectedMsgId === null) {
            // First load: select latest appended message
            selectMessageById(data.latest.id, false);
          } else {
            // Stable selection! Re-verify message exists
            const exists = data.messages.some(m => m.id === selectedMsgId);
            if (data.count > prevCount && prevCount > 0) {
              if (autoFollow) {
                // User explicitly enabled Auto-follow: track live messages
                selectMessageById(data.latest.id, false);
                showToast(`Auto-followed new message [${data.latest.id}] from ${data.latest.sender}`, '🚀');
              } else {
                // Reading mode: keep stable selection without jumping
                showToast(`New message [${data.latest.id}] from ${data.latest.sender} arrived at top of feed`, '📬');
              }
            } else if (!exists) {
              selectMessageById(data.latest.id, false);
            }
          }
        }

        renderFeed();
      } catch (err) {
        console.error('Polling error:', err);
      }
    }

    // Window resize listener: reset mobile detail mode if expanded to desktop
    window.addEventListener('resize', () => {
      if (!isSinglePane()) {
        document.body.classList.remove('mobile-detail-mode');
      }
    });

    // Initialize saved collapse state
    if (localStorage.getItem('mailbox_taskboard_collapsed') === 'true') {
      const board = document.getElementById('ai-task-board');
      const bar = document.getElementById('ai-task-compact-bar');
      const arrow = document.getElementById('toggle-arrow');
      if (board && bar && arrow) {
        board.classList.add('hidden');
        bar.classList.remove('hidden');
        arrow.textContent = '▼';
      }
    }

    setInterval(pollMailbox, 1000);
    pollMailbox();
  </script>
</body>
</html>
"""


class MailboxHTTPHandler(BaseHTTPRequestHandler):
    """Serves the responsive dashboard, JSON API, and Compose endpoint."""

    def log_message(self, format, *args):
        # Silence access logs to keep terminal output clean
        pass

    def do_OPTIONS(self):
        self.send_response(200)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/api/mailbox":
            data = MailboxParser.parse_file()
            lan_ip = get_lan_ip()
            data["lan_ip"] = lan_ip
            data["lan_url"] = f"http://{lan_ip}:{DEFAULT_PORT}"
            data["next_owner_id"] = MailboxWriter.get_next_id("O")

            self.send_response(200)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()
            self.wfile.write(json.dumps(data).encode("utf-8"))
        elif url.path in ["/", "/index.html"]:
            self.send_response(200)
            self.send_header("Content-Type", "text/html; charset=utf-8")
            self.end_headers()
            self.wfile.write(HTML_TEMPLATE.encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()

    def do_POST(self):
        url = urlparse(self.path)
        if url.path == "/api/send":
            try:
                content_length = int(self.headers.get("Content-Length", 0))
                post_data = self.rfile.read(content_length).decode("utf-8")
                payload = json.loads(post_data)

                sender = payload.get("sender", "Owner").strip() or "Owner"
                recipient = payload.get("recipient", "All").strip() or "All"
                body = payload.get("body", "").strip()
                task = payload.get("task", "").strip()
                prefix = payload.get("prefix", "O").strip().upper() or "O"

                if not body:
                    self.send_response(400)
                    self.send_header("Content-Type", "application/json; charset=utf-8")
                    self.send_header("Access-Control-Allow-Origin", "*")
                    self.end_headers()
                    self.wfile.write(json.dumps({"success": False, "error": "Message body cannot be empty"}).encode("utf-8"))
                    return

                result = MailboxWriter.append_message(
                    sender=sender,
                    recipient=recipient,
                    body=body,
                    task=task,
                    prefix=prefix
                )

                self.send_response(200)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps(result).encode("utf-8"))

            except Exception as e:
                self.send_response(500)
                self.send_header("Content-Type", "application/json; charset=utf-8")
                self.send_header("Access-Control-Allow-Origin", "*")
                self.end_headers()
                self.wfile.write(json.dumps({"success": False, "error": str(e)}).encode("utf-8"))
        else:
            self.send_response(404)
            self.end_headers()


def start_web_server(port=DEFAULT_PORT):
    # Bind to 0.0.0.0 so phone/tablet devices on the same Wi-Fi can connect
    server = HTTPServer(("0.0.0.0", port), MailboxHTTPHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server


# ==============================================================================
# 4. TKINTER DESKTOP GUI
# ==============================================================================

def run_tkinter_gui(port=DEFAULT_PORT):
    import tkinter as tk
    from tkinter import ttk, messagebox
    from tkinter.scrolledtext import ScrolledText

    class MailboxTkinterApp:
        def __init__(self, root):
            self.root = root
            self.root.title("One Boss Fight — Team Mailbox Monitor")
            self.root.geometry("1280x820")
            self.root.minsize(960, 600)

            # Colors
            self.bg_dark = "#0f172a"
            self.bg_card = "#1e293b"
            self.bg_panel = "#090d16"
            self.fg_text = "#f8fafc"
            self.fg_muted = "#94a3b8"
            self.accent_cyan = "#38bdf8"
            self.accent_amber = "#f59e0b"
            self.accent_green = "#10b981"
            self.accent_purple = "#c084fc"

            self.root.configure(bg=self.bg_dark)

            self.data = None
            self.selected_index = None
            self.filter_agent = tk.StringVar(value="ALL")
            self.filter_actions_only = tk.BooleanVar(value=False)
            self.search_text = tk.StringVar()
            self.auto_follow_latest = tk.BooleanVar(value=True)

            self._setup_styles()
            self._build_ui()
            self._poll()

        def _setup_styles(self):
            style = ttk.Style()
            style.theme_use("clam")

            style.configure(".", background=self.bg_dark, foreground=self.fg_text)
            style.configure("TFrame", background=self.bg_dark)
            style.configure("Card.TFrame", background=self.bg_card)
            style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), background=self.bg_card, foreground=self.accent_cyan)
            style.configure("Muted.TLabel", font=("Segoe UI", 9), background=self.bg_card, foreground=self.fg_muted)

            style.configure("Treeview",
                            background=self.bg_panel,
                            foreground=self.fg_text,
                            fieldbackground=self.bg_panel,
                            rowheight=28,
                            font=("Segoe UI", 9))
            style.configure("Treeview.Heading",
                            background=self.bg_card,
                            foreground=self.accent_cyan,
                            font=("Segoe UI", 9, "bold"))
            style.map("Treeview", background=[("selected", "#334155")], foreground=[("selected", "#38bdf8")])

        def _build_ui(self):
            # Top Banner
            banner = tk.Frame(self.root, bg="#1e293b", height=50)
            banner.pack(fill=tk.X, side=tk.TOP, padx=0, pady=0)

            title_lbl = tk.Label(banner, text="⚔️ ONE BOSS FIGHT — TEAM MAILBOX", bg="#1e293b", fg=self.accent_cyan, font=("Segoe UI", 11, "bold"))
            title_lbl.pack(side=tk.LEFT, padx=16, pady=8)

            self.badge_live = tk.Label(banner, text="● LIVE (1s)", bg="#1e293b", fg=self.accent_green, font=("Segoe UI", 9, "bold"))
            self.badge_live.pack(side=tk.LEFT, padx=8)

            self.badge_count = tk.Label(banner, text="Total: 0", bg="#0f172a", fg="#e2e8f0", font=("Consolas", 9, "bold"), padx=8, pady=2)
            self.badge_count.pack(side=tk.LEFT, padx=8)

            self.badge_latest = tk.Label(banner, text="Latest: None", bg="#0f172a", fg=self.accent_amber, font=("Consolas", 9, "bold"), padx=8, pady=2)
            self.badge_latest.pack(side=tk.LEFT, padx=8)

            # Web and Compose Buttons
            btn_web = tk.Button(banner, text="🌐 Open Web View", bg="#0284c7", fg="#ffffff", activebackground="#0369a1",
                                font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, command=lambda: webbrowser.open(f"http://localhost:{port}"))
            btn_web.pack(side=tk.RIGHT, padx=12, pady=8)

            btn_compose = tk.Button(banner, text="✍️ Compose Message", bg="#10b981", fg="#ffffff", activebackground="#059669",
                                    font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, command=self._open_compose_dialog)
            btn_compose.pack(side=tk.RIGHT, padx=4, pady=8)

            # Live AI Task Board
            self.task_board_frame = tk.Frame(self.root, bg="#090d16", padx=8, pady=6)
            self.task_board_frame.pack(fill=tk.X, side=tk.TOP, padx=10, pady=4)

            self.agent_cards = {}
            col_configs = [
                ("Claude", "🟢 Claude (Lead Reviewer)", "#34d399", "#0e2920"),
                ("Antigravity", "🔵 Antigravity (Implementer & Operator)", "#38bdf8", "#0e2338"),
                ("Owner", "🟡 Owner (Project Steering)", "#fbbf24", "#2c1f0a"),
                ("Codex", "🟣 Codex (Retired)", "#c084fc", "#1e1430")
            ]

            for key, title, fg_color, bg_card in col_configs:
                card = tk.Frame(self.task_board_frame, bg=bg_card, highlightbackground="#334155", highlightthickness=1, padx=6, pady=4)
                card.pack(side=tk.LEFT, fill=tk.BOTH, expand=True, padx=4)

                lbl_title = tk.Label(card, text=title, bg=bg_card, fg=fg_color, font=("Segoe UI", 9, "bold"), anchor="w")
                lbl_title.pack(fill=tk.X, side=tk.TOP)

                lbl_status = tk.Label(card, text="Status: ...", bg=bg_card, fg="#cbd5e1", font=("Segoe UI", 8), anchor="w")
                lbl_status.pack(fill=tk.X, side=tk.TOP, pady=(1, 2))

                lbl_tasks = tk.Label(card, text="Loading active tasks...", bg=bg_card, fg="#94a3b8", font=("Segoe UI", 8), justify=tk.LEFT, anchor="nw")
                lbl_tasks.pack(fill=tk.BOTH, expand=True)

                self.agent_cards[key] = {
                    "card": card,
                    "lbl_title": lbl_title,
                    "lbl_status": lbl_status,
                    "lbl_tasks": lbl_tasks
                }

            # Filter Bar
            filter_frame = tk.Frame(self.root, bg=self.bg_dark)
            filter_frame.pack(fill=tk.X, side=tk.TOP, padx=10, pady=4)

            tk.Label(filter_frame, text="Filter Agent:", bg=self.bg_dark, fg=self.fg_muted, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(0, 4))
            agent_cb = ttk.Combobox(filter_frame, textvariable=self.filter_agent, values=["ALL", "Claude", "Codex", "Antigravity", "Owner"], state="readonly", width=12)
            agent_cb.pack(side=tk.LEFT, padx=4)
            agent_cb.bind("<<ComboboxSelected>>", lambda e: self._render_tree())

            chk_act = tk.Checkbutton(filter_frame, text="⚡ Action Items Only", variable=self.filter_actions_only, bg=self.bg_dark, fg="#fbbf24",
                                     selectcolor="#1e293b", activebackground=self.bg_dark, activeforeground="#fbbf24",
                                     command=self._render_tree)
            chk_act.pack(side=tk.LEFT, padx=12)

            tk.Label(filter_frame, text="Search:", bg=self.bg_dark, fg=self.fg_muted, font=("Segoe UI", 9)).pack(side=tk.LEFT, padx=(12, 4))
            search_ent = tk.Entry(filter_frame, textvariable=self.search_text, bg="#1e293b", fg="#ffffff", insertbackground="#ffffff", width=26)
            search_ent.pack(side=tk.LEFT, padx=4)
            search_ent.bind("<KeyRelease>", lambda e: self._render_tree())

            chk_follow = tk.Checkbutton(filter_frame, text="Auto-Follow Latest", variable=self.auto_follow_latest, bg=self.bg_dark, fg=self.accent_cyan,
                                        selectcolor="#1e293b", activebackground=self.bg_dark, activeforeground=self.accent_cyan)
            chk_follow.pack(side=tk.RIGHT, padx=6)

            # Main Panes
            panes = tk.PanedWindow(self.root, orient=tk.HORIZONTAL, bg="#334155", bd=0, sashwidth=4)
            panes.pack(fill=tk.BOTH, expand=True, padx=10, pady=(2, 10))

            left_frame = tk.Frame(panes, bg=self.bg_panel)
            cols = ("id", "sender", "recipient", "preview", "actions")
            self.tree = ttk.Treeview(left_frame, columns=cols, show="headings", selectmode="browse")

            self.tree.heading("id", text="ID")
            self.tree.heading("sender", text="From")
            self.tree.heading("recipient", text="To")
            self.tree.heading("preview", text="Summary Preview")
            self.tree.heading("actions", text="Actions")

            self.tree.column("id", width=65, stretch=False, anchor="center")
            self.tree.column("sender", width=95, stretch=False)
            self.tree.column("recipient", width=95, stretch=False)
            self.tree.column("preview", width=250, stretch=True)
            self.tree.column("actions", width=65, stretch=False, anchor="center")

            tree_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
            self.tree.configure(yscrollcommand=tree_scroll.set)

            self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)
            self.tree.bind("<<TreeviewSelect>>", self._on_select)

            panes.add(left_frame, width=540)

            # Right Detail Frame
            right_frame = tk.Frame(panes, bg=self.bg_panel)

            detail_header = tk.Frame(right_frame, bg="#1e293b", height=40)
            detail_header.pack(fill=tk.X, side=tk.TOP, padx=0, pady=0)

            self.lbl_detail_meta = tk.Label(detail_header, text="Select a message from the list", bg="#1e293b", fg=self.fg_text, font=("Segoe UI", 10, "bold"))
            self.lbl_detail_meta.pack(side=tk.LEFT, padx=12, pady=6)

            self.text_detail = ScrolledText(right_frame, bg="#090d16", fg="#e2e8f0", insertbackground="#ffffff",
                                            font=("Consolas", 10), wrap=tk.WORD, bd=0, padx=10, pady=10)
            self.text_detail.pack(fill=tk.BOTH, expand=True)

            panes.add(right_frame, width=720)

        def _open_compose_dialog(self):
            dialog = tk.Toplevel(self.root)
            dialog.title("Compose Message to Team Mailbox")
            dialog.geometry("640x520")
            dialog.configure(bg="#0f172a")
            dialog.transient(self.root)
            dialog.grab_set()

            tk.Label(dialog, text="✍️ Compose Message", bg="#0f172a", fg=self.accent_cyan, font=("Segoe UI", 12, "bold")).pack(anchor="w", padx=16, pady=(12, 4))

            form = tk.Frame(dialog, bg="#0f172a")
            form.pack(fill=tk.X, padx=16, pady=4)

            tk.Label(form, text="Sender:", bg="#0f172a", fg="#94a3b8", font=("Segoe UI", 9)).grid(row=0, column=0, sticky="w", pady=2)
            cb_sender = ttk.Combobox(form, values=["Owner", "Codex", "Claude", "Antigravity"], state="readonly", width=16)
            cb_sender.set("Owner")
            cb_sender.grid(row=0, column=1, sticky="w", padx=8, pady=2)

            tk.Label(form, text="Recipient:", bg="#0f172a", fg="#94a3b8", font=("Segoe UI", 9)).grid(row=0, column=2, sticky="w", pady=2)
            cb_recipient = ttk.Combobox(form, values=["All", "Codex (lead)", "Claude", "Antigravity", "Owner"], state="readonly", width=18)
            cb_recipient.set("All")
            cb_recipient.grid(row=0, column=3, sticky="w", padx=8, pady=2)

            tk.Label(dialog, text="Task Directive / Subject:", bg="#0f172a", fg="#94a3b8", font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=(6, 2))
            ent_task = tk.Entry(dialog, bg="#1e293b", fg="#ffffff", insertbackground="#ffffff")
            ent_task.pack(fill=tk.X, padx=16, pady=2)

            tk.Label(dialog, text="Message Body (Markdown):", bg="#0f172a", fg="#94a3b8", font=("Segoe UI", 9)).pack(anchor="w", padx=16, pady=(6, 2))
            txt_body = ScrolledText(dialog, bg="#090d16", fg="#ffffff", insertbackground="#ffffff", font=("Consolas", 10), height=12)
            txt_body.pack(fill=tk.BOTH, expand=True, padx=16, pady=2)

            btn_frame = tk.Frame(dialog, bg="#0f172a")
            btn_frame.pack(fill=tk.X, padx=16, pady=12)

            def send_msg():
                body_content = txt_body.get("1.0", tk.END).strip()
                if not body_content:
                    messagebox.showerror("Error", "Message body cannot be empty", parent=dialog)
                    return
                try:
                    res = MailboxWriter.append_message(
                        sender=cb_sender.get(),
                        recipient=cb_recipient.get(),
                        task=ent_task.get().strip(),
                        body=body_content
                    )
                    messagebox.showinfo("Success", f"Message [{res['message_id']}] posted to Mailbox!", parent=dialog)
                    dialog.destroy()
                    self._poll()
                except Exception as err:
                    messagebox.showerror("Error", str(err), parent=dialog)

            tk.Button(btn_frame, text="Cancel", bg="#334155", fg="#ffffff", relief=tk.FLAT, padx=12, pady=4, command=dialog.destroy).pack(side=tk.RIGHT, padx=4)
            tk.Button(btn_frame, text="🚀 Send to Mailbox", bg="#10b981", fg="#ffffff", font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=14, pady=4, command=send_msg).pack(side=tk.RIGHT, padx=4)

        def _poll(self):
            try:
                data = MailboxParser.parse_file()
                prev_count = self.data["count"] if self.data else 0
                self.data = data

                self.badge_count.config(text=f"Total: {data['count']}")
                if data["latest"]:
                    self.badge_latest.config(text=f"Latest: [{data['latest']['id']}] {data['latest']['sender']}")

                # Update live task cards
                if data.get("ai_tasks"):
                    self._update_task_board(data["ai_tasks"])

                if data["count"] != prev_count:
                    self._render_tree()
                    if self.auto_follow_latest.get() and data["count"] > 0:
                        latest_id = data["latest"]["id"]
                        if self.tree.exists(latest_id):
                            self.tree.selection_set(latest_id)
                            self.tree.see(latest_id)
            except Exception as e:
                print(f"[!] Polling error: {e}")

            self.root.after(1000, self._poll)

        def _update_task_board(self, ai_tasks):
            for key, prof in ai_tasks.items():
                if key in self.agent_cards:
                    c = self.agent_cards[key]
                    c["lbl_status"].config(text=f"Status: {prof.get('status', 'Active')} | {prof.get('active_directive', '')[:40]}")
                    tasks = prof.get("tasks", [])
                    if tasks:
                        task_lines = [f"{t['status_icon']} [{t.get('source', '')}] {t['title'][:32]}" for t in tasks[:3]]
                        c["lbl_tasks"].config(text="\n".join(task_lines))
                    else:
                        c["lbl_tasks"].config(text="No active tasks logged")

        def _render_tree(self):
            if not self.data or not self.data["messages"]:
                return

            self.tree.delete(*self.tree.get_children())
            agent_filter = self.filter_agent.get()
            act_only = self.filter_actions_only.get()
            query = self.search_text.get().lower().strip()

            # Render newest appended message first in desktop GUI as well
            for m in reversed(self.data["messages"]):
                if act_only and not m["has_actions"]:
                    continue
                if agent_filter != "ALL":
                    if m["sender_norm"] != agent_filter and m["recipient_norm"] != agent_filter:
                        continue
                if query:
                    full_str = f"{m['id']} {m['sender']} {m['recipient']} {m['body']}".lower()
                    if query not in full_str:
                        continue

                act_badge = "⚡ Yes" if m["has_actions"] else ""
                clean_prev = m["body"].replace("\n", " ").strip()[:80]
                self.tree.insert("", tk.END, iid=m["id"], values=(f"[{m['id']}]", m["sender"], m["recipient"], clean_prev, act_badge))

        def _on_select(self, event):
            sel = self.tree.selection()
            if not sel or not self.data:
                return
            msg_id = sel[0]
            m = next((x for x in self.data["messages"] if x["id"] == msg_id), None)
            if not m:
                return
            self.lbl_detail_meta.config(text=f"[{m['id']}]  {m['sender']} ➔ {m['recipient']}  |  {m['timestamp']}")
            self.text_detail.delete("1.0", tk.END)
            self.text_detail.insert(tk.END, m["body"])

    app = MailboxTkinterApp(root)
    root.mainloop()


# ==============================================================================
# 5. MAIN ENTRYPOINT
# ==============================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Real-time Team Mailbox Monitor UI")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port for local web dashboard")
    parser.add_argument("--web-only", action="store_true", help="Run only the local web server without desktop GUI")
    args = parser.parse_args()

    lan_ip = get_lan_ip()

    # Start background HTTP server accessible from localhost and mobile Wi-Fi
    start_web_server(port=args.port)
    print(f"[*] Mailbox Web Server listening:")
    print(f"    - Desktop/Local: http://localhost:{args.port}")
    print(f"    - Mobile/LAN:    http://{lan_ip}:{args.port}")

    if args.web_only:
        print("[*] Running in web-only mode. Press Ctrl+C to exit.")
        webbrowser.open(f"http://localhost:{args.port}")
        try:
            while True:
                time.sleep(1)
        except KeyboardInterrupt:
            print("\n[*] Exiting.")
            sys.exit(0)
    else:
        try:
            import tkinter as tk
            root = tk.Tk()
            run_tkinter_gui(port=args.port)
        except Exception as e:
            print(f"[!] Tkinter desktop GUI not available ({e}). Falling back to web view...")
            webbrowser.open(f"http://localhost:{args.port}")
            try:
                while True:
                    time.sleep(1)
            except KeyboardInterrupt:
                sys.exit(0)


if __name__ == "__main__":
    main()
