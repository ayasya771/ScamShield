"""
Check a message from the command line.

    python cli.py "Your parcel is held, pay a 1.99 fee at royal-mail.top/redeliver"

With no message it reads from standard input, so you can also do:

    Get-Content message.txt | python cli.py        (PowerShell)
"""

import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from scamshield import ScamShield

# A coloured risk bar if the terminal supports it; plain text otherwise.
_ICON = {"danger": "[!]", "warning": "[?]", "safe": "[OK]"}


def render(result):
    bar_len = 28
    filled = round(result["risk"] / 100 * bar_len)
    bar = "#" * filled + "-" * (bar_len - filled)

    print()
    print(f'  {_ICON[result["level"]]} {result["verdict"]}   '
          f'(risk {result["risk"]}/100, confidence: {result["confidence"]})')
    print(f'  [{bar}]')
    print()
    print(f'  Message: {result["text"]}')
    print()
    if result["reasons"]:
        print("  Why:")
        for reason in result["reasons"]:
            arrow = "scam ->" if reason["direction"] == "scam" else "genuine ->"
            print(f'     {arrow:<10} {reason["text"]}')
        print()
    print(f'  Advice: {result["advice"]}')
    print()


def main():
    message = " ".join(sys.argv[1:]).strip()
    if not message:
        message = sys.stdin.read().strip()
    if not message:
        print(__doc__)
        return

    shield = ScamShield()
    render(shield.classify(message))


if __name__ == "__main__":
    main()
