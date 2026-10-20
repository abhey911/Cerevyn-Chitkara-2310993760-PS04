"""Evaluate the transparent rule-based baseline on the held-out 10 sample tickets."""
import json
import sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
from main import classify

data = json.loads((ROOT / "sample_data" / "tickets.json").read_text())
test_set = data[20:]  # Keep S001-S020 out of this simple holdout evaluation.
correct = 0
for row in test_set:
    predicted, confidence = classify(row["message"])
    is_correct = predicted == row["label"]
    correct += is_correct
    print(f'{row["ticket_id"]}: expected={row["label"]}, predicted={predicted}, correct={is_correct}, confidence={confidence:.2f}')
print(f"Accuracy: {correct}/{len(test_set)} = {correct/len(test_set):.1%}")
print("Note: this is a small synthetic holdout; it is not evidence of production performance.")
