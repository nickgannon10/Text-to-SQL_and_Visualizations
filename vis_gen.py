import logging, os 
import autogen
from IPython import get_ipython
from typing_extensions import Annotated, Dict, Any
from IPython.terminal.interactiveshell import TerminalInteractiveShell
from contextlib import contextmanager
import logging

from src.config import Config, load_config
from src.file_operations import read_file
from src.plt_encoding import encode_seaborn_plot_to_base64


@contextmanager
def ipython_context(**kwargs):
    ipython = get_ipython()
    if ipython is None:
        ipython = TerminalInteractiveShell.instance()

    original_values = {k: ipython.user_ns.get(k, None) for k in kwargs.keys()}
    ipython.push(kwargs)  # Injecting the variables and functions into the IPython environment
    try:
        yield
    finally:
        # Restore the original values to clean up
        for key, value in original_values.items():
            if value is None:
                ipython.user_ns.pop(key, None)
            else:
                ipython.user_ns[key] = value


logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class VisualizationGenerator: 
    def __init__(self, config_path, pandas_df, csv_string, user_input):
        try:     

            self.config = load_config(os.path.join(os.path.dirname(__file__), config_path))
            self.configure_openai_api = Config()
            self.autogen_config_list = self.configure_openai_api.autogen_load_environment_variables()
            self.pandas_df = pandas_df
            self.csv_string = csv_string
            self.user_input = user_input
            self.llm_config = {"config_list": self.autogen_config_list, "timeout": 120, "cache_seed": None}
            os.environ['AUTOGEN_USE_DOCKER'] = "False"

            self.cell_contents = []
            self.error_logs = []

            logging.info("VisualizationGenerator initialized successfully.")
        except Exception as e:
            logging.error("Error initializing VisualizationGenerator: %s", e)
            raise

    def generate_visualization(self):
        try: 
            logging.info("Generating visualization...")
            initial_prompt = read_file(self.config['groupchat_3']['InitialPrompt'])
            data_scientist_system = read_file(self.config['groupchat_3']['DataScientistSystem'])
            iterative_output = read_file(self.config['groupchat_3']['IterativeOutput'])


            user_vis_input = f"Generate a visualization to supplement the answer of {self.user_input}"
            initial_prompt = initial_prompt.format(
                USER_INPUT=user_vis_input,
                PANDAS_DF_STRING=self.csv_string
            )


            data_scientist = autogen.AssistantAgent(
                name="data_scientist",
                system_message=data_scientist_system,
                llm_config=self.llm_config
            )

            user_proxy = autogen.UserProxyAgent(
                name="user_proxy",
                is_termination_msg=lambda x: x.get("content", "") and x.get("content", "").rstrip().endswith("TERMINATE"),
                human_input_mode="NEVER",
                max_consecutive_auto_reply=10,
                code_execution_config={
                    "work_dir": "",
                    "use_docker": False,
                }, 
            )

            @user_proxy.register_for_execution()
            @data_scientist.register_for_llm(name="python", description="run cell in ipython and return the execution result.")
            def exec_python(cell: Annotated[str, "Valid Python cell to execute."]) -> str:
                self.cell_contents.append(cell)
                ipython = get_ipython()
                if ipython is None:
                    ipython = TerminalInteractiveShell.instance()
                
                result = ipython.run_cell(cell)
                    # Initialize an empty string to log potential errors.
                error_log = ""
                
                if result.error_before_exec is not None:
                    error_log += f"Error before execution: {result.error_before_exec}\n"
                
                if result.error_in_exec is not None:
                    error_log += f"Error during execution: {result.error_in_exec}\n"
                    
                # Only append to the error logs if there was an error.
                if error_log:
                    self.error_logs.append(error_log)

                log = str(result.result) if result.result is not None else "No result"
                return log + "\n" + error_log                    


            @user_proxy.register_for_execution()
            @data_scientist.register_for_llm(name="sh", description="run a shell script and return the execution result.")
            def exec_sh(script: Annotated[str, "Valid Python cell to execute."]) -> str:
                return user_proxy.execute_code_blocks([("sh", script)])
            
            logging.info("Python Kernel Initializing ...")


            with ipython_context(pandas_df=self.pandas_df, encode_seaborn_plot_to_base64=encode_seaborn_plot_to_base64):
                user_proxy.initiate_chat(data_scientist, message=initial_prompt)

            last_element = ""

            if len(self.cell_contents) > 0:
                last_element = self.cell_contents[-1]

            if len(self.error_logs) > 0:
                last_error = self.error_logs[-1]


            ipython = get_ipython()
            if ipython is None:
                ipython = TerminalInteractiveShell.instance()

            encoded_image = ipython.user_ns.get('encoded_image', None)

            if len(self.error_logs) > 0 and len(self.error_logs) > 0:
                iterative_output = iterative_output.format(
                    ERROR = last_error, 
                    CELL_CONTENTS = last_element
                )

    
            if encoded_image is None:
                logging.warning("encoded_image not found in IPython namespace. Defaulting to a placeholder or alternative processing.")
                encoded_image = 'default_placeholder_or_error_message'
            logging.info("Visualization generated successfully.")

        except Exception as e:
            logging.error(f"An error occurred during visualization generation: {e}")
            encoded_image = 'error_state_placeholder'
            
        finally:
            logging.info("Visualization process completed, with or without successful image generation.")

        return encoded_image, iterative_output

