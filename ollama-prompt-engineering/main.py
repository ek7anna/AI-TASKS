"""
AI MODEL INFERENCE AND PROMPT ENGINEERING USING OLLAMA

Student: Eilene Anna Kuriakose

Covers:
1. Ollama implementation
2. Installed-model listing
3. Zero-shot prompting
4. One-shot prompting
5. Few-shot prompting
6. Chain-of-thought prompting
7. LLM next-text generation
8. LLM summarization
9. LLM question answering
10. LCM-style concept-level processing
11. Actual SAM image segmentation
12. Inference-time measurement
13. JSON and TXT result saving
"""

# ============================================================
# IMPORTS
# ============================================================

from ollama import chat
from ollama import list as ollama_list

from datetime import datetime
from pathlib import Path

import json
import time


# ============================================================
# CONFIGURATION
# ============================================================

OLLAMA_MODEL = "llama3.2"

DEFAULT_TEMPERATURE = 0.7
DEFAULT_MAX_TOKENS = 512

RESULTS_FOLDER = Path("results")

JSON_FILE = RESULTS_FOLDER / "model_results.json"
TEXT_FILE = RESULTS_FOLDER / "model_results.txt"

INPUT_IMAGE = Path("input_image.jpg")
SAM_OUTPUT_IMAGE = RESULTS_FOLDER / "sam_segmented_output.png"

all_results = []


# ============================================================
# DISPLAY FUNCTION
# ============================================================

def print_header(title):

    print("\n" + "=" * 75)
    print(title.center(75))
    print("=" * 75)


# ============================================================
# LIST INSTALLED OLLAMA MODELS
# ============================================================

def list_installed_models():

    print_header("INSTALLED OLLAMA MODELS")

    try:

        response = ollama_list()

        if hasattr(response, "models"):
            models = response.models
        else:
            models = response.get("models", [])

        if not models:

            print("No locally installed Ollama models were found.")

            return

        print("Models available locally:")

        for model in models:

            if hasattr(model, "model"):

                model_name = model.model

            elif isinstance(model, dict):

                model_name = model.get(
                    "model",
                    model.get("name", "Unknown")
                )

            else:

                model_name = str(model)

            print(f"- {model_name}")

    except Exception as error:

        print("Unable to list Ollama models.")

        print(f"Reason: {error}")


# ============================================================
# OLLAMA MODEL INFERENCE FUNCTION
# ============================================================

def call_ollama_model(
    task_name,
    prompt,
    temperature=DEFAULT_TEMPERATURE,
    max_tokens=DEFAULT_MAX_TOKENS
):

    print_header(task_name)

    print(f"Model: {OLLAMA_MODEL}")
    print(f"Temperature: {temperature}")
    print(f"Maximum output tokens: {max_tokens}")

    print("\nPROMPT:\n")
    print(prompt)

    print("\nMODEL RESPONSE:\n")

    start_time = time.perf_counter()

    try:

        response = chat(
            model=OLLAMA_MODEL,
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ],
            options={
                "temperature": temperature,
                "num_predict": max_tokens
            }
        )

        answer = response["message"]["content"]

        status = "Success"

    except Exception as error:

        answer = f"Model inference failed: {error}"

        status = "Failed"

    inference_time = time.perf_counter() - start_time

    print(answer)

    print(
        f"\nInference time: "
        f"{inference_time:.2f} seconds"
    )

    all_results.append(
        {
            "task": task_name,
            "model": OLLAMA_MODEL,
            "model_category": "Large Language Model",
            "prompt": prompt,
            "response": answer,
            "temperature": temperature,
            "maximum_tokens": max_tokens,
            "inference_time_seconds": round(
                inference_time,
                2
            ),
            "status": status,
            "timestamp": datetime.now().isoformat(
                timespec="seconds"
            )
        }
    )

    return answer


# ============================================================
# 1. ZERO-SHOT PROMPTING
# ============================================================

