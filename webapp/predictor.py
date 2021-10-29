# Implement the following two in another class
import pickle



def loadmodel(path):
    ##../datavol/trained/active
    with open(f'{path}/model.pkl', 'rb') as f:
        clf2 = pickle.load(f)
    return clf2

def loadVectorCatogory(path):
    ##../datavol/trained/active
    with open(f"{path}/vectorCategory.pkl", 'rb') as infile:
        data = pickle.load(infile)
    return data


def predict(clf2,data,text):
    print(f"data={data}")
    predicted = clf2.predict(text)
    return data[predicted[0]]