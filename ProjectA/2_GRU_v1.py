import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader, random_split
from sklearn.metrics import classification_report, confusion_matrix
import matplotlib.pyplot as plt

#===== VARIABLES & CONFIG =====
DATA_PATH = "/Users/noorelbanna/Desktop/ProjectMUSEEG/Experiment/StimuliSet/epochs/"
BATCH_SIZE = 32
EPOCHS = 50
LR = 1e-3
HIDDEN_SIZE = 64
NUM_LAYERS = 2
DROPOUT = 0.3
SEED = 42

torch.manual_seed(SEED)
device = torch.device(
    "mps"  if torch.backends.mps.is_available() else
    "cuda" if torch.cuda.is_available()         else
    "cpu"
)
print(f"Using device: {device}")

#====== DATASET ======
class EEGDataset(Dataset):
    def __init__(self, X, y):
        self.X = torch.tensor(X, dtype=torch.float32)
        self.y = torch.tensor(y, dtype=torch.float32)

    def __len__(self):
        return len(self.y)

    def __getitem__(self, idx):
        return self.X[idx], self.y[idx]



#===== MODEL =====
class EEG_GRU(nn.Module):
    """
    Input:  (batch, timesteps, channels)   e.g. (32, 250, 16)
    Output: (batch,)  —  probability of positive state
    """
    def __init__(self, input_size, hidden_size, num_layers, dropout):
        super().__init__()

        self.gru = nn.GRU(
            input_size = input_size,
            hidden_size = hidden_size,
            num_layers = num_layers,
            batch_first = True,
            dropout = dropout if num_layers > 1 else 0.0,
        )

        self.classifier = nn.Sequential(
            nn.Linear(hidden_size, 32),
            nn.ReLU(),
            nn.Dropout(dropout),
            nn.Linear(32, 1),     
        )

    def forward(self, x):
        # x: (batch, timesteps, channels)
        out, _ = self.gru(x)           # out: (batch, timesteps, hidden)
        last = out[:, -1, :]        # take the final timestep
        logit = self.classifier(last).squeeze(1)
        return logit
    
#===== TRAINING & EVALUATION =====
def train_one_epoch(model, loader, optimizer, criterion):
    model.train()
    total_loss, correct = 0, 0
    for X_batch, y_batch in loader:
        X_batch, y_batch = X_batch.to(device), y_batch.to(device)
        optimizer.zero_grad()
        logits = model(X_batch)
        loss   = criterion(logits, y_batch)
        loss.backward()
        optimizer.step()
        total_loss += loss.item() * len(y_batch)
        correct    += ((logits > 0).float() == y_batch).sum().item()
    n = len(loader.dataset)
    return total_loss / n, correct / n


@torch.no_grad()
def evaluate(model, loader, criterion):
    model.eval()
    total_loss, correct = 0, 0
    all_preds, all_labels = [], []
    for X_batch, y_batch in loader:
        X_batch, y_batch = X_batch.to(device), y_batch.to(device)
        logits = model(X_batch)
        loss   = criterion(logits, y_batch)
        total_loss += loss.item() * len(y_batch)
        preds  = (logits > 0).float()
        correct += (preds == y_batch).sum().item()
        all_preds.extend(preds.cpu().numpy())
        all_labels.extend(y_batch.cpu().numpy())
    n = len(loader.dataset)
    return total_loss / n, correct / n, np.array(all_preds), np.array(all_labels)