def zero_shot_prompting():

    prompt = """
Classify the sentiment of the following sentence
as Positive, Negative, or Neutral.

Sentence:
I really enjoy learning about artificial intelligence.

Return only the sentiment label.
"""

    call_ollama_model(
        "1. ZERO-SHOT PROMPTING",
        prompt
    )


# ============================================================
# 2. ONE-SHOT PROMPTING
# ============================================================

def one_shot_prompting():

    prompt = """
Classify the sentiment by following the example.

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

    call_ollama_model(
        "2. ONE-SHOT PROMPTING",
        prompt
    )


# ============================================================
# 3. FEW-SHOT PROMPTING
# ============================================================

def few_shot_prompting():

    prompt = """
Classify the sentiment by following the examples.

EXAMPLE 1

Input:
The weather is wonderful.

Output:
Positive


EXAMPLE 2

Input:
The service was terrible.

Output:
Negative


EXAMPLE 3

Input:
The parcel arrived on Monday.

Output:
Neutral


NOW CLASSIFY:

Input:
This phone has an excellent camera.

Output:
"""

    call_ollama_model(
        "3. FEW-SHOT PROMPTING",
        prompt
    )


# ============================================================
# 4. CHAIN-OF-THOUGHT PROMPTING
# ============================================================

def chain_of_thought_prompting():

    prompt = """
Solve the following problem carefully.

Show the important calculation steps
and provide the final answer.

A bat and a ball cost $1.10 in total.

The bat costs $1 more than the ball.

How much does the ball cost?
"""

    call_ollama_model(
        "4. CHAIN-OF-THOUGHT PROMPTING",
        prompt
    )


# ============================================================
# 5. LLM - NEXT-TEXT GENERATION
# ============================================================

def llm_next_text_generation():

    prompt = """
Complete the following sentence naturally.

Return only one completed sentence.

In the future, artificial intelligence will
"""

    call_ollama_model(
        "5. LLM - NEXT-TEXT GENERATION",
        prompt,
        temperature=0.8,
        max_tokens=100
    )


# ============================================================
# 6. LLM - TEXT SUMMARIZATION
# ============================================================

def llm_summarization():

    article = """
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

{article}

SUMMARY:
"""

    call_ollama_model(
        "6. LLM - TEXT SUMMARIZATION",
        prompt
    )


# ============================================================
# 7. LLM - QUESTION ANSWERING
# ============================================================

def llm_question_answering():

    prompt = """
Answer the following question
clearly in three sentences.

What is the difference between
artificial intelligence and machine learning?
"""

    call_ollama_model(
        "7. LLM - QUESTION ANSWERING",
        prompt
    )


# ============================================================
# 8. LCM-STYLE CONCEPT-LEVEL PROCESSING
# ============================================================

def lcm_concept_task():

    prompt = """
Perform concept-level processing on the text below.

TEXT:

Artificial intelligence is increasingly used
in hospitals, schools, businesses, transport
systems, and scientific research.

AI can improve efficiency, automate repetitive
work, support decisions, and analyze large
amounts of information.

However, AI can also create challenges involving
privacy, bias, employment, accountability,
and safety.

Return:

1. Three major concepts

2. One relationship between the concepts

