# SPARX Science Homework Automator (⚠️ No Longer Maintained)

> **Alert:** This project is no longer actively maintained.

---

## Overview

This project was designed to automate the retrieval and answering of homework questions from **SPARX Science**. It combines **Selenium** for browser automation, **OCR** for question extraction, and AI (via `You.com`) to generate answers.

> **Note:** `sydney-py` is no longer maintained. Using other AI libraries would require an API key, which was not anticipated when this project was originally developed. Additionally, the project relies heavily on specific CSS selectors, which change frequently, making maintenance difficult.

---

## How It Works

1. **Login Simulation**  
   - The script simulates the login process.  
   - Users are prompted to manually enter their password for authentication.

2. **Homework Parsing**  
   - The system currently supports **SPARX Science** only (`SPARX Maths` is not implemented).  
   - It gathers active homework, displays progress percentages, and other relevant information.

3. **Task Navigation**  
   - Users can select which homework to process.  
   - The script loops through each question in the selected tasks.  
   - Screenshots of questions are taken and saved locally.

4. **Answer Extraction**  
   - `science/parseQuestion.py` uses **OCR** to extract the question text from screenshots.  
   - The text is sent to an AI model (You.com) to generate an answer.  
   - Answers are printed to the console.

> ⚠️ **Limitations:**  
> - The automatic navigation between questions does **not fully work**.  
> - Requires manual handling for dynamic page elements.  
> - Extensive mapping of CSS selectors is needed for full automation.  

---

## Final Notes

- This project was a proof-of-concept and may work under the right conditions with additional effort.  
- Anyone interested is welcome to take over and improve it. Contributions are encouraged!

---

## Disclaimer

This tool interacts with SPARX Science for educational purposes. Use responsibly and ensure compliance with any platform terms of service.
