"""Utility to shrink and snapshot SQLite databases as compressed SQL dumps.

Creates .sql.gz dumps for database.db (legacy) and database2.db (v2) if they
exist in the repository root. Intended to run inside CI before committing so
large binary SQLite files are not stored directly in git history (avoids the
100 MB hard limit and keeps diffs small).

APPENDS snapshots to existing .sql.gz files to maintain complete history.
Each snapshot is prefixed with JSON metadata and terminated with blank lines.
Format: [JSON metadata]\\n[SQL dump]\\n\\n

Restoration from latest snapshot:
  python3 -c "from scripts.prepare_db_snapshots import restore_latest; 
              restore_latest('database.sql.gz', 'database.db')"
  
Or manually extract and skip JSON:
  python3 scripts/prepare_db_snapshots.py --restore database.sql.gz database.db

We do a LIGHT optimization (optional pruning hook, PRAGMA optimize, VACUUM).
Add any domain‑specific row pruning inside prune_db() if desired.
"""
from __future__ import annotations
import gzip, os, sqlite3, subprocess, sys, json, time
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DB_FILES = ["database.db", "database2.db"]

def human(size: int) -> str:
    units = ["B", "KB", "MB", "GB"]
    n = float(size)
    for u in units:
        if n < 1024 or u == units[-1]:
            return f"{n:.2f}{u}"
        n /= 1024
    return f"{size}B"

def prune_db(db_path: Path) -> None:
    """Hook to optionally prune old / unnecessary rows to cap growth.
    Currently a no‑op. Example (keep last 30 days of pricesV2):
        cur.execute("DELETE FROM pricesV2 WHERE timestamp < strftime('%s','now') - 30*86400")
    """
    pass

def optimize_and_dump(db_path: Path):
    """Optimize database and create/append SQL dump to .sql.gz file.
    
    Appends the dump to existing .sql.gz file with metadata separator.
    Format: [JSON metadata]\\n[SQL dump]\\n\\n
    """
    if not db_path.exists():
        return None
    dump_path = db_path.with_suffix(".sql.gz")
    try:
        con = sqlite3.connect(str(db_path))
        cur = con.cursor()
        prune_db(db_path)
        try:
            cur.execute("PRAGMA optimize;")
        except Exception:
            pass
        con.commit()
        try:
            temp_file = db_path.with_suffix(".vacuuming")
            cur.execute(f"VACUUM INTO '{temp_file.name}'")
            con.close()
            temp_file.replace(db_path)
            con = sqlite3.connect(str(db_path))
            cur = con.cursor()
        except Exception:
            try:
                cur.execute("VACUUM;")
                con.commit()
            except Exception:
                pass
        con.close()
        
        # Get dump from sqlite3
        dump_bytes = subprocess.check_output(["sqlite3", str(db_path), ".dump"], text=False)
        orig = db_path.stat().st_size
        
        # Create metadata header (JSON on single line for easy parsing)
        metadata = {
            "timestamp": int(time.time()),
            "source": str(db_path),
            "size_before_optimization": orig
        }
        metadata_line = json.dumps(metadata, separators=(',', ':')) + '\n'
        metadata_bytes = metadata_line.encode('utf-8')
        
        # Combine metadata + dump
        combined_bytes = metadata_bytes + dump_bytes + b'\n\n'
        
        # Append to existing .sql.gz or create new
        try:
            with gzip.GzipFile(filename=str(dump_path), mode="ab", compresslevel=9, mtime=0) as gz:
                gz.write(combined_bytes)
        except TypeError:
            # Fallback without mtime for older interpreters
            with gzip.GzipFile(filename=str(dump_path), mode="ab", compresslevel=9) as gz:
                gz.write(combined_bytes)
        
        comp = dump_path.stat().st_size
        ratio = (1 - comp / orig) * 100 if orig else 0
        action = "Updated" if comp > len(combined_bytes) else "Created"
        print(f"{action} {dump_path.name}: {human(orig)} original -> {human(comp)} total (latest {ratio:.1f}% smaller)")
        return dump_path
    except subprocess.CalledProcessError as e:
        print(f"Error dumping {db_path}: {e}", file=sys.stderr)
    except Exception as e:
        print(f"Unexpected error processing {db_path}: {e}", file=sys.stderr)
    return None

def restore_latest(gz_path: str | Path, db_path: str | Path) -> bool:
    """Extract the latest SQL snapshot from a .sql.gz file and restore to database.
    
    Handles both appended snapshots with JSON metadata and plain SQL dumps.
    Returns True if successful, False otherwise.
    """
    gz_path = Path(gz_path)
    db_path = Path(db_path)
    
    if not gz_path.exists():
        print(f"Error: {gz_path} not found", file=sys.stderr)
        return False
    
    try:
        with gzip.open(gz_path, 'rt') as f:
            content = f.read()
        
        lines = content.split('\n')
        
        # Find all JSON metadata lines (they start with '{')
        json_line_indices = []
        for i, line in enumerate(lines):
            if line.strip().startswith('{'):
                json_line_indices.append(i)
        
        if json_line_indices:
            # File has appended snapshots with metadata
            # Extract SQL from the last snapshot (after the last JSON line)
            last_json_idx = json_line_indices[-1]
            sql_lines = lines[last_json_idx + 1:]
            sql_dump = '\n'.join(sql_lines)
        else:
            # Plain SQL format (no metadata)
            sql_dump = content
        
        # Restore to database
        con = sqlite3.connect(str(db_path))
        con.executescript(sql_dump)
        con.close()
        
        print(f"✓ Restored {db_path.name} from {gz_path.name}")
        return True
        
    except Exception as e:
        print(f"Error restoring {db_path}: {e}", file=sys.stderr)
        return False

def main() -> int:
    # Check for restore command
    if len(sys.argv) > 1:
        if sys.argv[1] == "--restore" and len(sys.argv) == 4:
            gz_path = sys.argv[2]
            db_path = sys.argv[3]
            success = restore_latest(gz_path, db_path)
            return 0 if success else 1
        elif sys.argv[1] in ["-h", "--help"]:
            print(f"Usage: {sys.argv[0]} [--restore <gz_file> <db_file>]")
            print("  Create snapshots for all databases in ROOT directory")
            print("  --restore: Restore database from latest snapshot in .sql.gz")
            return 0
    
    produced = []
    for name in DB_FILES:
        p = ROOT / name
        out = optimize_and_dump(p)
        if out:
            produced.append(out)
    if not produced:
        print("No databases found to snapshot.")
        return 0
    # Keep raw DB files for the next run; snapshots are appended to .sql.gz
    print(f"Successfully created/updated {len(produced)} snapshot(s).")
    print("Raw DB files retained for next run (snapshots append to .sql.gz files).")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
