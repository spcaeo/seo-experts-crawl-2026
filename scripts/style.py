import os
from matplotlib import font_manager as fm, pyplot as plt
FONTS = os.environ.get('STUDY_FONTS', '/workspace/toadstone/fonts')
for f in ('Inter-Regular', 'Inter-SemiBold', 'Inter-Bold', 'SpaceGrotesk-Bold', 'JetBrainsMono-Regular', 'JetBrainsMono-Bold'):
    p = os.path.join(FONTS, f + '.ttf')
    if os.path.exists(p): fm.fontManager.addfont(p)
BG, PANEL, INK, MUTED, GRID = '#0d1411', '#15201b', '#eaf2ec', '#93a89e', '#243229'
AMBER, MINT, CORAL, ORANGE, BLUE, VIOLET = '#f5b942', '#5ee3a1', '#ff6b6b', '#ff9f43', '#6cb6ff', '#b69cff'
ISSUE_COLORS = {'missing_meta_description': BLUE, 'missing_canonical': VIOLET, 'missing_h1': '#ffd166',
                'multiple_h1': '#f78fb3', 'pages_content_img_no_alt': MINT, 'broken_urls': CORAL, 'redirecting_internal_urls': ORANGE}
def apply():
    plt.rcParams.update({'font.family': 'Inter', 'figure.facecolor': BG, 'axes.facecolor': BG, 'savefig.facecolor': BG,
        'text.color': INK, 'axes.labelcolor': MUTED, 'xtick.color': MUTED, 'ytick.color': INK, 'axes.edgecolor': GRID,
        'axes.spines.top': False, 'axes.spines.right': False, 'axes.grid': True, 'grid.color': GRID, 'grid.linewidth': 0.8,
        'axes.axisbelow': True, 'font.size': 12})
