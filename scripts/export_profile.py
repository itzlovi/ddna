import shutil
import argparse
from pathlib import Path
from core.profile_manager import ProfileManager

def export_profile(user_id: str, output_archive_path: str):
    p_mgr = ProfileManager()
    p_dir = p_mgr.get_profile_path(user_id)
    if not p_dir.exists():
        raise FileNotFoundError(f"Profile for {user_id} does not exist.")
    out = Path(output_archive_path)
    out.parent.mkdir(parents=True, exist_ok=True)
    base_name = str(out.with_suffix(""))
    fmt = "zip"
    shutil.make_archive(base_name, fmt, root_dir=p_dir)

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--user", required=True)
    parser.add_argument("--output", required=True)
    args = parser.parse_args()
    export_profile(args.user, args.output)

if __name__ == "__main__":
    main()
