# Project Title:
AI-Powered Menu Recommender

## Project Description:
This web application recommends food items from a menu based on user preferences and budget constraints. Leveraging the Gemini API, a large language model developed by Google AI 
AI.GOOGLE.DEV
, the system provides personalized dining suggestions. The application is built using Django for the backend and employs HTML and Bootstrap for the frontend interface.

## Features:
Personalized Recommendations: Tailors menu suggestions according to individual taste profiles and financial considerations.
Responsive Design: Ensures compatibility across various devices through the use of Bootstrap.
Scalable Architecture: Built on Django, facilitating easy scalability and maintenance.


## Installation Instructions:

Clone the Repository:
```bash
git clone https://github.com/Mahesh7922/Menu_recommender.git
```

Navigate to the Project Directory:
```bash
cd Menu_recommender
```


Set Up a Virtual Environment:
```bash
python3 -m venv env
source env/bin/activate  # On Windows, use `env\Scripts\activate`
```

Install Dependencies:
```bash
pip install -r requirements.txt
```


Configure Environment Variables:
- Create a .env file in the project root.

Add your Gemini API key and other necessary configurations:
- GEMINI_API_KEY=your_api_key_here



Apply Migrations:
```bash
python manage.py makemigrations
python manage.py migrate
```


Run the Development Server:
```bash
python manage.py runserver
```

## Usage Guide:
Accessing the Application:
- Open a web browser and navigate to http://127.0.0.1:8000/.

## Interacting with the Recommender:
Input your taste preferences and budget.
- Receive a curated list of menu items tailored to your inputs.

    
## Contributing:
Contributions are welcome! To contribute:
- Fork the repository.
- Create a new branch: git checkout -b feature-name.
- Make your changes and commit them: git commit -m 'Add feature'.
- Push to the branch: git push origin feature-name.
- Submit a pull request.
