#!/usr/bin/env python3
"""
MailboxViewer - Real-time monitoring UI app for One Boss Fight team mailbox.
Continuously reads Documentation/TEAM_MAILBOX.md, parses sender/recipient relationships,
detects actionable items for each AI (Claude, Codex, Antigravity, Owner),
and highlights the latest message.

Supports:
  - Native Windows desktop GUI (Tkinter)
  - Embedded real-time web dashboard (http://localhost:8080)
  - Auto-refresh every 1000ms

Usage:
  python Scripts/MailboxViewer.py            # Opens desktop GUI + local web dashboard
  python Scripts/MailboxViewer.py --web-only # Headless mode, web dashboard only
  python Scripts/MailboxViewer.py --port 8085
"""

import os
import sys
import re
import json
import time
import threading
import webbrowser
from datetime import datetime
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs

# Determine project paths
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.abspath(os.path.join(SCRIPT_DIR, ".."))
MAILBOX_PATH = os.path.join(PROJECT_ROOT, "Documentation", "TEAM_MAILBOX.md")

# Default HTTP server port
DEFAULT_PORT = 8080


# ==============================================================================
# 1. PARSER & DATA MODEL
# ==============================================================================

class MailboxParser:
    """Parses TEAM_MAILBOX.md into structured message models with action extraction."""

    HEADER_REGEX = re.compile(
        r'(?m)^### \[(?P<id>[^\]]+)\]\s*(?P<sender>[^->\n\r]+?)\s*->\s*(?P<recipient>[^,\n\r]+?)(?:,\s*(?P<timestamp>[^\r\n]*))?$'
    )

    @classmethod
    def parse_file(cls, filepath=MAILBOX_PATH):
        if not os.path.exists(filepath):
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

        matches = list(cls.HEADER_REGEX.finditer(text))
        messages = []

        for i, match in enumerate(matches):
            msg_id = match.group("id").strip()
            sender = match.group("sender").strip()
            recipient = match.group("recipient").strip()
            timestamp = (match.group("timestamp") or "").strip()

            start_idx = match.end()
            end_idx = matches[i + 1].start() if i + 1 < len(matches) else len(text)
            body = text[start_idx:end_idx].strip()

            sender_norm = cls._normalize_agent(sender)
            recip_norm = cls._normalize_agent(recipient)
            actions = cls._extract_action_points(body)

            has_actions = any(len(v) > 0 for k, v in actions.items() if k != "General")

            msg = {
                "index": i + 1,
                "id": msg_id,
                "sender": sender,
                "sender_norm": sender_norm,
                "recipient": recipient,
                "recipient_norm": recip_norm,
                "timestamp": timestamp,
                "body": body,
                "actions": actions,
                "has_actions": has_actions,
                "is_last": (i == len(matches) - 1)
            }
            messages.append(msg)

        latest = messages[-1] if messages else None

        # Build current pending queue summary from latest messages
        action_summary = cls._compute_team_status(messages)

        return {
            "exists": True,
            "error": None,
            "filepath": filepath,
            "mtime": mtime,
            "size": size,
            "count": len(messages),
            "messages": messages,
            "latest": latest,
            "action_summary": action_summary
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
        current_target = None

        for line in lines:
            sline = line.strip()
            if not sline:
                continue

            # Identify target agent block
            m_codex = re.match(r'^(?:CODEX|OPEN FOR CODEX|CODEX QUEUE|FOR CODEX):\s*(.*)', sline, re.I)
            m_ag = re.match(r'^(?:ANTIGRAVITY|AG|OPEN FOR AG|FOR AG|FOR ANTIGRAVITY):\s*(.*)', sline, re.I)
            m_claude = re.match(r'^(?:CLAUDE|OPEN FOR CLAUDE|FOR CLAUDE):\s*(.*)', sline, re.I)
            m_owner = re.match(r'^(?:OWNER|DECISION NEEDED(?:\s*\(owner\))?|OWNER DECISION|FOR OWNER):\s*(.*)', sline, re.I)
            m_task = re.match(r'^(?:TASK|NEXT ACTION|QUEUE|ACTION):\s*(.*)', sline, re.I)

            if m_codex:
                current_target = "Codex"
                val = m_codex.group(1).strip()
                if val: actions["Codex"].append(val)
            elif m_ag:
                current_target = "Antigravity"
                val = m_ag.group(1).strip()
                if val: actions["Antigravity"].append(val)
            elif m_claude:
                current_target = "Claude"
                val = m_claude.group(1).strip()
                if val: actions["Claude"].append(val)
            elif m_owner:
                current_target = "Owner"
                val = m_owner.group(1).strip()
                if val: actions["Owner"].append(val)
            elif m_task:
                current_target = "General"
                val = m_task.group(1).strip()
                if val: actions["General"].append(val)
            elif sline.startswith(("- ", "* ", "> ")) or re.match(r'^\d+\.', sline):
                if current_target and len(actions[current_target]) > 0:
                    actions[current_target].append(sline)
            elif any(sline.upper().startswith(k) for k in ["STATUS:", "VALIDATION:", "VERDICT:", "FINDINGS:", "RESULT:", "SUMMARY:"]):
                current_target = None

        return {k: v for k, v in actions.items() if v}

    @staticmethod
    def _compute_team_status(messages):
        """Looks at recent messages to deduce the latest active directives for each party."""
        status = {
            "Claude": {"latest_task": "Idle / Leading", "source_msg": ""},
            "Codex": {"latest_task": "Pending Queue", "source_msg": ""},
            "Antigravity": {"latest_task": "Standby (A-80 delivered)", "source_msg": ""},
            "Owner": {"latest_task": "None pending", "source_msg": ""}
        }

        # Scan backwards
        for msg in reversed(messages):
            actions = msg.get("actions", {})
            for agent in ["Claude", "Codex", "Antigravity", "Owner"]:
                if agent in actions and status[agent]["source_msg"] == "":
                    first_item = actions[agent][0] if actions[agent] else ""
                    if first_item:
                        status[agent]["latest_task"] = first_item
                        status[agent]["source_msg"] = msg["id"]

        return status


# ==============================================================================
# 2. WEB SERVER & DASHBOARD
# ==============================================================================

HTML_TEMPLATE = r"""<!DOCTYPE html>
<html lang="en">
<head>
  <meta charset="UTF-8">
  <meta name="viewport" content="width=device-width, initial-scale=1.0">
  <title>One Boss Fight — Team Mailbox Monitor</title>
  <script src="https://cdn.tailwindcss.com"></script>
  <style>
    body { background-color: #0f172a; color: #e2e8f0; font-family: system-ui, -apple-system, sans-serif; }
    .custom-scroll::-webkit-scrollbar { width: 6px; height: 6px; }
    .custom-scroll::-webkit-scrollbar-track { background: #1e293b; }
    .custom-scroll::-webkit-scrollbar-thumb { background: #475569; border-radius: 3px; }
    .tag-claude { background: rgba(16, 185, 129, 0.2); color: #34d399; border: 1px solid rgba(16, 185, 129, 0.4); }
    .tag-codex { background: rgba(168, 85, 247, 0.2); color: #c084fc; border: 1px solid rgba(168, 85, 247, 0.4); }
    .tag-ag { background: rgba(56, 189, 248, 0.2); color: #38bdf8; border: 1px solid rgba(56, 189, 248, 0.4); }
    .tag-owner { background: rgba(245, 158, 11, 0.2); color: #fbbf24; border: 1px solid rgba(245, 158, 11, 0.4); }
    .tag-general { background: rgba(148, 163, 184, 0.2); color: #94a3b8; border: 1px solid rgba(148, 163, 184, 0.4); }
  </style>
</head>
<body class="h-screen flex flex-col overflow-hidden">

  <!-- Header -->
  <header class="bg-slate-900 border-b border-slate-800 px-6 py-3 flex items-center justify-between shrink-0 shadow-md">
    <div class="flex items-center space-x-3">
      <div class="w-3 h-3 rounded-full bg-emerald-400 animate-pulse"></div>
      <h1 class="text-lg font-bold text-slate-100 tracking-wide flex items-center gap-2">
        <span>⚔️ One Boss Fight</span>
        <span class="text-xs bg-slate-800 text-slate-400 px-2 py-0.5 rounded border border-slate-700 font-mono">TEAM MAILBOX</span>
      </h1>
    </div>

    <!-- Stats & Live Indicator -->
    <div class="flex items-center space-x-4 text-xs">
      <span class="text-slate-400">Total: <strong id="msg-count" class="text-emerald-400 font-mono">0</strong></span>
      <span class="text-slate-500">|</span>
      <span class="text-slate-400">Latest: <strong id="latest-badge" class="text-amber-400 font-mono">None</strong></span>
      <span class="text-slate-500">|</span>
      <span id="poll-indicator" class="text-emerald-400 font-mono">● LIVE 1s</span>
    </div>
  </header>

  <!-- Latest Directives Bar -->
  <div class="bg-slate-950 border-b border-slate-800 px-6 py-2.5 grid grid-cols-4 gap-3 text-xs shrink-0">
    <div class="bg-slate-900/80 p-2 rounded border border-slate-800">
      <div class="flex justify-between items-center mb-1">
        <span class="font-semibold text-emerald-400">🟢 Claude (Tech Lead)</span>
        <span id="status-claude-src" class="text-[10px] text-slate-500 font-mono"></span>
      </div>
      <p id="status-claude" class="text-slate-300 truncate">Monitoring</p>
    </div>
    <div class="bg-slate-900/80 p-2 rounded border border-slate-800">
      <div class="flex justify-between items-center mb-1">
        <span class="font-semibold text-purple-400">🟣 Codex (Astra Reviewer)</span>
        <span id="status-codex-src" class="text-[10px] text-slate-500 font-mono"></span>
      </div>
      <p id="status-codex" class="text-slate-300 truncate">Queue Review</p>
    </div>
    <div class="bg-slate-900/80 p-2 rounded border border-slate-800">
      <div class="flex justify-between items-center mb-1">
        <span class="font-semibold text-sky-400">🔵 Antigravity (Visual/Anim)</span>
        <span id="status-ag-src" class="text-[10px] text-slate-500 font-mono"></span>
      </div>
      <p id="status-ag" class="text-slate-300 truncate">Standby</p>
    </div>
    <div class="bg-slate-900/80 p-2 rounded border border-slate-800">
      <div class="flex justify-between items-center mb-1">
        <span class="font-semibold text-amber-400">🟡 Owner Decisions</span>
        <span id="status-owner-src" class="text-[10px] text-slate-500 font-mono"></span>
      </div>
      <p id="status-owner" class="text-slate-300 truncate">None pending</p>
    </div>
  </div>

  <!-- Search & Filter Controls -->
  <div class="bg-slate-900 px-6 py-2 border-b border-slate-800 flex items-center justify-between gap-4 text-xs shrink-0">
    <div class="flex items-center gap-2 flex-1 max-w-lg">
      <input type="text" id="search-box" placeholder="Search by ID, agent, task, or keyword..."
             class="w-full bg-slate-950 border border-slate-700 rounded px-3 py-1.5 text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500">
    </div>
    <div class="flex items-center gap-2">
      <button onclick="setFilter('ALL')" class="filter-btn px-2.5 py-1 rounded bg-slate-800 border border-slate-700 hover:bg-slate-700 text-slate-200 font-medium" data-filter="ALL">All</button>
      <button onclick="setFilter('ACTIONS')" class="filter-btn px-2.5 py-1 rounded bg-slate-800/50 border border-slate-700 hover:bg-slate-700 text-amber-300" data-filter="ACTIONS">⚡ Has Action Items</button>
      <button onclick="setFilter('Claude')" class="filter-btn px-2.5 py-1 rounded bg-slate-800/50 border border-slate-700 hover:bg-slate-700 text-emerald-400" data-filter="Claude">Claude</button>
      <button onclick="setFilter('Codex')" class="filter-btn px-2.5 py-1 rounded bg-slate-800/50 border border-slate-700 hover:bg-slate-700 text-purple-400" data-filter="Codex">Codex</button>
      <button onclick="setFilter('Antigravity')" class="filter-btn px-2.5 py-1 rounded bg-slate-800/50 border border-slate-700 hover:bg-slate-700 text-sky-400" data-filter="Antigravity">Antigravity</button>
    </div>
    <div class="flex items-center gap-2">
      <label class="flex items-center gap-1.5 cursor-pointer text-slate-400">
        <input type="checkbox" id="auto-scroll" checked class="rounded bg-slate-800 border-slate-700 text-cyan-500 focus:ring-0">
        <span>Auto-select latest</span>
      </label>
    </div>
  </div>

  <!-- Main Split Layout -->
  <div class="flex-1 flex overflow-hidden">
    <!-- Left Message Feed -->
    <div id="feed" class="w-2/5 border-r border-slate-800 overflow-y-auto custom-scroll p-4 space-y-2.5 bg-slate-950/40">
      <!-- Cards rendered via JS -->
    </div>

    <!-- Right Detailed View -->
    <div class="w-3/5 flex flex-col overflow-hidden bg-slate-900/60">
      <!-- Active Message Header -->
      <div id="detail-header" class="p-5 border-b border-slate-800 bg-slate-900/90 shrink-0">
        <div class="flex items-center justify-between">
          <div class="flex items-center gap-3">
            <span id="detail-id" class="text-base font-bold text-cyan-400 font-mono px-2 py-0.5 bg-cyan-950/80 rounded border border-cyan-800">[---]</span>
            <span id="detail-sender" class="font-semibold text-slate-200 text-sm">Select a message</span>
            <span class="text-slate-500">➔</span>
            <span id="detail-recipient" class="text-slate-300 text-sm"></span>
          </div>
          <span id="detail-time" class="text-xs text-slate-500 font-mono"></span>
        </div>
      </div>

      <!-- Action Points Banner in Detail View -->
      <div id="detail-actions" class="p-4 border-b border-slate-800 bg-slate-950/70 shrink-0 space-y-2 hidden">
        <!-- Rendered action tags -->
      </div>

      <!-- Message Raw Body Viewer -->
      <div class="flex-1 overflow-y-auto custom-scroll p-5 font-mono text-xs text-slate-300 whitespace-pre-wrap leading-relaxed select-text" id="detail-body">
        Select a message from the left to view its complete content and parsed action items.
      </div>
    </div>
  </div>

  <script>
    let currentData = null;
    let selectedMsgIndex = null;
    let activeFilter = 'ALL';
    let searchQuery = '';

    function setFilter(f) {
      activeFilter = f;
      document.querySelectorAll('.filter-btn').forEach(b => {
        if (b.dataset.filter === f) {
          b.classList.remove('bg-slate-800/50');
          b.classList.add('bg-slate-700', 'ring-1', 'ring-cyan-500');
        } else {
          b.classList.add('bg-slate-800/50');
          b.classList.remove('bg-slate-700', 'ring-1', 'ring-cyan-500');
        }
      });
      renderList();
    }

    document.getElementById('search-box').addEventListener('input', (e) => {
      searchQuery = e.target.value.toLowerCase().trim();
      renderList();
    });

    function selectMessage(idx) {
      if (!currentData || !currentData.messages) return;
      selectedMsgIndex = idx;
      const msg = currentData.messages.find(m => m.index === idx);
      if (!msg) return;

      document.getElementById('detail-id').textContent = `[${msg.id}]`;
      document.getElementById('detail-sender').textContent = msg.sender;
      document.getElementById('detail-recipient').textContent = msg.recipient;
      document.getElementById('detail-time').textContent = msg.timestamp || 'No timestamp';
      document.getElementById('detail-body').textContent = msg.body;

      // Render action points box
      const actsContainer = document.getElementById('detail-actions');
      actsContainer.innerHTML = '';
      const acts = msg.actions || {};
      const entries = Object.entries(acts);

      if (entries.length > 0) {
        actsContainer.classList.remove('hidden');
        const title = document.createElement('div');
        title.className = 'text-xs font-bold text-amber-400 mb-1.5 flex items-center gap-1.5';
        title.innerHTML = '⚡ Parsed Action Points & Directives';
        actsContainer.appendChild(title);

        entries.forEach(([target, items]) => {
          const row = document.createElement('div');
          let tagClass = 'tag-general';
          if (target === 'Claude') tagClass = 'tag-claude';
          if (target === 'Codex') tagClass = 'tag-codex';
          if (target === 'Antigravity') tagClass = 'tag-ag';
          if (target === 'Owner') tagClass = 'tag-owner';

          row.className = `p-2 rounded text-xs ${tagClass} space-y-1`;
          row.innerHTML = `<strong>Action for ${target}:</strong><ul class="list-disc ml-4 space-y-0.5">${items.map(it => `<li>${escapeHtml(it)}</li>`).join('')}</ul>`;
          actsContainer.appendChild(row);
        });
      } else {
        actsContainer.classList.add('hidden');
      }

      // Highlight in feed
      document.querySelectorAll('.msg-card').forEach(el => {
        if (parseInt(el.dataset.index) === idx) {
          el.classList.add('border-cyan-500', 'bg-slate-800/80');
          el.classList.remove('border-slate-800');
        } else {
          el.classList.remove('border-cyan-500', 'bg-slate-800/80');
          el.classList.add('border-slate-800');
        }
      });
    }

    function escapeHtml(text) {
      const map = {'&': '&amp;', '<': '&lt;', '>': '&gt;', '"': '&quot;', "'": '&#039;'};
      return text.replace(/[&<>"']/g, m => map[m]);
    }

    function renderList() {
      if (!currentData || !currentData.messages) return;
      const feed = document.getElementById('feed');
      feed.innerHTML = '';

      let list = currentData.messages.slice().reverse();

      // Apply search
      if (searchQuery) {
        list = list.filter(m =>
          m.id.toLowerCase().includes(searchQuery) ||
          m.sender.toLowerCase().includes(searchQuery) ||
          m.recipient.toLowerCase().includes(searchQuery) ||
          m.body.toLowerCase().includes(searchQuery)
        );
      }

      // Apply filter
      if (activeFilter === 'ACTIONS') {
        list = list.filter(m => m.has_actions);
      } else if (activeFilter !== 'ALL') {
        list = list.filter(m => m.sender_norm === activeFilter || m.recipient_norm.includes(activeFilter));
      }

      list.forEach(msg => {
        const card = document.createElement('div');
        const isSelected = (selectedMsgIndex === msg.index);
        card.dataset.index = msg.index;
        card.className = `msg-card cursor-pointer p-3 rounded-lg border transition-all text-xs ${
          isSelected ? 'border-cyan-500 bg-slate-800/80' : 'border-slate-800 bg-slate-900/60 hover:bg-slate-800/50'
        } ${msg.is_last ? 'ring-1 ring-amber-500/50' : ''}`;

        let senderColor = 'text-slate-300';
        if (msg.sender_norm === 'Claude') senderColor = 'text-emerald-400 font-semibold';
        if (msg.sender_norm === 'Codex') senderColor = 'text-purple-400 font-semibold';
        if (msg.sender_norm === 'Antigravity') senderColor = 'text-sky-400 font-semibold';
        if (msg.sender_norm === 'Owner') senderColor = 'text-amber-400 font-semibold';

        let actionTags = '';
        if (msg.actions) {
          Object.keys(msg.actions).forEach(target => {
            if (target === 'Claude') actionTags += `<span class="px-1.5 py-0.5 rounded text-[10px] tag-claude">Action: Claude</span> `;
            if (target === 'Codex') actionTags += `<span class="px-1.5 py-0.5 rounded text-[10px] tag-codex">Action: Codex</span> `;
            if (target === 'Antigravity') actionTags += `<span class="px-1.5 py-0.5 rounded text-[10px] tag-ag">Action: AG</span> `;
            if (target === 'Owner') actionTags += `<span class="px-1.5 py-0.5 rounded text-[10px] tag-owner">Action: Owner</span> `;
          });
        }

        const latestBadge = msg.is_last ? `<span class="px-1.5 py-0.5 rounded bg-amber-500 text-slate-950 font-bold text-[9px] uppercase tracking-wider">LATEST</span>` : '';

        card.innerHTML = `
          <div class="flex items-center justify-between mb-1">
            <div class="flex items-center gap-1.5">
              <span class="font-mono font-bold text-cyan-400">[${msg.id}]</span>
              ${latestBadge}
            </div>
            <span class="text-slate-500 font-mono text-[10px]">${msg.timestamp || ''}</span>
          </div>
          <div class="flex items-center gap-1.5 text-slate-400 mb-1.5">
            <span class="${senderColor}">${escapeHtml(msg.sender)}</span>
            <span>➔</span>
            <span class="text-slate-300">${escapeHtml(msg.recipient)}</span>
          </div>
          ${actionTags ? `<div class="flex flex-wrap gap-1 mt-1 mb-1.5">${actionTags}</div>` : ''}
          <div class="text-slate-400 line-clamp-2 font-mono text-[11px] leading-snug">
            ${escapeHtml(msg.body.slice(0, 160))}
          </div>
        `;

        card.addEventListener('click', () => selectMessage(msg.index));
        feed.appendChild(card);
      });
    }

    async function pollMailbox() {
      try {
        const res = await fetch('/api/mailbox');
        if (!res.ok) throw new Error('Network error');
        const data = await res.json();

        const countChanged = !currentData || currentData.count !== data.count;
        currentData = data;

        document.getElementById('msg-count').textContent = data.count || 0;
        if (data.latest) {
          document.getElementById('latest-badge').textContent = `[${data.latest.id}] by ${data.latest.sender_norm}`;
        }

        // Update directives summary
        if (data.action_summary) {
          const s = data.action_summary;
          if (s.Claude) {
            document.getElementById('status-claude').textContent = s.Claude.latest_task;
            document.getElementById('status-claude-src').textContent = s.Claude.source_msg ? `[${s.Claude.source_msg}]` : '';
          }
          if (s.Codex) {
            document.getElementById('status-codex').textContent = s.Codex.latest_task;
            document.getElementById('status-codex-src').textContent = s.Codex.source_msg ? `[${s.Codex.source_msg}]` : '';
          }
          if (s.Antigravity) {
            document.getElementById('status-ag').textContent = s.Antigravity.latest_task;
            document.getElementById('status-ag-src').textContent = s.Antigravity.source_msg ? `[${s.Antigravity.source_msg}]` : '';
          }
          if (s.Owner) {
            document.getElementById('status-owner').textContent = s.Owner.latest_task;
            document.getElementById('status-owner-src').textContent = s.Owner.source_msg ? `[${s.Owner.source_msg}]` : '';
          }
        }

        renderList();

        // Auto select latest if changed or initial
        const autoScrollChecked = document.getElementById('auto-scroll').checked;
        if ((countChanged && autoScrollChecked) || selectedMsgIndex === null) {
          if (data.latest) {
            selectMessage(data.latest.index);
          }
        }
      } catch (err) {
        console.error('Polling error:', err);
      }
    }

    setInterval(pollMailbox, 1000);
    pollMailbox();
  </script>
</body>
</html>
"""


class MailboxHTTPHandler(BaseHTTPRequestHandler):
    """Serves the web dashboard and JSON API endpoint."""

    def log_message(self, format, *args):
        # Silence HTTP access logs to keep console clean
        pass

    def do_GET(self):
        url = urlparse(self.path)
        if url.path == "/api/mailbox":
            data = MailboxParser.parse_file()
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


def start_web_server(port=DEFAULT_PORT):
    server = HTTPServer(("127.0.0.1", port), MailboxHTTPHandler)
    t = threading.Thread(target=server.serve_forever, daemon=True)
    t.start()
    return server


# ==============================================================================
# 3. TKINTER DESKTOP GUI
# ==============================================================================

def run_tkinter_gui(port=DEFAULT_PORT):
    import tkinter as tk
    from tkinter import ttk, font

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

            # Start polling loop (1000ms)
            self._poll()

        def _setup_styles(self):
            style = ttk.Style()
            style.theme_use("clam")

            style.configure(".", background=self.bg_dark, foreground=self.fg_text)
            style.configure("TFrame", background=self.bg_dark)
            style.configure("Card.TFrame", background=self.bg_card)
            style.configure("Header.TLabel", font=("Segoe UI", 12, "bold"), background=self.bg_card, foreground=self.accent_cyan)
            style.configure("Muted.TLabel", font=("Segoe UI", 9), background=self.bg_card, foreground=self.fg_muted)

            # Treeview styling
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

            btn_web = tk.Button(banner, text="🌐 Open Web View", bg="#0284c7", fg="#ffffff", activebackground="#0369a1", activeforeground="#ffffff",
                                font=("Segoe UI", 9, "bold"), relief=tk.FLAT, padx=10, command=lambda: webbrowser.open(f"http://localhost:{port}"))
            btn_web.pack(side=tk.RIGHT, padx=16, pady=8)

            # Directives Bar
            dir_frame = tk.Frame(self.root, bg="#090d16", height=42)
            dir_frame.pack(fill=tk.X, side=tk.TOP, padx=10, pady=4)

            self.lbl_claude_dir = tk.Label(dir_frame, text="🟢 Claude: ...", bg="#090d16", fg="#34d399", font=("Segoe UI", 9), anchor="w")
            self.lbl_claude_dir.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)

            self.lbl_codex_dir = tk.Label(dir_frame, text="🟣 Codex: ...", bg="#090d16", fg="#c084fc", font=("Segoe UI", 9), anchor="w")
            self.lbl_codex_dir.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)

            self.lbl_ag_dir = tk.Label(dir_frame, text="🔵 AG: ...", bg="#090d16", fg="#38bdf8", font=("Segoe UI", 9), anchor="w")
            self.lbl_ag_dir.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)

            self.lbl_owner_dir = tk.Label(dir_frame, text="🟡 Owner: ...", bg="#090d16", fg="#fbbf24", font=("Segoe UI", 9), anchor="w")
            self.lbl_owner_dir.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=6)

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
            panes.pack(fill=tk.BOTH, expand=True, padx=10, pady=(2, 8))

            # Left Treeview Frame
            left_frame = tk.Frame(panes, bg=self.bg_panel)
            panes.add(left_frame, minsize=400, width=540)

            cols = ("id", "from_to", "time", "action")
            self.tree = ttk.Treeview(left_frame, columns=cols, show="headings", selectmode="browse")
            self.tree.heading("id", text="ID")
            self.tree.heading("from_to", text="From ➔ To")
            self.tree.heading("time", text="Timestamp")
            self.tree.heading("action", text="Action Target")

            self.tree.column("id", width=68, anchor="center")
            self.tree.column("from_to", width=220, anchor="w")
            self.tree.column("time", width=110, anchor="center")
            self.tree.column("action", width=120, anchor="w")

            tree_scroll = ttk.Scrollbar(left_frame, orient=tk.VERTICAL, command=self.tree.yview)
            self.tree.configure(yscrollcommand=tree_scroll.set)

            self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            tree_scroll.pack(side=tk.RIGHT, fill=tk.Y)

            self.tree.bind("<<TreeviewSelect>>", self._on_select_message)

            # Right Detail Frame
            right_frame = tk.Frame(panes, bg="#0f172a")
            panes.add(right_frame, minsize=460)

            # Header Card
            self.card_header = tk.Frame(right_frame, bg="#1e293b", padx=12, pady=10)
            self.card_header.pack(fill=tk.X, side=tk.TOP, pady=(0, 6))

            self.lbl_det_id = tk.Label(self.card_header, text="[---]", font=("Consolas", 12, "bold"), bg="#1e293b", fg=self.accent_cyan)
            self.lbl_det_id.pack(side=tk.LEFT)

            self.lbl_det_route = tk.Label(self.card_header, text="Select a message", font=("Segoe UI", 10, "bold"), bg="#1e293b", fg="#ffffff")
            self.lbl_det_route.pack(side=tk.LEFT, padx=10)

            self.lbl_det_time = tk.Label(self.card_header, text="", font=("Consolas", 9), bg="#1e293b", fg=self.fg_muted)
            self.lbl_det_time.pack(side=tk.RIGHT)

            # Action Points Alert Box
            self.card_actions = tk.Frame(right_frame, bg="#111827", padx=12, pady=8, highlightbackground="#374151", highlightthickness=1)
            self.card_actions.pack(fill=tk.X, side=tk.TOP, pady=(0, 6))

            self.lbl_act_title = tk.Label(self.card_actions, text="⚡ ACTION POINTS & DIRECTIVES", font=("Segoe UI", 9, "bold"), bg="#111827", fg="#fbbf24")
            self.lbl_act_title.pack(anchor="w")

            self.lbl_act_content = tk.Label(self.card_actions, text="None", font=("Segoe UI", 9), bg="#111827", fg="#e5e7eb", justify="left", wraplength=550)
            self.lbl_act_content.pack(anchor="w", pady=(4, 0))

            # Full Text Area
            text_frame = tk.Frame(right_frame, bg=self.bg_panel)
            text_frame.pack(fill=tk.BOTH, expand=True)

            self.txt_body = tk.Text(text_frame, bg="#090d16", fg="#cbd5e1", insertbackground="#ffffff",
                                    font=("Consolas", 10), wrap=tk.WORD, bd=0, padx=10, pady=10)
            body_scroll = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=self.txt_body.yview)
            self.txt_body.configure(yscrollcommand=body_scroll.set)

            self.txt_body.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
            body_scroll.pack(side=tk.RIGHT, fill=tk.Y)

        def _poll(self):
            try:
                new_data = MailboxParser.parse_file()
                count_changed = (self.data is None or self.data.get("count") != new_data.get("count"))
                self.data = new_data

                self.badge_count.config(text=f"Total: {new_data.get('count', 0)}")
                latest = new_data.get("latest")
                if latest:
                    self.badge_latest.config(text=f"Latest: [{latest['id']}] {latest['sender_norm']}")

                # Update directives summary
                s = new_data.get("action_summary", {})
                if s.get("Claude"):
                    self.lbl_claude_dir.config(text=f"🟢 Claude: {s['Claude']['latest_task'][:42]}")
                if s.get("Codex"):
                    self.lbl_codex_dir.config(text=f"🟣 Codex: {s['Codex']['latest_task'][:42]}")
                if s.get("Antigravity"):
                    self.lbl_ag_dir.config(text=f"🔵 AG: {s['Antigravity']['latest_task'][:42]}")
                if s.get("Owner"):
                    self.lbl_owner_dir.config(text=f"🟡 Owner: {s['Owner']['latest_task'][:42]}")

                if count_changed:
                    self._render_tree()
                    if self.auto_follow_latest.get() and latest:
                        self._select_by_index(latest["index"])
            except Exception as e:
                print("Polling error:", e)

            # Re-schedule in 1000ms
            self.root.after(1000, self._poll)

        def _render_tree(self):
            if not self.data or not self.data.get("messages"):
                return

            sel = self.tree.selection()
            prev_id = self.tree.item(sel[0], "values")[0] if sel else None

            self.tree.delete(*self.tree.get_children())

            agent_filter = self.filter_agent.get()
            actions_only = self.filter_actions_only.get()
            q = self.search_text.get().lower().strip()

            messages = self.data["messages"]
            for m in reversed(messages):
                # Apply filter
                if agent_filter != "ALL" and m["sender_norm"] != agent_filter and agent_filter not in m["recipient_norm"]:
                    continue
                if actions_only and not m["has_actions"]:
                    continue
                if q and (q not in m["id"].lower() and q not in m["sender"].lower() and q not in m["recipient"].lower() and q not in m["body"].lower()):
                    continue

                act_targets = []
                for tgt in ["Codex", "Antigravity", "Claude", "Owner"]:
                    if tgt in m.get("actions", {}):
                        act_targets.append(tgt)
                act_str = ", ".join(act_targets) if act_targets else "-"

                from_to = f"{m['sender']} ➔ {m['recipient']}"
                if len(from_to) > 34:
                    from_to = from_to[:32] + "..."

                item_id = self.tree.insert("", tk.END, values=(m["id"], from_to, m["timestamp"], act_str), tags=("latest",) if m["is_last"] else ())

                if prev_id and m["id"] == prev_id:
                    self.tree.selection_set(item_id)

            self.tree.tag_configure("latest", foreground="#f59e0b")

        def _select_by_index(self, idx):
            for item in self.tree.get_children():
                val = self.tree.item(item, "values")
                if val:
                    msg = next((m for m in self.data["messages"] if m["id"] == val[0]), None)
                    if msg and msg["index"] == idx:
                        self.tree.selection_set(item)
                        self.tree.see(item)
                        self._display_message(msg)
                        break

        def _on_select_message(self, event):
            sel = self.tree.selection()
            if not sel:
                return
            msg_id = self.tree.item(sel[0], "values")[0]
            msg = next((m for m in self.data["messages"] if m["id"] == msg_id), None)
            if msg:
                self._display_message(msg)

        def _display_message(self, msg):
            self.lbl_det_id.config(text=f"[{msg['id']}]")
            self.lbl_det_route.config(text=f"{msg['sender']} ➔ {msg['recipient']}")
            self.lbl_det_time.config(text=msg["timestamp"] or "No timestamp")

            # Action Points Alert
            acts = msg.get("actions", {})
            if acts:
                self.card_actions.pack(fill=tk.X, side=tk.TOP, pady=(0, 6))
                act_lines = []
                for tgt, items in acts.items():
                    act_lines.append(f"• {tgt}: {items[0]}")
                self.lbl_act_content.config(text="\n".join(act_lines))
            else:
                self.card_actions.pack_forget()

            # Body
            self.txt_body.delete("1.0", tk.END)
            self.txt_body.insert(tk.END, msg["body"])

    app = MailboxTkinterApp(root)
    root.mainloop()


# ==============================================================================
# 4. MAIN ENTRYPOINT
# ==============================================================================

def main():
    import argparse
    parser = argparse.ArgumentParser(description="Real-time Team Mailbox Monitor UI")
    parser.add_argument("--port", type=int, default=DEFAULT_PORT, help="Port for local web dashboard")
    parser.add_argument("--web-only", action="store_true", help="Run only the local web server without desktop GUI")
    args = parser.parse_args()

    # Always spin up the background HTTP server
    start_web_server(port=args.port)
    print(f"[*] Mailbox Web Server listening on http://localhost:{args.port}")

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
        # Launch Tkinter Desktop App
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
