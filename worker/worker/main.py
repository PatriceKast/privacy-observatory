import os

import worker

def main():
    print("Started main routine")
    worker.Worker(os.environ['api_host'], os.environ['api_tkn'])

if __name__ == "__main__":
    main()