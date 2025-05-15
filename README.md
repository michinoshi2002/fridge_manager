# Fridge Manager

Fridge Manager is a Django web application designed to help users manage the contents of their refrigerator and suggest recipes based on available ingredients. This application integrates with ChatGPT to provide personalized recipe suggestions.

## Features

- Manage refrigerator contents (add, remove, and view items).
- Suggest recipes based on the items currently in the refrigerator.

## Installation

1. Clone the repository:
   ```
   git clone <repository-url>
   cd fridge_manager
   ```

2. Create a virtual environment:
   ```
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. Install the required packages:
   ```
   pip install -r requirements.txt
   ```

4. Apply migrations:
   ```
   python manage.py migrate
   ```

5. Run the development server:
   ```
   python manage.py runserver
   ```

6. Access the application at `http://127.0.0.1:8000/`.

## Usage

- Navigate to the main page to view and manage refrigerator contents.
- Use the recipe suggestion feature to find recipes based on the items you have.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any enhancements or bug fixes.