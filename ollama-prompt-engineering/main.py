"""
============================================================
PROMPT ENGINEERING AND MULTI-MODEL INFERENCE USING OLLAMA
============================================================

Student: Eilene Anna Kuriakose

Models used:

1. LLM - Large Language Model
   Model: Llama 3.2
   Tasks:
   - Zero-shot prompting
   - One-shot prompting
   - Few-shot prompting
   - Chain-of-thought prompting
   - Text summarization
   - Question answering

2. SLM - Small Language Model
   Model: Qwen2.5 0.5B
   Tasks:
   - Next-text generation
   - Short-text summarization

3. VLM - Vision-Language Model
   Model: Moondream
   Task:
   - Image understanding

The program also:

- Lists locally installed Ollama models
- Calls actual models using Ollama
- Runs inference
- Measures inference time
- Saves results as JSON
- Saves results as TXT
============================================================
"""


# ============================================================
# IMPORTS
# ============================================================

from datetime import datetime
from pathlib import Path

import json
import time

from ollama import chat
from ollama import list as ollama_list


# ============================================================
# MODEL CONFIGURATION
# ============================================================

LLM_MODEL = "llama3.2"

SLM_MODEL = "qwen2.5:0.5b"

VLM_MODEL = "moondream"


# ============================================================
# FILE CONFIGURATION
# ============================================================

PROJECT_FOLDER = Path(__file__).resolve().parent
INPUT_IMAGE = PROJECT_FOLDER / "test_image.jpg"

RESULTS_FOLDER = PROJECT_FOLDER / "results"

JSON_FILE = RESULTS_FOLDER / "model_results.json"

TEXT_FILE = RESULTS_FOLDER / "model_results.txt"


# ============================================================
# STORE ALL RESULTS
# ============================================================

all_results = []


# ============================================================
# DISPLAY FUNCTION
# ============================================================

def print_header(title):

    print("\n" + "=" * 75)

    print(title.center(75))

    print("=" * 75)


# ============================================================
# GET RESPONSE CONTENT
# ============================================================

def get_response_content(response):

    """
    Extracts the generated text from
    an Ollama response.
    """

    if hasattr(response, "message"):

        message = response.message

        if hasattr(message, "content"):

            return message.content


    return response["message"]["content"]


# ============================================================
# LIST INSTALLED OLLAMA MODELS
# ============================================================

def list_installed_models():

    print_header(
        "INSTALLED OLLAMA MODELS"
    )


    try:

        response = ollama_list()


        if hasattr(
            response,
            "models"
        ):

            models = response.models

        else:

            models = response.get(
                "models",
                []
            )


        if not models:

            print(
                "No locally installed "
                "Ollama models were found."
            )

            return


        print(
            "Models available locally:"
        )


        for model in models:

            if hasattr(
                model,
                "model"
            ):

                model_name = model.model


            elif isinstance(
                model,
                dict
            ):

                model_name = model.get(

                    "model",

                    model.get(
                        "name",
                        "Unknown"
                    )

                )


            else:

                model_name = str(
                    model
                )


            print(
                f"- {model_name}"
            )


    except Exception as error:

        print(
            "Unable to list "
            "Ollama models."
        )

        print(
            f"Reason: {error}"
        )


# ============================================================
# GENERAL TEXT-MODEL INFERENCE FUNCTION
# ============================================================

def call_text_model(

    task_name,

    model_name,

    model_type,

    prompt,

    temperature=0.7,

    max_tokens=512

):

    """
    Calls an Ollama text model.

    The function:

    1. Sends a prompt
    2. Runs model inference
    3. Displays the response
    4. Measures inference time
    5. Stores the result
    """


    print_header(
        task_name
    )


    print(
        f"Model type: {model_type}"
    )

    print(
        f"Model: {model_name}"
    )

    print(
        f"Temperature: {temperature}"
    )

    print(
        "Maximum output tokens: "
        f"{max_tokens}"
    )


    print(
        "\nPROMPT:\n"
    )

    print(
        prompt.strip()
    )


    start_time = time.perf_counter()


    try:

        response = chat(

            model=model_name,

            messages=[

                {

                    "role": "user",

                    "content": prompt

                }

            ],

            options={

                "temperature":
                    temperature,

                "num_predict":
                    max_tokens

            }

        )


        answer = get_response_content(
            response
        )


        status = "Success"


    except Exception as error:

        answer = (

            "Model inference failed: "

            f"{type(error).__name__}: "

            f"{error}"

        )


        status = "Failed"


    inference_time = (

        time.perf_counter()

        - start_time

    )


    print(
        "\nMODEL RESPONSE:\n"
    )

    print(
        answer
    )


    print(

        "\nInference time: "

        f"{inference_time:.2f} seconds"

    )


    result = {

        "task":
            task_name,

        "model_type":
            model_type,

        "model":
            model_name,

        "prompt":
            prompt.strip(),

        "response":
            answer,

        "temperature":
            temperature,

        "maximum_output_tokens":
            max_tokens,

        "inference_time_seconds":
            round(
                inference_time,
                2
            ),

        "status":
            status,

        "timestamp":
            datetime.now().isoformat(

                timespec="seconds"

            )

    }


    all_results.append(
        result
    )


    return answer


