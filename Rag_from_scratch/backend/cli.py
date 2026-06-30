"""CLI: python cli.py ingest ./docs   |   python cli.py ask "your question"."""
import sys
from dotenv import load_dotenv

load_dotenv()


def main():
    if len(sys.argv) < 3:
        print("usage: python cli.py [ingest <folder> | ask <question>]")
        return
    cmd, arg = sys.argv[1], sys.argv[2]
    if cmd == "ingest":
        import ingest
        print("Ingested", ingest.ingest(arg), "chunks.")
    elif cmd == "ask":
        import answer
        out = answer.ask(arg)
        print(out["answer"])
        print("\nSources:")
        for c in out["citations"]:
            print(" -", c["file_path"] + ":" + str(c["start_line"]) + "-" + str(c["end_line"]))


if __name__ == "__main__":
    main()