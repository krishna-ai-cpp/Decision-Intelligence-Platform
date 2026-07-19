import os
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
from sklearn.metrics import confusion_matrix
import phase1_config


def save_chart(fig, name):
    os.makedirs(phase1_config.charts_f, exist_ok=True)
    path = os.path.join(phase1_config.charts_f, name)
    fig.savefig(path, bbox_inches="tight")
    plt.close(fig)
    return path


def plot_act_pred(y_test, pred):
    fig = plt.figure()
    plt.scatter(y_test, pred)
    plt.xlabel("Actual values")
    plt.ylabel("Predicted Values")
    plt.title("Actual VS Predicted")
    plt.grid(True)
    return save_chart(fig, "Actual vs predicted.png")


def plot_conf_mat(y_test, pred):
    cm = confusion_matrix(y_test, pred)
    fig = plt.figure()
    plt.imshow(cm, cmap="Blues")
    plt.xlabel("Confusion Matrix")
    plt.ylabel("Predicted Values")
    plt.title("Confusion Matrix VS Predicted")
    plt.grid(True)
    for r in range(cm.shape[0]):
        for c in range(cm.shape[1]):
            plt.text(r, c, str(cm[r, c]), ha="center", va="center")
    return save_chart(fig, "Confusion Matrix vs predicted.png")


def plot_feat_imp(imp):
    if not imp:
        return None
    names = [n for n, v in imp]
    val = [v for n, v in imp]
    fig = plt.figure()
    plt.barh(names, val)
    plt.xlabel("Importance")
    plt.title("Feature importance")
    plt.grid(True)
    return save_chart(fig, "feature_importance.png")


def plot_elbow_curve(k_values, inertia_values):
    """
    Shows the Elbow Curve used to pick the best number of clusters.
    """
    figure = plt.figure()
    plt.plot(list(k_values), inertia_values, marker="o")
    plt.xlabel("Number of Clusters (K)")
    plt.ylabel("Inertia")
    plt.title("Elbow Method for Optimal K")
    return save_chart(figure, "elbow_curve.png")


def plot_cluster_visualization(features, cluster_labels):
    """
    Draws a simple 2D scatter plot of the clusters using the first
    two numeric columns available, so the user can visually see the groups.
    """
    numeric_columns = features.select_dtypes(include="number").columns

    if len(numeric_columns) < 2:
        print("Not enough numeric columns to draw a 2D cluster chart.")
        return None

    x_column = numeric_columns[0]
    y_column = numeric_columns[1]

    figure = plt.figure()
    plt.scatter(features[x_column], features[y_column], c=cluster_labels, cmap="viridis")
    plt.xlabel(x_column)
    plt.ylabel(y_column)
    plt.title("Cluster Visualization")
    return save_chart(figure, "cluster_visualization.png")