# ============================================================
# 1. ZERO-SHOT PROMPTING
# ============================================================

def zero_shot_prompting():

    """
    Zero-shot prompting:

    The model performs the task
    without receiving any examples.
    """


    prompt = """

Classify the sentiment of the following
sentence as Positive, Negative, or Neutral.

Sentence:

I really enjoy learning about
artificial intelligence.

Return only the sentiment label.

"""


    call_text_model(

        task_name=
            "1. ZERO-SHOT PROMPTING",

        model_name=
            LLM_MODEL,

        model_type=
            "LLM - Large Language Model",

        prompt=
            prompt

    )


# ============================================================
# 2. ONE-SHOT PROMPTING
# ============================================================

def one_shot_prompting():

    """
    One-shot prompting:

    The model receives one example
    before performing a new task.
    """


    prompt = """

Classify the sentiment by following
the example.


EXAMPLE:

Input:

The food was amazing.

Output:

Positive


NOW CLASSIFY:

Input:

The movie was disappointing.

Output:

"""


    call_text_model(

        task_name=
            "2. ONE-SHOT PROMPTING",

        model_name=
            LLM_MODEL,

        model_type=
            "LLM - Large Language Model",

        prompt=
            prompt

    )


# ============================================================
# 3. FEW-SHOT PROMPTING
# ============================================================

def few_shot_prompting():

    """
    Few-shot prompting:

    The model receives multiple examples
    before performing a new task.
    """


    prompt = """

Classify the sentiment by following
the examples.


EXAMPLE 1:

Input:

The weather is wonderful.

Output:

Positive


EXAMPLE 2:

Input:

The service was terrible.

Output:

Negative


EXAMPLE 3:

Input:

The parcel arrived on Monday.

Output:

Neutral


NOW CLASSIFY:

Input:

This phone has an excellent camera.

Output:

"""


    call_text_model(

        task_name=
            "3. FEW-SHOT PROMPTING",

        model_name=
            LLM_MODEL,

        model_type=
            "LLM - Large Language Model",

        prompt=
            prompt

    )


# ============================================================
# 4. CHAIN-OF-THOUGHT PROMPTING
# ============================================================

def chain_of_thought_prompting():

    """
    Chain-of-thought prompting:

    The model solves a reasoning problem
    using important calculation steps.
    """


    prompt = """

Solve the following problem carefully.

Show the important calculation steps
and provide the final answer.

A bat and a ball cost $1.10 in total.

The bat costs $1 more than the ball.

How much does the ball cost?

"""


    call_text_model(

        task_name=
            "4. CHAIN-OF-THOUGHT PROMPTING",

        model_name=
            LLM_MODEL,

        model_type=
            "LLM - Large Language Model",

        prompt=
            prompt

    )


# ============================================================
# 5. LLM - TEXT SUMMARIZATION
# ============================================================

def llm_text_summarization():

    """
    Model category:

    LLM - Large Language Model

    Actual model:

    Llama 3.2

    Task:

    Text summarization
    """


    passage = """

Artificial intelligence is transforming
healthcare by helping doctors analyze
medical images, identify diseases earlier,
and create personalized treatment plans.

AI systems can process large amounts of
medical information quickly and may reduce
the workload of healthcare professionals.

However, healthcare organizations must
also consider patient privacy, data
security, algorithmic fairness, and the
importance of human supervision.

"""


    prompt = f"""

Summarize the following passage
in exactly two sentences.

PASSAGE:

{passage}

SUMMARY:

"""


    call_text_model(

        task_name=
            "5. LLM - TEXT SUMMARIZATION",

        model_name=
            LLM_MODEL,

        model_type=
            "LLM - Large Language Model",

        prompt=
            prompt,

        temperature=
            0.5,

        max_tokens=
            200

    )


# ============================================================
# 6. LLM - QUESTION ANSWERING
# ============================================================

def llm_question_answering():

    """
    LLM task:

    Question answering
    """


    prompt = """

Answer the following question
clearly in three sentences.

What is the difference between
artificial intelligence
and machine learning?

"""


    call_text_model(

        task_name=
            "6. LLM - QUESTION ANSWERING",

        model_name=
            LLM_MODEL,

        model_type=
            "LLM - Large Language Model",

        prompt=
            prompt,

        temperature=
            0.5,

        max_tokens=
            200

    )


