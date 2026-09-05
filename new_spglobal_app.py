import argparse  # noqa: F401
import csv  # noqa: F401
import json  # noqa: F401
import logging
import os  # noqa: F401
import time  # noqa: F401
from datetime import datetime, timedelta  # noqa: F401
from pathlib import Path   # noqa: F401
from typing import TYPE_CHECKING, Any, Dict, List, Union   # noqa: F401
import itertools
import threading
import tempfile

from doyles_sdk.cli.apps._base_app import DoyleApp

try:
    from . import register_cmd
except ImportError:

    def register_cmd(cls):
        return cls

if TYPE_CHECKING:
    logger: logging.Logger  # just for type checkers

# if you need an API session to a Splunk instance
# or any access that requires retry and connection pooling
# uncomment the following lines

from doyles_sdk._wrappers import SplunkSession

_token = "eyJraWQiOiJzcGx1bmsuc2VjcmV0IiwiYWxnIjoiSFM1MTIiLCJ2ZXIiOiJ2MiIsInR0eXAiOiJzdGF0aWMifQ.eyJpc3MiOiJtZG95bGUgZnJvbSBzaC1pLTBjZmI4ZjU2MmEwNWI4ZjQ3Iiwic3ViIjoibWRveWxlIiwiYXVkIjoiY29weSBldmVudHMgZnJvbSBsYXN0Y2hhbmNlaW5kZXMiLCJpZHAiOiJTcGx1bmsiLCJqdGkiOiJhZDQyZGEwYTc1OTc2MjQ3N2RlMzU2MDYzNDEzNzkwNjgyMDA2YzAxNTEyOGIxYzAwN2NmNmM2ZDJmNWRlZGE2IiwiaWF0IjoxNzg3NTg1MTEzLCJleHAiOjE3OTAxNzcxMTMsIm5iciI6MTc4NzU4NTExM30.bySPu5TniTh20tumAzF1dUoOtrwSuNxT22hEPt7N3K-6a_H0sA5WGrTlevUCRyAIx4WnI4x19So7FQsUgo4mFQ"
session = SplunkSession(token=_token, include_post=True)

testmode = "false"

server_list = [
    "sh-i-0084fbe9d072d19bf",
    "sh-i-01c82c9c8849c2059",
    "sh-i-065fe812b39bfa388",
    # "sh-i-089c6e59818c12bc7",
    "sh-i-0cfb8f562a05b8f47"
]

destination_pool = itertools.cycle(server_list)
pool_lock = threading.Lock()

