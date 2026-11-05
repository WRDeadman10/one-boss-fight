# E165 decision audit: refusal-token and terminal cleanup contract

The D126-D131 references cover move-model refusal precedence, score boundaries/reset, and executor open-window terminal cleanup. They are not one universal token/cleanup contract: refusal names are subsystem-specific, and cleanup obligations are owned by the executor/window lifecycle.

Current documented source behavior is to preserve named refusal reasons and close active windows on terminal cleanup. The audited reports do not establish a cross-subsystem stable-token compatibility guarantee or prove every terminal path in a live authored montage. Do not claim either as a universal API contract.

No policy change is needed for internal diagnostics. Owner approval is required before external consumers depend on token spelling or a broader compatibility guarantee; Lead owns review of any expanded terminal-path proof. Static inspection only; no tests/build/Editor run.