# ============================================================
# 7. SLM - NEXT-TEXT GENERATION
# ============================================================

def slm_next_text_generation():

    """
    Model category:

    SLM - Small Language Model

    Actual model:

    Qwen2.5 0.5B

    Task:

    Next-text generation
    """


    prompt = """

Complete the following sentence naturally.

Return only one completed sentence.

In the future,
artificial intelligence will

"""


    call_text_model(

        task_name=
            "7. SLM - NEXT-TEXT GENERATION",

        model_name=
            SLM_MODEL,

        model_type=
            "SLM - Small Language Model",

        prompt=
            prompt,

        temperature=
            0.7,

        max_tokens=
            100

    )


# ============================================================
# 8. SLM - SHORT-TEXT SUMMARIZATION
# ============================================================

def slm_short_text_summarization():

    """
    SLM task:

    Short-text summarization
    """


    prompt = """

Summarize the following text
in one sentence.

Machine learning allows computer systems
to identify patterns in data and improve
their performance without being explicitly
programmed for every possible situation.

Return only the summary.

"""


    call_text_model(

        task_name=
            "8. SLM - SHORT-TEXT SUMMARIZATION",

        model_name=
            SLM_MODEL,

        model_type=
            "SLM - Small Language Model",

        prompt=
            prompt,

        temperature=
            0.4,

        max_tokens=
            100

    )


# ============================================================
# 9. VLM - IMAGE UNDERSTANDING
# ============================================================

def vlm_image_understanding():

    """
    Model category:

    VLM - Vision-Language Model

    Actual model:

    Moondream

    Task:

    Image understanding

    Input:

    input_image.jpg

    Output:

    Natural-language image description
    """


    task_name = (

        "9. VLM - IMAGE UNDERSTANDING"

    )


    model_type = (

        "VLM - Vision-Language Model"

    )


    prompt = (

        "Describe the main subject and "

        "important visible details in this image. "

        "Answer in three clear sentences."

    )


    print_header(
        task_name
    )


    print(
        f"Model type: {model_type}"
    )

    print(
        f"Model: {VLM_MODEL}"
    )

    print(
        f"Input image: {INPUT_IMAGE.name}"
    )


    print(
        "\nPROMPT:\n"
    )

    print(
        prompt
    )


    if not INPUT_IMAGE.exists():

        answer = (

            "VLM inference was skipped because "

            "'input_image.jpg' was not found."

        )


        print(
            "\nMODEL RESPONSE:\n"
        )

        print(
            answer
        )


        all_results.append(

            {

                "task":
                    task_name,

                "model_type":
                    model_type,

                "model":
                    VLM_MODEL,

                "input_image":
                    str(INPUT_IMAGE),

                "prompt":
                    prompt,

                "response":
                    answer,

                "status":
                    "Skipped - image missing",

                "timestamp":
                    datetime.now().isoformat(

                        timespec="seconds"

                    )

            }

        )


        return answer


    start_time = time.perf_counter()


    try:

        print(
            "\nRunning VLM inference..."
        )


        response = chat(

            model=
                VLM_MODEL,

            messages=[

                {

                    "role":
                        "user",

                    "content":
                        prompt,

                    "images":

                        [

                            str(
                                INPUT_IMAGE
                            )

                        ]

                }

            ],

            options={

                "temperature":
                    0.3,

                "num_predict":
                    300

            }

        )


        answer = get_response_content(
            response
        )


        status = "Success"


    except Exception as error:

        answer = (

            "VLM inference failed: "

            f"{type(error).__name__}: "

            f"{error}"

        )


        status = "Failed"


    inference_time = (

        time.perf_counter()

        - start_time

    )


    print(
        "\nMODEL RESPONSE:\n"
    )

    print(
        answer
    )


    print(

        "\nInference time: "

        f"{inference_time:.2f} seconds"

    )


    all_results.append(

        {

            "task":
                task_name,

            "model_type":
                model_type,

            "model":
                VLM_MODEL,

            "input_image":
                str(INPUT_IMAGE),

            "prompt":
                prompt,

            "response":
                answer,

            "temperature":
                0.3,

            "maximum_output_tokens":
                300,

            "inference_time_seconds":

                round(

                    inference_time,

                    2

                ),

            "status":
                status,

            "timestamp":

                datetime.now().isoformat(

                    timespec="seconds"

                )

        }

    )


    return answer


# ============================================================
# SAVE RESULTS
# ============================================================

