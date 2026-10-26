@echo off
title One Boss Fight - Team Mailbox Monitor
cd /d "%~dp0.."
python Scripts\MailboxViewer.py
if errorlevel 1 pause
