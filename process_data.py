import pandas as pd
import numpy as np

# define required columns for the plots, output dataset feeding to app
subset_cols = ['year','set_num','name','parent_theme_name','num_parts']
output_dataset = './data/processed/op_data.csv'

sets_data = pd.read_csv('data/sets.csv')
themes_data = pd.read_csv('data/themes.csv')

# set final parent theme id for themes
themes_data['parent_id_final'] = themes_data\
    .apply(lambda x: x['id'] if pd.isnull(x['parent_id']) else x['parent_id'],axis=1)

# merge in parent theme name
themes_data['parent_name'] = themes_data[['parent_id_final','id']].\
    merge(themes_data[['id','name']],left_on='parent_id_final',right_on='id',how='inner')['name']

# bring in parent theme name into the lego sets dataset
sets_data['parent_theme_name'] = sets_data.\
    merge(themes_data,left_on='theme_id',right_on='id',how='left')['parent_name']

# write to disk
sets_data[subset_cols].to_csv(output_dataset,index=False)