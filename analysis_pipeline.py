import re
from pathlib import Path
import pandas as pd
from scipy.stats import chi2_contingency

GEOAI_TITLE_PATTERNS = [
    r'\bgeoai\b',
    r'\bgeospatial\b',
    r'\bspatial\b',
    r'\bgis\b'
]

HEALTH_TITLE_PATTERNS = [
    r'\bhealth\b',
    r'\bpublic\s+health\b',
    r'\bepidemiolog(?:y|ical)\b',
    r'\bvulnerability\b',
    r'\bdisease\b',
    r'\brisk\b',
    r'\bsurveillance\b',
    r'\bdisparit(?:y|ies)\b',
    r'\binequalit(?:y|ies)\b',
    r'\bexposure\b',
    r'\baccessibilit(?:y|ies)\b'
]

EXCLUDE_NON_HEALTH_PATTERNS = [
    r'\bagricultur(?:e|al)\b',
    r'\beducation\b',
    r'\bwaste\b',
    r'\benergy\b'
]

GOVERNANCE_CORE_PATTERNS = [
    r'\bbias\b',
    r'\bequit(?:y|ies)\b',
    r'\bgovernance\b',
    r'\bethic(?:s|al)?\b'
]

DICTIONARIES = {
    'governance': [
        r'\bgovernance\b', r'\baccountab(?:le|ility)\b', r'\bcontestab(?:le|ility)\b',
        r'\bfair(?:ness)?\b', r'\bequit(?:y|ies)\b', r'\bbias\b', r'\bethic(?:s|al)?\b'
    ],
    'validation': [
        r'\bvalidat(?:e|ed|ion)\b', r'\bcalibrat(?:e|ion)\b', r'\brobust(?:ness)?\b',
        r'\bgenerali[sz](?:e|ation|ability)\b', r'\btransferab(?:le|ility)\b', r'\bcross[- ]validation\b'
    ],
    'intelligence': [
        r'\bdata\b', r'\bcoverage\b', r'\bmissing(?:ness)?\b', r'\bprovenance\b',
        r'\bpopulation(?:s)?\b', r'\bterritor(?:y|ial|ies)\b', r'\brepresentation\b'
    ],
    'processing': [
        r'\bfeature(?:s)?\b', r'\bproxy(?:ies)?\b', r'\baggregation\b', r'\bharmoni[sz](?:e|ation)\b',
        r'\bspatial\s+unit(?:s)?\b', r'\bvariable(?:s)?\b', r'\bpreprocess(?:ing)?\b'
    ],
    'design': [
        r'\bmodel(?:s)?\b', r'\bclassification\b', r'\bprediction(?:s)?\b', r'\bmachine\s+learning\b',
        r'\bdeep\s+learning\b', r'\bcnn\b', r'\bneural\s+network(?:s)?\b', r'\bgraph\s+neural\s+network(?:s)?\b'
    ],
    'choice': [
        r'\ballocation\b', r'\btarget(?:ing|ed)?\b', r'\bintervention(?:s)?\b', r'\bdecision(?:s)?\b',
        r'\boverride\b', r'\bappeal(?:s)?\b', r'\bresource(?:s)?\b', r'\bprioriti[sz](?:e|ation)\b'
    ],
    'urban': [r'\burban\b', r'\bcity\b', r'\bcities\b', r'\bmetropolitan\b', r'\bsuburban\b'],
    'rural': [r'\brural\b', r'\bremote\b', r'\bperipher(?:y|al)\b', r'\bnonurban\b']
}


def find_col(df, options):
    cols = {c.lower(): c for c in df.columns}
    for opt in options:
        if opt.lower() in cols:
            return cols[opt.lower()]
    for c in df.columns:
        low = c.lower()
        if any(opt.lower() in low for opt in options):
            return c
    return None


def compile_union(patterns):
    return re.compile('|'.join(patterns), flags=re.I)


def text_join(df, cols):
    present = [c for c in cols if c in df.columns and c is not None]
    if not present:
        return pd.Series([''] * len(df), index=df.index)
    return df[present].fillna('').astype(str).agg(' '.join, axis=1).str.lower()


def load_scopus_csv(path):
    df = pd.read_csv(path)
    title = find_col(df, ['Title'])
    abstract = find_col(df, ['Abstract'])
    keywords = find_col(df, ['Author Keywords', 'Index Keywords', 'Keywords'])
    eid = find_col(df, ['EID'])
    doi = find_col(df, ['DOI'])

    df = df.copy()
    for col in [title, abstract, keywords, eid, doi]:
        if col and col not in df.columns:
            df[col] = ''

    df['title_norm'] = df[title].fillna('').astype(str).str.strip().str.lower() if title else ''
    df['doi_norm'] = df[doi].fillna('').astype(str).str.strip().str.lower() if doi else ''
    df['eid_norm'] = df[eid].fillna('').astype(str).str.strip().str.lower() if eid else ''
    df['text_all'] = text_join(df, [title, abstract, keywords])
    df['text_title'] = text_join(df, [title])
    return df


