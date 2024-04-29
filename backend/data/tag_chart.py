from numpy import dot
from numpy.linalg import norm
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

categories = {'Texture': 0, 'Finish': 1, 'Coverage': 2, 'Formula Benefits': 3,
              'Ingredient Focus': 4, 'Performance': 5,  "Color and Effect": 6, "Utility and Design": 7}
makeup_categories = {'Creamy': 'Texture', 'Lightweight': 'Texture', 'Heavy': 'Texture', 'Mousse': 'Texture', 'Gel': 'Texture', 'Liquid': 'Texture', 'Powder': 'Texture', 'Butter': 'Texture', 'Matte': 'Finish', 'Glossy': 'Finish', 'Dewy': 'Finish', 'Satin': 'Finish', 'Metallic': 'Finish', 'Frosted': 'Finish', 'Velvety': 'Finish', 'Radiant': 'Finish', 'Sheer': 'Coverage', 'Full coverage': 'Coverage', 'Medium coverage': 'Coverage', 'Buildable': 'Coverage', 'Natural': 'Coverage', 'Hydrating': 'Formula Benefits', 'Moisturizing': 'Formula Benefits', 'Nourishing': 'Formula Benefits', 'Repairing': 'Formula Benefits', 'Soothing': 'Formula Benefits', 'Antioxidant-rich': 'Formula Benefits', 'Pore-minimizing': 'Formula Benefits', 'Exfoliating': 'Formula Benefits', 'Color-correcting': 'Formula Benefits', 'Broad-spectrum': 'Formula Benefits', 'Collagen-boosting': 'Formula Benefits', 'Elasticizing': 'Formula Benefits', 'Plumping': 'Formula Benefits', 'Lifting': 'Formula Benefits', 'Firming': 'Formula Benefits', 'pH-balancing': 'Formula Benefits', 'Redness-reducing': 'Formula Benefits', 'Wrinkle-concealing': 'Formula Benefits', 'Protective': 'Formula Benefits', 'Sealing': 'Formula Benefits', 'Primer': 'Formula Benefits', 'Second-skin': 'Formula Benefits', 'Breathable': 'Formula Benefits', 'Vegan': 'Ingredient Focus', 'Cruelty-free': 'Ingredient Focus',
                     'Organic': 'Ingredient Focus', 'Chemical-free': 'Ingredient Focus', 'Paraben-free': 'Ingredient Focus', 'Silicone-free': 'Ingredient Focus', 'Gluten-free': 'Ingredient Focus', 'Alcohol-free': 'Ingredient Focus', 'Mineral-based': 'Ingredient Focus', 'Long-lasting': 'Performance', 'Smudge-proof': 'Performance', 'Waterproof': 'Performance', 'Budge-proof': 'Performance', 'Streak-free': 'Performance', 'Non-greasy': 'Performance', 'Fade-resistant': 'Performance', 'Humidity-resistant': 'Performance', 'Shimmery': 'Color and Effect', 'Glittery': 'Color and Effect', 'Pigmented': 'Color and Effect', 'Brightening': 'Color and Effect', 'Tinted': 'Color and Effect', 'Iridescent': 'Color and Effect', 'Holographic': 'Color and Effect', 'Color-rich': 'Color and Effect', 'Multi-purpose': 'Utility and Design', 'Specialty': 'Utility and Design', 'Budget-friendly': 'Utility and Design', 'Professional-grade': 'Utility and Design', 'Beginner-friendly': 'Utility and Design', 'Reusable': 'Utility and Design', 'Disposable': 'Utility and Design', 'Compact': 'Utility and Design', 'Travel-sized': 'Utility and Design', 'Full-sized': 'Utility and Design', 'Refillable': 'Utility and Design', 'Customizable': 'Utility and Design', 'Classic': 'Utility and Design', 'Modern': 'Utility and Design', 'Retro': 'Utility and Design', 'Trendy': 'Utility and Design', 'Timeless': 'Utility and Design'}
# compare meaning of input words to meaning of each category


def generate_graphs(input, rel_products):
    """
    input: dictionary for an input. keys are product_name, tags, tag_vector
    relevant_products: dictionary of rel products. keys are product_name, tags, tag_vector 
    """
    if input['product_name'] != '':
        sim_scores = get_sim_scores(input['tags'], rel_products)
    # input =


def get_sim_scores(tags, rel_product):
    sim_scores = [0] * 8
    # for category in makeup_categories:


def make_fig(data):
    df = pd.DataFrame(data)
    fig = px.line_polar(df, r="sim_scores",
                        theta="categories",
                        line_close=True,
                        color_discrete_sequence=["#ee0db3", "#eabee6"],
                        )
    fig.update_layout(
        polar=dict(
            bgcolor='white',
            angularaxis_showgrid=True,
            radialaxis_gridwidth=0,
            radialaxis=dict(range=[0, 1.01], showticklabels=False,
                            gridcolor="#eabee6", gridwidth=2),
            gridshape='linear',
            radialaxis_showticklabels=False,
            radialaxis_showline=False,  # Show radial axis line
            radialaxis_tickcolor='white',
        ),
        font=dict(color='black', size=15),
        paper_bgcolor='white',
        polar_angularaxis_showline=True,
    )

    # Fill with blue color with 30% opacity
    fig.update_traces(fill='toself', fillcolor='rgba(245,118,212,0.5)')
    fig.show()
    return fig


data = {'categories': list(makeup_categories.keys()),
        'sim_scores': [0.8, 0.6, 0.9, 0.7, 0.5, 0.4, 0.6, 0.85]
        }
# make_fig(data)
