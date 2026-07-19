def rank_regression_winner(results):
    sr = sorted(results, key=lambda item: item["r2"], reverse=True)
    winner = sr[0]
    exp = (
        f"{winner['model_name']} was selected as the best model because it achieved --\n"
        f"The highest R^2 score of {winner['r2']*100:.1f}% of the pattern in the data\n"
        f"It also had a training time of {winner['training_time']:.4f} seconds"
    )
    return exp


def rank_winner_class(results):
    sr = sorted(results, key=lambda item: item["accuracy"], reverse=True)
    winner = sr[0]
    exp = (
        f"{winner['model_name']} was selected as the best model because it achieved --\n"
        f"The highest accuracy of {winner['accuracy']*100:.1f}%\n"
        f"It also had a training time of {winner['training_time']:.4f} seconds"
    )
    return exp


def comp_reg_class(results):
    print("________MODEL BENCHMARKING CLASSIFICATION___________\n")
    for item in results:
        print(f"{item['model_name']}: accuracy={item['accuracy']:.4f}, training time={item['training_time']:.4f}s")
    return results

