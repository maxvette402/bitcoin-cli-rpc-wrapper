- [Context]
	- I'd like to connect to a local bitcoin knots node using a python serverless functions running in my local
- [Task]
	- This is the stack I want:
		- The Bitcoin Node is running and, as you certainly know, exposes RPC functions like "getblockchaininfo"
		- The Python script as to act as a wrapper
			- the original response and/or error is returned to the request, is not manipulated
		- I can invoke it through the terminal using a Single CLI Tool with Subcommands:
			- python3 bitcoin_cli_wrapper.py getblockchaininfo
			- python3 bitcoin_cli_wrapper.py getblock <hash>
			- python3 bitcoin_cli_wrapper.py --help
		- Commands that needs hashing will be hashed with SHA512 or the necessary algorythm
- [Instruction]
	- Core Components:
		- Configuration Management (.env + validation)
		- RPC Client Library (secure connection handling)
		- Command Router (dynamic command execution)
		- CLI Interface (user-friendly command line)
		- Testing Framework (unit + integration tests)
	- Structure:
		- bitcoin_cli_wrapper.py (main entry point)
		- lib/
		  ├── rpc_client.py
		  ├── commands/
		  │   ├── blockchain.py
		  │   ├── wallet.py
		  │   └── network.py
		  ├── config.py
		  └── validators.py
		- tests/
		- .env
		- secrets managements
			- # config.py
				- password = os.getenv('BITCOIN_RPC_PASSWORD') or \
         						read_docker_secret('bitcoin_rpc_password') or \
          						read_env_file('.env')
        - 
	- everything can be configured in a .env file
			- # Connection
				BITCOIN_RPC_HOST=127.0.0.1
				BITCOIN_RPC_PORT=8332
				BITCOIN_RPC_USER=your_user
				BITCOIN_RPC_PASSWORD=your_password
				BITCOIN_RPC_TIMEOUT=30
				BITCOIN_NETWORK=mainnet  # mainnet, testnet, regtest

				# Security
				BITCOIN_RPC_USE_SSL=true
				BITCOIN_RPC_SSL_VERIFY=false  # Self-signed OK for localhost
				BITCOIN_RPC_SSL_CERT_PATH=/certs/localhost.pem

				# Logging
				LOG_LEVEL=INFO
				LOG_FILE=bitcoin_wrapper.log
		- for now I have just localhost but the idea is to use it also for remote connection
			- Authentication: just one host for .env configuration
			- localhost should reflect a real environment so configure https using Let's Encrypt
	- Do not support all bitcoin-cli commands or just a subset:
		- COMMAND_MAP = {
    		'getblockchaininfo': 'getblockchaininfo',
    		'getblockcount': 'getblockcount',
    		'getblock': 'getblock',
    		# ... more mappings
			}
	- Error Handling: depends on the .env properties LOG_LEVEL
	- Output Format: json
- [Clarification]
	- everything must be open source
	- everything must use secure protocols
	- all the code must be covered by:
		- functional tests
		- integration test
		- docker test
	- Deployment:
		- this run in a local Python but I also need a Dockerfile and/or docker-compose with:
			- Environment Variables
			- Volumes also for configurations
			- Networks
			- Init System
			- Health Checks
			- Every piece has its own container
	- Core Design Principles:
		- Separation of Concerns: Each component has a single responsibility
		- Configuration-Driven: Everything configurable via .env
		- Secure by Default: SSL support, credential validation, timeout handling
		- Extensible: Easy to add new commands without touching core logic
		- Container-Ready: Dockerized for consistent deployment
	- Scaling:
		- for now is not necessary as the commands will be invoked manually
	- Remote Security:
		- no tor
		- just the internet public traffic
	- Security
		- put in front of everything a reverse proxy using Caddy
- [Revision]
	- for now do not generate codes, just suggest me the solution
	- I'd like to discuss with you pro and cons oo your proposal
	- a 50 bucks tips is waiting for you at the end of the challenge :)