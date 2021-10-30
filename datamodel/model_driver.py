import shutil
import time
import os
import glob

import schedule

from datacleanser import cleanseData
from multiclass_model import generateSaveModel

kaggle_data_set     ="datavol/raw/kagglestatic/*.csv"
input_data_set      = "datavol/raw/newsfeeds/*.csv"
cleansed_output_dir = "datavol/cleansed"
model_input_dir     = "datavol/cleansed"
model_output_dir    = "datavol/trained/work"
model_active_dir    = "datavol/trained/active"

## copy the files from work directory to acgive directory
def replaceNewModel():

    if os.path.exists(f"{model_active_dir}/model.pkl"):
        os.remove(f"{model_active_dir}/model.pkl")


    if os.path.exists(f"{model_active_dir}/vectorCategory.pkl"):
        os.remove(f"{model_active_dir}/vectorCategory.pkl")

    for filename in glob.glob(os.path.join(model_output_dir, '*.*')):
        print(f"copying the filename={filename} {model_active_dir} to started")
        shutil.copy(filename, model_active_dir)
        print(f"copying the filename={filename} {model_active_dir} completed")



def generate_model():
    cleanseData(kaggle_data_set, input_data_set, cleansed_output_dir)
    ##sleep(60)
    generateSaveModel(model_input_dir, model_output_dir)

def complete_workflow():
    generate_model()
    replaceNewModel()

## first time it needs to run and then it is going to be every day at early hours of the day
generate_model()
## schedule every day at 1:30 AM.  Assuming no one going to use this system at that time
schedule.every().day.at("01:30").do(complete_workflow)

while True:
    ## If it is pending then wait for 5 mins and then restart
    schedule.run_pending()
    time.sleep(60*5)

