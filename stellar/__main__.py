from stellar import *
import sys 

# set maximum recursion depth 
sys.setrecursionlimit(64*1024)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python -m table_transformer <path_to_file>")
        sys.exit(1)
    f = open(sys.argv[1], "r")
    run(f.read())