@register_cmd
class NewSpglobalCliApp(DoyleApp):
    """
    Auto-generated CLI scaffold for DoyleApp.

    Provides:
        - argument parsing
        - logging
        - threading and multiprocessing support

    Customize this class by overriding:
        - add_arguments()
        - args_post_process()
        - do_* methods
        - run()

    The following can referenced directly in your methods:

        - __package__
        - __author__
        - __email__
        - __license__
        - __python__
        - __platform__
        - __system__
        - __machine__
        - __release__
        - __mem_total__
        - __mem_avail__
        - __cpu_count__
        - __version__
    """

    command_name = "new_spglobal"
    mp_safe = False       # Allow multiprocessing
    thread_safe = True   # Allow threads


    @classmethod
    def add_arguments(cls, parser):
        """
        # Add your custom CLI arguments here.

        The following arguments are **already defined by the base parser**
        and should NOT be redefined here:

        --help
        --debug
        --verbose
        --log-dir
        --version
        --log-level

        **Example:**
            parser.add_argument("--example", help="Example argument", default="value")
        """
        # parser.add_argument("--no-testmode", help="Use testmode=false", action="save_true")
        pass

    @classmethod
    def args_post_process(cls, parser):
        """
        # Validate or transform parsed args.

        **Example:**
            if parser.my_option and not valid(parser.my_option):
                raise ValueError("Invalid option")
        """
        pass

    @staticmethod
    def do_example_task(arg):
        """
        Example do_* method demonstrating concurrency support.

        logger is automatically injected to all do_* methods

        """
        payload = {
            "output_mode": "json",
            "count": 0,
            "adhoc_search_level": "fast",
            "allow_partial_results": "false",
            "earliest_time": "-4mon@mon",
            "enable_lookups": "false",
            "exec_mode": "oneshot",
            "latest_time": "@mon",
            "reload_macros": "false"}
        # time.sleep(0.5)
        data = arg.get("result")
        if data:
            indexes = data.get("index")
            if not isinstance(indexes, list):
                logger.error("Unknown dest index for event %s", data)
                return {"status_code": None, "result": data, "count": 0, "messages": ["Unknown dest index for event"]}
            else:
                st = data.get("sourcetype")
                s = data.get("source")
                h = data.get("host")

                if isinstance(s, list):
                    sources = "(" + ", ".join([json.dumps(x) for x in s]) + ")"
                    logger.debug(sources)
                else:
                    sources = f'({json.dumps(s)})'

                idx = [x for x in indexes if x != "lastchanceindex"]
                logger.debug(idx[0])

                payload["search"] = f"search index=lastchanceindex (sourcetype={json.dumps(st)} OR _sourcetype={json.dumps(st)}) (source IN {sources} OR _source IN {sources}) host={json.dumps(h)} | fields _time, _raw, sourcetype, source, host | collect testmode={testmode} index={idx[0]} output_format=hec"

                logger.debug(f"Running task with {list(payload.items())}") # noqa: F821

                with pool_lock:
                    url = f"https://{next(destination_pool)}.spglobal.splunkcloud.com:8089/services/search/jobs"

                response = session.post(url, data=payload)
                logger.debug(json.dumps(response.json(), indent=2))
                result = {"status_code": response.status_code, "result": data, "count": len(response.json().get("results", [])), "messages": response.json().get("messages", [])}
                if response.status_code in [200, 201]:
                    if result.get("messages"):
                        logger.warning(result)
                    else:
                     logger.notice(result)
                else:
                    logger.error(result)

                return result

                # if response.status_code in [200, 201]:
                #     result = {"status_code": response.status_code, "result": data, "count": len(response.json().get("results"))}
                #     return result
                # else:
                #     result = {"status_code": response.status_code, "message": response.json().get("messages"), "arg": arg}
                #     logger.error(result)
                #     return result


    def reprocess(self, result: dict) -> list[tuple[callable, object]]:
        """Retries failed attempts by adding returning the tuple of failed attempts"""

        if result.status_code in [200, 201]:
            return []
        else:
            return([(self.do_example_task, result)])

    def run(self):
        """
        # Main application logic.
        Prefer delegating to do_* methods for consitent behavior using any execution method.

        The following are available:

            - self.logger
            - self.args
        """
        # open the jsonl file and dispatch to the workers
        if testmode == "true":
            self._results_file_path = "./testmode_new_results.jsonl"
        elif testmode == "false":
            self._results_file_path = "./new_results.jsonl"
        else:
            raise SystemExit(f"Invalid value for testmode={testmode}")

        src_list = list()
        done_set = set()
        args_list = list()

        src_file = "updated_missing.jsonl"
        target_dir = os.path.dirname(os.path.abspath(src_file))

        # 1. Read source data
        with open(src_file, "r") as f:
            for line in f:
                stripped = line.strip()
                if stripped:
                    src_list.append(json.loads(stripped))

        # 2. Build the set using standardized JSON strings
        try:
            with open(self._results_file_path, "r") as f:
                for line in f:
                    stripped = line.strip()
                    if stripped:
                        x = json.loads(stripped)
                        if x is not None:
                            # sort_keys=True guarantees identical dicts/lists stringify exactly the same
                            hashable_str = json.dumps(x["result"], sort_keys=True)
                            done_set.add(hashable_str)
        except FileNotFoundError:
            pass

        # 3. Blazing fast lookup loop
        for item in src_list:
            item_str = json.dumps(item["result"], sort_keys=True)
            if item_str not in done_set:
                args_list.append(item)
            else:
                self.logger.warning("Skipping previously processed %s", item)

        with tempfile.NamedTemporaryFile("w", dir=target_dir, delete=False, suffix=".tmp") as tf:
            temp_path = tf.name
            try:
                # 3. Stream data into the temporary file line-by-line (for JSONL)
                for item in args_list:
                    # Intentionally simulate an error here if you want to test safety:
                    # if "trigger" in item: raise ValueError("Simulated crash!")
                    
                    tf.write(json.dumps(item) + "\n")
                
                # Flush internal buffers to disk before closing
                tf.flush()
                os.fsync(tf.fileno()) 
                
            except Exception as e:
                # 4. If anything goes wrong, clean up the temp file and re-raise the error
                tf.close()
                os.remove(temp_path)
                print(f"Error occurred! Original file is untouched. Details: {e}")
                raise e

        # 5. Success! Atomically replace the old file with the new complete file
        # This operation is instantaneous and safe from interruptions
        os.replace(temp_path, src_file)

        # args_list = [self.args.example] if isinstance(self.args.example, str) else self.args.example
        results = self.run_with_workers(self.do_example_task, args_list, max_workers=25, result_func=self.log_result)

        with open(self._results_file_path.replace("jsonl", "json"), "w") as f:
            f.write(json.dumps(results, indent=2))


# The following is required boilerplate
# DO NOT MODIFY
def cli():
    app = NewSpglobalCliApp()
    try:
        app.run()
    finally:
        app.shutdown_logging()

if __name__ == "__main__":
    import sys
    sys.exit(cli())
