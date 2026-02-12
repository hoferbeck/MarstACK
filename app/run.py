import json
import os
import sys
import logging

# Configure logging for the startup script
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("startup")

OPTIONS_FILE = os.environ.get("HASSIO_OPTIONS_FILE", "/data/options.json")

def read_options():
    try:
        if os.path.exists(OPTIONS_FILE):
            logger.info(f"Reading options from {OPTIONS_FILE}")
            with open(OPTIONS_FILE, "r") as f:
                return json.load(f)
        else:
            logger.warning(f"Options file {OPTIONS_FILE} not found. Using environment variables or defaults.")
            return {}
    except Exception as e:
        logger.error(f"Failed to read options file: {e}")
        return {}

def main():
    options = read_options()

    # Map options to environment variables
    # Priority: Options file > Existing Env Var > Default
    
    log_level = options.get("log_level", os.environ.get("LOG_LEVEL", "info"))
    os.environ["LOG_LEVEL"] = log_level
    
    timezone = options.get("timezone", os.environ.get("APP_TIMEZONE", "UTC"))
    os.environ["APP_TIMEZONE"] = timezone
    os.environ["TZ"] = timezone
    
    # FORWARDED_ALLOW_IPS can be a comma separated string in options
    forwarded_ips = options.get("forwarded_allow_ips", os.environ.get("FORWARDED_ALLOW_IPS", ""))
    if forwarded_ips:
        os.environ["FORWARDED_ALLOW_IPS"] = forwarded_ips

    logger.info(f"Starting application with LOG_LEVEL={log_level}, TIMEZONE={timezone}")

    # Prepare command
    # We use su-exec to drop privileges to 'mack' user
    # The command mirrors the original CMD in Dockerfile but we need to ensure paths are correct
    # Original: uvicorn main:app --log-level ${LOG_LEVEL} --log-config /code/logging_config.yaml --host 0.0.0.0 --port 8000
    
    cmd = [
        "su-exec", "mack:mack",
        "uvicorn", "main:app",
        "--log-level", log_level,
        "--log-config", "/code/logging_config.yaml",
        "--host", "0.0.0.0",
        "--port", "8000"
    ]
    
    if forwarded_ips:
        cmd.extend(["--forwarded-allow-ips", forwarded_ips])

    # Replace current process with uvicorn
    # process replacement is important for signal handling
    try:
        os.execvp("su-exec", cmd)
    except OSError as e:
        logger.error(f"Failed to execute command: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
