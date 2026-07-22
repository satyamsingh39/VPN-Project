import json

with open("models/vpn_detector/feature_columns.json", "r") as f:
    features = json.load(f)

print(f"Number of features: {len(features)}")
print("\nFeatures:\n")

for i, feature in enumerate(features, 1):
    print(f"{i}. {feature}")