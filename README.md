# Trading Machine Learning Web Application

This project is a web application for trading machine learning models. It provides an interface for users to interact with machine learning algorithms and visualize trading data.

## Project Structure

```
Tradi
├── app               
│   ├── __init__.py   
│   ├── main.py       
│   ├── models        
│   │   ├── __init__.py
│   │   └── sk_models.py
│   │   └── tf_models.py
│   ├── routes        # API endpoints
│   │   ├── __init__.py
│   │   └── api.py
│   │   └── view.py
│   ├── static        
│   │   ├── css
│   │   │   └── style.css
│   │   └── js
│   │       └── main.js
│   └── templates    
│       ├── about.html
│       └── analyse.html
│       └── analysis_result.html
│       └── base.html
│       └── index.html
│       └── predict.html
│       └── predictions.html
├── utils             
│   └── .gitkeep
│   └──  ai_utils.py
│   └──  chart_utils.py
│   └── trading_strategy
├── notebooks        
│   └── analysis.ipynb
├── tests             
│   ├── __init__.py
│   └── test_models.py
├── .gitignore       
├── config.py        
├── requirements.txt 
└── README.md         
```

## Installation

To set up the project, clone the repository and install the required dependencies:

```bash
git clone https://github.com/emiridbest/tradi
cd tradi
pip install -r requirements.txt
```

## Usage

To run the web application, execute the following command:

```bash
python app/main.py
```

Visit `http://localhost:5000` in your web browser to access the application.

## Contributing

Contributions are welcome! Please open an issue or submit a pull request for any improvements or bug fixes.

## License

This project is licensed under the MIT License.
