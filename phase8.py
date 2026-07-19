import os
from datetime import datetime
import matplotlib
matplotlib.use("Agg")  # lets us save charts as images without opening a window
import matplotlib.pyplot as plt
import phase1_config
import phase1_database
def save_chart(fig, chart_name):
    os.makedirs(phase1_config.charts_f, exist_ok=True)
    chart_path = os.path.join(phase1_config.charts_f, chart_name)
    fig.savefig(chart_path, bbox_inches="tight")
    plt.close(fig)
    print("Chart saved:", chart_path)
    return chart_path
def plot_feature_distributions(data_frame, numeric_columns):
    """
    Draws a histogram for every numeric column.
    A histogram shows HOW the values are spread out.
    """
    for column in numeric_columns:
        figure = plt.figure()
        data_frame[column].hist(bins=20)
        plt.title(f"Distribution of {column}")
        plt.xlabel(column)
        plt.ylabel("Frequency")
        save_chart(figure, f"distribution_{column}.png")


def plot_category_frequencies(data_frame, categorical_columns):
    """
    Draws a bar chart showing how many times each category appears.
    """
    for column in categorical_columns:
        figure = plt.figure()
        data_frame[column].value_counts().head(10).plot(kind="bar")
        plt.title(f"Top Categories in {column}")
        plt.xlabel(column)
        plt.ylabel("Count")
        save_chart(figure, f"category_{column}.png")


def plot_correlation_matrix(data_frame, numeric_columns):
    """
    Draws a heatmap showing how strongly numeric columns relate to each other.
    """
    if len(numeric_columns) < 2:
        return

    figure = plt.figure()
    correlation_matrix = data_frame[numeric_columns].corr()
    plt.imshow(correlation_matrix, cmap="coolwarm", interpolation="nearest")
    plt.colorbar()
    plt.xticks(range(len(numeric_columns)), numeric_columns, rotation=90)
    plt.yticks(range(len(numeric_columns)), numeric_columns)
    plt.title("Correlation Heatmap")
    save_chart(figure, "correlation_heatmap.png")


def plot_outliers(data_frame, numeric_columns):
    """
    Draws a box plot for each numeric column.
    Box plots make it easy to SEE outliers (unusual extreme values).
    """
    for column in numeric_columns:
        figure = plt.figure()
        plt.boxplot(data_frame[column].dropna())
        plt.title(f"Outlier Check for {column}")
        save_chart(figure, f"boxplot_{column}.png")


def generate_written_insights(data_frame, numeric_columns, categorical_columns):
    """
    Converts basic statistics into simple English sentences.
    This is what makes the tool feel "intelligent" instead of just
    showing raw numbers.
    """
    insights = []

    # Insight about the numeric column with the biggest average value
    if numeric_columns:
        averages = data_frame[numeric_columns].mean()
        top_column = averages.idxmax()
        insights.append(
            f"On average, '{top_column}' has the highest value among numeric columns "
            f"(average = {averages[top_column]:.2f})."
        )

    # Insight about the most common category
    if categorical_columns:
        first_cat_column = categorical_columns[0]
        most_common_value = data_frame[first_cat_column].mode()
        if len(most_common_value) > 0:
            insights.append(
                f"The most common value in '{first_cat_column}' is "
                f"'{most_common_value[0]}'."
            )

    # Insight about missing data
    missing_total = int(data_frame.isnull().sum().sum())
    if missing_total > 0:
        insights.append(f"The dataset still has {missing_total} missing values to be aware of.")
    else:
        insights.append("The dataset has no missing values remaining.")

    return insights


def explore_dataset(data_frame, numeric_columns, categorical_columns, session_id):
    """
    Main function for Phase 9.
    Draws all charts and saves written insights to the database.
    """
    print("\n----- EXPLORATORY DATA ANALYSIS -----")

    plot_feature_distributions(data_frame, numeric_columns)
    plot_category_frequencies(data_frame, categorical_columns)
    plot_correlation_matrix(data_frame, numeric_columns)
    plot_outliers(data_frame, numeric_columns)

    insights = generate_written_insights(data_frame, numeric_columns, categorical_columns)

    print("\nInsights:")
    now = datetime.now()
    for insight_text in insights:
        print("-", insight_text)
        phase1_database.run_query(
            "INSERT INTO insights (session_id, insight_text, created_on) VALUES (%s, %s, %s)",
            (session_id, insight_text, now)
        )

    print("--------------------------------------\n")
    return insights