def deduplicate(df):
    df = df.copy()
    before = len(df)
    if 'doi_norm' in df.columns:
        nonempty = df['doi_norm'].ne('')
        df = pd.concat([
            df.loc[nonempty].drop_duplicates(subset=['doi_norm'], keep='first'),
            df.loc[~nonempty]
        ], axis=0).sort_index()
    if 'eid_norm' in df.columns:
        nonempty = df['eid_norm'].ne('')
        df = pd.concat([
            df.loc[nonempty].drop_duplicates(subset=['eid_norm'], keep='first'),
            df.loc[~nonempty]
        ], axis=0).sort_index()
    df = df.drop_duplicates(subset=['title_norm'], keep='first')
    removed = before - len(df)
    return df, removed


def filter_geoai_core(df):
    pat = compile_union(GEOAI_TITLE_PATTERNS)
    return df[df['text_title'].str.contains(pat, na=False)].copy()


def filter_health_subset(df):
    include = compile_union(HEALTH_TITLE_PATTERNS)
    exclude = compile_union(EXCLUDE_NON_HEALTH_PATTERNS)
    out = df[df['text_title'].str.contains(include, na=False)].copy()
    out = out[~out['text_title'].str.contains(exclude, na=False)].copy()
    return out


def filter_governance_core(df):
    pat = compile_union(GOVERNANCE_CORE_PATTERNS)
    return df[df['text_all'].str.contains(pat, na=False)].copy()


def apply_dictionary_flags(df):
    df = df.copy()
    for name, patterns in DICTIONARIES.items():
        pat = compile_union(patterns)
        df[name] = df['text_all'].str.contains(pat, na=False).astype(int)
    return df


def summarize_flags(df, label):
    row = {'subset': label, 'n': len(df)}
    for name in DICTIONARIES:
        row[name] = round(df[name].mean() * 100, 1) if len(df) else 0.0
    return row


def chi_square_binary(df, subset_mask, flag):
    a = int(df.loc[subset_mask, flag].sum())
    b = int(subset_mask.sum() - a)
    c = int(df.loc[~subset_mask, flag].sum())
    d = int((~subset_mask).sum() - c)
    table = [[a, b], [c, d]]
    chi2, p, dof, exp = chi2_contingency(table)
    n = sum(map(sum, table))
    v = (chi2 / n) ** 0.5 if n else float('nan')
    return {'flag': flag, 'chi2': chi2, 'p': p, 'dof': dof, 'cramers_v': v, 'table': table}


def run_pipeline(input_csv, out_dir='output/repo_results'):
    out = Path(out_dir)
    out.mkdir(parents=True, exist_ok=True)

    df0 = load_scopus_csv(input_csv)
    df1, removed = deduplicate(df0)
    df_geo = filter_geoai_core(df1)
    df_health = filter_health_subset(df1)
    df_ph = filter_health_subset(df_geo)
    df_gov = filter_governance_core(df_ph)

    df1 = apply_dictionary_flags(df1)
    df_health_flags = df1[df1.index.isin(df_health.index)].copy()
    df_ph_flags = df1[df1.index.isin(df_ph.index)].copy()

    subset_mask = df1.index.isin(df_health.index)
    chi_rows = [chi_square_binary(df1, subset_mask, flag) for flag in ['governance','validation','choice','rural']]

    summary = pd.DataFrame([
        summarize_flags(df1, 'all_corpus'),
        summarize_flags(df_health_flags, 'health_related_subset'),
        summarize_flags(df_ph_flags, 'stricter_public_health_subset')
    ])
    summary.to_csv(out / 'table6_reconstructed.csv', index=False)

    pd.DataFrame([{
        'initial_records': len(df0),
        'deduplicated_records': len(df1),
        'duplicates_removed': removed,
        'geoai_core_records': len(df_geo),
        'health_related_records': len(df_health),
        'stricter_public_health_records': len(df_ph),
        'governance_core_records': len(df_gov)
    }]).to_csv(out / 'prisma_counts_reconstructed.csv', index=False)

    pd.DataFrame(chi_rows).drop(columns=['table']).to_csv(out / 'chi_square_results.csv', index=False)

    for name, frame in {
        'deduplicated_corpus': df1,
        'geoai_core': df_geo,
        'health_related_subset': df_health,
        'public_health_subset': df_ph,
        'governance_core_subset': df_gov
    }.items():
        frame.to_csv(out / f'{name}.csv', index=False)

    return {
        'initial_records': len(df0),
        'deduplicated_records': len(df1),
        'duplicates_removed': removed,
        'geoai_core_records': len(df_geo),
        'health_related_records': len(df_health),
        'stricter_public_health_records': len(df_ph),
        'governance_core_records': len(df_gov)
    }


if __name__ == '__main__':
    import argparse
    parser = argparse.ArgumentParser()
    parser.add_argument('--input', required=True, help='Path to Scopus CSV export')
    parser.add_argument('--out', default='output/repo_results', help='Output directory')
    args = parser.parse_args()
    result = run_pipeline(args.input, args.out)
    print(result)
