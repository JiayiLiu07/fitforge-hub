# FitForge Hub: An AI-Driven Comprehensive Wellness Platform 🚀

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.48+-FF4B4B.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## Project Overview 📖

FitForge Hub is an interactive web application developed using the Streamlit framework, designed to deliver data-driven health management solutions. Leveraging artificial intelligence, it integrates health data analysis, obesity risk assessment, personalized meal planning, long-term body progression forecasting, and holistic wellness planning to empower users in achieving evidence-based wellness goals. The platform supports natural language to SQL query conversion, obesity level prediction based on lifestyle factors, dynamic 7-day meal planning, 30-day weight trend forecasting, and comprehensive wellness analytics.

The project is stored in the `FitForge Hub` directory, which includes the following subdirectories:
- `pages`: Contains Python scripts for the six functional modules.
- `model`: Stores machine learning model files (e.g., `obesity_xgb.pkl`).
- `data`: Contains datasets (e.g., `obesity_level_attribute_clean.csv` and `obesity_level_result_clean.csv`).

The project repository is located at: [https://github.com/JiayiLiu07/fitforge-hub](https://github.com/JiayiLiu07/fitforge-hub).

## Functional Modules 📂

- `1_👋_Pandas_Obesity_Data_Analyzer.py`: Uses Pandas and pandasql to convert natural language queries into SQL statements, generating interactive Plotly visualizations for obesity data analysis.
- `1_🗣️_PySpark_Obesity_Data_Explorer.py`: Employs PySpark for scalable natural language to Spark SQL query conversion, delivering interactive visualizations with Plotly.
- `2_🔮_Obesity_Level_Prediction.py`: Performs obesity risk assessment based on user lifestyle data, calculates BMI, and provides personalized health recommendations.
- `3_🥗_7-Day_Smart_Meal_Planner.py`: Generates a 7-day intelligent meal plan based on user dietary preferences, with support for nutritional analysis and shopping list export.
- `4_📅_30-Day_Body_Planner.py`: Simulates 30-day weight trends based on lifestyle adjustments, with multi-scenario comparison and Altair-based visualization.
- `5_🧠_Holistic_Wellness_Planner.py`: Provides comprehensive wellness analytics, including stress factor analysis and personalized health programs with 3D visualizations.

## Core Features 🔍

- **Natural Language to SQL (NL2SQL)** 🗣️: Converts natural language queries (e.g., “Show obesity levels by gender”) into SQL statements using Pandas or Spark SQL, visualized via Plotly charts.
- **Obesity Level Prediction** 🔮: Analyzes lifestyle data (e.g., diet, exercise, sleep) to predict obesity risk, compute BMI, and provide tailored health recommendations and visualizations.
- **7-Day Smart Meal Planner** 🥗: Generates customizable meal plans based on dietary preferences, exclusions, and nutritional targets, with visualization and shopping list export.
- **30-Day Body Planner** 📅: Simulates 30-day weight trends based on lifestyle adjustments, enabling scenario comparison and Altair-based visualization.
- **Holistic Wellness Planner** 🧠: Offers stress factor analysis through 3D visualizations, integrating workload, social support, and relaxation time to provide actionable wellness insights.
- **Interactive Dashboard** 📊: Features a user check-in interface for setting personalized goals, real-time BMI calculations, and seamless navigation to all modules.
- **Health Insights Rotation** 💡: Displays rotating health management tips in the sidebar to enhance user engagement and education.

## Development Approach 🛠️

FitForge Hub was developed to create a user-friendly platform for health management, integrating big data analytics and artificial intelligence. The project employs Python and the Streamlit framework for rapid prototyping and interactive user experience. Key technological choices include:
- **PySpark**: Facilitates efficient querying of large-scale health datasets for the NL2SQL feature in the PySpark Obesity Data Explorer.
- **Pandas and pandasql**: Enables lightweight, flexible SQL-based data analysis in the Pandas Obesity Data Analyzer.
- **OpenAI API**: Powers natural language processing for accurate SQL query generation and personalized meal planning.
- **XGBoost**: Drives obesity level prediction with a high-accuracy classification model.
- **Plotly and Altair**: Enable interactive data visualizations to enhance user understanding of health data.
- **Streamlit**: Provides an intuitive web interface for dynamic user input and real-time feedback.

During development, datasets (stored in the `data` folder) were cleaned for consistency, and the model file (stored in the `model` folder) was trained using XGBoost. The project emphasizes modular design for independent and extensible functionality.

## Installation Instructions ⚙️

1. **Clone the Repository**:
```bash
git clone https://github.com/JiayiLiu07/fitforge-hub.git
cd fitforge-hub
```

2. **Set Up Python Environment**:
   - Ensure Python 3.9 or higher is installed:
     ```bash
     python --version
     ```
   - Use a virtual environment to avoid dependency conflicts:
     ```bash
     python -m venv venv
     source venv/bin/activate  # Linux/Mac
     venv\Scripts\activate     # Windows
     ```

3. **Install Dependencies**:
```bash
pip install -r requirements.txt
```

4. **Prepare Data**:
   - Ensure the `data` folder contains datasets (e.g., `obesity_level_attribute_clean.csv` and `obesity_level_result_clean.csv`).
   - Place the `obesity_xgb.pkl` model file in the `model` folder.

5. **Configure API Key**:
   - Set the OpenAI API key in `FitForge_Hub🚀.py`, `1_👋_Pandas_Obesity_Data_Analyzer.py`, `1_🗣️_PySpark_Obesity_Data_Explorer.py`, `3_🥗_7-Day_Smart_Meal_Planner.py`, or `5_🧠_Holistic_Wellness_Planner.py` via environment variables:
     ```bash
     export OPENAI_API_KEY='your-api-key'  # Linux/Mac
     set OPENAI_API_KEY=your-api-key       # Windows
     ```

## Running Instructions 🚀

Launch the Streamlit application:
`[Make sure you are using streamlit in the virtual environment]`
```bash
streamlit run "FitForge Hub.py"
```

- **User Check-In**: Enter personal details (e.g., age, sex, weight, height) and health goals on the main interface.
- **Goal Setting**: Select a fitness objective (e.g., fat loss, muscle gain) and target weight.
- **Module Navigation**: Access individual tools via the “Next Steps” buttons.
- **Health Tips**: Review rotating health management insights in the sidebar.

## System Requirements 📋

The required Python packages and their versions are listed in `requirements.txt`:

```text
streamlit==1.48.0
streamlit-autorefresh==1.0.1
streamlit-option-menu==0.4.0
openai==1.99.9
tenacity==9.1.2
pandas==2.2.3
pandasql==0.7.3
pyspark==4.0.0
numpy==2.2.6
scipy==1.15.3
scikit-learn==1.6.1
xgboost==3.0.4
joblib==1.5.1
plotly==6.3.0
altair==5.5.0
matplotlib==3.10.3
seaborn==0.13.2
pydeck==0.9.1
requests==2.32.4
python-dotenv==1.1.1
pytz==2025.2
python-dateutil==2.9.0.post0
jsonschema==4.25.0
pdfkit==1.0.0
tqdm==4.67.1
```

### Dependency Version Verification
- List installed package versions:
  ```bash
  pip list
  ```
- Export dependencies to `requirements.txt`:
  ```bash
  pip freeze > requirements.txt
  ```
- Check Python version (3.9 or higher recommended):
  ```bash
  python --version
  ```

**Note**: Dependency versions may require adjustment based on your environment. Verify the latest versions on PyPI (https://pypi.org/).

## Known Issues ⚠️

- **API Key Configuration**: Failure to set a valid OpenAI API key may cause the NL2SQL, meal planning, or wellness planning features to fail. Ensure the key is correctly configured.
- **Missing Data Files**: The NL2SQL features depend on datasets in the `data` folder. Missing or incorrectly formatted files may result in query errors.
- **Dependency Conflicts**: Certain versions (e.g., `numpy==2.2.6` or `pyspark==4.0.0`) may cause compatibility issues in some environments. Use a virtual environment to mitigate.
- **Local Environment**: If running locally, you need to configure the Spark environment locally for the PySpark Obesity Data Explorer.

## Bug Tracker 🐞

Report issues or submit feature requests via GitHub Issues:
[https://github.com/JiayiLiu07/fitforge-hub/issues](https://github.com/JiayiLiu07/fitforge-hub/issues)

## Author and Contact Information 📧

FitForge Hub was lovingly crafted by Jiayi Liu to inspire health and wellness! 🌟 Try it out and let me know what you think! 😊 For any questions or feedback, feel free to reach out:

- **Author**: Jiayi Liu (GitHub: [JiayiLiu07](https://github.com/JiayiLiu07))
- **Contact**: Drop by the [GitHub Issues page](https://github.com/JiayiLiu07/fitforge-hub/issues) to share your thoughts or connect with me directly on GitHub. I’d love to hear from you! 📬