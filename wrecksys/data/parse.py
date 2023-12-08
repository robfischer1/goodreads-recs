import gc
import gzip
import logging
import pathlib
import sys

import pyarrow as pa
import pyarrow.compute as pc
import pyarrow.feather as feather
import pyarrow.json as pj
from tqdm.auto import tqdm

from wrecksys import utils

logger = logging.getLogger(__name__)

def _convert_dates(table: pa.Table) -> pa.Table:
    date_format = "%a %b %d %H:%M:%S %z %Y"
    timestamp_columns = {'date_added', 'date_updated', 'read_at', 'started_at'}
    for col in timestamp_columns:
        if col in table.column_names:
            table = table.set_column(
                table.column_names.index(col),
                col,
                pc.strptime(table.column(col), format=date_format, unit='s', error_is_null=True)
            )
    logger.info(f"Dates Converted: {utils.display_size(table.nbytes)}")
    return table


def _convert_empty_strings(table: pa.Table) -> pa.Table:
    nulls = pa.nulls(table.num_rows)
    for col in table.column_names:
        logger.debug(f"{col} column type: {table.column(col).type}, Chunks: {table.column(col).num_chunks}, Condition: {table.column(col).type == 'string'}")
        if table.column(col).type == 'string':
            cond = pc.not_equal(table.column(col), "")
            new_col = pc.if_else(cond, table.column(col), nulls)
            table = table.set_column(
                table.column_names.index(col),
                col,
                new_col
            )

    logger.info(f"Empty Strings Eliminated: {utils.display_size(table.nbytes)}")
    return table


def _convert_dtypes(table: pa.Table, columns: dict) -> pa.Table:
    for col, col_type in columns.items():
        if col in table.column_names:
            logger.debug(f"Converting column {col} to {col_type}")
            table = table.set_column(
                table.column_names.index(col),
                col,
                table.column(col).cast(col_type)
            )
    logger.info(f"Column Dtypes Converted: {utils.display_size(table.nbytes)}")
    return table


def _convert_table(table: pa.Table, columns: dict[str, pa.DataType]) -> pa.Table:
    table = _convert_empty_strings(table)
    table = _convert_dtypes(table, columns)
    table = _convert_dates(table)
    table = table.combine_chunks()
    logger.info(f"Table converted: {utils.display_size(table.nbytes)}")
    return table


def json_to_feather(file_pointer: gzip.GzipFile, file_size: int, output_file: pathlib.Path) -> None:
    dispatcher = {
        'goodreads_book_authors': author_parser,
        'goodreads_book_works': work_parser,
        'goodreads_books_fantasy_paranormal': book_parser,
        'goodreads_interactions_fantasy_paranormal': interaction_parser,
        'goodreads_reviews_fantasy_paranormal': review_parser
    }
    file_name = utils.get_file_name(str(output_file))

    with tqdm.wrapattr(file_pointer, 'read', desc='Converting: ',
                       file=sys.stdout, unit='B', unit_scale=True, total=file_size) as f:
        table: pa.Table = pj.read_json(f)
        logger.info(f"Table Loaded: {utils.display_size(table.nbytes)}")
        parse = dispatcher.get(file_name, generic_parser)
        table = parse(table)
        feather.write_feather(table, str(output_file))
        del table
        gc.collect()


def generic_parser(table: pa.Table) -> pa.Table:
    return _convert_table(table, {})


def author_parser(table: pa.Table) -> pa.Table:

    simple_columns = {
        'average_rating': pa.float32(),
        'author_id': pa.int32(),
        'text_reviews_count': pa.int32(),
        'ratings_count': pa.int32()
    }

    return _convert_table(table, simple_columns)


def book_parser(table: pa.Table) -> pa.Table:

    simple_columns = {
        'text_reviews_count': pa.int32(),
        'is_ebook': pa.bool_(),
        'average_rating': pa.float32(),
        'num_pages': pa.int32(),
        'publication_day': pa.int8(),
        'publication_month': pa.int8(),
        'publication_year': pa.int32(),
        'book_id': pa.int32(),
        'work_id': pa.int32()
    }

    return _convert_table(table, simple_columns)


def review_parser(table: pa.Table) -> pa.Table:

    col = 'user_id'
    table = table.set_column(table.column_names.index(col), col, table.column(col).dictionary_encode())

    simple_columns = {
        'book_id': pa.int32(),
        'rating': pa.int8(),
        'n_votes': pa.int32(),
        'n_comments': pa.int32()
    }

    return _convert_table(table, simple_columns)


def interaction_parser(table: pa.Table) -> pa.Table:

    col = 'user_id'
    table = table.set_column(
        table.column_names.index(col),
        col,
        pc.add(
            pc.index_in(
                table.column('user_id'),
                table.column('user_id').unique()
            ).dictionary_encode(),
            1
        )
    )
    logger.info(f"User IDs Processed: {utils.display_size(table.nbytes)}")

    table = table.append_column(
        'is_reviewed',
        pc.not_equal(table.column('review_text_incomplete'), "")
    )
    logger.info(f"Review Count: {sum(chunk.true_count for chunk in table.column('is_reviewed').iterchunks()):,}")

    simple_columns = {
        'book_id': pa.int32(),
        'rating': pa.int8(),
    }

    return _convert_table(table, simple_columns)


def work_parser(table: pa.Table) -> pa.Table:
    simple_columns = {
        'book_count': pa.int16(),
        'reviews_count': pa.int32(),
        'original_publication_month': pa.int32(),
        'text_reviews_count': pa.int32(),
        'best_book_id': pa.int32(),
        'original_publication_year': pa.int32(),
        'original_publication_day': pa.int32(),
        'ratings_count': pa.int32(),
        'ratings_sum': pa.int32(),
        'work_id': pa.int32()
    }
    return _convert_table(table, simple_columns)


def _feather_to_feather(file_name) -> None:
    logger.info(f"Logging is working at least.")
    dispatcher = {
        'goodreads_book_authors': author_parser,
        'goodreads_book_works': work_parser,
        'goodreads_books_fantasy_paranormal': book_parser,
        'goodreads_interactions_fantasy_paranormal': interaction_parser,
        'goodreads_reviews_fantasy_paranormal': review_parser
    }
    output_file = pathlib.Path(__file__).parent / f'../../data/raw/{file_name}.feather'

    table: pa.Table = feather.read_table(output_file)
    logger.info(f"Table Loaded: {utils.display_size(table.nbytes)}")
    parse = dispatcher.get(file_name, generic_parser)
    table = parse(table)
    feather.write_feather(table, output_file)