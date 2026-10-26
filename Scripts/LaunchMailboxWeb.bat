@echo off
title One Boss Fight - Team Mailbox Web Dashboard
cd /d "%~dp0.."
python Scripts\MailboxViewer.py --web-only
if errorlevel 1 pause
