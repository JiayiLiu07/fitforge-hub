# FitForge Hub：人工智能驱动的全方位健康管理平台 🚀

![Python](https://img.shields.io/badge/python-3.9+-blue.svg)
![Streamlit](https://img.shields.io/badge/Streamlit-1.48+-FF4B4B.svg)
![License](https://img.shields.io/badge/license-MIT-green.svg)

## 项目概述 📖

FitForge Hub 是一个基于 Streamlit 框架开发的交互式 Web 应用程序，旨在提供数据驱动的健康管理解决方案。该平台利用人工智能技术整合健康数据分析、肥胖风险评估、个性化膳食规划、长期身体变化预测以及全面的健康规划，助力用户实现科学化健康管理。它支持自然语言查询到 SQL 的转换、基于生活方式的肥胖等级预测、动态生成的 7 天膳食计划、30 天体重趋势预测以及压力因素分析和个性化健康计划。

项目存储在 `FitForge Hub` 文件夹中，包含以下子文件夹：
- `pages`：存储六个功能模块的 Python 脚本。
- `model`：存储机器学习模型文件（如 `obesity_xgb.pkl`）。
- `data`：存储数据集文件（如 `obesity_level_attribute_clean.csv` 和 `obesity_level_result_clean.csv`）。

项目仓库位于：[https://github.com/JiayiLiu07/fitforge-hub](https://github.com/JiayiLiu07/fitforge-hub)。

## 功能模块 📂

- `1_👋_Pandas_Obesity_Data_Analyzer.py`：使用 Pandas 和 pandasql 将自然语言查询转换为 SQL 语句，生成交互式 Plotly 可视化图表，用于肥胖数据分析。
- `1_🗣️_PySpark_Obesity_Data_Explorer.py`：利用 PySpark 实现可扩展的自然语言到 Spark SQL 查询转换，生成交互式 Plotly 可视化。
- `2_🔮_Obesity_Level_Prediction.py`：基于用户生活习惯数据进行肥胖风险评估，计算 BMI 并提供个性化健康建议。
- `3_🥗_7-Day_Smart_Meal_Planner.py`：根据用户饮食偏好生成 7 天智能膳食计划，支持营养分析和购物清单导出。
- `4_📅_30-Day_Body_Planner.py`：通过生活方式调整模拟 30 天体重变化趋势，支持多场景比较和 Altair 可视化。
- `5_🧠_Holistic_Wellness_Planner.py`：提供全面的健康分析，包括压力因素的 3D 可视化，结合工作负荷、社交支持和放松时间，提供可操作的健康洞察。

## 核心功能 🔍

- **自然语言转 SQL（NL2SQL）** 🗣️：将自然语言查询（如“按性别显示肥胖等级分布”）转换为 Pandas 或 Spark SQL 语句，通过 Plotly 生成交互式可视化图表。
- **肥胖等级预测** 🔮：分析用户生活习惯数据（如饮食、运动、睡眠），计算 BMI，预测肥胖风险，并提供个性化健康建议和可视化分析。
- **7 天智能膳食计划** 🥗：根据饮食偏好、排除食材及营养目标，生成动态膳食计划，支持营养分析和购物清单导出。
- **30 天身体规划器** 📅：模拟生活方式调整（如运动、睡眠、饮食）下的 30 天体重变化趋势，支持多场景比较和 Altair 可视化。
- **全面健康规划器** 🧠：通过 3D 可视化分析压力因素，结合工作负荷、社交支持和放松时间，提供个性化的健康计划。
- **交互式仪表板** 📊：提供用户登记界面以设定个性化健康目标，实时计算 BMI，并快速导航至各功能模块。
- **健康建议循环展示** 💡：在侧边栏动态展示健康管理建议，增强用户参与度和教育效果。

## 制作方法 🛠️

FitForge Hub 旨在开发一个用户友好的健康管理平台，结合大数据分析与人工智能技术。项目采用 Python 和 Streamlit 框架，确保快速原型开发和交互式用户体验。核心技术选型包括：
- **PySpark**：支持 PySpark Obesity Data Explorer 中 NL2SQL 功能的高效大规模数据查询。
- **Pandas 和 pandasql**：在 Pandas Obesity Data Analyzer 中实现轻量级、灵活的 SQL 基础数据分析。
- **OpenAI API**：驱动自然语言处理，生成精确的 SQL 查询和个性化膳食计划。
- **XGBoost**：用于肥胖等级预测，提供高精度分类模型。
- **Plotly 和 Altair**：实现交互式数据可视化，增强用户对健康数据的理解。
- **Streamlit**：提供直观的 Web 界面，支持动态用户输入和实时反馈。

开发过程中，数据集（`data` 文件夹）经过清洗以确保一致性，模型文件（`model` 文件夹）通过 XGBoost 训练生成。项目采用模块化设计，确保功能独立且可扩展。

## 安装步骤 ⚙️

1. **克隆代码仓库**：
```bash
git clone https://github.com/JiayiLiu07/fitforge-hub.git
cd fitforge-hub
```

2. **设置 Python 环境**：
   - 确保安装 Python 3.9 或更高版本：
     ```bash
     python --version
     ```
   - 建议使用虚拟环境以避免依赖冲突：
     ```bash
     python -m venv venv
     source venv/bin/activate  # Linux/Mac
     venv\Scripts\activate     # Windows
     ```

3. **安装依赖**：
```bash
pip install -r requirements.txt
```

4. **准备数据**：
   - 确保 `data` 文件夹包含数据集文件（如 `obesity_level_attribute_clean.csv` 和 `obesity_level_result_clean.csv`）。
   - 将 `obesity_xgb.pkl` 模型文件置于 `model` 文件夹。

5. **配置 API 密钥**：
   - 在 `FitForge_Hub🚀.py`、`1_👋_Pandas_Obesity_Data_Analyzer.py`、`1_🗣️_PySpark_Obesity_Data_Explorer.py`、`3_🥗_7-Day_Smart_Meal_Planner.py` 或 `5_🧠_Holistic_Wellness_Planner.py` 中设置 OpenAI API 密钥，或通过环境变量配置：
     ```bash
     export OPENAI_API_KEY='your-api-key'  # Linux/Mac
     set OPENAI_API_KEY=your-api-key       # Windows
     ```

## 运行说明 🚀

启动 Streamlit 应用程序 
`【请确保你使用的是虚拟环境中的streamlit】`

```bash
streamlit run "FitForge Hub🚀.py"
```

- **用户登记**：在主界面输入个人信息（如年龄、性别、体重、身高）及健康目标。
- **目标设定**：选择健身目标（如减脂、增肌）并指定期望体重。
- **功能导航**：通过“下一步”按钮访问各功能模块。
- **健康建议**：查看侧边栏循环展示的健康管理建议。

## 系统要求 📋

以下为所需 Python 包及其版本，详见 `requirements.txt`：

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

### 验证依赖版本
- 查看当前环境包版本：
  ```bash
  pip list
  ```
- 导出依赖到 `requirements.txt`：
  ```bash
  pip freeze > requirements.txt
  ```
- 检查 Python 版本（推荐 3.9 或更高）：
  ```bash
  python --version
  ```

**注意**：依赖版本可能需根据实际环境调整，可通过 PyPI（https://pypi.org/）确认最新版本。

## 已知问题 ⚠️

- **API 密钥配置**：若未正确设置 OpenAI API 密钥，NL2SQL、膳食规划或健康规划功能可能失败。请确保密钥有效并正确配置。
- **数据文件缺失**：NL2SQL 功能依赖 `data` 文件夹中的数据集。若文件缺失或格式不正确，可能导致查询错误。
- **依赖冲突**：某些依赖版本（如 `numpy==2.2.6` 或 `pyspark==4.0.0`）可能在特定环境中引发兼容性问题，建议使用虚拟环境。
- **本地环境**：若在本地运行，需在本地配置好 Spark 环境以支持 PySpark Obesity Data Explorer。

## Bug 追踪器 🐞

请通过 GitHub Issues 报告问题或提交功能请求：
[https://github.com/JiayiLiu07/fitforge-hub/issues](https://github.com/JiayiLiu07/fitforge-hub/issues)

## 作者与联系方式 📧

FitForge Hub 由 Jiayi Liu 倾情打造，希望为您带来健康与活力！🌟 欢迎体验这个项目，并分享您的宝贵建议！😊 有任何问题或想法，请随时联系：

- **作者**：Jiayi Liu (GitHub: [JiayiLiu07](https://github.com/JiayiLiu07))
- **联系方式**：通过 [GitHub Issues 页面](https://github.com/JiayiLiu07/fitforge-hub/issues) 提交反馈，或在 GitHub 上与我直接交流。期待听到您的声音！📬