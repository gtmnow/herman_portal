import subprocess
import sys


def main() -> None:
    subprocess.run([sys.executable, "-m", "alembic", "upgrade", "head"], check=True)
    print("Database migrated to head.")


if __name__ == "__main__":
    main()
