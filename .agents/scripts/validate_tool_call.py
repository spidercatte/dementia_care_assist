import sys
import json

def main():
    try:
        # Read the hook event data from stdin
        if not sys.stdin.isatty():
            event_data = json.load(sys.stdin)
        else:
            event_data = {}

        # Simple logging of the validated command
        print(f"[Agent Hook] Validating tool call: {event_data.get('tool_name', 'unknown')}", file=sys.stderr)

        # Allow the execution by exiting with 0
        sys.exit(0)
    except Exception as e:
        print(f"[Agent Hook] Validation error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == "__main__":
    main()
