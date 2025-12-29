from stellar import *
from stellar.server import server
import sys 
from orgasm import command_executor_main

class Commands:
    def run(self, path: str):
        with open(path, "r") as f:
            run(f.read())
    def lsp_tcp(self, port: int, *, host: str = "127.0.0.1"):
        server.start_tcp(host, port)
    
    def lsp_stdio(self):
        server.start_io()

# set maximum recursion depth 
def main():
    sys.setrecursionlimit(64*1024)
    command_executor_main(Commands, explicit_params=False)
if __name__ == "__main__":
    main()
    