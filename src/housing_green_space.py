from pathlib import Path
import unicodedata
import pandas as pd
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from adjustText import adjust_text

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'data' / 'figures'
OUT.mkdir(parents=True, exist_ok=True)
plt.rcParams.update({'font.family': 'DejaVu Sans', 'font.size': 10,
                     'axes.spines.top': False, 'axes.spines.right': False,
                     'savefig.facecolor': 'white'})

def key(value):
    value = unicodedata.normalize('NFKD', str(value)).casefold()
    return ''.join(c for c in value if c.isalnum())

def load(name):
    df = pd.read_csv(ROOT / 'data' / name).rename(columns={'Borough': 'borough'})
    df['key'] = df.borough.map(key)
    assert not df.key.duplicated().any(), f'Duplicate boroughs in {name}'
    return df

def housing():
    df = load('housing_dataset.csv').sort_values('key').reset_index(drop=True)
    assert len(df) == 19
    return df

def save(fig, name, data):
    fig.savefig(OUT / (name + '.png'), dpi=200)
    plt.close(fig)
    print(f'{name}: saved PNG ({len(data)} boroughs)')

def scatter_panels(df, x, xlabel, title, note, name):
    fig, axes = plt.subplots(1, 2, figsize=(13, 8), sharex=True, sharey=True)
    fig.subplots_adjust(top=.84, bottom=.38, left=.08, right=.98, wspace=.12)
    for ax, bedrooms, color in zip(axes, (2, 3), ('#167d9a', '#b7642c')):
        y = f'median_monthly_shelter_cost_{bedrooms}br_cad'
        assert df[[x, y]].notna().all().all()
        ax.scatter(df[x], df[y], s=35, color=color, alpha=.85, edgecolor='white')
        texts=[]
        for i, row in df.iterrows():
            texts.append(ax.text(row[x], row[y], str(i+1), ha='center', va='center', fontsize=9, color=color))
        ax.set_title(f'{bedrooms}-bedroom homes', loc='left', fontweight='bold')
        ax.set_xlabel(xlabel)
        ax.margins(.10)
        ax.grid(alpha=.18)
        ax.set_axisbelow(True)
        adjust_text(texts, x=df[x].to_numpy(), y=df[y].to_numpy(), ax=ax,
                    iter_lim=300, arrowprops={'arrowstyle':'-', 'color':color,'lw':.6})
    axes[0].set_ylabel('Median monthly shelter cost in 2021 (CAD)')
    fig.suptitle(title, x=.08, ha='left', fontsize=16, fontweight='bold', y=.97)
    fig.text(.08, .91, 'Each numbered dot is one borough. Numbers follow alphabetical order, not a ranking.', fontsize=10)
    for start, xpos in ((0,.08),(7,.40),(14,.73)):
        labels=[f'{i+1:02d}  {df.iloc[i].borough}' for i in range(start,min(start+7,len(df)))]
        fig.text(xpos,.29,'\n'.join(labels),va='top',fontsize=8,linespacing=1.6)
    fig.text(.08,.025,note,fontsize=8,va='bottom')
    cols=['borough',x,'median_monthly_shelter_cost_2br_cad','median_monthly_shelter_cost_3br_cad']
    save(fig,name,df[cols])

"""Compare historical housing costs with the recorded park-area share."""

def main():
    df=housing().merge(load('parks_dataset.csv')[['key','green_area (%)']],on='key',how='left',validate='one_to_one')
    scatter_panels(df,'green_area (%)','Recorded park area (% of borough area)',
        'Does higher housing cost come with more green space?',
        'Sources: Montréal housing profiles (2021 Census) and the project’s parks dataset.\n'
        'Park area covers selected borough-managed parks, not all vegetation; park reference year is unconfirmed. Association is not causation.',
        'figure_1_housing_green_space')

if __name__=='__main__': main()
