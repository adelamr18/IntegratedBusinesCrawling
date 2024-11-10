To run the individual scripts please do the following steps:
1- Open project in terminal then type: python3 -m venv myenv (to create virtual environment)
2- Then type: source myenv/bin/activate (to activate virtual environment)
3- Then type: pip install -r requirements.txt (to install all dependencies)
4- Now that everything is setup to run a specific script to crawl a website type in the terminal:

python -m scripts.Carrefour.carrefour_extract_data (For Carrefour)
python -m scripts.Seoudi.seoudi_extract:data (For Seoudi)
python -m scripts.Spinneys.spinneys_extract_data (For Spinneys)