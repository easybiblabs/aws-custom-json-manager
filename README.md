# AWS Custom-JSON Tool
A tool for managing AWS OpsWorks custom-JSON stack-settings.

Usage:

- Create a file `mystack.json` with the following contents: `{"stack-id": <stack-id>}`, where
  `<stack-id>` stands for the OpsWorksID of the stack.
- Fetch the current custom JSON from OpsWorks with `./sync-tool pull mystack.json`
- Modify the contents of the custom JSON with you favourite editor.
- Push the new custom JSON to OpsWorks with `./sync-tool push mystack.json`
- Providing the -y|--yes option will automatically opt-in to all questions - e.g. if this script
  needs to be run in an automated fashion or without an attached pty.

## Dependencies
See: requirements.txt

To install all dependencies:
```
# pip install -r requirements.txt
```