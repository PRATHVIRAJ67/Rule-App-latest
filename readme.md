# Rule Engine Application with AST
![Homepage](./rule%20engine.png)

## Overview

This project is a 3-tier rule engine application that allows for the dynamic creation, combination, and modification of rules to determine user eligibility based on attributes such as age, department, income, spending habits, and more. The system leverages Abstract Syntax Trees (AST) to represent conditional rules, allowing them to be dynamically modified and efficiently evaluated against user data.

## Features

- **Rule Creation**: Dynamically create rules from string representations, which are then converted into ASTs for efficient processing.
- **Rule Combination**: Combine multiple rules into a single AST using logical operators (AND/OR), minimizing redundant checks and ensuring efficient evaluation.
- **Rule Evaluation**: Evaluate user eligibility based on a set of predefined rules and given user attributes.
- **User Interface**: A simple front-end built with HTML and CSS allows users to create, combine, and evaluate rules via an intuitive interface.
- **Backend API**: Developed using Python, with a MongoDB database to store and manage rules.

## How to Run

### Prerequisites

- **MongoDB**: Ensure MongoDB is installed and running on your system.
- **Python**: Python 3.x must be installed on your system.

### Steps

1. **Clone the repository**:
   ```bash
   git clone https://github.com/PRATHVIRAJ67/Zeotap-Rule-engine-web-App.git
   ```

2. **Navigate to the backend directory**:
   ```bash
   cd backend
   ```

3. **Install the required dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Run the backend server**:
   ```bash
   python app.py
   ```

5. **Open the frontend**:
   Navigate to the `frontend/index.html` file and open it in your browser.

## Project Structure

- **backend/**: Contains the Python backend code that handles rule creation, modification, and evaluation.
- **frontend/**: Contains HTML, CSS, and JavaScript files for the user interface.

