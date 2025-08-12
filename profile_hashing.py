import sys
from pathlib import Path
import cProfile
import pstats
import io

# Add the backend directory to the Python path
# This allows us to import from 'app' as if we were inside the backend directory
backend_path = Path(__file__).parent / 'backend'
sys.path.insert(0, str(backend_path))

from app.auth.security import get_password_hash

def profile_password_hashing():
    """
    Profiles the get_password_hash function.
    """
    profiler = cProfile.Profile()
    profiler.enable()

    print("Starting profiling...")
    for i in range(100):
        get_password_hash("my-super-secret-password-that-is-long")
    print("Finished profiling.")

    profiler.disable()

    s = io.StringIO()
    sortby = pstats.SortKey.CUMULATIVE
    ps = pstats.Stats(profiler, stream=s).sort_stats(sortby)
    ps.print_stats()
    print(s.getvalue())

if __name__ == "__main__":
    profile_password_hashing()
