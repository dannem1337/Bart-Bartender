import pandas as pd
from sklearn.linear_model import LogisticRegression, RidgeClassifier, PassiveAggressiveClassifier
from sklearn.model_selection import train_test_split, GridSearchCV
from sklearn.metrics import accuracy_score
from sklearn.svm import SVC

# part 1
data = pd.read_csv("dataset.csv")
emotions = data["emotion"]
inputs = data.drop(labels="emotion", axis=1)

accuracies = {}

for number in range(50): # Run 50 times to find the best model
# part 2
    data_in, test_in, data_out, test_out = train_test_split(inputs, emotions, test_size=0.15, stratify=emotions) # test = 15%, data= 85%
    train_in, val_in, train_out, val_out = train_test_split(data_in, data_out, test_size=0.2) # val is 0.85*0.2 = 0.17 -> 17 %, train is 68%

    #part 3
    model = LogisticRegression()
    model.fit(X=train_in, y=train_out)
    predictions = model.predict(X=val_in)
    accuracy = accuracy_score(y_true=val_out, y_pred=predictions)
    acc_tuple = accuracies.get("LR", (0,0))
    accuracies["LR"] = (acc_tuple[0] + accuracy, acc_tuple[1] + 1)
    

    model2 = RidgeClassifier()
    model2.fit(X=train_in, y=train_out)
    predictions2 = model2.predict(X=val_in)
    accuracy2 = accuracy_score(y_true=val_out, y_pred=predictions2)
    acc_tuple = accuracies.get("RC", (0,0))
    accuracies["RC"] = (acc_tuple[0] + accuracy2, acc_tuple[1] + 1)

    model3 = PassiveAggressiveClassifier()
    model3.fit(X=train_in, y=train_out)
    predictions3 = model3.predict(X=val_in)
    accuracy3 = accuracy_score(y_true=val_out, y_pred=predictions3)
    acc_tuple = accuracies.get("PAC", (0,0))
    accuracies["PAC"] = (acc_tuple[0] + accuracy3, acc_tuple[1] + 1)

    # part 4
    model = SVC()
    search_grid = [
        {"kernel": ["poly", "linear", "rbf", "sigmoid"], "gamma": ["auto", "scale"]},
        {"kernel": ["poly"], "degree": [1,2,3,4,5, 10, 15, 20, 25, 30, 40], "gamma":["auto", "scale"]}
    ]

    SVM_model = GridSearchCV(estimator = model, param_grid=search_grid)
    SVM_model.fit(X=train_in, y=train_out)
    predictions_SVM = SVM_model.predict(X=val_in)
    SVM_accuracy = accuracy_score(y_true=val_out, y_pred=predictions_SVM)
    acc_tuple = accuracies.get(str(SVM_model.best_params_), (0,0))
    accuracies[str(SVM_model.best_params_)] = (acc_tuple[0] + SVM_accuracy, acc_tuple[1] + 1)

    # part 5
    print(accuracies)

for model in accuracies:
    (cummulative_acc, number) = accuracies[model]
    precision = cummulative_acc/number
    print("accuracy of model ", model, "in ", number, " times: ", precision)

# part 6 execute on given dataset
model = SVC()
optimal_params = [
    {"kernel": ["poly"], "degree": [2], "gamma": ["scale"]}
]
optimal_SVM_model = GridSearchCV(estimator = model, param_grid=optimal_params)

data_in, test_in, data_out, test_out = train_test_split(inputs, emotions, test_size=0.15, stratify=emotions) # test = 15%, data= 85%
train_in, val_in, train_out, val_out = train_test_split(data_in, data_out, test_size=0.2) # val is 0.85*0.2 = 0.17 -> 17 %, train is 68%
optimal_SVM_model.fit(X=train_in, y=train_out)

hand_in_data = pd.read_csv("test_to_submit.csv")
hand_in_prediction = optimal_SVM_model.predict(X=hand_in_data)

df = pd.DataFrame(hand_in_prediction)
df.to_csv("output", index=False)