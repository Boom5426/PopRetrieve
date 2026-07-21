import pandas as pd
import json
import re

# --- repo-root path resolution (added for public release; replaces hardcoded /data/boom/DART) ---
from pathlib import Path as _P
REPO = _P(__file__).resolve().parents[2]
SRC = str(REPO / "src")
RESULTS_AUDIT = str(REPO / "results" / "upgrade")
DATA_PROC = str(REPO / "data" / "processed")
DATA_ANNO = str(REPO / "data" / "annotation")
# ------------------------------------------------------------------------------------------------

LINE_MAP = {'A549': 'A549', 'K562': 'K-562', 'MCF7': 'MCF7'}

with open(str(_P(RESULTS_AUDIT) / 'sciplex3_drugs.json')) as f:
    sp_drugs = json.load(f)
print(f"SciPlex3 drugs: {len(sp_drugs)}")

df1 = pd.read_excel(str(_P(RESULTS_AUDIT) / 'GDSC1_fitted_dose_response.xlsx'))
df2 = pd.read_excel(str(_P(RESULTS_AUDIT) / 'GDSC2_fitted_dose_response.xlsx'))

# Filter to our cell lines only (for speed)
our_lines = list(LINE_MAP.values())
df1 = df1[df1['CELL_LINE_NAME'].isin(our_lines)].copy()
df2 = df2[df2['CELL_LINE_NAME'].isin(our_lines)].copy()
print(f"GDSC1 rows for our lines: {len(df1)}")
print(f"GDSC2 rows for our lines: {len(df2)}")

all_gdsc_drugs = set(df1['DRUG_NAME'].unique()) | set(df2['DRUG_NAME'].unique())
print(f"Unique GDSC drugs across our lines: {len(all_gdsc_drugs)}")

def normalize(name):
    if not isinstance(name, str):
        return ''
    n = name.lower().strip()
    for suffix in [' hydrochloride', ' hcl', ' dihydrochloride', ' mesylate', ' maleate',
                   ' fumarate', ' tosylate', ' citrate', ' sodium', ' potassium',
                   ' acetate', ' succinate', ' tartrate', ' sulfate', ' phosphate',
                   ' disodium', ' calcium', ' bromide', ' chloride', ' nitrate',
                   ' trifluoroacetate']:
        n = n.replace(suffix, '')
    n = re.sub(r'\([^)]*\)', '', n)
    n = re.sub(r'[-\s_]+', '', n)
    return n

# Build normalized GDSC lookup
gdsc_norm = {}
for name in all_gdsc_drugs:
    norm = normalize(str(name))
    if norm:
        gdsc_norm[norm] = str(name)

# Also build a lookup by chembl_id if GDSC has any (they don't in dose-response file)
# So we rely on name matching

# Match
matches = {}
unmatched = []
for d in sp_drugs:
    sp_name = d['drug_name']
    sp_norm = normalize(sp_name)
    
    matched = False
    # Exact normalized match
    if sp_norm in gdsc_norm:
        matches[sp_name] = {'gdsc_name': gdsc_norm[sp_norm], 'method': 'normalized_name_exact'}
        matched = True
    else:
        # Try without digits (some GDSC drugs are just numeric IDs)
        # Try substring matching for known aliases
        for gdsc_n, gdsc_orig in gdsc_norm.items():
            if len(sp_norm) > 3 and (sp_norm in gdsc_n or gdsc_n in sp_norm):
                # substring match, but be careful with short names
                if abs(len(sp_norm) - len(gdsc_n)) <= 3:
                    matches[sp_name] = {'gdsc_name': gdsc_orig, 'method': 'normalized_name_substr'}
                    matched = True
                    break
    
    if not matched:
        unmatched.append(sp_name)

print(f"\nMatched: {len(matches)}/{len(sp_drugs)}")
print(f"Unmatched: {len(unmatched)}")

# Build result table
results = []
for sp_name, info in matches.items():
    gdsc_name = info['gdsc_name']
    method = info['method']
    
    for sp_line, gdsc_line in LINE_MAP.items():
        rows2 = df2[(df2['DRUG_NAME'] == gdsc_name) & (df2['CELL_LINE_NAME'] == gdsc_line)]
        rows1 = df1[(df1['DRUG_NAME'] == gdsc_name) & (df1['CELL_LINE_NAME'] == gdsc_line)]
        
        if len(rows2) > 0:
            row = rows2.iloc[0]
            results.append({
                'sp_drug': sp_name, 'gdsc_drug': gdsc_name, 'cell_line': sp_line,
                'gdsc_cell_line': gdsc_line, 'gdsc_source': 'GDSC2',
                'match_method': method,
                'AUC': float(row['AUC']), 'LN_IC50': float(row['LN_IC50']),
                'DRUG_ID': int(row['DRUG_ID'])
            })
        elif len(rows1) > 0:
            row = rows1.iloc[0]
            results.append({
                'sp_drug': sp_name, 'gdsc_drug': gdsc_name, 'cell_line': sp_line,
                'gdsc_cell_line': gdsc_line, 'gdsc_source': 'GDSC1',
                'match_method': method,
                'AUC': float(row['AUC']), 'LN_IC50': float(row['LN_IC50']),
                'DRUG_ID': int(row['DRUG_ID'])
            })

match_df = pd.DataFrame(results)
print(f"\nTotal drug-cellline pairs: {len(match_df)}")
for ln in ['A549', 'K562', 'MCF7']:
    sub = match_df[match_df['cell_line'] == ln]
    print(f"  {ln}: {sub['sp_drug'].nunique()} matched drugs")

print("\nGDSC source:", match_df['gdsc_source'].value_counts().to_dict())
print("Match method:", match_df['match_method'].value_counts().to_dict())

match_df.to_csv(str(_P(RESULTS_AUDIT) / 'drug_match_table.csv'), index=False)

# Print matched drug names per cell line
for ln in ['A549', 'K562', 'MCF7']:
    sub = match_df[match_df['cell_line'] == ln]
    if len(sub) > 0:
        print(f"\n{ln} ({sub['sp_drug'].nunique()} drugs):")
        for _, r in sub.iterrows():
            print(f"  {r['sp_drug']} -> {r['gdsc_drug']} (AUC={r['AUC']:.4f}, IC50={r['LN_IC50']:.3f}, src={r['gdsc_source']})")

# Save unmatched
with open(str(_P(RESULTS_AUDIT) / 'unmatched_drugs.json'), 'w') as f:
    json.dump(unmatched, f, indent=2)
print(f"\nUnmatched: {unmatched[:50]}")

