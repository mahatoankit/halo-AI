import pandas as pd
import os

# Get the directory of the Excel file
excel_file_path = '/home/ankit/WindowsFuneral/Hackathons/IdeaForImpact-25/Codebase/crop2.xlsx'
directory = os.path.dirname(excel_file_path)

# Read the Excel file
df = pd.read_excel(excel_file_path)

# Create CSV file path in the same directory
csv_file_path = os.path.join(directory, 'crop2.csv')

# Save as CSV
df.to_csv(csv_file_path, index=False)

print(f"Successfully converted {excel_file_path} to {csv_file_path}")
print(f"Dataset shape: {df.shape}")
print(f"Columns: {list(df.columns)}")