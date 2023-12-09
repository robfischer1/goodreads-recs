import logging
import sys
from collections import namedtuple

import numpy as np
import pandas as pd
import pyarrow as pa
from tqdm.auto import tqdm

from wrecksys.data.download import FileManager

logger = logging.getLogger(__name__)

UserHistory = namedtuple("UserHistory", ["history", "books", "ratings"])
UserContext = namedtuple("UserContext", ["context_id", "context_rating", "label_id"])

def format_works(books_source: FileManager,
                 authors_source: FileManager,
                 works_source: FileManager) -> pd.DataFrame:

    logger.info(' Processing book data.')
    books = books_source.dataframe(cols=['title', 'url', 'image_url', 'link', 'authors', 'book_id', 'work_id'])
    books['author_id'] = (
        books.pop('authors')
        .map(lambda x: x[0] if len(x) > 0 else None, na_action='ignore')
        .map(lambda x: int(x['author_id']) if isinstance(x, dict) else x, na_action='ignore')
        .astype(pd.ArrowDtype(pa.int32()))
    )
    books = books[~books['author_id'].isna()]

    logger.info(' Processing author data.')
    authors = authors_source.dataframe(cols=['author_id', 'name']).rename(columns={'name': 'author_name'})
    authors = authors[~authors['author_name'].isna()]
    books = books.merge(authors, how='left')
    del authors

    logger.info('Processing works data.')
    works = (
        works_source
        .dataframe(cols=['work_id', 'best_book_id', 'ratings_count', 'ratings_sum'])
        .rename(columns={'best_book_id': 'book_id'})
    )
    works['average_rating'] = round(works['ratings_sum'] / works['ratings_count'], 1)

    logger.info('Merging Book Files.')
    works = works[(works['work_id'].isin(books['work_id'].unique()))]
    works = works.merge(books, how='inner', on=['book_id', 'work_id'])
    works = works[~works.author_id.isna()]
    del books

    return works


def format_ratings(ratings_source: FileManager):
    logger.info(' Processing rating data.')
    df = ratings_source.dataframe(cols=['user_id', 'book_id', 'rating', 'date_updated'])
    return df[(df['rating'] >= 3)]


def filter_dataframes(ratings: pd.DataFrame, works: pd.DataFrame) -> tuple[pd.DataFrame, pd.DataFrame]:
    logger.info('Filtering Datasets')
    # Replace all the book_ids with the corresponding work_id
    work_id_mapping = works[['book_id', 'work_id']]
    ratings = ratings.merge(work_id_mapping, how='left').drop(columns='book_id')
    ratings = ratings[~ratings.work_id.isna()].drop_duplicates(subset=['user_id', 'work_id'])

    # Check the ratings distribution by book, and keep the top 20% most popular.
    book_view = ratings['work_id'].value_counts().reset_index().sort_values(by='count')
    top_books = book_view['count'].quantile(.8)
    book_view = book_view[(book_view['count'] > top_books)]
    ratings = ratings[ratings['work_id'].isin(book_view['work_id'])]

    # Check the book distribution by user, and keep the most active 20%
    user_view = ratings['user_id'].value_counts().reset_index().sort_values(by='count')
    top_users = user_view['count'].quantile(.8)
    user_view = user_view[(user_view['count'] > top_users)]
    ratings = ratings[ratings['user_id'].isin(user_view['user_id'])].reset_index(drop=True)
    del book_view, user_view

    # Create the Work Index
    logger.info('Reindexing Works')
    works = works[works.work_id.isin(ratings.work_id)].reset_index(drop=True)
    works = works.sort_values(by=['ratings_sum', 'ratings_count'], ascending=False).reset_index(drop=True)
    works['work_index'] = works.index + 1
    works['work_index'] = works['work_index'].astype(pd.ArrowDtype(pa.int32()))
    index_mapping = works[['work_id', 'work_index']]
    ratings = (
        ratings
        .merge(index_mapping, how='left')
        .drop(columns='work_id')
        .rename(columns={'work_index': 'work_id', 'date_updated': 'timestamp'})
        .reset_index(drop=True)
    )


    return ratings, works


def prepare_data(fm: dict[str, FileManager])  -> tuple[pd.DataFrame, pd.DataFrame]:
    work_df = format_works(fm['books'], fm['authors'], fm['works'])
    rate_df = format_ratings(fm['ratings'])
    rate_df, work_df = filter_dataframes(rate_df, work_df)
    return rate_df, work_df


def build_records(df: pd.DataFrame, min_length: int, max_length: int):
    context_ids = []
    context_ratings = []
    label_ids = []

    timeline = build_timelines(df)

    with tqdm(total=len(timeline),
              desc="Converting to records",
              file=sys.stdout,
              unit=' timelines') as conversion_progress:
        for user in timeline:
            if user.history < min_length:
                conversion_progress.update(1)
                continue
            user_context_ids, user_context_ratings, user_label_ids = build_contexts(user, min_length, max_length)
            context_ids.extend(user_context_ids)
            context_ratings.extend(user_context_ratings)
            label_ids.extend(user_label_ids)
            conversion_progress.update(1)

    return context_ids, context_ratings, label_ids


def build_timelines(df: pd.DataFrame) -> list[UserHistory]:
    timelines = []

    with tqdm(total=len(df.user_id.unique()),
              desc="Building user timelines",
              file=sys.stdout,
              unit=' users') as timeline_progress:
        for _, group in df.groupby('user_id', observed=True):
            books: list = group['work_id'].tolist()
            ratings: list = group['rating'].tolist()
            size: int = len(books)
            timelines.append(UserHistory(size, books, ratings))
            timeline_progress.update(1)

    return timelines


def build_contexts(user: UserHistory, min_length: int, max_length: int) -> tuple:
    context_ids = []
    context_ratings = []
    label_ids = []

    for label in range(1, len(user.books)):
        pos = max(0, label - max_length)
        if (label - pos) >= min_length:
            context_id = np.array(user.books[pos:label], dtype=np.int32)
            context_id.resize(max_length)
            context_ids.append(context_id)

            context_rating = np.array(user.ratings[pos:label], dtype=np.float32)
            context_rating.resize(max_length)
            context_ratings.append(context_rating)

            label_id = np.array([user.books[label]], dtype=np.int32)
            label_ids.append(label_id)

    return context_ids, context_ratings, label_ids
