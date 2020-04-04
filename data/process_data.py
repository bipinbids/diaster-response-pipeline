import sys

import pandas as pd

from sqlalchemy import create_engine

def load_data(messages_filepath, categories_filepath):
    messages_data = pd.read_csv(messages_filepath)
    categories_data = pd.read_csv(categories_filepath)
    df = messages_data.merge(categories_data, on='id')
    return df


def clean_data(df):
    categories_data = df['categories'].str.split(pat=';', expand=True)
    colnames = []
    row = categories_data.loc[0]
    
    for entry in row:
        colnames.append(entry[:-2])
    category_colnames = colnames
    categories_data.columns = category_colnames
    print('Column names:', category_colnames)
    
    for column in categories_data:
        categories_data[column] = categories_data[column].str[-1:]
        categories_data[column] = categories_data[column].astype(int)
    df.drop('categories', axis=1, inplace=True)
    df = pd.concat([df, categories_data], axis=1)
    df.drop_duplicates(inplace=True)
    df = df[df['related'] != 2]
    print('Duplicates remaining:', df.duplicated().sum())
    return df

def save_data(df, database):

    database_name = 'sqlite:///' + database
    database_engine = create_engine(database_name)
    df.to_sql('Disasters', database_engine, index=False) 


def main():
    if len(sys.argv) == 4:

        messages_filepath, categories_filepath, database_filepath = sys.argv[1:]

        print('Loading data...\n    MESSAGES: {}\n    CATEGORIES: {}'
              .format(messages_filepath, categories_filepath))
        df = load_data(messages_filepath, categories_filepath)

        print('Cleaning data...')
        df = clean_data(df)
        
        print('Saving data...\n    DATABASE: {}'.format(database_filepath))
        save_data(df, database_filepath)
        
        print('Cleaned data saved to database!')
    
    else:
        print('Please provide the filepaths of the messages and categories '\
              'datasets as the first and second argument respectively, as '\
              'well as the filepath of the database to save the cleaned data '\
              'to as the third argument. \n\nExample: python process_data.py '\
              'disaster_messages.csv disaster_categories.csv '\
              'DisasterResponse.db')


if __name__ == '__main__':
    main()