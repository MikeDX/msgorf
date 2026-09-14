#!/usr/bin/env python3
"""Stamp MSGORF_BUILD_ID into web/index.html and cache-bust index.js src."""
import pathlib
import re
import sys


def main() -> None:
    html_path = pathlib.Path(sys.argv[1])
    build_id = sys.argv[2]
    text = html_path.read_text(encoding="utf-8")
    if "MSGORF_BUILD_ID" not in text and f"?v={build_id}" not in text:
        print("warning: MSGORF_BUILD_ID placeholder not found in", html_path, file=sys.stderr)
    text = text.replace("MSGORF_BUILD_ID", build_id)
    text, n = re.subn(
        r'(src=["\']index\.js)(["\'])',
        rf"\1?v={build_id}\2",
        text,
        count=1,
    )
    if n == 0:
        # Already stamped or unusual script tag form
        text, n = re.subn(
            r'(src=["\']index\.js)\?v=[^"\']*(["\'])',
            rf"\1?v={build_id}\2",
            text,
            count=1,
        )
    html_path.write_text(text, encoding="utf-8")
    print(f"stamped build id {build_id} ({n} script src update(s))")


if __name__ == "__main__":
    main()
