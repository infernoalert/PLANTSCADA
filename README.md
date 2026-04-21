# SCADA CSV Processor App

A lightweight, local desktop utility designed to parse, filter, and process very large CSV exports from SCADA systems without overwhelming system memory.

## Architecture: Lightweight MVC
This application intentionally avoids heavy frameworks to remain fast, maintainable, and easy for other Python developers to understand. It is built using a strict **Model-View-Controller (MVC)** design pattern separated into three core files:

1. **processor.py (The Model)**
   - The data processing engine powered by Pandas.
   - Strictly handles reading, filtering, mathematical operations, and writing CSVs.
   - Completely isolated from any UI logic.

2. **ui.py (The View)**
   - The graphical user interface built with Tkinter / CustomTkinter.
   - Handles window drawing, buttons, file selection dialogs, and gathering user parameters.
   - Completely isolated from data manipulation logic.

3. **main.py (The Controller)**
   - The central nervous system of the app.
   - Initializes the UI and listens for user actions. When the 'Process' button is clicked, it routes the file paths and parameters from the View to the Model for execution.

## Folder Structure
- /input/ - Place raw SCADA .csv files here. (Ignored by Git)
- /output/ - Processed .csv files are generated here. (Ignored by Git)
- main.py, ui.py, processor.py - Core application logic.
- equirements.txt - Python package dependencies.

## Setup Instructions
1. Create a virtual environment: python -m venv venv
2. Activate it: .\venv\Scripts\activate
3. Install dependencies: pip install -r requirements.txt
4. Run the app: python main.py
