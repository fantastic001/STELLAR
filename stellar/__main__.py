from stellar import *
import sys 

# set maximum recursion depth 
def main():
    sys.setrecursionlimit(64*1024)
    if len(sys.argv) < 2:
        print("Usage: python -m stellar <path_to_file>")
        sys.exit(1)
    f = open(sys.argv[1], "r")
    run(f.read())
if __name__ == "__main__":
    main()
    