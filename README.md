# AI Based FloorPlan Retrieval and Generator

## Overview
This project provides a Conda environment setup and installs all the necessary dependencies listed in the `requirements.txt` file. It includes libraries for Flask, FAISS, Google AI APIs, Hugging Face models, OpenCV, PyTorch, and more.

## Prerequisites
- Install [Miniconda](https://docs.conda.io/en/latest/miniconda.html) or [Anaconda](https://www.anaconda.com/)

## Setup
### 1. Create a Conda Environment
```sh
conda create --name my_env python=3.9
```
Replace `my_env` with your preferred environment name.

### 2. Activate the Environment
```sh
conda activate my_env
```

### 3. Install Dependencies
Make sure you have `requirements.txt` in your project directory. Then run:
```sh
pip install -r requirements.txt
```

## Dependencies
Below are the main dependencies required for this project:

```sh
# Flask & Extensions
Flask
flask-cors

# Machine Learning & AI
torch
torchvision
torchaudio
transformers
faiss-cpu
huggingface-hub

# Google AI APIs
google-generativeai
google-ai-generativelanguage
google-api-python-client
google-auth

# Data Processing
numpy
pandas
scipy
scikit-image

# Visualization
matplotlib
networkx
svgwrite

# Other Utilities
opencv-python
regex
tqdm
requests
```

## Verifying Installation
To check if all packages are installed correctly, run:
```sh
pip list
```

## Running the Project
You can start your Flask application (if applicable) using:
```sh
python app.py
```
Replace `app.py` with the entry script of your project.

## Contribution
Feel free to submit issues and pull requests to improve this project!

## License
This project is licensed under the MIT License.

