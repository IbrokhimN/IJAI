
# DeepSeek-R1 Wrapper

## Disclaimer

**Important:** This project provides a Python wrapper for the `deepseek-r1:8b` model via Ollama.  

- **Ownership:** The model `deepseek-r1:8b` is provided by DeepSeek through Ollama. This project does **not** claim ownership of the model or the Ollama software.  
- **Prerequisite:** Ollama must already be installed on your system. The wrapper does not install Ollama automatically.  
- **Installer Script:** An `installer.sh` script is provided to download the `deepseek-r1:8b` model.  
- **Manual Installation:** If you encounter errors when running the Python code, it is recommended to manually execute `installer.sh` to ensure the model is properly installed. This may be required if the automated installation fails.  

---

## Installation & Usage

1. Ensure Ollama is installed on your system.  
2. Optionally, make the installer executable:
   ```bash
   chmod +x installer.sh
    ```

3. If the model is not available locally, run:

   ```bash
   ./installer.sh
   ```
4. Use the Python wrapper:

   ```python
   from deepseek_r1 import DeepSeekR1  # or deepseek_wrapper if named differently

   # Initialize the model
   model = DeepSeekR1()

   # Send a prompt
   prompt = "Explain the basics of quantum computing in simple terms."
   answer = model.response(prompt)

   print("Model response:", answer)
   ```

* The wrapper will attempt to use the locally installed model.
* In case the model is missing and the automatic installer fails, running `installer.sh` manually is necessary.

---

## Notes

* This project is a derivative wrapper for the Ollama `deepseek-r1:8b` model.
* Users are responsible for their environment, including having Ollama installed and sufficient storage (\~5.2 GB) for the model.
* The author of this wrapper is not responsible for any issues arising from the use of Ollama or the DeepSeek-R1 model.

