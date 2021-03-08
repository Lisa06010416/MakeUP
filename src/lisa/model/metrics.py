from sklearn.metrics import accuracy_score


def acc_metrics(pred):
    labels = pred.label_ids
    try:
        preds = pred.predictions.argmax(-1)
    except:
        preds = pred.predictions[0].argmax(-1)
    acc = accuracy_score(labels, preds)
    return {
        'accuracy': acc
    }