def save_results():

    """
    Saves all inference results
    in JSON and TXT formats.
    """


    RESULTS_FOLDER.mkdir(

        parents=True,

        exist_ok=True

    )


    with open(

        JSON_FILE,

        "w",

        encoding="utf-8"

    ) as file:

        json.dump(

            all_results,

            file,

            indent=4,

            ensure_ascii=False

        )


    with open(

        TEXT_FILE,

        "w",

        encoding="utf-8"

    ) as file:


        file.write(

            "PROMPT ENGINEERING AND "

            "MULTI-MODEL INFERENCE "

            "USING OLLAMA\n"

        )


        file.write(

            "=" * 75

            + "\n"

        )


        file.write(

            "Student: "

            "Eilene Anna Kuriakose\n"

        )


        file.write(

            "\nMODELS USED\n"

        )


        file.write(

            f"LLM: {LLM_MODEL}\n"

        )


        file.write(

            f"SLM: {SLM_MODEL}\n"

        )


        file.write(

            f"VLM: {VLM_MODEL}\n"

        )


        file.write(

            "\nGenerated: "

            + datetime.now().strftime(

                "%Y-%m-%d %H:%M:%S"

            )

            + "\n"

        )


        for result in all_results:


            file.write(

                "\n"

                + "=" * 75

                + "\n"

            )


            file.write(

                "TASK:\n"

                + str(

                    result.get(
                        "task"
                    )

                )

                + "\n"

            )


            file.write(

                "\nMODEL TYPE:\n"

                + str(

                    result.get(
                        "model_type"
                    )

                )

                + "\n"

            )


            file.write(

                "\nMODEL:\n"

                + str(

                    result.get(
                        "model"
                    )

                )

                + "\n"

            )


            file.write(

                "\nSTATUS:\n"

                + str(

                    result.get(
                        "status"
                    )

                )

                + "\n"

            )


            if result.get(
                "input_image"
            ):


                file.write(

                    "\nINPUT IMAGE:\n"

                    + str(

                        result.get(
                            "input_image"
                        )

                    )

                    + "\n"

                )


            if result.get(
                "prompt"
            ):


                file.write(

                    "\nPROMPT:\n"

                    + str(

                        result.get(
                            "prompt"
                        )

                    )

                    + "\n"

                )


            file.write(

                "\nRESPONSE:\n"

                + str(

                    result.get(
                        "response"
                    )

                )

                + "\n"

            )


            if result.get(

                "inference_time_seconds"

            ) is not None:


                file.write(

                    "\nINFERENCE TIME:\n"

                    + str(

                        result.get(

                            "inference_time_seconds"

                        )

                    )

                    + " seconds\n"

                )


    print_header(
        "RESULTS SAVED"
    )


    print(

        "JSON results: "

        f"{JSON_FILE.relative_to(PROJECT_FOLDER)}"

    )


    print(

        "Text results: "

        f"{TEXT_FILE.relative_to(PROJECT_FOLDER)}"

    )


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print_header(

        "PROMPT ENGINEERING AND "

        "MULTI-MODEL INFERENCE"

    )


    print(

        "Student: "

        "Eilene Anna Kuriakose"

    )


    print(
        "\nActual models used:"
    )


    print(

        f"1. LLM: {LLM_MODEL}"

    )


    print(

        f"2. SLM: {SLM_MODEL}"

    )


    print(

        f"3. VLM: {VLM_MODEL}"

    )


    print(

        "\nStarted: "

        + datetime.now().strftime(

            "%Y-%m-%d %H:%M:%S"

        )

    )


    # Display locally installed
    # Ollama models.

    list_installed_models()


    # Prompt-engineering methods
    # using Llama 3.2.

    zero_shot_prompting()

    one_shot_prompting()

    few_shot_prompting()

    chain_of_thought_prompting()


    # LLM inference tasks.

    llm_text_summarization()

    llm_question_answering()


    # SLM inference tasks.

    slm_next_text_generation()

    slm_short_text_summarization()


    # VLM inference task.

    vlm_image_understanding()


    # Save all results.

    save_results()


    print_header(
        "ALL TASKS COMPLETED"
    )


    successful_tasks = sum(

        1

        for result in all_results

        if result.get(
            "status"
        )

        == "Success"

    )


    failed_tasks = sum(

        1

        for result in all_results

        if result.get(
            "status"
        )

        == "Failed"

    )


    print(

        "Total inference tasks: "

        f"{len(all_results)}"

    )


    print(

        "Successful inference tasks: "

        f"{successful_tasks}"

    )


    print(

        "Failed inference tasks: "

        f"{failed_tasks}"

    )


    print(
        "\nModels tested:"
    )


    print(

        f"- LLM: {LLM_MODEL}"

    )


    print(

        f"- SLM: {SLM_MODEL}"

    )


    print(

        f"- VLM: {VLM_MODEL}"

    )


    print(

        "\nCheck the results folder "

        "for the JSON and TXT outputs."

    )


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":

    main()