3. A two-sentence conceptual summary
"""

    call_ollama_model(
        "8. LCM-STYLE CONCEPT-LEVEL TASK",
        prompt
    )


# ============================================================
# 9. ACTUAL SAM IMAGE SEGMENTATION
# ============================================================

def run_sam_segmentation():

    print_header("9. SAM - IMAGE SEGMENTATION")

    print(
        "Model: facebook/sam-vit-base"
    )

    print(
        "Model category: "
        "Computer-Vision Segmentation Model"
    )

    print(
        "Task: Image segmentation"
    )

    if not INPUT_IMAGE.exists():

        message = (
            "SAM was skipped because "
            "'input_image.jpg' was not found.\n"
            "Place input_image.jpg in the project folder "
            "and run the program again."
        )

        print("\n" + message)

        all_results.append(
            {
                "task": "9. SAM - IMAGE SEGMENTATION",
                "model": "facebook/sam-vit-base",
                "model_category":
                    "Computer-Vision Segmentation Model",
                "input": str(INPUT_IMAGE),
                "output": None,
                "response": message,
                "status": "Skipped - input image missing",
                "timestamp":
                    datetime.now().isoformat(
                        timespec="seconds"
                    )
            }
        )

        return

    start_time = time.perf_counter()

    try:

        import numpy as np
        import torch

        import matplotlib

        matplotlib.use("Agg")

        import matplotlib.pyplot as plt

        from PIL import Image

        from transformers import (
            SamModel,
            SamProcessor
        )

        print(
            "\nLoading the SAM processor..."
        )

        sam_model_name = (
            "facebook/sam-vit-base"
        )

        processor = (
            SamProcessor.from_pretrained(
                sam_model_name
            )
        )

        print(
            "Loading the SAM model..."
        )

        sam_model = (
            SamModel.from_pretrained(
                sam_model_name
            )
        )

        device = (
            "cuda"
            if torch.cuda.is_available()
            else "cpu"
        )

        sam_model.to(device)

        sam_model.eval()

        print(
            f"Device: {device}"
        )

        print(
            "Reading input image..."
        )

        image = (
            Image.open(INPUT_IMAGE)
            .convert("RGB")
        )

        original_size = image.size

        # Resize the image correctly before SAM inference.
        # This lowers memory usage on CPU.
        image.thumbnail(
            (512, 512)
        )

        print(
            f"Original image size: "
            f"{original_size}"
        )

        print(
            f"Image size used for SAM: "
            f"{image.size}"
        )

        width, height = image.size

        # Use the center of the image
        # as the point prompt for SAM.
        input_points = [
            [
                [
                    width // 2,
                    height // 2
                ]
            ]
        ]

        print(
            "Preparing SAM inputs..."
        )

        inputs = processor(
            images=image,
            input_points=input_points,
            return_tensors="pt"
        )

        inputs = {
            key: value.to(device)
            for key, value
            in inputs.items()
        }

        print(
            "Running SAM inference..."
        )

        with torch.inference_mode():

            outputs = sam_model(
                **inputs
            )

        print(
            "Processing segmentation masks..."
        )

        masks = (
            processor.image_processor
            .post_process_masks(
                outputs.pred_masks.cpu(),
                inputs[
                    "original_sizes"
                ].cpu(),
                inputs[
                    "reshaped_input_sizes"
                ].cpu()
            )
        )

        predicted_masks = (
            masks[0]
            .cpu()
            .numpy()
        )

        predicted_masks = (
            np.squeeze(
                predicted_masks
            )
        )

        scores = (
            outputs.iou_scores
            .detach()
            .cpu()
            .numpy()
            .reshape(-1)
        )

        if predicted_masks.ndim == 2:

            selected_mask = (
                predicted_masks
            )

        else:

            best_mask_index = int(
                np.argmax(scores)
            )

            selected_mask = (
                predicted_masks[
                    best_mask_index
                ]
            )

        RESULTS_FOLDER.mkdir(
            parents=True,
            exist_ok=True
        )

        print(
            "Saving segmentation output..."
        )

        plt.figure(
            figsize=(8, 8)
        )

        plt.imshow(
            image
        )

        plt.imshow(
            selected_mask,
            alpha=0.5
        )

        plt.axis(
            "off"
        )

        plt.title(
            "SAM Image Segmentation"
        )

        plt.tight_layout()

        plt.savefig(
            SAM_OUTPUT_IMAGE,
            bbox_inches="tight",
            dpi=150
        )

        plt.close()

        inference_time = (
            time.perf_counter()
            - start_time
        )

        message = (
            "SAM segmentation completed successfully.\n"
            f"Output: {SAM_OUTPUT_IMAGE}\n"
            f"Execution time: "
            f"{inference_time:.2f} seconds"
        )

        print(
            "\n" + message
        )

        all_results.append(
            {
                "task":
                    "9. SAM - IMAGE SEGMENTATION",

                "model":
                    sam_model_name,

                "model_category":
                    "Computer-Vision "
                    "Segmentation Model",

                "input":
                    str(INPUT_IMAGE),

                "original_image_size":
                    str(original_size),

                "processed_image_size":
                    str(image.size),

                "output":
                    str(SAM_OUTPUT_IMAGE),

                "response":
                    message,

                "inference_time_seconds":
                    round(
                        inference_time,
                        2
                    ),

                "status":
                    "Success",

                "timestamp":
                    datetime.now().isoformat(
                        timespec="seconds"
                    )
            }
        )

        # Free model memory.
        del outputs
        del sam_model

        if torch.cuda.is_available():

            torch.cuda.empty_cache()

    except Exception as error:

        inference_time = (
            time.perf_counter()
            - start_time
        )

        message = (
            f"SAM inference failed: "
            f"{type(error).__name__}: "
            f"{error}"
        )

        print(
            "\n" + message
        )

        all_results.append(
            {
                "task":
                    "9. SAM - IMAGE SEGMENTATION",

                "model":
                    "facebook/sam-vit-base",

                "model_category":
                    "Computer-Vision "
                    "Segmentation Model",

                "input":
                    str(INPUT_IMAGE),

                "output":
                    None,

                "response":
                    message,

                "inference_time_seconds":
                    round(
                        inference_time,
                        2
                    ),

                "status":
                    "Failed",

                "timestamp":
                    datetime.now().isoformat(
                        timespec="seconds"
                    )
            }
        )


# ============================================================
# SAVE ALL RESULTS
# ============================================================

def save_results():

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
            "AI MODEL INFERENCE "
            "AND PROMPT ENGINEERING\n"
        )

        file.write(
            "=" * 75 + "\n"
        )

        file.write(
            "Student: "
            "Eilene Anna Kuriakose\n"
        )

        file.write(
            f"Ollama model: "
            f"{OLLAMA_MODEL}\n"
        )

        file.write(
            "Generated: "
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
                f"TASK:\n"
                f"{result.get('task')}\n"
            )

            file.write(
                f"\nMODEL:\n"
                f"{result.get('model')}\n"
            )

            file.write(
                f"\nSTATUS:\n"
                f"{result.get('status')}\n"
            )

            if result.get(
                "prompt"
            ):

                file.write(
                    f"\nPROMPT:\n"
                    f"{result.get('prompt')}\n"
                )

            file.write(
                f"\nRESPONSE:\n"
                f"{result.get('response')}\n"
            )

    print_header(
        "RESULTS SAVED"
    )

    print(
        f"JSON results: "
        f"{JSON_FILE}"
    )

    print(
        f"Text results: "
        f"{TEXT_FILE}"
    )


# ============================================================
# MAIN PROGRAM
# ============================================================

def main():

    print_header(
        "AI MODEL INFERENCE "
        "AND PROMPT ENGINEERING"
    )

    print(
        "Student: "
        "Eilene Anna Kuriakose"
    )

    print(
        f"Ollama model: "
        f"{OLLAMA_MODEL}"
    )

    print(
        "Started: "
        + datetime.now().strftime(
            "%Y-%m-%d %H:%M:%S"
        )
    )

    # Display locally installed Ollama models.
    list_installed_models()

    # Prompt-engineering tasks.
    zero_shot_prompting()
    one_shot_prompting()
    few_shot_prompting()
    chain_of_thought_prompting()

    # LLM inference tasks.
    llm_next_text_generation()
    llm_summarization()
    llm_question_answering()

    # Concept-level processing task.
    lcm_concept_task()

    # Actual SAM image-segmentation task.
    run_sam_segmentation()

    # Save all outputs.
    save_results()

    print_header(
        "ALL TASKS COMPLETED"
    )

    successful_tasks = sum(
        1
        for result in all_results
        if result.get("status")
        == "Success"
    )

    print(
        f"Total recorded tasks: "
        f"{len(all_results)}"
    )

    print(
        f"Successful tasks: "
        f"{successful_tasks}"
    )

    print(
        "\nCheck the results folder "
        "for all generated outputs."
    )


# ============================================================
# RUN PROGRAM
# ============================================================

if __name__ == "__main__":

    main()