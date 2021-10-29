from datacleanser import cleanseData
from multiclass_model import generateSaveModel
from\
    time import sleep
# This is not a right approach but as this is not a production based code, going with simple if conditions
## Ideal approach can be through properties file with profile settings like profile==prod or profile=local

kaggle_data_set     ="/datavol/raw/kagglestatic/*.csv"
input_data_set      = "/datavol/raw/newsfeeds/*.csv"
cleansed_output_dir = "/datavol/cleansed"
model_input_dir     = "/datavol/cleansed"
model_output_dir    = "/datavol/trained/work"

if __name__ == "__main__":
    cleanseData(kaggle_data_set,input_data_set,cleansed_output_dir)
    ##sleep(60)
    generateSaveModel(model_input_dir,model_output_dir)