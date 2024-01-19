import requests
from os import environ
import logging
import subprocess
import traceback

logging.basicConfig(level="INFO")
logger = logging.getLogger(__name__)

rollup_server = environ["ROLLUP_HTTP_SERVER_URL"]
logger.info(f"HTTP rollup_server url is {rollup_server}")

def hex2str(hex):
    """
    Decodes a hex string into a regular string
    """
    return bytes.fromhex(hex[2:]).decode("utf-8")

def str2hex(str):
    """
    Encodes a string as a hex string
    """
    return "0x" + str.encode("utf-8").hex()


# function to run the command on the terminal as stated on the readme of the module
def run_inference(image_path, height):
    result = subprocess.run(["python3", "inference.py", "-i", image_path, "-ht", str(height)], stdout=subprocess.PIPE, universal_newlines=True)
    return result.stdout

def handle_advance(data):
    logger.info(f"Received advance request data {data}")

    status = "accept"

    try:
        input = hex2str(data["payload"])
        # logs out input
        logger.info(f"Received input: {input}")
        parts = input.split(" ")

        image_path = parts[0]
        height = int(parts[1])
        logger.info(f"Image path: {image_path}")
        logger.info(f"Height: {height}")
        output = run_inference(image_path, height)
        logger.info(f"Output: {output}")
        # logs input again
        logger.info(f"Adding notice with payload: '{input}'")
        response = requests.post(rollup_server + "/notice", json={"payload": output})
        logger.info(f"Received notice status {response.status_code} body {response.content}")

    except Exception as e:
        status = "reject"
        msg = f"Error processing data {data}\n{traceback.format_exc()}"
        logger.error(msg)
        response = requests.post(rollup_server + "/report", json={"payload": str2hex(msg)})
        logger.info(f"Received report status {response.status_code} body {response.content}")

    return status
    # return "accept"


def handle_inspect(data):
    logger.info(f"Received inspect request data {data}")
    return "accept"


handlers = {
    "advance_state": handle_advance,
    "inspect_state": handle_inspect,
}

finish = {"status": "accept"}

while True:
    logger.info("Sending finish")
    response = requests.post(rollup_server + "/finish", json=finish)
    logger.info(f"Received finish status {response.status_code}")
    if response.status_code == 202:
        logger.info("No pending rollup request, trying again")
    else:
        rollup_request = response.json()
        data = rollup_request["data"]
        handler = handlers[rollup_request["request_type"]]
        finish["status"] = handler(rollup_request["data"])
