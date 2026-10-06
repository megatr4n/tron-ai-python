import random
import joblib
import pandas as pd
from sklearn.neural_network import MLPRegressor
from game.state import TronState, P1, P2, ROWS, COLS

def generate_dataset(num_samples=5000):
    from game.state import LEVELS
    dataset = []
    for _ in range(num_samples):
        s = TronState(random.randint(0, len(LEVELS) - 1))
        s.p1 = (random.randint(1, ROWS - 2), random.randint(1, COLS // 2 - 1))
        s.p2 = (random.randint(1, ROWS - 2), random.randint(COLS // 2 + 1, COLS - 2))
        if s.p1 in s.walls or s.p2 in s.walls:
            continue
        dataset.append({'P1_DistCenter': abs(s.p1[0] - 8) + abs(s.p1[1] - 12), 'P2_DistCenter': abs(s.p2[0] - 8) + abs(s.p2[1] - 12), 'DistBetween': abs(s.p1[0] - s.p2[0]) + abs(s.p1[1] - s.p2[1]), 'P1_Moves': len(s.get_moves(P1)), 'P2_Moves': len(s.get_moves(P2)), 'TargetScore': (s.get_bfs_area(P1) - s.get_bfs_area(P2)) * 10})
    return pd.DataFrame(dataset)

def load_or_train_model(model_path):
    try:
        model = joblib.load(model_path)
        return model
    except Exception:
        print('Model not found. Generating dataset and training MLPRegressor...')
        df = generate_dataset()
        X = df[['P1_DistCenter', 'P2_DistCenter', 'DistBetween', 'P1_Moves', 'P2_Moves']]
        y = df['TargetScore']
        model = MLPRegressor(hidden_layer_sizes=(16, 16), max_iter=500, random_state=42)
        model.fit(X, y)
        joblib.dump(model, model_path)
        print('Training complete. Model saved.')
        return model