#===== MAIN SCRIPT =====
if __name__ == "__main__":

    # Load data
    X = np.load(DATA_PATH + "X_all.npy") # (N, timesteps, channels)
    y = np.load(DATA_PATH + "y_all.npy") # (N,)
    print(f"Loaded — X: {X.shape}  y: {y.shape}")

    INPUT_SIZE = X.shape[2] # number of EEG channels (16)

    # Split 70 / 15 / 15
    dataset  = EEGDataset(X, y)
    n        = len(dataset)
    n_train  = int(0.70 * n)
    n_val    = int(0.15 * n)
    n_test   = n - n_train - n_val

    train_set, val_set, test_set = random_split(
        dataset, [n_train, n_val, n_test],
        generator=torch.Generator().manual_seed(SEED)
    )

    train_loader = DataLoader(train_set, batch_size=BATCH_SIZE, shuffle=True)
    val_loader   = DataLoader(val_set,   batch_size=BATCH_SIZE)
    test_loader  = DataLoader(test_set,  batch_size=BATCH_SIZE)

    print(f"Split — Train: {n_train}  Val: {n_val}  Test: {n_test}")

    # Class imbalance weight
    # Count positives/negatives in the TRAINING set only
    train_labels = np.array([dataset[i][1].item() for i in train_set.indices])
    pos_count    = (train_labels == 1).sum()
    neg_count    = (train_labels == 0).sum()
    pos_weight   = torch.tensor([neg_count / pos_count], dtype=torch.float32).to(device)
    print(f"pos_weight: {pos_weight.item():.3f}  (pos: {pos_count}, neg: {neg_count})")

    # Model, loss, optimiser
    model     = EEG_GRU(INPUT_SIZE, HIDDEN_SIZE, NUM_LAYERS, DROPOUT).to(device)
    criterion = nn.BCEWithLogitsLoss(pos_weight=pos_weight)   # penalise missed positives more
    optimizer = torch.optim.Adam(model.parameters(), lr=LR)
    scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau(optimizer, patience=5, factor=0.5)

    print(f"\nModel parameters: {sum(p.numel() for p in model.parameters()):,}")

    # Training
    history = {"train_loss": [], "val_loss": [], "train_acc": [], "val_acc": []}
    best_val_loss = float("inf")

    for epoch in range(1, EPOCHS + 1):
        tr_loss, tr_acc = train_one_epoch(model, train_loader, optimizer, criterion)
        vl_loss, vl_acc, _, _ = evaluate(model, val_loader, criterion)
        scheduler.step(vl_loss)

        history["train_loss"].append(tr_loss)
        history["val_loss"].append(vl_loss)
        history["train_acc"].append(tr_acc)
        history["val_acc"].append(vl_acc)

        if vl_loss < best_val_loss:
            best_val_loss = vl_loss
            torch.save(model.state_dict(), DATA_PATH + "best_gru.pt")

        if epoch % 5 == 0 or epoch == 1:
            print(f"Epoch {epoch:3d}/{EPOCHS}  "
                  f"Train loss: {tr_loss:.4f}  acc: {tr_acc:.3f}  |  "
                  f"Val loss: {vl_loss:.4f}  acc: {vl_acc:.3f}")

    # Test evaluation
    model.load_state_dict(torch.load(DATA_PATH + "best_gru.pt"))
    _, test_acc, preds, labels = evaluate(model, test_loader, criterion)

    print(f"\n{'='*50}")
    print(f"Test Accuracy: {test_acc:.4f}")
    print(f"\nClassification Report:")
    print(classification_report(labels, preds, target_names=["Negative", "Positive"]))
    print("Confusion Matrix:")
    print(confusion_matrix(labels, preds))

    # Plot learning curves
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(12, 4))

    ax1.plot(history["train_loss"], label="Train")
    ax1.plot(history["val_loss"],   label="Val")
    ax1.set_title("Loss")
    ax1.set_xlabel("Epoch")
    ax1.legend()

    ax2.plot(history["train_acc"], label="Train")
    ax2.plot(history["val_acc"],   label="Val")
    ax2.set_title("Accuracy")
    ax2.set_xlabel("Epoch")
    ax2.legend()

    plt.tight_layout()
    plt.savefig(DATA_PATH + "training_curves.png", dpi=150)
    plt.show()
    print("Saved training_curves.png")