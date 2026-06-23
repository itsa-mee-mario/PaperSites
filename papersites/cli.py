"""Command-line interface: `papersites build` / `papersites serve`."""

import argparse
import functools
import http.server
import sys

from .builder import build_site


def main() -> None:
    parser = argparse.ArgumentParser(prog="papersites", description="A small Markdown -> HTML static site generator.")
    sub = parser.add_subparsers(dest="command", required=True)

    build = sub.add_parser("build", help="Build content/ into a static site")
    build.add_argument("--content", default="content", help="Source markdown directory (default: content)")
    build.add_argument("--out", default="site", help="Output directory (default: site)")
    build.add_argument("--config", default=None, help="Path to site.json (default: <content>/site.json)")

    serve = sub.add_parser("serve", help="Serve a built site locally")
    serve.add_argument("--dir", default="site", help="Directory to serve (default: site)")
    serve.add_argument("--port", type=int, default=8000)

    args = parser.parse_args()

    if args.command == "build":
        try:
            written = build_site(args.content, args.out, args.config)
        except FileNotFoundError as e:
            print(f"papersites: error: {e}", file=sys.stderr)
            raise SystemExit(1)
        for path in written:
            print(f"  {path}")
        print(f"Built {len(written)} page(s) into {args.out}/")

    elif args.command == "serve":
        handler = functools.partial(http.server.SimpleHTTPRequestHandler, directory=args.dir)
        with http.server.HTTPServer(("", args.port), handler) as httpd:
            print(f"Serving {args.dir}/ at http://localhost:{args.port}  (Ctrl+C to stop)")
            try:
                httpd.serve_forever()
            except KeyboardInterrupt:
                pass


if __name__ == "__main__":
    main()
