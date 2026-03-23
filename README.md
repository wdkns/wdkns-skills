[English](./README.md) | [简体中文](./README_CN.md)

# LLM Note Generator

A toolset designed to semi-automatically convert course presentation slides (PDF) and their corresponding lecture subtitles (TXT) into professional LaTeX course notes. By automatically extracting, converting, and building a strictly templated Prompt, this tool helps you leverage Large Language Models (like Gemini, ChatGPT) to quickly generate high-quality, structured notes.

## Included Files

*   **`prompt.py`**: The core processing script. It handles converting the PDF into multiple images stored in a directory, reading the TXT subtitle content, generating a complex Prompt rich with instructions and a LaTeX template, and automatically copying it to your system clipboard.
*   **`clean.sh`**: The archiving and cleanup script. After a note generation session is complete, it single-handedly archives the current directory's PDF, TXT materials, generated TEX file, and the image directory into a specifically named folder, keeping your workspace tidy.

## Prerequisites

Before using, ensure you have the necessary dependencies installed:

1.  **Python Libraries**:
    ```bash
    pip install pdf2image pyperclip
    ```
2.  **System Dependencies (for PDF to image conversion)**:
    For macOS users, you need to install `poppler`:
    ```bash
    brew install poppler
    ```
    For Ubuntu/Debian:
    ```bash
    sudo apt-get install poppler-utils
    ```

## Usage Guide

### Step 1: Preparation
Place the **single** course presentation PDF file and its corresponding text subtitle file (`.txt`) you want to process into the current working directory (where these scripts are located).
> **Note**: Please ensure there is only *one* `.pdf` file and *one* `.txt` file in the directory; otherwise, the script will throw an error.

### Step 2: Generate Prompt (Run `prompt.py`)
Execute the following command in your terminal:
```bash
python prompt.py
```
**Internal workflow of `prompt.py`**:
1. Locates and identifies the PDF and TXT files.
2. Checks for source image resources: If a `pic` folder doesn't exist, it automatically creates one and converts the PDF into PNG images page by page (this may take a few dozen seconds). If `pic` already exists, it reuses it to save time.
3. Reads the subtitle content and merges it into the pre-configured structured Prompt template.
4. Notifies you of successful generation and **automatically copies the result to your system clipboard**.

### Step 3: Generate LaTeX Notes with LLM
1. Open an AI tool that supports document parsing in your browser (e.g., Gemini Advanced or ChatGPT).
2. **Upload your PDF lecture file** in the chat interface.
3. **Paste (Cmd+V / Ctrl+V)** the Prompt from your clipboard into the text input box and send it to the AI model.
4. The model will return beautifully typeset, complete `.tex` source code based on the instructions, including custom components (like "Core Concepts", "Supplementary Knowledge") and automatically referencing the corresponding images in the `pic/` directory.
5. Copy this code locally and save it as a `.tex` file (e.g., `lesson1.tex`). As long as the `.tex` file is in the same directory level as the `pic/` folder, you can compile it into a PDF smoothly.

### Step 4: Archive and Cleanup (Run `clean.sh`)
Once the notes for a lecture are generated, verified, and the `.tex` file is saved, you can use the cleanup script directly to move and package all related files from this session:
```bash
chmod +x clean.sh   # You might need to grant execute permissions the first time you use it
./clean.sh <new_folder_name>

# Example:
./clean.sh Lec_01_Intro
```
After running, the script will automatically create a `Lec_01_Intro` directory and archive the `pic/` directory as well as all `.pdf`, `.txt`, and `.tex` files into it. Your current directory will be clean and ready for preparing the generation of the next lecture.
